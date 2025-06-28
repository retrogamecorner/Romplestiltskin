#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.scanned_roms_manager import ScannedROMsManager, ROMStatus
from core.db_manager import DatabaseManager

def test_missing_ignore():
    """Test adding and retrieving missing ignored ROMs."""
    
    # Initialize managers
    db_path = os.path.expanduser('~/.romplestiltskin/romplestiltskin.db')
    scanned_roms_manager = ScannedROMsManager(db_path)
    
    # Test system ID (assuming 1 exists)
    system_id = 1
    test_crc32 = "12345678"
    
    print("Testing missing ROM ignore functionality...")
    
    # Add a missing ROM as ignored
    print(f"Adding missing ROM with CRC32: {test_crc32}")
    try:
        scanned_roms_manager.add_rom(
            system_id=system_id,
            status=ROMStatus.IGNORED,
            file_path=None,
            file_size=None,
            crc32=test_crc32,
            original_status=ROMStatus.MISSING
        )
        print("Successfully added missing ROM to ignored list")
    except Exception as e:
        print(f"Error adding missing ROM: {e}")
        return
    
    # Retrieve ignored ROMs
    print("Retrieving ignored ROMs...")
    try:
        ignored_roms = scanned_roms_manager.get_scanned_roms_by_status(
            system_id, ROMStatus.IGNORED
        )
        print(f"Found {len(ignored_roms)} ignored ROMs:")
        for rom in ignored_roms:
            print(f"  - File: {rom['file_path']}, CRC32: {rom['calculated_crc32']}, Original Status: {rom.get('original_status')}")
    except Exception as e:
        print(f"Error retrieving ignored ROMs: {e}")
    
    # Clean up - remove the test ROM
    print("Cleaning up test data...")
    try:
        with scanned_roms_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM scanned_roms WHERE system_id = ? AND calculated_crc32 = ?",
                (system_id, test_crc32)
            )
            conn.commit()
            print("Test data cleaned up")
    except Exception as e:
        print(f"Error cleaning up: {e}")

if __name__ == "__main__":
    test_missing_ignore()