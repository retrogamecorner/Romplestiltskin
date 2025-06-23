#!/usr/bin/env python3
"""
Debug script to test color coding logic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.scanned_roms_manager import ScannedROMsManager
from core.rom_scanner import ROMStatus
from pathlib import Path

def debug_color_coding():
    """Debug the color coding functionality."""
    
    # Check for database files in current directory and common locations
    possible_db_paths = [
        "roms.db",
        "romplestiltskin.db", 
        Path.home() / ".romplestiltskin" / "romplestiltskin.db",
        "src/romplestiltskin.db"
    ]
    
    db_path = None
    for path in possible_db_paths:
        if Path(path).exists():
            db_path = path
            print(f"Found database at: {path}")
            break
    
    if db_path is None:
        print("No database file found in any of these locations:")
        for path in possible_db_paths:
            print(f"  - {path}")
        return
    
    scanned_roms_manager = ScannedROMsManager(db_path)
    
    # Get all ignored ROMs
    with scanned_roms_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT calculated_crc32, status, original_status, file_path
            FROM scanned_roms 
            WHERE status = 'ignored'
        """)
        ignored_roms = cursor.fetchall()
    
    print(f"Found {len(ignored_roms)} ignored ROMs:")
    for rom in ignored_roms:
        crc32, status, original_status, file_path = rom
        print(f"  CRC32: {crc32}, Status: {status}, Original Status: {original_status}, File: {file_path}")
        
        # Test the color coding logic
        if original_status == 'missing':
            print(f"    -> Should be YELLOW (#f2d712)")
        elif original_status == 'not_recognized':
            print(f"    -> Should be ORANGE (#ff993c)")
        else:
            print(f"    -> No color (original_status: '{original_status}')")
    
    # Also check the ROMStatus enum values
    print(f"\nROMStatus enum values:")
    print(f"  MISSING: '{ROMStatus.MISSING.value}'")
    print(f"  NOT_RECOGNIZED: '{ROMStatus.NOT_RECOGNIZED.value}'")
    print(f"  IGNORED: '{ROMStatus.IGNORED.value}'")

if __name__ == "__main__":
    debug_color_coding()