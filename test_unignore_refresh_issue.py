#!/usr/bin/env python3
"""
Test script to reproduce and verify the unignore refresh issue.
This tests whether unignored Missing ROMs properly reappear in the Missing tab.
"""

import sqlite3
import json
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from core.settings_manager import SettingsManager

def test_unignore_refresh_issue():
    """Test the unignore refresh issue using SettingsManager and direct database access."""
    print("=== Testing Unignore Refresh Issue ===")
    
    # Setup test data
    test_system_id = "test_system"
    test_crc32 = "ABCD1234"
    
    # Initialize settings manager
    settings_manager = SettingsManager()
    db_path = Path(settings_manager.get_database_path())
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Step 1: Add a Missing ROM to the database
        print("\n1. Adding a Missing ROM to database...")
        cursor.execute("""
            INSERT OR REPLACE INTO scanned_roms 
            (system_id, file_path, file_size, calculated_crc32, status, original_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (test_system_id, "/test/missing_rom.zip", 1024, test_crc32, "Missing", "Missing"))
        conn.commit()
        
        # Verify it's in the database
        cursor.execute("""
            SELECT * FROM scanned_roms 
            WHERE system_id = ? AND status = 'Missing'
        """, (test_system_id,))
        missing_roms = cursor.fetchall()
        print(f"   Missing ROMs in database: {len(missing_roms)}")
        
        # Step 2: Simulate ignoring the ROM (add to settings)
        print("\n2. Simulating ignoring the ROM...")
        
        # Get current ignored CRCs using SettingsManager
        ignored_crcs = set(settings_manager.get_ignored_crcs(test_system_id))
        
        ignored_crcs.add(test_crc32)
        
        # Save back to settings using SettingsManager
        settings_manager.set_ignored_crcs(test_system_id, list(ignored_crcs))
        
        print(f"   Ignored CRCs: {ignored_crcs}")
        print(f"   Test CRC32 is ignored: {test_crc32 in ignored_crcs}")
        
        # Step 3: Simulate unignoring the ROM (like the UI does)
        print("\n3. Simulating unignoring the ROM...")
        
        # Remove from ignored list using SettingsManager
        ignored_crcs.discard(test_crc32)
        settings_manager.set_ignored_crcs(test_system_id, list(ignored_crcs))
        
        # Restore to original status (should already be Missing)
        cursor.execute("""
            SELECT original_status FROM scanned_roms 
            WHERE system_id = ? AND calculated_crc32 = ?
        """, (test_system_id, test_crc32))
        result = cursor.fetchone()
        original_status = result['original_status'] if result else None
        print(f"   Original status from database: {original_status}")
        
        if original_status:
            cursor.execute("""
                UPDATE scanned_roms 
                SET status = ?
                WHERE system_id = ? AND calculated_crc32 = ?
            """, (original_status, test_system_id, test_crc32))
        
        conn.commit()
        
        # Step 4: Check if the ROM should appear in Missing tab
        print("\n4. Checking if ROM should appear in Missing tab...")
        
        # Check ignored status
        print(f"   Ignored CRCs after unignore: {ignored_crcs}")
        print(f"   Test CRC32 is still ignored: {test_crc32 in ignored_crcs}")
        
        # Check ROM status in database
        cursor.execute("""
            SELECT * FROM scanned_roms 
            WHERE system_id = ? AND calculated_crc32 = ?
        """, (test_system_id, test_crc32))
        rom_data = cursor.fetchone()
        if rom_data:
            print(f"   ROM status in database: {rom_data['status']}")
            print(f"   ROM original status: {rom_data['original_status']}")
        else:
            print("   ROM not found in database!")
        
        # Check missing ROMs query
        cursor.execute("""
            SELECT * FROM scanned_roms 
            WHERE system_id = ? AND status = 'Missing'
        """, (test_system_id,))
        missing_roms_after = cursor.fetchall()
        print(f"   Missing ROMs in database after unignore: {len(missing_roms_after)}")
        
        # Simulate the Missing tab logic
        print("\n5. Simulating Missing tab logic...")
        should_appear = False
        for rom in missing_roms_after:
            rom_crc32 = rom['calculated_crc32'] or rom.get('matched_game_crc32')
            if rom_crc32 == test_crc32 and rom_crc32 not in ignored_crcs:
                should_appear = True
                print(f"   ✅ ROM should appear in Missing tab")
                break
        
        if not should_appear:
            print(f"   ❌ ROM should NOT appear in Missing tab")
            print(f"      This indicates the refresh issue!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        # Cleanup
        print("\n6. Cleaning up test data...")
        try:
            cursor.execute("""
                DELETE FROM scanned_roms 
                WHERE system_id = ? AND calculated_crc32 = ?
            """, (test_system_id, test_crc32))
            
            # Clean up ignored CRCs using SettingsManager
            ignored_crcs = set(settings_manager.get_ignored_crcs(test_system_id))
            if test_crc32 in ignored_crcs:
                ignored_crcs.discard(test_crc32)
                settings_manager.set_ignored_crcs(test_system_id, list(ignored_crcs))
            
            conn.commit()
            conn.close()
            print("   Cleanup completed")
        except Exception as e:
            print(f"   Cleanup error: {e}")

if __name__ == "__main__":
    test_unignore_refresh_issue()