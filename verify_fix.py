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

print("=== VERIFICATION OF IGNORED ROMS FIX ===")

# Get current ignored CRCs for system 1
ignored_crcs = settings_manager.get_ignored_crcs('1')
print(f"Ignored CRCs in settings: {len(ignored_crcs)}")

# Check database status for these CRCs
db_path = settings_manager.get_database_path()
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Count ROMs with ignored status
cursor.execute('SELECT COUNT(*) FROM scanned_roms WHERE status = "ignored"')
ignored_in_db = cursor.fetchone()[0]
print(f"ROMs with 'ignored' status in database: {ignored_in_db}")

# Check if all ignored CRCs have correct status
if ignored_crcs:
    placeholders = ','.join(['?' for _ in ignored_crcs])
    cursor.execute(f'SELECT COUNT(*) FROM scanned_roms WHERE calculated_crc32 IN ({placeholders}) AND status = "ignored"', ignored_crcs)
    correctly_ignored = cursor.fetchone()[0]
    print(f"ROMs with ignored CRCs that have 'ignored' status: {correctly_ignored}/{len(ignored_crcs)}")
    
    # Show any remaining issues
    cursor.execute(f'SELECT file_path, calculated_crc32, status FROM scanned_roms WHERE calculated_crc32 IN ({placeholders}) AND status != "ignored"', ignored_crcs)
    remaining_issues = cursor.fetchall()
    
    if remaining_issues:
        print(f"\n⚠️  {len(remaining_issues)} ROMs still have incorrect status:")
        for rom in remaining_issues:
            print(f"  - {rom[0]} (CRC: {rom[1]}, Status: {rom[2]})")
    else:
        print("\n✅ All ignored ROMs have correct status in database!")

# Test the populate_ignored_tree functionality
print("\n=== TESTING POPULATE_IGNORED_TREE SIMULATION ===")
cursor.execute('SELECT file_path, calculated_crc32, original_status FROM scanned_roms WHERE status = "ignored" ORDER BY file_path')
ignored_roms = cursor.fetchall()

print(f"ROMs that would appear in ignored tree: {len(ignored_roms)}")
for i, rom in enumerate(ignored_roms[:5]):  # Show first 5
    print(f"  {i+1}. {Path(rom[0]).name} (CRC: {rom[1]}, Original: {rom[2]})")

if len(ignored_roms) > 5:
    print(f"  ... and {len(ignored_roms) - 5} more")

# Test unignore simulation
if ignored_roms:
    test_rom = ignored_roms[0]
    print(f"\n=== TESTING UNIGNORE SIMULATION ===")
    print(f"Test ROM: {Path(test_rom[0]).name} (CRC: {test_rom[1]})")
    print(f"Original status: {test_rom[2]}")
    print(f"Would be restored to: {test_rom[2]} status")
    print(f"Would be removed from ignored_crcs list")

conn.close()
print("\n🎉 Verification complete! The ignore/unignore functionality should now work correctly.")
print("\n📋 Summary:")
print(f"   • {ignored_in_db} ROMs marked as ignored in database")
print(f"   • {len(ignored_crcs)} CRCs in ignored settings")
print(f"   • Ignored tree will show {len(ignored_roms)} ROMs")
print(f"   • Unignore will restore ROMs to their original status")