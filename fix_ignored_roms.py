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

print("=== FIXING IGNORED ROMS DATABASE STATUS ===")

# Get current ignored CRCs for system 1
ignored_crcs = settings_manager.get_ignored_crcs('1')
print(f"Found {len(ignored_crcs)} ignored CRCs in settings: {ignored_crcs}")

if not ignored_crcs:
    print("No ignored CRCs found in settings. Nothing to fix.")
    exit(0)

# Check database status for these CRCs
db_path = settings_manager.get_database_path()
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find ROMs that should be ignored but aren't marked as such
placeholders = ','.join(['?' for _ in ignored_crcs])
cursor.execute(f'SELECT file_path, calculated_crc32, status, original_status FROM scanned_roms WHERE calculated_crc32 IN ({placeholders}) AND status != "ignored"', ignored_crcs)
roms_to_fix = cursor.fetchall()

print(f"\nFound {len(roms_to_fix)} ROMs that need status update:")
for rom in roms_to_fix:
    print(f"  {rom[0]} (CRC: {rom[1]}, Current Status: {rom[2]}, Original: {rom[3]})")

if not roms_to_fix:
    print("All ignored ROMs already have correct status in database.")
    conn.close()
    exit(0)

# Update each ROM to ignored status
print(f"\nUpdating {len(roms_to_fix)} ROM statuses...")
for rom in roms_to_fix:
    file_path, crc32, current_status, original_status = rom
    
    # Determine the original status if not set
    if not original_status:
        original_status = current_status
    
    print(f"Updating {file_path} (CRC: {crc32}) to ignored...")
    
    # Update using the scanned_roms_manager
    try:
        scanned_roms_manager.update_rom_status(
            system_id=1,
            new_status=ROMStatus.IGNORED,
            file_path=file_path,
            crc32=crc32,
            original_status=ROMStatus(original_status) if original_status else ROMStatus.NOT_RECOGNIZED
        )
        print(f"  ✓ Updated successfully")
    except Exception as e:
        print(f"  ✗ Error updating: {e}")

print("\n=== VERIFICATION ===")
# Verify the updates
cursor.execute(f'SELECT file_path, calculated_crc32, status, original_status FROM scanned_roms WHERE calculated_crc32 IN ({placeholders})', ignored_crcs)
updated_roms = cursor.fetchall()

ignored_count = sum(1 for rom in updated_roms if rom[2] == 'ignored')
print(f"After update: {ignored_count}/{len(updated_roms)} ROMs have 'ignored' status")

print("\nFinal status of all ROMs with ignored CRCs:")
for rom in updated_roms:
    status_icon = "✓" if rom[2] == 'ignored' else "✗"
    print(f"  {status_icon} {rom[0]} (CRC: {rom[1]}, Status: {rom[2]}, Original: {rom[3]})")

conn.close()
print("\nFix completed! The ignored ROMs should now appear correctly in the application.")
print("Please restart the application to see the changes.")