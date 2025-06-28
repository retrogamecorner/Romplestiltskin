#!/usr/bin/env python3
"""
Test script to verify that Missing ROMs can be properly unignored.
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.scanned_roms_manager import ScannedROMsManager, ROMStatus
from core.db_manager import DatabaseManager

def test_unignore_missing_rom():
    """
    Test the unignore functionality for Missing ROMs.
    """
    print("Testing Missing ROM unignore functionality...")
    
    # Initialize managers
    db_path = os.path.expanduser('~/.romplestiltskin/romplestiltskin.db')
    scanned_roms_manager = ScannedROMsManager(db_path)
    
    # Use system_id = 1 (Atari 2600)
    system_id = 1
    test_crc32 = "test_missing_crc32"
    
    print(f"\n1. Adding a test Missing ROM with CRC32: {test_crc32}")
    
    # First, add a Missing ROM to the database
    scanned_roms_manager.add_rom(
        system_id=system_id,
        status=ROMStatus.MISSING,
        file_path="/test/missing_rom.bin",
        file_size=1024,
        crc32=test_crc32
    )
    
    # Verify it was added
    rom_data = scanned_roms_manager.get_rom_by_crc32(system_id, test_crc32)
    if rom_data:
        print(f"   ✅ Missing ROM added successfully with status: {rom_data['status']}")
    else:
        print("   ❌ Failed to add Missing ROM")
        return False
    
    print(f"\n2. Ignoring the Missing ROM (simulating user action)...")
    
    # Ignore the ROM with original_status preserved
    rows_affected = scanned_roms_manager.update_rom_status(
        system_id=system_id,
        new_status=ROMStatus.IGNORED,
        crc32=test_crc32,
        original_status=ROMStatus.MISSING
    )
    
    print(f"   Rows affected by ignore operation: {rows_affected}")
    
    # Verify it's now ignored
    rom_data = scanned_roms_manager.get_rom_by_crc32(system_id, test_crc32)
    if rom_data and rom_data['status'] == 'ignored':
        print(f"   ✅ ROM successfully ignored with status: {rom_data['status']}")
        original_status_preserved = rom_data['original_status'] if rom_data['original_status'] else 'None'
        print(f"   Original status preserved: {original_status_preserved}")
    else:
        print(f"   ❌ Failed to ignore ROM. Current status: {rom_data['status'] if rom_data else 'Not found'}")
        return False
    
    print(f"\n3. Testing get_rom_original_status method...")
    
    # Test the get_rom_original_status method
    original_status = scanned_roms_manager.get_rom_original_status(system_id, test_crc32)
    if original_status:
        print(f"   ✅ Original status retrieved: {original_status}")
    else:
        print("   ❌ Failed to retrieve original status")
        return False
    
    print(f"\n4. Unignoring the ROM (simulating user action)...")
    
    # Unignore the ROM by restoring to original status
    if original_status:
        rows_affected = scanned_roms_manager.update_rom_status(
            system_id=system_id,
            new_status=original_status,
            crc32=test_crc32
        )
        print(f"   Rows affected by unignore operation: {rows_affected}")
    
    # Verify it's back to Missing status
    rom_data = scanned_roms_manager.get_rom_by_crc32(system_id, test_crc32)
    if rom_data and rom_data['status'] == 'missing':
        print(f"   ✅ ROM successfully unignored with status: {rom_data['status']}")
    else:
        print(f"   ❌ Failed to unignore ROM. Current status: {rom_data['status'] if rom_data else 'Not found'}")
        return False
    
    print(f"\n5. Cleaning up test data...")
    
    # Clean up: remove the test ROM
    with scanned_roms_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM scanned_roms WHERE system_id = ? AND calculated_crc32 = ?",
            (system_id, test_crc32)
        )
        conn.commit()
        print(f"   Test ROM removed from database")
    
    print("\n✅ UNIGNORE TEST PASSED: Missing ROMs can be properly unignored!")
    return True

def check_existing_ignored_roms():
    """
    Check if there are any existing ignored ROMs that were originally Missing.
    """
    print("\nChecking existing ignored ROMs...")
    
    db_path = os.path.expanduser('~/.romplestiltskin/romplestiltskin.db')
    scanned_roms_manager = ScannedROMsManager(db_path)
    
    with scanned_roms_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT system_id, calculated_crc32, file_path, status, original_status
            FROM scanned_roms 
            WHERE status = 'ignored'
        """)
        
        ignored_roms = cursor.fetchall()
        
        if ignored_roms:
            print(f"Found {len(ignored_roms)} ignored ROMs:")
            for rom in ignored_roms:
                original_status = rom['original_status'] if rom['original_status'] else 'None'
                print(f"  - CRC32: {rom['calculated_crc32']}, Original Status: {original_status}")
                
                # Test if we can get the original status
                original_status = scanned_roms_manager.get_rom_original_status(rom['system_id'], rom['calculated_crc32'])
                if original_status:
                    print(f"    ✅ Can retrieve original status: {original_status}")
                else:
                    print(f"    ❌ Cannot retrieve original status")
        else:
            print("No ignored ROMs found in database")

if __name__ == '__main__':
    print("=" * 60)
    print("MISSING ROM UNIGNORE FUNCTIONALITY TEST")
    print("=" * 60)
    
    try:
        # Check existing ignored ROMs first
        check_existing_ignored_roms()
        
        # Run the main test
        success = test_unignore_missing_rom()
        
        if success:
            print("\n🎉 All tests passed! Unignore functionality is working correctly.")
        else:
            print("\n❌ Tests failed! There are issues with the unignore functionality.")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()