#!/usr/bin/env python3
"""
Script to check for ignored ROMs that have Missing as their original status
"""

import sqlite3
from pathlib import Path

def check_ignored_missing_roms():
    """Check for ignored ROMs with Missing original status"""
    import os
    db_path = Path(os.path.expanduser('~/.romplestiltskin/romplestiltskin.db'))
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # First check the schema
        cursor.execute("PRAGMA table_info(systems)")
        systems_schema = cursor.fetchall()
        print("Systems table schema:")
        for col in systems_schema:
            print(f"  {col}")
        print()
        
        # Query for ignored ROMs with Missing original status
        query = """
        SELECT sr.*, s.system_name as system_name
        FROM scanned_roms sr
        JOIN systems s ON sr.system_id = s.id
        WHERE sr.status = 'ignored' AND sr.original_status = 'missing'
        ORDER BY s.system_name, sr.calculated_crc32
        """
        
        cursor.execute(query)
        ignored_missing_roms = cursor.fetchall()
        
        print(f"🔍 Found {len(ignored_missing_roms)} ignored ROMs with Missing original status:")
        print()
        
        if ignored_missing_roms:
            for rom in ignored_missing_roms:
                print(f"System: {rom['system_name']}")
                print(f"  CRC32: {rom['calculated_crc32']}")
                print(f"  File Path: {rom['file_path']}")
                print(f"  Status: {rom['status']}")
                print(f"  Original Status: {rom['original_status']}")
                print(f"  Scan Timestamp: {rom['scan_timestamp']}")
                print()
        else:
            print("✅ No ignored ROMs with Missing original status found.")
            
        # Also check all ignored ROMs
        query_all_ignored = """
        SELECT sr.*, s.system_name as system_name
        FROM scanned_roms sr
        JOIN systems s ON sr.system_id = s.id
        WHERE sr.status = 'ignored'
        ORDER BY s.system_name, sr.calculated_crc32
        """
        
        cursor.execute(query_all_ignored)
        all_ignored_roms = cursor.fetchall()
        
        print(f"📋 All ignored ROMs ({len(all_ignored_roms)} total):")
        print()
        
        for rom in all_ignored_roms:
            print(f"System: {rom['system_name']}")
            print(f"  CRC32: {rom['calculated_crc32']}")
            print(f"  File Path: {rom['file_path']}")
            print(f"  Status: {rom['status']}")
            print(f"  Original Status: {rom['original_status'] or 'None'}")
            print(f"  Scan Timestamp: {rom['scan_timestamp']}")
            print()
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_ignored_missing_roms()