#!/usr/bin/env python3
"""Create test data for development."""

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

def create_test_data():
    app = create_app('development')
    
    with app.app_context():
        print("Creating test invitations and guests...")
        
        # Get RSVP statuses
        status_accepted = RSVPStatus.query.filter_by(status_key='ACCEPTED').first()
        status_declined = RSVPStatus.query.filter_by(status_key='DECLINED').first()
        status_pending = RSVPStatus.query.filter_by(status_key='PENDING').first()
        
        if not status_accepted:
            print("❌ Error: RSVP statuses not found. Run 'python scripts/init_db.py' first.")
            return
        
        # Get menu items
        menu_meat = MenuItem.query.filter_by(menu_key='MEAT').first()
        menu_fish = MenuItem.query.filter_by(menu_key='FISH').first()
        menu_veg = MenuItem.query.filter_by(menu_key='VEGETARIAN').first()
        menu_child = MenuItem.query.filter_by(menu_key='CHILD').first()
        
        # Get dietary restrictions
        gluten = DietaryRestriction.query.filter_by(restriction_key='GLUTEN').first()
        lactose = DietaryRestriction.query.filter_by(restriction_key='LACTOSE').first()
        nuts = DietaryRestriction.query.filter_by(restriction_key='NUTS').first()
        
        # Clear existing test data (optional - comment out if you want to keep existing data)
        print("Clearing existing test invitations...")
        Invitation.query.filter(Invitation.invitation_code.like('WEDDING2026-%')).delete()
        db.session.commit()
        
        # Test Invitation 1 - Spanish couple (accepted)
        print("\nCreating invitation 1: Spanish couple (accepted)...")
        inv1 = Invitation(
            invitation_code='WEDDING2026-ES-001',
            country_code='ES'
        )
        db.session.add(inv1)
        db.session.flush()
        
        guest1 = Guest(
            invitation_id=inv1.id,
            first_name='Carlos',
            last_name='García',
            email='carlos.garcia@example.com',
            is_primary_guest=1,
            is_vegetarian=0
        )
        db.session.add(guest1)
        db.session.flush()
        
        guest1_rsvp = GuestRSVP(
            guest_id=guest1.id,
            rsvp_status_id=status_accepted.id,
            responded_at=datetime.utcnow().isoformat()
        )
        db.session.add(guest1_rsvp)
        
        guest1_menu = GuestMenuChoice(
            guest_id=guest1.id,
            menu_item_id=menu_meat.id
        )
        db.session.add(guest1_menu)
        
        guest2 = Guest(
            invitation_id=inv1.id,
            first_name='María',
            last_name='López',
            email='maria.lopez@example.com',
            is_primary_guest=0,
            is_vegetarian=1
        )
        db.session.add(guest2)
        db.session.flush()
        
        guest2_rsvp = GuestRSVP(
            guest_id=guest2.id,
            rsvp_status_id=status_accepted.id,
            responded_at=datetime.utcnow().isoformat()
        )
        db.session.add(guest2_rsvp)
        
        guest2_menu = GuestMenuChoice(
            guest_id=guest2.id,
            menu_item_id=menu_veg.id
        )
        db.session.add(guest2_menu)
        
        # Add dietary restriction for María
        guest2_dietary = GuestDietaryRestriction(
            guest_id=guest2.id,
            dietary_restriction_id=gluten.id
        )
        db.session.add(guest2_dietary)
        
        # Test Invitation 2 - Portuguese family (pending)
        print("Creating invitation 2: Portuguese family (pending)...")
        inv2 = Invitation(
            invitation_code='WEDDING2026-PT-001',
            country_code='PT'
        )
        db.session.add(inv2)
        db.session.flush()
        
        guest3 = Guest(
            invitation_id=inv2.id,
            first_name='João',
            last_name='Silva',
            email='joao.silva@example.com',
            is_primary_guest=1,
            is_vegetarian=0
        )
        db.session.add(guest3)
        
        guest4 = Guest(
            invitation_id=inv2.id,
            first_name='Ana',
            last_name='Silva',
            is_primary_guest=0,
            is_vegetarian=0
        )
        db.session.add(guest4)
        
        guest5 = Guest(
            invitation_id=inv2.id,
            first_name='Pedro',
            last_name='Silva',
            is_primary_guest=0,
            is_vegetarian=0,
            notes='Child - 8 years old'
        )
        db.session.add(guest5)
        
        # Test Invitation 3 - Declined
        print("Creating invitation 3: Spanish guest (declined)...")
        inv3 = Invitation(
            invitation_code='WEDDING2026-ES-002',
            country_code='ES'
        )
        db.session.add(inv3)
        db.session.flush()
        
        guest6 = Guest(
            invitation_id=inv3.id,
            first_name='Laura',
            last_name='Martínez',
            email='laura.martinez@example.com',
            is_primary_guest=1,
            is_vegetarian=0
        )
        db.session.add(guest6)
        db.session.flush()
        
        guest6_rsvp = GuestRSVP(
            guest_id=guest6.id,
            rsvp_status_id=status_declined.id,
            responded_at=datetime.utcnow().isoformat()
        )
        db.session.add(guest6_rsvp)
        
        # Test Invitation 4 - Large family with dietary restrictions
        print("Creating invitation 4: Large Spanish family...")
        inv4 = Invitation(
            invitation_code='WEDDING2026-ES-003',
            country_code='ES'
        )
        db.session.add(inv4)
        db.session.flush()
        
        guest7 = Guest(
            invitation_id=inv4.id,
            first_name='Antonio',
            last_name='Fernández',
            email='antonio.fernandez@example.com',
            is_primary_guest=1,
            is_vegetarian=0
        )
        db.session.add(guest7)
        db.session.flush()
        
        # Add nut allergy
        guest7_dietary = GuestDietaryRestriction(
            guest_id=guest7.id,
            dietary_restriction_id=nuts.id
        )
        db.session.add(guest7_dietary)
        
        guest8 = Guest(
            invitation_id=inv4.id,
            first_name='Isabel',
            last_name='Fernández',
            is_primary_guest=0,
            is_vegetarian=0
        )
        db.session.add(guest8)
        db.session.flush()
        
        # Add lactose intolerance
        guest8_dietary = GuestDietaryRestriction(
            guest_id=guest8.id,
            dietary_restriction_id=lactose.id
        )
        db.session.add(guest8_dietary)
        
        guest9 = Guest(
            invitation_id=inv4.id,
            first_name='Sofia',
            last_name='Fernández',
            is_primary_guest=0,
            is_vegetarian=0,
            notes='Child - 5 years old'
        )
        db.session.add(guest9)
        
        guest10 = Guest(
            invitation_id=inv4.id,
            first_name='Miguel',
            last_name='Fernández',
            is_primary_guest=0,
            is_vegetarian=0,
            notes='Child - 3 years old'
        )
        db.session.add(guest10)
        
        # Test Invitation 5 - Single Portuguese guest
        print("Creating invitation 5: Single Portuguese guest...")
        inv5 = Invitation(
            invitation_code='WEDDING2026-PT-002',
            country_code='PT'
        )
        db.session.add(inv5)
        db.session.flush()
        
        guest11 = Guest(
            invitation_id=inv5.id,
            first_name='Ricardo',
            last_name='Santos',
            email='ricardo.santos@example.com',
            is_primary_guest=1,
            is_vegetarian=1
        )
        db.session.add(guest11)
        
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ Test data created successfully!")
        print("="*60)
        print("\nTest Invitation Codes:")
        print("  1. WEDDING2026-ES-001 - Carlos & María (Spanish couple, ACCEPTED)")
        print("  2. WEDDING2026-PT-001 - Silva family (Portuguese, 3 guests, PENDING)")
        print("  3. WEDDING2026-ES-002 - Laura (Spanish, DECLINED)")
        print("  4. WEDDING2026-ES-003 - Fernández family (Spanish, 4 guests, PENDING)")
        print("  5. WEDDING2026-PT-002 - Ricardo (Portuguese, vegetarian, PENDING)")
        print("\nYou can now test the RSVP flow with these codes!")
        print("Visit: http://127.0.0.1:5000/rsvp")
        print("="*60 + "\n")

if __name__ == '__main__':
    create_test_data()