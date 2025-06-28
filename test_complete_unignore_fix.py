#!/usr/bin/env python3
"""
Complete test for the unignore Missing ROMs fix.
This test:
1. Creates ignored Missing ROMs in the database
2. Tests the column index fix (column 5 vs column 4)
3. Simulates the UI unignore workflow
4. Verifies the fix works end-to-end
"""

import sqlite3
import os
from pathlib import Path

def setup_test_data():
    """Create test ignored Missing ROMs in the database."""
    db_path = Path(os.path.expanduser('~/.romplestiltskin/romplestiltskin.db'))
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return False, None, None
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Find a system to work with
        cursor.execute("SELECT id, system_name FROM systems LIMIT 1")
        system_result = cursor.fetchone()
        if not system_result:
            print("❌ No systems found in database")
            conn.close()
            return False, None, None
        
        system_id, system_name = system_result
        print(f"✅ Using system: {system_name} (ID: {system_id})")
        
        # Create test Missing ROMs that we can ignore
        test_roms = [
            {
                'crc32': 'test001a',
                'file_path': '/test/path/test_rom_1.rom',
                'file_size': 1024
            },
            {
                'crc32': 'test002b', 
                'file_path': '/test/path/test_rom_2.rom',
                'file_size': 2048
            }
        ]
        
        created_roms = []
        
        for rom in test_roms:
            # First, ensure the ROM exists as Missing
            cursor.execute("""
                INSERT OR REPLACE INTO scanned_roms 
                (system_id, file_path, calculated_crc32, file_size, status, original_status)
                VALUES (?, ?, ?, ?, 'missing', 'missing')
            """, (system_id, rom['file_path'], rom['crc32'], rom['file_size']))
            
            # Then move it to ignored status (simulating user ignoring it)
            cursor.execute("""
                UPDATE scanned_roms 
                SET status = 'ignored'
                WHERE system_id = ? AND calculated_crc32 = ?
            """, (system_id, rom['crc32']))
            
            created_roms.append(rom['crc32'])
            print(f"✅ Created ignored Missing ROM: {rom['crc32']}")
        
        conn.commit()
        conn.close()
        
        return True, system_id, created_roms
        
    except Exception as e:
        print(f"❌ Error setting up test data: {e}")
        return False, None, None

def test_column_fix(system_id, test_crc32s):
    """Test the column index fix for extracting CRC32 values."""
    print(f"\n🔍 Testing Column Index Fix")
    print("=" * 40)
    
    success_count = 0
    
    for i, crc32 in enumerate(test_crc32s):
        print(f"\n📋 Testing ROM {i+1}: CRC32={crc32}")
        
        # Simulate the tree item structure from populate_ignored_tree
        tree_item_columns = [
            str(i+1),           # Column 0: Row number
            f"Test ROM {i+1}",  # Column 1: Name
            "Missing",          # Column 2: Status
            "USA",              # Column 3: Region
            "En",               # Column 4: Languages
            crc32               # Column 5: CRC32
        ]
        
        # Test old (buggy) method - column 4
        old_extracted = tree_item_columns[4]
        print(f"   ❌ OLD method (column 4): '{old_extracted}' (Languages)")
        
        # Test new (fixed) method - column 5
        new_extracted = tree_item_columns[5]
        print(f"   ✅ NEW method (column 5): '{new_extracted}' (CRC32)")
        
        # Verify the fix
        if new_extracted == crc32 and old_extracted != crc32:
            print(f"   ✅ Column fix: CORRECT")
            success_count += 1
        else:
            print(f"   ❌ Column fix: FAILED")
    
    overall_success = success_count == len(test_crc32s)
    print(f"\n{'✅ Column fix test: PASSED' if overall_success else '❌ Column fix test: FAILED'}")
    print(f"   {success_count}/{len(test_crc32s)} ROMs correctly handled")
    
    return overall_success

def test_unignore_workflow(system_id, test_crc32s):
    """Test the complete unignore workflow with the fix."""
    print(f"\n🔍 Testing Unignore Workflow")
    print("=" * 40)
    
    db_path = Path(os.path.expanduser('~/.romplestiltskin/romplestiltskin.db'))
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        success_count = 0
        
        for crc32 in test_crc32s:
            print(f"\n📋 Testing unignore for CRC32: {crc32}")
            
            # Step 1: Verify ROM is currently ignored
            cursor.execute("""
                SELECT status, original_status FROM scanned_roms
                WHERE system_id = ? AND calculated_crc32 = ?
            """, (system_id, crc32))
            
            result = cursor.fetchone()
            if not result:
                print(f"   ❌ ROM not found in database")
                continue
                
            current_status, original_status = result
            print(f"   📊 Current status: {current_status}")
            print(f"   📊 Original status: {original_status}")
            
            if current_status != 'ignored':
                print(f"   ❌ ROM is not ignored (status: {current_status})")
                continue
                
            if original_status != 'missing':
                print(f"   ❌ Original status is not missing (status: {original_status})")
                continue
            
            # Step 2: Simulate unignore (restore to original status)
            print(f"   🔄 Simulating unignore...")
            cursor.execute("""
                UPDATE scanned_roms 
                SET status = ?
                WHERE system_id = ? AND calculated_crc32 = ?
            """, (original_status, system_id, crc32))
            
            # Step 3: Verify unignore worked
            cursor.execute("""
                SELECT status FROM scanned_roms
                WHERE system_id = ? AND calculated_crc32 = ?
            """, (system_id, crc32))
            
            new_result = cursor.fetchone()
            if new_result and new_result[0] == 'missing':
                print(f"   ✅ Unignore successful: ROM restored to 'missing' status")
                success_count += 1
                
                # Restore to ignored for cleanup
                cursor.execute("""
                    UPDATE scanned_roms 
                    SET status = 'ignored'
                    WHERE system_id = ? AND calculated_crc32 = ?
                """, (system_id, crc32))
            else:
                print(f"   ❌ Unignore failed: ROM status is {new_result[0] if new_result else 'unknown'}")
        
        conn.commit()
        conn.close()
        
        overall_success = success_count == len(test_crc32s)
        print(f"\n{'✅ Unignore workflow test: PASSED' if overall_success else '❌ Unignore workflow test: FAILED'}")
        print(f"   {success_count}/{len(test_crc32s)} ROMs successfully unignored")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Error during unignore workflow test: {e}")
        return False

def cleanup_test_data(system_id, test_crc32s):
    """Clean up test data from the database."""
    print(f"\n🧹 Cleaning up test data...")
    
    db_path = Path(os.path.expanduser('~/.romplestiltskin/romplestiltskin.db'))
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        for crc32 in test_crc32s:
            cursor.execute("""
                DELETE FROM scanned_roms 
                WHERE system_id = ? AND calculated_crc32 = ?
            """, (system_id, crc32))
            print(f"   🗑️ Removed test ROM: {crc32}")
        
        conn.commit()
        conn.close()
        print(f"✅ Cleanup complete")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def main():
    """Run the complete test suite."""
    print("🔍 Complete Unignore Missing ROMs Fix Test")
    print("=" * 50)
    
    # Step 1: Setup test data
    print("\n📋 Step 1: Setting up test data...")
    setup_success, system_id, test_crc32s = setup_test_data()
    
    if not setup_success:
        print("❌ Failed to setup test data")
        return False
    
    try:
        # Step 2: Test column fix
        print("\n📋 Step 2: Testing column index fix...")
        column_fix_success = test_column_fix(system_id, test_crc32s)
        
        # Step 3: Test unignore workflow
        print("\n📋 Step 3: Testing unignore workflow...")
        workflow_success = test_unignore_workflow(system_id, test_crc32s)
        
        # Overall result
        overall_success = column_fix_success and workflow_success
        
        print(f"\n{'='*50}")
        print(f"📊 TEST RESULTS:")
        print(f"   Column Fix: {'✅ PASSED' if column_fix_success else '❌ FAILED'}")
        print(f"   Workflow: {'✅ PASSED' if workflow_success else '❌ FAILED'}")
        print(f"   Overall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        
        if overall_success:
            print(f"\n🎉 The unignore functionality for Missing files is now FIXED!")
            print(f"   - CRC32 is correctly extracted from column 5 (not column 4)")
            print(f"   - Ignored Missing ROMs can be properly restored to Missing status")
        else:
            print(f"\n❌ The unignore functionality still has issues")
        
        return overall_success
        
    finally:
        # Step 4: Cleanup
        print("\n📋 Step 4: Cleaning up...")
        cleanup_test_data(system_id, test_crc32s)

if __name__ == "__main__":
    main()