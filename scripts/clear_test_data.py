#!/usr/bin/env python3
"""Delete only TEST- prefixed invitations (and their guests via cascade).
Safe to run in dev or prod — never touches real invitation codes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models import Invitation

TEST_PREFIX = 'TEST-'


def clear_test_data(config_name='development'):
    app = create_app(config_name)
    with app.app_context():
        count = Invitation.query.filter(
            Invitation.invitation_code.like(f'{TEST_PREFIX}%')
        ).count()

        if count == 0:
            print("No test invitations found. Nothing to do.")
            return

        print(f"Deleting {count} test invitation(s)...")
        Invitation.query.filter(
            Invitation.invitation_code.like(f'{TEST_PREFIX}%')
        ).delete(synchronize_session=False)
        db.session.commit()
        print("✅ Test data cleared.")


if __name__ == '__main__':
    config_name = sys.argv[1] if len(sys.argv) > 1 else 'development'
    clear_test_data(config_name)