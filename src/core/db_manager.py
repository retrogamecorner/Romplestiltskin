#!/usr/bin/env python3
"""
Database Manager for Romplestiltskin

Handles SQLite database operations, schema creation, and CRUD operations.
"""

import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager

class DatabaseManager:
    """Manages SQLite database operations for ROM and system data."""
    
    def __init__(self, db_path: str):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize database with required tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create Systems table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS systems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    system_name TEXT UNIQUE NOT NULL,
                    dat_file_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create Games table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    system_id INTEGER NOT NULL,
                    dat_game_name TEXT NOT NULL,
                    dat_rom_name TEXT NOT NULL,
                    major_name TEXT NOT NULL,
                    region TEXT,
                    languages TEXT,
                    is_beta BOOLEAN DEFAULT 0,
                    is_demo BOOLEAN DEFAULT 0,
                    is_proto BOOLEAN DEFAULT 0,
                    is_unlicensed BOOLEAN DEFAULT 0,
                    release_version INTEGER DEFAULT 0,
                    is_unofficial_translation BOOLEAN DEFAULT 0,
                    is_verified_dump BOOLEAN DEFAULT 0,
                    is_modified_release BOOLEAN DEFAULT 0,
                    is_pirate BOOLEAN DEFAULT 0,
                    is_hack BOOLEAN DEFAULT 0,
                    is_trainer BOOLEAN DEFAULT 0,
                    is_overdump BOOLEAN DEFAULT 0,
                    crc32 TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    md5 TEXT,
                    sha1 TEXT,
                    clone_of_id_string TEXT,
                    disc_info TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (system_id) REFERENCES systems (id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_games_system_id ON games(system_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_games_crc32 ON games(crc32)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_games_major_name ON games(major_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_games_region ON games(region)
            """)
            
            # Add a column to systems table to store game count
            try:
                cursor.execute("ALTER TABLE systems ADD COLUMN game_count INTEGER DEFAULT 0")
            except sqlite3.OperationalError as e:
                if 'duplicate column name' not in str(e).lower(): # pragma: no cover
                    raise # Re-raise if it's not a 'duplicate column' error
            
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
    
    def add_system(self, system_name: str, dat_file_path: str) -> int:
        """Add a new system to the database.
        
        Args:
            system_name: Name of the system
            dat_file_path: Path to the DAT file
            
        Returns:
            System ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO systems (system_name, dat_file_path, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (system_name, dat_file_path))
            conn.commit()
            return cursor.lastrowid
    
    def get_system_by_name(self, system_name: str) -> Optional[Dict[str, Any]]:
        """Get system by name.
        
        Args:
            system_name: Name of the system
            
        Returns:
            System data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM systems WHERE system_name = ?
            """, (system_name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_systems(self) -> List[Dict[str, Any]]:
        """Get all systems from the database.
        
        Returns:
            List of system data dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM systems ORDER BY system_name
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_system(self, system_id: int) -> None:
        """Delete a system and all its games.
        
        Args:
            system_id: ID of the system to delete
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM systems WHERE id = ?", (system_id,))
            conn.commit()

    def update_system_game_count(self, system_id: int) -> None:
        """Update the game count for a specific system."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM games WHERE system_id = ?", (system_id,))
            count = cursor.fetchone()[0]
            cursor.execute("UPDATE systems SET game_count = ? WHERE id = ?", (count, system_id))
            conn.commit()
    
    def add_game(self, system_id: int, game_data: Dict[str, Any]) -> int:
        """Add a new game to the database.
        
        Args:
            game_data: Dictionary containing game information
            
        Returns:
            Game ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Prepare the SQL statement
            columns = [
                'dat_game_name', 'dat_rom_name', 'major_name',
                'region', 'languages', 'is_beta', 'is_demo', 'is_proto',
                'is_unlicensed', 'release_version', 'is_unofficial_translation',
                'is_verified_dump', 'is_modified_release', 
                'is_pirate', 'is_hack', 'is_trainer', # Added new columns
                'is_overdump',
                'crc32', 'size', 'md5', 'sha1', 'clone_of_id_string', 'disc_info'
            ]
            
            # Prepend system_id to the list of columns for the INSERT statement
            insert_columns = ['system_id'] + columns
            placeholders = ', '.join(['?' for _ in insert_columns])
            
            # Prepare values, starting with system_id
            values = [system_id] + [game_data.get(col) for col in columns]
            
            cursor.execute(f"""
                INSERT INTO games ({', '.join(insert_columns)})
                VALUES ({placeholders})
            """, values)
            
            conn.commit()
            return cursor.lastrowid
    
    def get_games_by_system(self, system_id: int) -> List[Dict[str, Any]]:
        """Get all games for a specific system.
        
        Args:
            system_id: ID of the system
            
        Returns:
            List of game data dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM games WHERE system_id = ? ORDER BY major_name, region
            """, (system_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_game_by_crc(self, system_id: int, crc32: str, size: int) -> Optional[Dict[str, Any]]:
        """Get game by CRC32 and size.
        
        Args:
            system_id: System ID
            crc32: CRC32 checksum
            size: File size
            
        Returns:
            Game data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM games 
                WHERE system_id = ? AND crc32 = ? AND size = ?
            """, (system_id, crc32.lower(), size))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def search_games_by_filename(self, system_id: int, filename: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search games by filename similarity.
        
        Args:
            system_id: ID of the system
            filename: Filename to search for
            limit: Maximum number of results
            
        Returns:
            List of game data dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Simple LIKE search - can be enhanced with fuzzy matching
            search_term = f"%{filename}%"
            cursor.execute("""
                SELECT * FROM games 
                WHERE system_id = ? AND (dat_rom_name LIKE ? OR major_name LIKE ?)
                ORDER BY major_name
                LIMIT ?
            """, (system_id, search_term, search_term, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def clear_system_games(self, system_id: int) -> None:
        """Clear all games for a specific system.
        
        Args:
            system_id: ID of the system
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM games WHERE system_id = ?", (system_id,))
            conn.commit()
    
    def get_game_count_by_system(self, system_id: int) -> int:
        """Get the number of games for a specific system.
        
        Args:
            system_id: ID of the system
            
        Returns:
            Number of games
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM games WHERE system_id = ?
            """, (system_id,))
            return cursor.fetchone()[0]
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM systems")
            system_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM games")
            game_count = cursor.fetchone()[0]
            
            return {
                'systems': system_count,
                'games': game_count
            }