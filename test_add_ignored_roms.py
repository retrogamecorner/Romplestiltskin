#!/usr/bin/env python3
"""
Test script to add some ignored ROMs to the database for testing color coding.
"""

import sqlite3
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.rom_scanner import ROMStatus

def main():
    """Add test ignored ROMs to the database."""
    
    # Connect to the database
    db_path = Path.home() / ".romplestiltskin" / "romplestiltskin.db"
    
    if not db_path.exists():
        print(f"Database file {db_path} not found!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if scanned_roms table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='scanned_roms'
    """)
    
    if not cursor.fetchone():
        print("scanned_roms table not found!")
        conn.close()
        return
    
    # Add some test ignored ROMs with different original_status values
    test_roms = [
        {
            'file_path': '/test/missing_rom.zip',
            'crc32': 'abc12345',
            'status': ROMStatus.IGNORED.value,
            'original_status': ROMStatus.MISSING.value,
            'game_name': 'Test Missing Game'
        },
        {
            'file_path': '/test/unrecognized_rom.zip', 
            'crc32': 'def67890',
            'status': ROMStatus.IGNORED.value,
            'original_status': ROMStatus.NOT_RECOGNIZED.value,
            'game_name': 'Test Unrecognized Game'
        },
        {
            'file_path': '/test/correct_rom.zip',
            'crc32': 'ghi11111', 
            'status': ROMStatus.IGNORED.value,
            'original_status': ROMStatus.CORRECT.value,
            'game_name': 'Test Correct Game'
        }
    ]
    
    # Insert test ROMs
    for rom in test_roms:
        cursor.execute("""
            INSERT OR REPLACE INTO scanned_roms 
            (file_path, crc32, status, original_status, game_name)
            VALUES (?, ?, ?, ?, ?)
        """, (rom['file_path'], rom['crc32'], rom['status'], 
               rom['original_status'], rom['game_name']))
    
    conn.commit()
    
    # Verify the data was inserted
    cursor.execute("""
        SELECT file_path, crc32, status, original_status, game_name 
        FROM scanned_roms 
        WHERE status = ?
    """, (ROMStatus.IGNORED.value,))
    
    ignored_roms = cursor.fetchall()
    print(f"Added {len(ignored_roms)} ignored ROMs:")
    
    for rom in ignored_roms:
        file_path, crc32, status, original_status, game_name = rom
        print(f"  - {game_name} (original_status: {original_status})")
    
    conn.close()
    print("\nTest data added successfully! Now restart the application to see the color coding.")

if __name__ == "__main__":
    main()