#!/usr/bin/env python3
"""
Database diagnostic script to check for potential corruption or issues
before recommending clearing ROM data.
"""

import sys
import os
import sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.settings_manager import SettingsManager
from core.scanned_roms_manager import ScannedROMsManager
from core.db_manager import DatabaseManager
from core.rom_scanner import ROMStatus

def check_database_integrity(db_path):
    """Check SQLite database integrity."""
    print("🔍 Checking database integrity...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Run SQLite integrity check
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        
        if result == "ok":
            print("✅ Database integrity: OK")
            return True
        else:
            print(f"❌ Database integrity issues found: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database integrity: {e}")
        return False
    finally:
        conn.close()

def check_table_counts(db_path):
    """Check table record counts and look for anomalies."""
    print("\n📊 Checking table record counts...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tables = ['systems', 'games', 'scanned_roms']
        counts = {}
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            counts[table] = count
            print(f"  {table}: {count} records")
        
        return counts
        
    except Exception as e:
        print(f"❌ Error checking table counts: {e}")
        return {}
    finally:
        conn.close()

def check_orphaned_records(db_path):
    """Check for orphaned records that might indicate corruption."""
    print("\n🔗 Checking for orphaned records...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for games without valid system_id
        cursor.execute("""
            SELECT COUNT(*) FROM games g 
            LEFT JOIN systems s ON g.system_id = s.id 
            WHERE s.id IS NULL
        """)
        orphaned_games = cursor.fetchone()[0]
        
        # Check for scanned_roms without valid system_id
        cursor.execute("""
            SELECT COUNT(*) FROM scanned_roms sr 
            LEFT JOIN systems s ON sr.system_id = s.id 
            WHERE s.id IS NULL
        """)
        orphaned_scanned_roms = cursor.fetchone()[0]
        
        print(f"  Orphaned games: {orphaned_games}")
        print(f"  Orphaned scanned ROMs: {orphaned_scanned_roms}")
        
        return orphaned_games == 0 and orphaned_scanned_roms == 0
        
    except Exception as e:
        print(f"❌ Error checking orphaned records: {e}")
        return False
    finally:
        conn.close()

def check_missing_rom_status_distribution(scanned_roms_manager):
    """Check the distribution of ROM statuses to identify potential issues."""
    print("\n📈 Checking ROM status distribution...")
    try:
        # Get all systems
        db_manager = DatabaseManager(scanned_roms_manager.db_path)
        systems = db_manager.get_all_systems()
        
        total_issues = 0
        
        for system in systems:
            system_id = system['id']
            system_name = system['system_name']
            print(f"\n  System: {system_name}")
            
            status_counts = {}
            for status in [ROMStatus.CORRECT, ROMStatus.MISSING, ROMStatus.NOT_RECOGNIZED, 
                          ROMStatus.BROKEN, ROMStatus.IGNORED]:
                roms = scanned_roms_manager.get_scanned_roms_by_status(system_id, status)
                count = len(roms)
                status_counts[status.value] = count
                print(f"    {status.value}: {count}")
            
            # Check for potential issues
            total_roms = sum(status_counts.values())
            if total_roms > 0:
                missing_ratio = status_counts.get('missing', 0) / total_roms
                broken_ratio = status_counts.get('broken', 0) / total_roms
                
                if missing_ratio > 0.8:  # More than 80% missing
                    print(f"    ⚠️  High missing ROM ratio: {missing_ratio:.1%}")
                    total_issues += 1
                    
                if broken_ratio > 0.5:  # More than 50% broken
                    print(f"    ⚠️  High broken ROM ratio: {broken_ratio:.1%}")
                    total_issues += 1
        
        return total_issues
        
    except Exception as e:
        print(f"❌ Error checking ROM status distribution: {e}")
        return -1

def check_duplicate_entries(db_path):
    """Check for duplicate entries that might indicate corruption."""
    print("\n🔍 Checking for duplicate entries...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check for duplicate scanned_roms by system_id + file_path
        cursor.execute("""
            SELECT system_id, file_path, COUNT(*) as count
            FROM scanned_roms 
            GROUP BY system_id, file_path 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            print(f"  Found {len(duplicates)} duplicate file entries:")
            for dup in duplicates[:5]:  # Show first 5
                print(f"    System {dup[0]}, File: {dup[1]}, Count: {dup[2]}")
            if len(duplicates) > 5:
                print(f"    ... and {len(duplicates) - 5} more")
            return False
        else:
            print("  ✅ No duplicate entries found")
            return True
            
    except Exception as e:
        print(f"❌ Error checking duplicates: {e}")
        return False
    finally:
        conn.close()

def main():
    print("🏥 Romplestiltskin Database Diagnostic Tool")
    print("=" * 50)
    
    # Initialize managers
    settings_manager = SettingsManager()
    db_path = settings_manager.get_database_path()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    print(f"📁 Database location: {db_path}")
    
    # Run diagnostics
    integrity_ok = check_database_integrity(db_path)
    table_counts = check_table_counts(db_path)
    orphans_ok = check_orphaned_records(db_path)
    duplicates_ok = check_duplicate_entries(db_path)
    
    # Initialize ROM manager for status checks
    scanned_roms_manager = ScannedROMsManager(db_path)
    status_issues = check_missing_rom_status_distribution(scanned_roms_manager)
    
    # Summary and recommendations
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    issues_found = []
    
    if not integrity_ok:
        issues_found.append("Database integrity check failed")
    
    if not orphans_ok:
        issues_found.append("Orphaned records found")
    
    if not duplicates_ok:
        issues_found.append("Duplicate entries found")
    
    if status_issues > 0:
        issues_found.append(f"ROM status distribution issues ({status_issues} systems affected)")
    
    if not issues_found:
        print("✅ No major issues detected in the database")
        print("\n💡 RECOMMENDATION:")
        print("   The database appears healthy. Before clearing ROM data, try:")
        print("   1. Restart the application")
        print("   2. Re-scan your ROM directories")
        print("   3. Check if the issue persists")
        print("   4. Only clear ROM data if the problem continues")
    else:
        print("⚠️  Issues detected:")
        for issue in issues_found:
            print(f"   • {issue}")
        
        print("\n💡 RECOMMENDATIONS:")
        if not integrity_ok:
            print("   🚨 CRITICAL: Database corruption detected!")
            print("   • Backup your database immediately")
            print("   • Clearing ROM data may be necessary")
        else:
            print("   • Try selective clearing first (per-system)")
            print("   • Consider backing up your database before clearing")
            print("   • Full ROM data clearing may resolve these issues")
    
    print("\n📊 Database Statistics:")
    for table, count in table_counts.items():
        print(f"   {table}: {count} records")

if __name__ == '__main__':
    main()