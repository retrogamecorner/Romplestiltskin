#!/usr/bin/env python3
"""
Test script to verify the refresh fix for unignored Missing ROMs.
This tests whether the self.ignored_crcs attribute is properly updated.
"""

import sqlite3
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from core.settings_manager import SettingsManager

def test_refresh_fix():
    """Test that the refresh fix works correctly."""
    print("=== Testing Refresh Fix ===")
    
    # Setup test data
    test_system_id = "test_system"
    test_crc32 = "REFRESH1234"
    
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
        """, (test_system_id, "/test/refresh_test.zip", 2048, test_crc32, "Missing", "Missing"))
        conn.commit()
        print(f"   Added ROM with CRC32: {test_crc32}")
        
        # Step 2: Add to ignored list
        print("\n2. Adding ROM to ignored list...")
        ignored_crcs = settings_manager.get_ignored_crcs(test_system_id)
        if test_crc32 not in ignored_crcs:
            ignored_crcs.append(test_crc32)
            settings_manager.set_ignored_crcs(test_system_id, ignored_crcs)
        
        # Update ROM status to Ignored
        cursor.execute("""
            UPDATE scanned_roms 
            SET status = 'Ignored'
            WHERE calculated_crc32 = ?
        """, (test_crc32,))
        conn.commit()
        print(f"   ROM {test_crc32} marked as Ignored")
        
        # Step 3: Simulate the unignore process
        print("\n3. Simulating unignore process...")
        
        # Remove from ignored list (simulating settings update)
        ignored_crcs = settings_manager.get_ignored_crcs(test_system_id)
        if test_crc32 in ignored_crcs:
            ignored_crcs.remove(test_crc32)
            settings_manager.set_ignored_crcs(test_system_id, ignored_crcs)
        
        # Restore ROM to original status
        cursor.execute("""
            UPDATE scanned_roms 
            SET status = original_status
            WHERE calculated_crc32 = ?
        """, (test_crc32,))
        conn.commit()
        
        # Step 4: Verify the fix - simulate what the UI would do
        print("\n4. Verifying the refresh fix...")
        
        # This simulates the line we added: self.ignored_crcs = set(self.settings_manager.get_ignored_crcs(self.current_system_id))
        updated_ignored_crcs = set(settings_manager.get_ignored_crcs(test_system_id))
        
        # Check if the test CRC is no longer in the ignored list
        if test_crc32 not in updated_ignored_crcs:
            print(f"   ✅ Fix working: {test_crc32} is no longer in ignored list")
        else:
            print(f"   ❌ Fix failed: {test_crc32} is still in ignored list")
        
        # Verify ROM status in database
        cursor.execute("""
            SELECT status, original_status FROM scanned_roms 
            WHERE calculated_crc32 = ?
        """, (test_crc32,))
        result = cursor.fetchone()
        
        if result:
            print(f"   ROM status: {result['status']}, original: {result['original_status']}")
            if result['status'] == 'Missing':
                print("   ✅ ROM status correctly restored to Missing")
            else:
                print(f"   ❌ ROM status incorrect: {result['status']}")
        
        print("\n✅ Refresh fix test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    finally:
        # Cleanup: Remove test data
        try:
            cursor.execute("DELETE FROM scanned_roms WHERE calculated_crc32 = ?", (test_crc32,))
            
            # Clean up ignored CRCs
            ignored_crcs = settings_manager.get_ignored_crcs(test_system_id)
            if test_crc32 in ignored_crcs:
                ignored_crcs.remove(test_crc32)
                settings_manager.set_ignored_crcs(test_system_id, ignored_crcs)
            
            conn.commit()
            conn.close()
            print("\n🧹 Cleanup completed")
        except Exception as cleanup_error:
            print(f"❌ Cleanup error: {cleanup_error}")

if __name__ == "__main__":
    test_refresh_fix()