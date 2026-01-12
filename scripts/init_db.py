# scripts/init_db.py
import sqlite3
from pathlib import Path

def init_database(db_path="data/wedding.db"):
    """Initialize the wedding database with schema and seed data."""
    
    db_path = Path(db_path)
    db_path.parent.mkdir(exist_ok=True)
    
    # Read the SQL schema file
    sql_file = Path(__file__).parent.parent / "schema" / "wedding_schema.sql"
    
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        
        # Execute the schema
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        conn.executescript(sql_script)
        
        print(f"✅ Database initialized at {db_path}")
        print("📊 Tables created:")
        
        # Show created tables
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        
        # Count records in key tables
        cursor = conn.execute("SELECT COUNT(*) FROM invitation")
        print(f"\n📋 Invitations: {cursor.fetchone()[0]}")
        
        cursor = conn.execute("SELECT COUNT(*) FROM guest")
        print(f"👥 Guests: {cursor.fetchone()[0]}")

if __name__ == "__main__":
    init_database()
