#!/usr/bin/env python3
"""Create TEST- prefixed invitations/guests for dev UI testing.
Refuses to run against a production config."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models import (
    Invitation, Guest, RSVPStatus, MenuItem,
    DietaryRestriction, GuestRSVP, GuestMenuChoice,
    GuestDietaryRestriction
)
from datetime import datetime

TEST_PREFIX = 'TEST-'


def create_test_data():
    app = create_app('development')

    if app.config.get('SQLALCHEMY_DATABASE_URI', '').endswith('data/wedding.db'):
        print("❌ Refusing to run: this looks like the production database path.")
        sys.exit(1)

    with app.app_context():
        print("Creating test invitations and guests...")

        status_accepted = RSVPStatus.query.filter_by(status_key='ACCEPTED').first()
        status_declined = RSVPStatus.query.filter_by(status_key='DECLINED').first()

        if not status_accepted:
            print("❌ Error: RSVP statuses not found. Run 'python scripts/seed_lookups.py' first.")
            return

        menu_meat = MenuItem.query.filter_by(menu_key='MEAT').first()
        menu_veg = MenuItem.query.filter_by(menu_key='VEGETARIAN').first()
        gluten = DietaryRestriction.query.filter_by(restriction_key='GLUTEN').first()

        print(f"Clearing existing {TEST_PREFIX}* invitations...")
        Invitation.query.filter(Invitation.invitation_code.like(f'{TEST_PREFIX}%')).delete()
        db.session.commit()

        inv1 = Invitation(invitation_code=f'{TEST_PREFIX}ES-001', country_code='ES')
        db.session.add(inv1)
        db.session.flush()

        g1 = Guest(invitation_id=inv1.id, first_name='Carlos', last_name='García',
                    email='carlos@example.com', is_primary_guest=1)
        db.session.add(g1)
        db.session.flush()
        db.session.add(GuestRSVP(guest_id=g1.id, rsvp_status_id=status_accepted.id,
                                   responded_at=datetime.utcnow().isoformat()))

        g2 = Guest(invitation_id=inv1.id, first_name='María', last_name='López',
                    email='maria@example.com', is_primary_guest=0)
        db.session.add(g2)
        db.session.flush()
        db.session.add(GuestRSVP(guest_id=g2.id, rsvp_status_id=status_accepted.id,
                                   responded_at=datetime.utcnow().isoformat()))

        inv2 = Invitation(invitation_code=f'{TEST_PREFIX}PT-001', country_code='PT')
        db.session.add(inv2)
        db.session.flush()
        db.session.add(Guest(invitation_id=inv2.id, first_name='João', last_name='Silva',
                               email='joao@example.com', is_primary_guest=1))
        db.session.add(Guest(invitation_id=inv2.id, first_name='Ana', last_name='Silva',
                               is_primary_guest=0))

        inv3 = Invitation(invitation_code=f'{TEST_PREFIX}ES-002', country_code='ES')
        db.session.add(inv3)
        db.session.flush()
        g3 = Guest(invitation_id=inv3.id, first_name='Laura', last_name='Martínez',
                    email='laura@example.com', is_primary_guest=1)
        db.session.add(g3)
        db.session.flush()
        db.session.add(GuestRSVP(guest_id=g3.id, rsvp_status_id=status_declined.id,
                                   responded_at=datetime.utcnow().isoformat()))

        db.session.commit()

        print("\n" + "=" * 60)
        print("✅ Test data created successfully!")
        print("=" * 60)
        print(f"  {TEST_PREFIX}ES-001 - Carlos & María (accepted)")
        print(f"  {TEST_PREFIX}PT-001 - Silva family (pending)")
        print(f"  {TEST_PREFIX}ES-002 - Laura (declined)")
        print("=" * 60 + "\n")


if __name__ == '__main__':
    create_test_data()