#!/usr/bin/env python3
"""
DAT Processor for Romplestiltskin

Handles parsing of No-Intro DAT files and extraction of game information.
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from .db_manager import DatabaseManager

class DATProcessor:
    """Processes DAT files and extracts game information."""
    
    # Regular expressions for parsing game names
    REGION_REGEX = re.compile(r'\((USA|Europe|Japan|World|Germany|France|Brazil|Australia|Korea|China|Taiwan|Spain|Italy|Netherlands|Sweden|Norway|Denmark|Finland|UK|Canada|Asia|Unknown)\)')
    LANGUAGE_REGEX = re.compile(r'\((En|Fr|De|Ja|Es|It|Nl|Pt|Sv|No|Da|Fi|Zh|Ko|Pl|Ru|M\d+(?:,[A-Za-z]{2,3})*)\)')
    PROTO_REGEX = re.compile(r'\((Proto|Prototype|Sample)\)')
    BETA_REGEX = re.compile(r'\((Beta)\)')
    DEMO_REGEX = re.compile(r'\((Demo|Kiosk)\)')
    UNL_REGEX = re.compile(r'\((Unl|Unlicensed)\)')
    VERSION_REGEX = re.compile(r'\((Rev\s*[\w\d.]+|v\d[\d.]*|PRG\d+|Alt\s*\d*)\)|(\[[abcfhprstuv\d]*\])')
    DISC_REGEX = re.compile(r'\((Disc|Disk|Side)\s*([\w\d]+)\)')
    TRANSLATION_REGEX = re.compile(r'\[T\+([A-Za-z]{2,3})\]')
    VERIFIED_REGEX = re.compile(r'\[!\]')
    PIRATE_REGEX = re.compile(r'\[p\]')
    HACK_REGEX = re.compile(r'\[h\]')
    TRAINER_REGEX = re.compile(r'\[t\]')
    OVERDUMP_REGEX = re.compile(r'\[o\]')
    
    # Default language mappings for regions
    REGION_LANGUAGE_DEFAULTS = {
        'USA': 'En',
        'Europe': 'En',
        'Japan': 'Ja',
        'Germany': 'De',
        'France': 'Fr',
        'Spain': 'Es',
        'Italy': 'It',
        'Netherlands': 'Nl',
        'Brazil': 'Pt',
        'Korea': 'Ko',
        'China': 'Zh',
        'Taiwan': 'Zh',
        'UK': 'En',
        'Canada': 'En',
        'Australia': 'En',
        'World': 'En',
        'Asia': 'En'
    }
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize DAT processor.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
    
    def scan_dat_folder(self, dat_folder: str) -> List[str]:
        """Scan folder for DAT files.
        
        Args:
            dat_folder: Path to folder containing DAT files
            
        Returns:
            List of DAT file paths
        """
        dat_path = Path(dat_folder)
        if not dat_path.exists():
            return []
        
        dat_files = []
        for file_path in dat_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.dat', '.xml']:
                dat_files.append(str(file_path))
        
        return sorted(dat_files)

    def import_dat_file(self, dat_file_path: str, progress_callback: Optional[callable] = None) -> bool:
        """Import a single DAT file into the database.

        Args:
            dat_file_path: Path to the DAT file
            progress_callback: Optional callback function for progress updates (current_game, total_games)

        Returns:
            True if import was successful, False otherwise.
        """
        parsed_data = self.parse_dat_file(dat_file_path)
        if not parsed_data:
            return False

        system_id = self.db_manager.add_system(parsed_data['system_name'], dat_file_path)
        if not system_id:
            print(f"Failed to add or find system: {parsed_data['system_name']}")
            return False

        total_games = len(parsed_data['games'])
        for i, game_data in enumerate(parsed_data['games']):
            self.db_manager.add_game(system_id, game_data)
            if progress_callback:
                progress_callback(i + 1, total_games)
        
        # After processing all games for this DAT, update system game count
        self.db_manager.update_system_game_count(system_id)
        return True

    def parse_dat_file(self, dat_file_path: str) -> Optional[Dict[str, Any]]:
        """Parse a DAT file and extract system and game information.
        
        Args:
            dat_file_path: Path to the DAT file
            
        Returns:
            Dictionary containing system info and games, or None if parsing failed
        """
        try:
            tree = ET.parse(dat_file_path)
            root = tree.getroot()
            
            # Extract system information from header
            header = root.find('header')
            if header is not None:
                system_name = header.find('name')
                system_name = system_name.text if system_name is not None else Path(dat_file_path).stem
            else:
                # Fallback to filename if no header
                system_name = Path(dat_file_path).stem
            
            # Parse games
            games = []
            for game_elem in root.findall('game'):
                game_data = self._parse_game_element(game_elem)
                if game_data:
                    games.append(game_data)
            
            return {
                'system_name': system_name,
                'dat_file_path': dat_file_path,
                'games': games
            }
            
        except ET.ParseError as e:
            print(f"Error parsing DAT file {dat_file_path}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error parsing DAT file {dat_file_path}: {e}")
            return None

    def import_dat_folder(self, dat_folder: str, progress_callback: Optional[callable] = None) -> Tuple[int, int]:
        """Import all DAT files from a folder into the database.

        Args:
            dat_folder: Path to folder containing DAT files
            progress_callback: Optional callback for overall file progress (current_file, total_files)

        Returns:
            Tuple (successful_imports, total_files)
        """
        dat_files = self.scan_dat_folder(dat_folder)
        total_files = len(dat_files)
        successful_imports = 0

        for i, dat_file_path in enumerate(dat_files):
            if self.import_dat_file(dat_file_path): # We can pass a game-level progress callback here if needed
                successful_imports += 1
            if progress_callback:
                progress_callback(i + 1, total_files)

        return successful_imports, total_files
    
    def _parse_game_element(self, game_elem) -> Optional[Dict[str, Any]]:
        """Parse a single game element from DAT XML.
        
        Args:
            game_elem: XML element representing a game
            
        Returns:
            Dictionary containing game data or None if parsing failed
        """
        try:
            # Get basic game information
            dat_game_name = game_elem.get('name', '')
            clone_of_id = game_elem.get('cloneofid')
            
            # Find ROM element
            rom_elem = game_elem.find('rom')
            if rom_elem is None:
                return None
            
            dat_rom_name = rom_elem.get('name', '')
            crc32 = rom_elem.get('crc', '').lower()
            size = int(rom_elem.get('size', '0'))
            md5 = rom_elem.get('md5')
            sha1 = rom_elem.get('sha1')
            status = rom_elem.get('status')
            
            # Parse game name attributes
            parsed_attrs = self._parse_game_name(dat_game_name)
            
            # Determine if verified dump
            is_verified = (status == 'verified') or bool(self.VERIFIED_REGEX.search(dat_game_name))
            is_pirate = bool(self.PIRATE_REGEX.search(dat_game_name))
            is_hack = bool(self.HACK_REGEX.search(dat_game_name))
            is_trainer = bool(self.TRAINER_REGEX.search(dat_game_name))

            game_data = {
                'dat_game_name': dat_game_name,
                'dat_rom_name': dat_rom_name,
                'major_name': parsed_attrs['major_name'],
                'region': parsed_attrs['region'],
                'languages': parsed_attrs['languages'],
                'is_beta': parsed_attrs['is_beta'],
                'is_demo': parsed_attrs['is_demo'],
                'is_proto': parsed_attrs['is_proto'],
                'is_unlicensed': parsed_attrs['is_unlicensed'],
                'release_version': parsed_attrs['release_version'],
                'is_unofficial_translation': parsed_attrs['is_unofficial_translation'],
                'is_verified_dump': is_verified,
                'is_modified_release': parsed_attrs['is_modified_release'],
                'is_pirate': is_pirate,
                'is_hack': is_hack,
                'is_trainer': is_trainer,
                'is_overdump': parsed_attrs['is_overdump'],
                'crc32': crc32,
                'size': size,
                'md5': md5,
                'sha1': sha1,
                'clone_of_id_string': clone_of_id,
                'disc_info': parsed_attrs['disc_info']
            }
            
            return game_data
            
        except Exception as e:
            print(f"Error parsing game element: {e}")
            return None
    
    def _parse_game_name(self, game_name: str) -> Dict[str, Any]:
        """Parse game name to extract attributes.
        
        Args:
            game_name: Full game name from DAT file
            
        Returns:
            Dictionary containing parsed attributes
        """
        # Initialize default values
        attrs = {
            'major_name': '',
            'region': None,
            'languages': None,
            'is_beta': False,
            'is_demo': False,
            'is_proto': False,
            'is_unlicensed': False,
            'release_version': 0,
            'is_unofficial_translation': False,
            'is_modified_release': False,
            'is_overdump': False,
            'disc_info': None
        }
        
        # Extract major name (text before first parenthesis)
        major_match = re.match(r'^([^(]+)', game_name)
        if major_match:
            attrs['major_name'] = major_match.group(1).strip()
        else:
            attrs['major_name'] = game_name
        
        # Extract region
        region_match = self.REGION_REGEX.search(game_name)
        if region_match:
            attrs['region'] = region_match.group(1)
        
        # Extract languages
        language_match = self.LANGUAGE_REGEX.search(game_name)
        if language_match:
            attrs['languages'] = language_match.group(1)
        else:
            # Set default language based on region if no explicit language found
            if attrs['region'] and attrs['region'] in self.REGION_LANGUAGE_DEFAULTS:
                attrs['languages'] = self.REGION_LANGUAGE_DEFAULTS[attrs['region']]
            else:
                # If no region or unknown region, try to infer from common patterns
                if any(pattern in game_name.lower() for pattern in ['usa', 'us', 'america']):
                    attrs['languages'] = 'En'
                elif any(pattern in game_name.lower() for pattern in ['japan', 'jp', 'jap']):
                    attrs['languages'] = 'Ja'
                elif any(pattern in game_name.lower() for pattern in ['europe', 'eu', 'eur']):
                    attrs['languages'] = 'En'  # Default to English for Europe
                else:
                    attrs['languages'] = 'En'  # Default to English instead of Unknown
        
        # Check for beta
        attrs['is_beta'] = bool(self.BETA_REGEX.search(game_name))
        
        # Check for demo
        attrs['is_demo'] = bool(self.DEMO_REGEX.search(game_name))
        
        # Check for prototype
        attrs['is_proto'] = bool(self.PROTO_REGEX.search(game_name))
        
        # Check for unlicensed
        attrs['is_unlicensed'] = bool(self.UNL_REGEX.search(game_name))
        
        # Extract release version
        attrs['release_version'] = self._parse_release_version(game_name)
        
        # Check for unofficial translation
        translation_match = self.TRANSLATION_REGEX.search(game_name)
        attrs['is_unofficial_translation'] = bool(translation_match)
        
        # Check for modified releases
        is_pirate = bool(self.PIRATE_REGEX.search(game_name))
        is_hack = bool(self.HACK_REGEX.search(game_name))
        is_trainer = bool(self.TRAINER_REGEX.search(game_name))
        attrs['is_modified_release'] = is_pirate or is_hack or is_trainer
        
        # Check for overdump
        attrs['is_overdump'] = bool(self.OVERDUMP_REGEX.search(game_name))
        
        # Extract disc information
        disc_match = self.DISC_REGEX.search(game_name)
        if disc_match:
            attrs['disc_info'] = f"{disc_match.group(1)} {disc_match.group(2)}"
        
        return attrs
    
    def _parse_release_version(self, game_name: str) -> int:
        """Parse release version from game name.
        
        Args:
            game_name: Full game name
            
        Returns:
            Numerical version (0 for base game, 1+ for revisions)
        """
        # Look for revision patterns
        version_patterns = [
            (r'\(Rev\s*A\)', 1),
            (r'\(Rev\s*B\)', 2),
            (r'\(Rev\s*C\)', 3),
            (r'\(Rev\s*D\)', 4),
            (r'\(Rev\s*(\d+)\)', lambda m: int(m.group(1))),
            (r'\(v1\.(\d+)\)', lambda m: int(m.group(1))),
            (r'\(PRG(\d+)\)', lambda m: int(m.group(1))),
            (r'\[a\]', 1),
            (r'\[b\]', 2),
            (r'\[c\]', 3),
            (r'\(Alt\s*(\d+)\)', lambda m: int(m.group(1))),
        ]
        
        for pattern, version in version_patterns:
            match = re.search(pattern, game_name, re.IGNORECASE)
            if match:
                if callable(version):
                    return version(match)
                else:
                    return version
        
        return 0  # Base version    

    
    def import_dat_folder(self, dat_folder: str) -> Tuple[int, int]:
        """Import all DAT files from a folder.
        
        Args:
            dat_folder: Path to folder containing DAT files
            
        Returns:
            Tuple of (successful_imports, total_files)
        """
        dat_files = self.scan_dat_folder(dat_folder)
        successful = 0
        
        for dat_file in dat_files:
            if self.import_dat_file(dat_file):
                successful += 1
        
        return successful, len(dat_files)
