#!/usr/bin/env python3
"""
Scanned ROMs Manager for Romplestiltskin

Manages persistent storage of scanned ROM data to enable filtering across all ROM tabs.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from .rom_scanner import ROMScanResult, ROMStatus


class ScannedROMsManager:
    """Manages persistent storage of scanned ROM data."""
    
    def __init__(self, db_path: str):
        """Initialize the scanned ROMs manager.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize the scanned ROMs table."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create scanned_roms table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scanned_roms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    system_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    calculated_crc32 TEXT,
                    status TEXT NOT NULL,
                    matched_game_id INTEGER,
                    similarity_score REAL,
                    error_message TEXT,
                    original_status TEXT,
                    scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (system_id) REFERENCES systems (id) ON DELETE CASCADE,
                    FOREIGN KEY (matched_game_id) REFERENCES games (id) ON DELETE SET NULL,
                    UNIQUE(system_id, file_path)
                )
            """)
            
            # Add original_status column if it doesn't exist (for existing databases)
            try:
                cursor.execute("ALTER TABLE scanned_roms ADD COLUMN original_status TEXT")
                conn.commit()
            except sqlite3.OperationalError:
                # Column already exists
                pass
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_scanned_roms_system_id ON scanned_roms(system_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_scanned_roms_status ON scanned_roms(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_scanned_roms_crc32 ON scanned_roms(calculated_crc32)
            """)
            
            conn.commit()

    def update_rom_status(self, system_id: int, new_status: ROMStatus, file_path: Optional[str] = None, crc32: Optional[str] = None, original_status: Optional[ROMStatus] = None):
        """Update the status of a specific ROM file using file_path or crc32.

        Args:
            system_id: ID of the system
            new_status: The new ROMStatus for the file
            file_path: Path to the ROM file (optional)
            crc32: CRC32 of the ROM file (optional)
            original_status: The original status before changing to ignored (optional)
        """
        if not file_path and not crc32:
            raise ValueError("Either file_path or crc32 must be provided")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if file_path:
                if original_status:
                    query = """
                        UPDATE scanned_roms
                        SET status = ?, original_status = ?
                        WHERE system_id = ? AND file_path = ?
                    """
                    cursor.execute(query, (new_status.value, original_status.value, system_id, file_path))
                else:
                    query = """
                        UPDATE scanned_roms
                        SET status = ?
                        WHERE system_id = ? AND file_path = ?
                    """
                    cursor.execute(query, (new_status.value, system_id, file_path))
            elif crc32:
                if original_status:
                    query = """
                        UPDATE scanned_roms
                        SET status = ?, original_status = ?
                        WHERE system_id = ? AND calculated_crc32 = ?
                    """
                    cursor.execute(query, (new_status.value, original_status.value, system_id, crc32))
                else:
                    query = """
                        UPDATE scanned_roms
                        SET status = ?
                        WHERE system_id = ? AND calculated_crc32 = ?
                    """
                    cursor.execute(query, (new_status.value, system_id, crc32))
            conn.commit()

    def update_rom_path(self, system_id: int, old_file_path: str, new_file_path: str):
        """Update the file path of a specific ROM file.

        Args:
            system_id: ID of the system
            old_file_path: The current path to the ROM file
            new_file_path: The new path for the ROM file
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scanned_roms
                SET file_path = ?
                WHERE system_id = ? AND file_path = ?
            """, (new_file_path, system_id, old_file_path))
            conn.commit()
    
    def add_rom(self, system_id: int, status: ROMStatus, file_path: Optional[str] = None, file_size: Optional[int] = None, crc32: Optional[str] = None, original_status: Optional[ROMStatus] = None):
        """Add a new ROM entry, typically for missing or ignored ROMs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO scanned_roms (system_id, file_path, file_size, calculated_crc32, status, original_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            # Use placeholder for file_path if not provided, to satisfy NOT NULL constraint
            final_file_path = file_path if file_path is not None else f"missing_{crc32}"
            final_file_size = file_size if file_size is not None else 0
            
            params = (
                system_id,
                final_file_path,
                final_file_size,
                crc32,
                status.value,
                original_status.value if original_status else None
            )
            cursor.execute(query, params)
            conn.commit()

    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def clear_system_scans(self, system_id: int):
        """Clear all scanned ROM data for a specific system.
        
        Args:
            system_id: ID of the system to clear
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scanned_roms WHERE system_id = ?", (system_id,))
            conn.commit()

    def store_scan_results(self, system_id: int, results: List[ROMScanResult]):
        """Store scan results in the database.
        
        Args:
            system_id: ID of the system being scanned
            results: List of scan results to store
        """
        # First clear existing scans for this system
        self.clear_system_scans(system_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for result in results:
                # Get matched game ID if available
                matched_game_id = None
                if result.matched_game and 'id' in result.matched_game:
                    matched_game_id = result.matched_game['id']
                
                cursor.execute("""
                    INSERT OR REPLACE INTO scanned_roms (
                        system_id, file_path, file_size, calculated_crc32, status,
                        matched_game_id, similarity_score, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    system_id,
                    result.file_path,
                    result.file_size,
                    result.calculated_crc32,
                    result.status.value,
                    matched_game_id,
                    getattr(result, 'similarity_score', None),
                    getattr(result, 'error_message', None)
                ))
            
            conn.commit()
    
    def get_scanned_roms_by_status(self, system_id: int, status: ROMStatus) -> List[Dict[str, Any]]:
        """Get scanned ROMs by status for a specific system.
        
        Args:
            system_id: ID of the system
            status: ROM status to filter by
            
        Returns:
            List of scanned ROM records
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sr.*, g.major_name, g.region, g.languages, g.dat_rom_name
                FROM scanned_roms sr
                LEFT JOIN games g ON sr.matched_game_id = g.id
                WHERE sr.system_id = ? AND sr.status = ?
                ORDER BY sr.file_path
            """, (system_id, status.value))
            
            return [dict(row) for row in cursor.fetchall()]

    def get_all_scanned_roms(self, system_id: int) -> List[Dict[str, Any]]:
        """Get all scanned ROMs for a specific system.
        
        Args:
            system_id: ID of the system
            
        Returns:
            List of all scanned ROM records
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sr.*, g.major_name, g.region, g.languages, g.dat_rom_name, g.crc32 as matched_game_crc32
                FROM scanned_roms sr
                LEFT JOIN games g ON sr.matched_game_id = g.id
                WHERE sr.system_id = ?
                ORDER BY sr.file_path
            """, (system_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_scanned_roms_with_matched_games(self, system_id: int, visible_game_crcs: set) -> List[Dict[str, Any]]:
        """Get scanned ROMs that have matched games visible in the current DAT filter.
        
        Args:
            system_id: ID of the system
            visible_game_crcs: Set of CRC32 values that are visible in the filtered DAT
            
        Returns:
            List of scanned ROM records with visible matched games
        """
        if not visible_game_crcs:
            return []
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create placeholders for the IN clause
            placeholders = ','.join('?' * len(visible_game_crcs))
            
            cursor.execute(f"""
                SELECT sr.*, g.major_name, g.region, g.languages, g.dat_rom_name
                FROM scanned_roms sr
                INNER JOIN games g ON sr.matched_game_id = g.id
                WHERE sr.system_id = ? AND g.crc32 IN ({placeholders})
                ORDER BY sr.file_path
            """, [system_id] + list(visible_game_crcs))
            
            return [dict(row) for row in cursor.fetchall()]

    def get_rom_by_crc32(self, system_id: int, crc32: str) -> Optional[Dict[str, Any]]:
        """Get a ROM by its CRC32 value for a specific system.
        
        Args:
            system_id: ID of the system
            crc32: CRC32 value of the ROM
            
        Returns:
            ROM record or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT sr.*, g.major_name, g.region, g.languages, g.dat_rom_name
                FROM scanned_roms sr
                LEFT JOIN games g ON sr.matched_game_id = g.id
                WHERE sr.system_id = ? AND sr.calculated_crc32 = ?
            """
            cursor.execute(query, (system_id, crc32))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                return None
            
    def get_scan_summary(self, system_id: int) -> Dict[str, int]:
        """Get summary statistics for scanned ROMs.
        
        Args:
            system_id: ID of the system
            
        Returns:
            Dictionary with scan statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM scanned_roms
                WHERE system_id = ?
                GROUP BY status
            """, (system_id,))
            
            summary = {
                'total': 0,
                'correct': 0,
                'wrong_filename': 0,
                'broken': 0,
                'not_recognized': 0,
                'duplicate': 0
            }
            
            for row in cursor.fetchall():
                status = row['status']
                count = row['count']
                summary['total'] += count
                
                if status == ROMStatus.CORRECT.value:
                    summary['correct'] = count
                elif status == ROMStatus.WRONG_FILENAME.value:
                    summary['wrong_filename'] = count
                elif status == ROMStatus.BROKEN.value:
                    summary['broken'] = count
                elif status == ROMStatus.NOT_RECOGNIZED.value:
                    summary['not_recognized'] = count
                elif status == ROMStatus.DUPLICATE.value:
                    summary['duplicate'] = count
            
            return summary