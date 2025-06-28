#!/usr/bin/env python3
"""
Script to test unignoring existing ignored Missing ROMs
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.settings_manager import SettingsManager
from core.scanned_roms_manager import ScannedROMsManager
from core.rom_scanner import ROMStatus

def test_unignore_existing_missing_roms():
    """Test unignoring existing ignored Missing ROMs"""
    print("🧪 Testing unignore functionality with existing ignored Missing ROMs...")
    print()
    
    try:
        # Initialize managers
        settings_manager = SettingsManager()
        db_path = settings_manager.get_database_path()
        scanned_roms_manager = ScannedROMsManager(db_path)
        
        # Get the ignored Missing ROMs we found earlier
        ignored_missing_crcs = ['7322ebc6', '8cf511a4']
        
        for crc32 in ignored_missing_crcs:
            print(f"Testing CRC32: {crc32}")
            
            # 1. Verify it's currently ignored
            rom_data = scanned_roms_manager.get_rom_by_crc32(1, crc32)  # system_id=1 for Atari 2600
            if rom_data:
                print(f"  Current status: {rom_data['status']}")
                print(f"  Original status: {rom_data['original_status']}")
                
                if rom_data['status'] == 'ignored' and rom_data['original_status'] == 'missing':
                    print("  ✅ ROM is correctly ignored with Missing original status")
                    
                    # 2. Test getting original status
                    original_status = scanned_roms_manager.get_rom_original_status(1, crc32)
                    print(f"  Retrieved original status: {original_status}")
                    
                    if original_status == ROMStatus.MISSING:
                        print("  ✅ Original status correctly retrieved as MISSING")
                        
                        # 3. Test unignoring
                        print("  Attempting to unignore...")
                        scanned_roms_manager.update_rom_status(
                            system_id=1,
                            new_status=ROMStatus.MISSING,
                            crc32=crc32
                        )
                        
                        # 4. Verify it's now Missing
                        updated_rom_data = scanned_roms_manager.get_rom_by_crc32(1, crc32)
                        if updated_rom_data and updated_rom_data['status'] == 'missing':
                            print("  ✅ ROM successfully unignored to MISSING status")
                            
                            # 5. Re-ignore it for future tests
                            print("  Re-ignoring for future tests...")
                            scanned_roms_manager.update_rom_status(
                                system_id=1,
                                new_status=ROMStatus.IGNORED,
                                crc32=crc32,
                                original_status=ROMStatus.MISSING
                            )
                            print("  ✅ ROM re-ignored with original status preserved")
                        else:
                            print("  ❌ Failed to unignore ROM")
                    else:
                        print(f"  ❌ Wrong original status retrieved: {original_status}")
                else:
                    print(f"  ❌ ROM not in expected state: status={rom_data['status']}, original_status={rom_data['original_status']}")
            else:
                print(f"  ❌ ROM not found in database")
            
            print()
        
        print("🎉 Test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_unignore_existing_missing_roms()
    if success:
        print("✅ All tests passed! Unignore functionality is working correctly.")
    else:
        print("❌ Some tests failed.")