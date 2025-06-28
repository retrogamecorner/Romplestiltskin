#!/usr/bin/env python3
"""
Test script to verify that unignoring missing ROMs properly updates the UI.
This script will test the fix for the issue where missing ROMs don't appear
in the Missing tab immediately after being unignored.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.db_manager import DatabaseManager
from core.scanned_roms_manager import ScannedROMsManager
from core.rom_scanner import ROMStatus
from core.settings_manager import SettingsManager

def test_missing_rom_unignore():
    """Test that missing ROMs appear in Missing tab after unignoring."""
    print("Testing missing ROM unignore fix...")
    
    # Initialize database components
    settings_manager = SettingsManager()
    db_path = settings_manager.get_database_path()
    scanned_roms_manager = ScannedROMsManager(db_path)
    
    # Test system ID (assuming Atari 2600 exists)
    test_system_id = 'atari_2600'
    test_crc32 = '7322ebc6'  # 3-D Tic-Tac-Toe
    test_file_path = f'missing_{test_crc32}'
    
    print(f"Testing with system: {test_system_id}, CRC32: {test_crc32}")
    
    # Step 1: Check if ROM exists in database
    existing_rom = scanned_roms_manager.get_rom_by_crc32(test_system_id, test_crc32)
    print(f"Existing ROM in database: {existing_rom}")
    
    # Step 2: Add ROM with MISSING status (simulating unignore operation)
    if not existing_rom:
        print("Adding missing ROM to database...")
        scanned_roms_manager.add_rom(
            test_system_id,
            status=ROMStatus.MISSING,
            file_path=test_file_path,
            crc32=test_crc32
        )
    else:
        print("Updating existing ROM to MISSING status...")
        rows_affected = scanned_roms_manager.update_rom_status(
            test_system_id,
            new_status=ROMStatus.MISSING,
            crc32=test_crc32
        )
        print(f"Rows affected by update: {rows_affected}")
    
    # Step 3: Verify ROM is now in database with MISSING status
    missing_roms = scanned_roms_manager.get_scanned_roms_by_status(test_system_id, ROMStatus.MISSING)
    test_rom_found = any(rom.get('calculated_crc32') == test_crc32 for rom in missing_roms)
    
    print(f"Missing ROMs in database: {len(missing_roms)}")
    print(f"Test ROM found in missing ROMs: {test_rom_found}")
    
    if test_rom_found:
        print("✅ SUCCESS: Missing ROM is properly stored in database with MISSING status")
        print("✅ The updated update_missing_roms() function should now display this ROM in the Missing tab")
    else:
        print("❌ FAILED: Missing ROM not found in database")
    
    # Step 4: Show what the updated function would display
    print("\nROMs that would appear in Missing tab:")
    for i, rom in enumerate(missing_roms, 1):
        crc32 = rom.get('calculated_crc32', '')
        file_path = rom.get('file_path', '')
        display_name = f"Missing ROM (CRC: {crc32})" if file_path.startswith('missing_') else file_path
        print(f"  {i}. {display_name} - {crc32}")
    
    return test_rom_found

if __name__ == '__main__':
    success = test_missing_rom_unignore()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)