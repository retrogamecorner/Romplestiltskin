import sys
sys.path.append('src')

import sqlite3
from pathlib import Path
from core.settings_manager import SettingsManager
from core.scanned_roms_manager import ScannedROMsManager
from core.rom_scanner import ROMStatus

# Initialize managers
settings_manager = SettingsManager()
scanned_roms_manager = ScannedROMsManager(settings_manager.get_database_path())

print("=== TESTING IGNORE/UNIGNORE FUNCTIONALITY ===")

# Get current ignored CRCs
ignored_crcs = settings_manager.get_ignored_crcs('1')
print(f"Current ignored CRCs in settings: {ignored_crcs}")

# Check database status for these CRCs
db_path = settings_manager.get_database_path()
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

if ignored_crcs:
    placeholders = ','.join(['?' for _ in ignored_crcs])
    cursor.execute(f'SELECT file_path, calculated_crc32, status, original_status FROM scanned_roms WHERE calculated_crc32 IN ({placeholders})', ignored_crcs)
    matching_roms = cursor.fetchall()
    print(f"\nROMs in database with ignored CRCs:")
    for rom in matching_roms:
        print(f"  {rom[0]} (CRC: {rom[1]}, Status: {rom[2]}, Original: {rom[3]})")

# Test updating one ROM to ignored status
if matching_roms:
    test_rom = matching_roms[0]
    test_crc = test_rom[1]
    test_path = test_rom[0]
    
    print(f"\n=== TESTING UPDATE TO IGNORED ===")
    print(f"Updating ROM: {test_path} (CRC: {test_crc})")
    
    # Update to ignored
    scanned_roms_manager.update_rom_status(
        system_id=1,
        new_status=ROMStatus.IGNORED,
        file_path=test_path,
        crc32=test_crc,
        original_status=ROMStatus.NOT_RECOGNIZED
    )
    
    # Check the result
    cursor.execute('SELECT file_path, calculated_crc32, status, original_status FROM scanned_roms WHERE calculated_crc32 = ?', (test_crc,))
    updated_rom = cursor.fetchone()
    print(f"After update: {updated_rom[0]} (CRC: {updated_rom[1]}, Status: {updated_rom[2]}, Original: {updated_rom[3]})")
    
    print(f"\n=== TESTING UPDATE BACK TO ORIGINAL ===")
    # Update back to original status
    scanned_roms_manager.update_rom_status(
        system_id=1,
        new_status=ROMStatus.NOT_RECOGNIZED,
        file_path=test_path,
        crc32=test_crc
    )
    
    # Check the result
    cursor.execute('SELECT file_path, calculated_crc32, status, original_status FROM scanned_roms WHERE calculated_crc32 = ?', (test_crc,))
    restored_rom = cursor.fetchone()
    print(f"After restore: {restored_rom[0]} (CRC: {restored_rom[1]}, Status: {restored_rom[2]}, Original: {restored_rom[3]})")

conn.close()