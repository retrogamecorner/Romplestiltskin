import sqlite3
import os
from pathlib import Path
import sys
sys.path.append('src')
from core.settings_manager import SettingsManager

# Check settings first
settings_manager = SettingsManager()
print("=== SETTINGS FILE ===")
ignored_crcs_global = settings_manager.get_ignored_crcs()
print(f"Global ignored CRCs: {ignored_crcs_global}")
ignored_crcs_system1 = settings_manager.get_ignored_crcs('1')
print(f"System 1 ignored CRCs: {ignored_crcs_system1}")

# Check settings database
settings_db = Path.home() / '.romplestiltskin' / 'romplestiltskin.db'
print(f"\n=== SETTINGS DATABASE ({settings_db}) ===")
conn = sqlite3.connect(settings_db)
cursor = conn.cursor()

# Check all ROMs in database
cursor.execute('SELECT COUNT(*) FROM scanned_roms')
total_roms = cursor.fetchone()[0]
print(f"Total ROMs in DB: {total_roms}")

# Check ROM statuses
cursor.execute('SELECT status, COUNT(*) FROM scanned_roms GROUP BY status')
status_counts = cursor.fetchall()
print("ROM status distribution:")
for status, count in status_counts:
    print(f"  {status}: {count}")

# Check for any ROMs with the ignored CRCs
if ignored_crcs_system1:
    placeholders = ','.join(['?' for _ in ignored_crcs_system1])
    cursor.execute(f'SELECT file_path, calculated_crc32, status, original_status FROM scanned_roms WHERE calculated_crc32 IN ({placeholders})', ignored_crcs_system1)
    matching_roms = cursor.fetchall()
    print(f"\nROMs matching ignored CRCs ({len(matching_roms)} found):")
    for rom in matching_roms:
        print(f"  {rom[0]} (CRC: {rom[1]}, Status: {rom[2]}, Original: {rom[3]})")

# Check for missing_ placeholder files
cursor.execute('SELECT file_path, calculated_crc32, status, original_status FROM scanned_roms WHERE file_path LIKE "missing_%"')
placeholder_roms = cursor.fetchall()
print(f"\nPlaceholder ROMs ({len(placeholder_roms)} found):")
for rom in placeholder_roms:
    print(f"  {rom[0]} (CRC: {rom[1]}, Status: {rom[2]}, Original: {rom[3]})")

conn.close()