import sqlite3
import os

def get_table_schema(cursor, table_name):
    cursor.execute(f'PRAGMA table_info({table_name})')
    return {row[1]: row[2] for row in cursor.fetchall()}

def main():
    db_path = os.path.expanduser('~/.romplestiltskin/romplestiltskin.db')
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    defined_schemas = {
        'systems': {
            'id': 'INTEGER',
            'system_name': 'TEXT',
            'dat_file_path': 'TEXT',
            'created_at': 'TIMESTAMP',
            'updated_at': 'TIMESTAMP',
            'game_count': 'INTEGER'
        },
        'games': {
            'id': 'INTEGER',
            'system_id': 'INTEGER',
            'dat_game_name': 'TEXT',
            'dat_rom_name': 'TEXT',
            'major_name': 'TEXT',
            'region': 'TEXT',
            'languages': 'TEXT',
            'is_beta': 'BOOLEAN',
            'is_demo': 'BOOLEAN',
            'is_proto': 'BOOLEAN',
            'is_unlicensed': 'BOOLEAN',
            'release_version': 'INTEGER',
            'is_unofficial_translation': 'BOOLEAN',
            'is_verified_dump': 'BOOLEAN',
            'is_modified_release': 'BOOLEAN',
            'is_pirate': 'BOOLEAN',
            'is_hack': 'BOOLEAN',
            'is_trainer': 'BOOLEAN',
            'is_overdump': 'BOOLEAN',
            'crc32': 'TEXT',
            'size': 'INTEGER',
            'md5': 'TEXT',
            'sha1': 'TEXT',
            'clone_of_id_string': 'TEXT',
            'disc_info': 'TEXT',
            'created_at': 'TIMESTAMP'
        }
    }

    for table_name, defined_schema in defined_schemas.items():
        print(f'--- Checking table: {table_name} ---')
        try:
            actual_schema = get_table_schema(cursor, table_name)
            for col, dtype in defined_schema.items():
                if col not in actual_schema:
                    print(f'  MISSING column: {col}')
                elif actual_schema[col] != dtype:
                    print(f'  MISMATCH column: {col} (expected {dtype}, got {actual_schema[col]})')
            for col in actual_schema:
                if col not in defined_schema:
                    print(f'  EXTRA column: {col}')
        except sqlite3.OperationalError:
            print(f'  Table not found')

    conn.close()

if __name__ == '__main__':
    main()