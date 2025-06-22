#!/usr/bin/env python3
"""
ROM Scanner for Romplestiltskin

Handles scanning ROM folders, calculating checksums, and verifying ROMs against DAT data.
"""

import os
import zlib
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable
from enum import Enum
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from .db_manager import DatabaseManager

try:
    from Levenshtein import distance as levenshtein_distance
except ImportError:
    # Fallback implementation if python-Levenshtein is not available
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Simple Levenshtein distance implementation."""
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

class ROMStatus(Enum):
    """ROM verification status."""
    CORRECT = "correct"  # ROM present, name matches DAT, CRC matches DAT
    WRONG_FILENAME = "wrong_filename"  # ROM present, CRC matches DAT, filename differs
    BROKEN = "broken"  # Found locally, CRC mismatch or unreadable
    NOT_RECOGNIZED = "not_recognized"  # Found locally, no match in DAT
    MISSING = "missing"  # In DAT, not found locally
    DUPLICATE = "duplicate"  # Multiple files with same CRC
    MOVED_EXTRA = "moved_extra"  # Unrecognized file moved to an 'extra' folder
    IGNORED = "ignored"  # User-marked as to be ignored
    MOVED_BROKEN = "moved_broken" # Broken file moved to a 'broken' folder

@dataclass
class ROMScanResult:
    """Result of ROM scanning operation."""
    file_path: str
    file_size: int
    calculated_crc32: Optional[str]
    status: ROMStatus
    system_id: int  # Added to associate scan result with a system
    matched_game: Optional[Dict[str, Any]] = None
    similarity_score: float = 0.0
    error_message: Optional[str] = None

class ROMScanner:
    """Scans ROM folders and verifies ROMs against DAT data."""
    
    def __init__(self, db_manager: DatabaseManager, chunk_size: int = 64 * 1024 * 1024):
        """Initialize ROM scanner.
        
        Args:
            db_manager: Database manager instance
            chunk_size: Chunk size for reading files (default 64MB)
        """
        self.db_manager = db_manager
        self.chunk_size = chunk_size
        self.supported_extensions = {
            '.zip', '.7z', '.rar',  # Archives
            '.bin', '.rom', '.img',  # Generic ROM formats
            '.nes', '.smc', '.sfc', '.gb', '.gbc', '.gba',  # Nintendo
            '.md', '.smd', '.gen', '.32x',  # Sega
            '.a26', '.a52', '.a78',  # Atari
            '.pce', '.tg16',  # PC Engine/TurboGrafx
            '.ngp', '.ngc',  # Neo Geo Pocket
            '.ws', '.wsc',  # WonderSwan
            '.chd', '.cue', '.iso', '.pbp',  # Disc formats
            '.n64', '.z64', '.v64',  # Nintendo 64
            '.nds', '.3ds',  # Nintendo DS/3DS
            '.psp', '.cso'  # PSP
        }
    
    def calculate_crc32(self, file_path: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> Optional[str]:
        """Calculate CRC32 checksum of a file.
        
        Args:
            file_path: Path to the file
            progress_callback: Optional callback for progress updates (bytes_read, total_size)
            
        Returns:
            CRC32 checksum as hex string, or None if error
        """
        try:
            crc = 0
            file_size = os.path.getsize(file_path)
            bytes_read = 0
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    crc = zlib.crc32(chunk, crc)
                    bytes_read += len(chunk)
                    
                    if progress_callback:
                        progress_callback(bytes_read, file_size)
            
            # Ensure unsigned 32-bit value
            return f"{crc & 0xFFFFFFFF:08x}"
            
        except (IOError, OSError) as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def scan_file(self, file_path: str, system_id: int) -> ROMScanResult:
        """Scan a single ROM file.
        
        Args:
            file_path: Path to the ROM file
            system_id: ID of the system to match against
            
        Returns:
            ROMScanResult object
        """
        try:
            file_size = os.path.getsize(file_path)
            
            # Calculate CRC32
            calculated_crc = self.calculate_crc32(file_path)
            if calculated_crc is None:
                return ROMScanResult(
                    file_path=file_path,
                    file_size=file_size,
                    calculated_crc32=None,
                    status=ROMStatus.BROKEN,
                    system_id=system_id,
                    error_message="Could not read file"
                )
            
            # Try to match by CRC32 and size
            matched_game = self.db_manager.get_game_by_crc(system_id, calculated_crc, file_size)
            
            if matched_game:
                # Check if filename matches
                filename = Path(file_path).name
                expected_filename = matched_game['dat_rom_name']
                
                if filename.lower() == expected_filename.lower():
                    status = ROMStatus.CORRECT
                else:
                    status = ROMStatus.WRONG_FILENAME
                
                return ROMScanResult(
                    file_path=file_path,
                    file_size=file_size,
                    calculated_crc32=calculated_crc,
                    status=status,
                    system_id=system_id,
                    matched_game=matched_game,
                    similarity_score=1.0
                )
            
            # No CRC match, try filename similarity
            filename = Path(file_path).stem  # Without extension
            similar_games = self.db_manager.search_games_by_filename(system_id, filename, limit=5)
            
            best_match = None
            best_similarity = 0.0
            
            for game in similar_games:
                # Calculate similarity with both dat_rom_name and major_name
                rom_name_sim = self._calculate_filename_similarity(filename, Path(game['dat_rom_name']).stem)
                major_name_sim = self._calculate_filename_similarity(filename, game['major_name'])
                similarity = max(rom_name_sim, major_name_sim)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = game
            
            # If we found a reasonably similar match, mark as broken (wrong CRC)
            if best_match and best_similarity > 0.7:
                return ROMScanResult(
                    file_path=file_path,
                    file_size=file_size,
                    calculated_crc32=calculated_crc,
                    status=ROMStatus.BROKEN,
                    system_id=system_id,
                    matched_game=best_match,
                    similarity_score=best_similarity
                )
            
            # No good match found
            return ROMScanResult(
                file_path=file_path,
                file_size=file_size,
                system_id=system_id,
                calculated_crc32=calculated_crc,
                status=ROMStatus.NOT_RECOGNIZED,
                similarity_score=best_similarity
            )
            
        except Exception as e:
            return ROMScanResult(
                file_path=file_path,
                file_size=0,
                system_id=system_id,
                calculated_crc32=None,
                status=ROMStatus.BROKEN,
                error_message=str(e)
            )
    
    def _calculate_filename_similarity(self, filename1: str, filename2: str) -> float:
        """Calculate similarity between two filenames.
        
        Args:
            filename1: First filename
            filename2: Second filename
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Normalize filenames
        name1 = filename1.lower().strip()
        name2 = filename2.lower().strip()
        
        if name1 == name2:
            return 1.0
        
        # Calculate Levenshtein distance
        max_len = max(len(name1), len(name2))
        if max_len == 0:
            return 1.0
        
        distance = levenshtein_distance(name1, name2)
        similarity = 1.0 - (distance / max_len)
        
        return max(0.0, similarity)
    
    def scan_folder(self, folder_path: str, system_id: int, 
                   progress_callback: Optional[Callable[[int, int], None]] = None,
                   max_workers: int = 4) -> List[ROMScanResult]:
        """Scan a folder for ROM files.
        
        Args:
            folder_path: Path to the ROM folder
            system_id: ID of the system to match against
            progress_callback: Optional callback for progress updates (current, total)
            max_workers: Maximum number of worker threads
            
        Returns:
            List of ROMScanResult objects
        """
        folder = Path(folder_path)
        if not folder.exists():
            print(f"ROM Scanner: Folder does not exist: {folder}")
            return []
        
        print(f"ROM Scanner: Scanning folder: {folder}")
        print(f"ROM Scanner: Supported extensions: {self.supported_extensions}")
        
        # Find all ROM files (excluding special subfolders)
        rom_files = []
        excluded_folders = {'broken', '_broken', 'extra', '_extra', 'filtered', '_filtered', 'multi', '_multi'}
        
        for file_path in folder.glob('*'):  # Changed rglob to glob
            if file_path.is_file():
                # No need to check for excluded subfolders if not scanning recursively
                print(f"ROM Scanner: Found file: {file_path} (extension: {file_path.suffix.lower()})")
                if file_path.suffix.lower() in self.supported_extensions:
                    rom_files.append(str(file_path))
                    print(f"ROM Scanner: Added ROM file: {file_path}")
        
        print(f"ROM Scanner: Found {len(rom_files)} ROM files")
        if not rom_files:
            return []
        
        results = []
        completed = 0
        
        # Use thread pool for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.scan_file, file_path, system_id): file_path
                for file_path in rom_files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    if progress_callback:
                        progress_callback(completed, len(rom_files))
                        
                except Exception as e:
                    file_path = future_to_file[future]
                    print(f"Error scanning {file_path}: {e}")
                    results.append(ROMScanResult(
                        file_path=file_path,
                        file_size=0,
                        system_id=system_id,
                        calculated_crc32=None,
                        status=ROMStatus.BROKEN,
                        error_message=str(e)
                    ))
                    completed += 1
                    
                    if progress_callback:
                        progress_callback(completed, len(rom_files))
        
        return results
    
    def find_missing_roms(self, system_id: int, scanned_results: List[ROMScanResult]) -> List[Dict[str, Any]]:
        """Find ROMs that are in the DAT but missing from the scanned folder.
        
        Args:
            system_id: ID of the system
            scanned_results: Results from scanning ROM folder
            
        Returns:
            List of missing game data
        """
        # Get all games for the system
        all_games = self.db_manager.get_games_by_system(system_id)
        
        # Get CRCs of found ROMs
        found_crcs = set()
        for result in scanned_results:
            if result.status in [ROMStatus.CORRECT, ROMStatus.WRONG_FILENAME]:
                if result.matched_game:
                    found_crcs.add(result.matched_game['crc32'])
        
        # Find missing games
        missing_games = []
        for game in all_games:
            if game['crc32'] not in found_crcs:
                missing_games.append(game)
        
        return missing_games
    
    def get_scan_summary(self, results: List[ROMScanResult]) -> Dict[str, int]:
        """Get summary statistics from scan results.
        
        Args:
            results: List of scan results
            
        Returns:
            Dictionary with count statistics
        """
        summary = {
            'total_files': len(results),
            'correct': 0,
            'wrong_filename': 0,
            'broken': 0,
            'not_recognized': 0,
            'duplicates': 0
        }
        
        # Count by status
        for result in results:
            if result.status == ROMStatus.CORRECT:
                summary['correct'] += 1
            elif result.status == ROMStatus.WRONG_FILENAME:
                summary['wrong_filename'] += 1
            elif result.status == ROMStatus.BROKEN:
                summary['broken'] += 1
            elif result.status == ROMStatus.NOT_RECOGNIZED:
                summary['not_recognized'] += 1
            elif result.status == ROMStatus.DUPLICATE:
                summary['duplicates'] += 1
        
        return summary
    
    def find_duplicates(self, results: List[ROMScanResult]) -> List[List[ROMScanResult]]:
        """Find duplicate ROMs (same CRC32).
        
        Args:
            results: List of scan results
            
        Returns:
            List of lists, each containing duplicate ROM results
        """
        crc_groups = {}
        
        for result in results:
            if result.calculated_crc32 and result.status != ROMStatus.BROKEN:
                crc = result.calculated_crc32
                if crc not in crc_groups:
                    crc_groups[crc] = []
                crc_groups[crc].append(result)
        
        # Return only groups with more than one file
        duplicates = [group for group in crc_groups.values() if len(group) > 1]
        
        return duplicates