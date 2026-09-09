#!/usr/bin/env python3
"""Load the final invitation/guest list from load_invitations.sql and
load_guests.sql. Uses the app's configured database — run with the right
config_name (development/production)."""

import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app

SCRIPTS_DIR = Path(__file__).parent


def load_final_guests(config_name='production'):
    app = create_app(config_name)
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']

    if not db_uri.startswith('sqlite:///'):
        print(f"❌ This script only supports SQLite. Got: {db_uri}")
        sys.exit(1)

    db_path = db_uri.replace('sqlite:///', '', 1)
    # Handle the 4-slash absolute-path form (sqlite:////abs/path)
    if not db_path.startswith('/'):
        db_path = '/' + db_path

    print(f"Target database: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")

    try:
        existing = conn.execute("SELECT COUNT(*) FROM invitation").fetchone()[0]
        if existing > 0:
            print(f"⚠️  {existing} invitation(s) already exist in this database.")
            confirm = input("Continue and INSERT on top of existing data? [y/N] ")
            if confirm.lower() != 'y':
                print("Aborted. Run reset_all_data.py first if you want a clean load.")
                return

        print("Loading invitations...")
        invitations_sql = (SCRIPTS_DIR / 'load_invitations.sql').read_text(encoding='utf-8')
        conn.executescript(invitations_sql)

        print("Loading guests...")
        guests_sql = (SCRIPTS_DIR / 'load_guests.sql').read_text(encoding='utf-8')
        conn.executescript(guests_sql)

        conn.commit()

        inv_count = conn.execute("SELECT COUNT(*) FROM invitation").fetchone()[0]
        guest_count = conn.execute("SELECT COUNT(*) FROM guest").fetchone()[0]
        print(f"✅ Loaded {inv_count} invitations, {guest_count} guests.")

    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"❌ Failed (integrity error, likely duplicate IDs/codes): {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    config_name = sys.argv[1] if len(sys.argv) > 1 else 'production'
    load_final_guests(config_name)