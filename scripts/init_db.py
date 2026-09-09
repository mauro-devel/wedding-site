#!/usr/bin/env python3
"""Create database tables only. Run seed_lookups.py afterward to populate
lookup tables (RSVP statuses, menu items, dietary restrictions)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db


def init_database(config_name='development'):
    app = create_app(config_name)
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Tables created. Now run: python scripts/seed_lookups.py")


if __name__ == '__main__':
    config_name = sys.argv[1] if len(sys.argv) > 1 else 'development'
    init_database(config_name)