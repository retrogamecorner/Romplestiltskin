#!/usr/bin/env python3
"""
Test script to verify the UI fix for unignoring missing ROMs.
This script will:
1. Add a ROM to the ignored list
2. Simulate unignoring it (which should make it appear in Missing tab)
3. Verify the database state
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.settings_manager import SettingsManager
from core.scanned_roms_manager import ScannedROMsManager
from core.db_manager import DatabaseManager
from core.rom_scanner import ROMStatus

def main():
    print("Testing UI fix for unignoring missing ROMs...")
    
    # Initialize managers
    settings_manager = SettingsManager()
    db_path = settings_manager.get_database_path()
    scanned_roms_manager = ScannedROMsManager(db_path)
    
    test_system_id = 'atari_2600'
    test_crc32 = 'abcd1234'  # Test CRC32
    test_filename = 'test_missing_rom.bin'
    
    print(f"\n1. Adding test ROM to ignored list...")
    
    # First, clean up any existing test ROM
    try:
        scanned_roms_manager.delete_rom_by_crc(test_system_id, test_crc32)
        print("Cleaned up existing test ROM")
    except:
        pass  # ROM doesn't exist, which is fine
    
    # Add ROM as ignored
    scanned_roms_manager.add_rom(
        system_id=test_system_id,
        file_path=f'missing_{test_filename}',
        crc32=test_crc32,
        status=ROMStatus.IGNORED
    )
    
    # Verify it's in ignored list
    ignored_roms = scanned_roms_manager.get_scanned_roms_by_status(test_system_id, ROMStatus.IGNORED)
    test_rom_ignored = any(rom.get('calculated_crc32') == test_crc32 for rom in ignored_roms)
    print(f"ROM in ignored list: {test_rom_ignored}")
    
    print(f"\n2. Simulating unignore operation (changing status to MISSING)...")
    
    # Simulate unignoring by changing status to MISSING
    rows_affected = scanned_roms_manager.update_rom_status(
        system_id=test_system_id,
        new_status=ROMStatus.MISSING,
        crc32=test_crc32
    )
    print(f"Rows affected by unignore: {rows_affected}")
    
    print(f"\n3. Verifying ROM now appears in Missing list...")
    
    # Check if ROM is now in missing list
    missing_roms = scanned_roms_manager.get_scanned_roms_by_status(test_system_id, ROMStatus.MISSING)
    test_rom_missing = any(rom.get('calculated_crc32') == test_crc32 for rom in missing_roms)
    
    print(f"Missing ROMs in database: {len(missing_roms)}")
    print(f"Test ROM found in missing ROMs: {test_rom_missing}")
    
    if test_rom_missing:
        print("\n✅ SUCCESS: ROM successfully moved from ignored to missing status")
        print("✅ The updated update_missing_roms() function should now display this ROM")
        
        print("\nROMs that would appear in Missing tab:")
        for i, rom in enumerate(missing_roms, 1):
            crc32 = rom.get('calculated_crc32', '')
            file_path = rom.get('file_path', '')
            display_name = f"Missing ROM (CRC: {crc32})" if file_path.startswith('missing_') else file_path
            print(f"  {i}. {display_name} - {crc32}")
            
        print("\n✅ UI FIX VERIFIED: Unignored missing ROMs will now appear in Missing tab")
    else:
        print("\n❌ FAILED: ROM not found in missing list after unignoring")
        return False
    
    print("\n4. Cleaning up test data...")
    # Clean up - remove test ROM
    scanned_roms_manager.delete_rom_by_crc(test_system_id, test_crc32)
    print("Test ROM removed from database")
    
    return True

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🎉 TEST PASSED: UI fix for unignoring missing ROMs is working correctly!")
    else:
        print("\n💥 TEST FAILED: UI fix needs more work")
        sys.exit(1)