#!/usr/bin/env python3
"""
Debug script to examine ignored ROMs and their original_status values.
"""

import sqlite3
from pathlib import Path
from src.core.rom_scanner import ROMStatus
from src.core.settings_manager import SettingsManager

def debug_ignored_roms():
    """Debug ignored ROMs in the database and settings."""
    
    # Initialize settings manager
    settings_manager = SettingsManager()
    
    # Get database path
    db_path = Path("scanned_roms.db")
    if not db_path.exists():
        print("Database file not found!")
        return
    
    print("=== DEBUGGING IGNORED ROMS ===")
    print(f"Database path: {db_path}")
    print()
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all ignored ROMs
    print("1. All ignored ROMs in database:")
    cursor.execute("""
        SELECT system_id, file_path, calculated_crc32, status, original_status
        FROM scanned_roms 
        WHERE status = ?
        ORDER BY system_id, file_path
    """, (ROMStatus.IGNORED.value,))
    
    ignored_roms = cursor.fetchall()
    print(f"Found {len(ignored_roms)} ignored ROMs:")
    for rom in ignored_roms:
        print(f"  System {rom['system_id']}: {rom['file_path']} (CRC32: {rom['calculated_crc32']}, Original: {rom['original_status']})")
    print()
    
    # Get all systems
    cursor.execute("SELECT DISTINCT system_id FROM scanned_roms ORDER BY system_id")
    systems = [row[0] for row in cursor.fetchall()]
    
    print("2. Ignored CRCs in settings by system:")
    for system_id in systems:
        ignored_crcs = settings_manager.get_ignored_crcs(system_id)
        print(f"  System {system_id}: {len(ignored_crcs)} ignored CRCs: {ignored_crcs}")
    
    # Global ignored CRCs
    global_ignored = settings_manager.get_ignored_crcs(None)
    print(f"  Global: {len(global_ignored)} ignored CRCs: {global_ignored}")
    print()
    
    # Check for ROMs with missing original_status
    print("3. Ignored ROMs with missing original_status:")
    cursor.execute("""
        SELECT system_id, file_path, calculated_crc32, status, original_status
        FROM scanned_roms 
        WHERE status = ? AND (original_status IS NULL OR original_status = '')
        ORDER BY system_id, file_path
    """, (ROMStatus.IGNORED.value,))
    
    missing_original = cursor.fetchall()
    print(f"Found {len(missing_original)} ignored ROMs with missing original_status:")
    for rom in missing_original:
        print(f"  System {rom['system_id']}: {rom['file_path']} (CRC32: {rom['calculated_crc32']})")
    print()
    
    # Check for ROMs that should be unrecognised but aren't showing up
    print("4. All NOT_RECOGNIZED ROMs:")
    cursor.execute("""
        SELECT system_id, file_path, calculated_crc32, status, original_status
        FROM scanned_roms 
        WHERE status = ?
        ORDER BY system_id, file_path
    """, (ROMStatus.NOT_RECOGNIZED.value,))
    
    unrecognised_roms = cursor.fetchall()
    print(f"Found {len(unrecognised_roms)} unrecognised ROMs:")
    for rom in unrecognised_roms:
        print(f"  System {rom['system_id']}: {rom['file_path']} (CRC32: {rom['calculated_crc32']})")
    print()
    
    # Check for entries with placeholder file paths
    print("5. ROMs with placeholder file paths (missing_*):")
    cursor.execute("""
        SELECT system_id, file_path, calculated_crc32, status, original_status
        FROM scanned_roms 
        WHERE file_path LIKE 'missing_%'
        ORDER BY system_id, file_path
    """)
    
    placeholder_roms = cursor.fetchall()
    print(f"Found {len(placeholder_roms)} ROMs with placeholder paths:")
    for rom in placeholder_roms:
        print(f"  System {rom['system_id']}: {rom['file_path']} (CRC32: {rom['calculated_crc32']}, Status: {rom['status']}, Original: {rom['original_status']})")
    print()
    
    conn.close()
    
    print("=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    debug_ignored_roms()