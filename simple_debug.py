import sqlite3

conn = sqlite3.connect('scanned_roms.db')
cursor = conn.cursor()

print("=== DATABASE TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f'Found {len(tables)} tables:')
for table in tables:
    print(f'  - {table[0]}')

if tables:
    print("\n=== TABLE SCHEMAS ===")
    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Show some sample data
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Rows: {count}")
        
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            print("  Sample data:")
            for row in rows:
                print(f"    {row}")

conn.close()