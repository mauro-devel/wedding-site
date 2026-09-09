#!/usr/bin/env python3
"""Wipe ALL invitations/guests/RSVPs (cascade). Keeps lookup tables
(rsvp_status, menu_item, dietary_restriction) intact. Requires --yes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models import Invitation


def reset_all_data(config_name='development'):
    app = create_app(config_name)
    with app.app_context():
        count = Invitation.query.count()
        print(f"This will delete ALL {count} invitation(s) and their guests/RSVPs.")
        print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")

        Invitation.query.delete(synchronize_session=False)
        db.session.commit()
        print("✅ All invitation/guest data wiped. Lookup tables untouched.")


if __name__ == '__main__':
    if '--yes' not in sys.argv:
        print("❌ Refusing to run without --yes flag (this is destructive).")
        print("   Usage: python scripts/reset_all_data.py [development|production] --yes")
        sys.exit(1)

    config_name = 'development'
    for arg in sys.argv[1:]:
        if arg in ('development', 'production'):
            config_name = arg

    reset_all_data(config_name)