#!/usr/bin/env python3
"""Initialize the database with schema and seed data."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models import (
    RSVPStatus, RSVPStatusTranslation,
    MenuItem, MenuItemTranslation,
    DietaryRestriction, DietaryRestrictionTranslation
)

def init_database():
    app = create_app('development')
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Seeding RSVP statuses...")
        seed_rsvp_statuses()
        
        print("Seeding menu items...")
        seed_menu_items()
        
        print("Seeding dietary restrictions...")
        seed_dietary_restrictions()
        
        print("✅ Database initialized successfully!")

def seed_rsvp_statuses():
    statuses = [
        {
            'key': 'ACCEPTED',
            'translations': {
                'es': 'Asistirá',
                'pt_PT': 'Confirmado'
            }
        },
        {
            'key': 'DECLINED',
            'translations': {
                'es': 'No asistirá',
                'pt_PT': 'Recusado'
            }
        },
        {
            'key': 'PENDING',
            'translations': {
                'es': 'Pendiente',
                'pt_PT': 'Pendente'
            }
        }
    ]
    
    for status_data in statuses:
        if not RSVPStatus.query.filter_by(status_key=status_data['key']).first():
            status = RSVPStatus(status_key=status_data['key'])
            db.session.add(status)
            db.session.flush()
            
            for lang, label in status_data['translations'].items():
                translation = RSVPStatusTranslation(
                    rsvp_status_id=status.id,
                    language_code=lang,
                    label=label
                )
                db.session.add(translation)
    
    db.session.commit()

def seed_menu_items():
    menu_items = [
        {
            'key': 'MEAT',
            'translations': {
                'es': {'name': 'Carne', 'description': 'Plato principal de carne'},
                'pt_PT': {'name': 'Carne', 'description': 'Prato principal de carne'}
            }
        },
        {
            'key': 'FISH',
            'translations': {
                'es': {'name': 'Pescado', 'description': 'Plato principal de pescado'},
                'pt_PT': {'name': 'Peixe', 'description': 'Prato principal de peixe'}
            }
        },
        {
            'key': 'VEGETARIAN',
            'translations': {
                'es': {'name': 'Vegetariano', 'description': 'Opción vegetariana'},
                'pt_PT': {'name': 'Vegetariano', 'description': 'Opção vegetariana'}
            }
        },
        {
            'key': 'VEGAN',
            'translations': {
                'es': {'name': 'Vegano', 'description': 'Opción vegana'},
                'pt_PT': {'name': 'Vegano', 'description': 'Opção vegana'}
            }
        },
        {
            'key': 'CHILD',
            'translations': {
                'es': {'name': 'Menú infantil', 'description': 'Para niños'},
                'pt_PT': {'name': 'Menu infantil', 'description': 'Para crianças'}
            }
        }
    ]
    
    for item_data in menu_items:
        if not MenuItem.query.filter_by(menu_key=item_data['key']).first():
            item = MenuItem(menu_key=item_data['key'])
            db.session.add(item)
            db.session.flush()
            
            for lang, trans_data in item_data['translations'].items():
                translation = MenuItemTranslation(
                    menu_item_id=item.id,
                    language_code=lang,
                    name=trans_data['name'],
                    description=trans_data.get('description')
                )
                db.session.add(translation)
    
    db.session.commit()

def seed_dietary_restrictions():
    restrictions = [
        {
            'key': 'GLUTEN',
            'translations': {
                'es': 'Sin gluten',
                'pt_PT': 'Sem glúten'
            }
        },
        {
            'key': 'LACTOSE',
            'translations': {
                'es': 'Sin lactosa',
                'pt_PT': 'Sem lactose'
            }
        },
        {
            'key': 'NUTS',
            'translations': {
                'es': 'Sin frutos secos',
                'pt_PT': 'Sem frutos secos'
            }
        },
        {
            'key': 'SEAFOOD',
            'translations': {
                'es': 'Sin mariscos',
                'pt_PT': 'Sem marisco'
            }
        },
        {
            'key': 'EGGS',
            'translations': {
                'es': 'Sin huevos',
                'pt_PT': 'Sem ovos'
            }
        }
    ]
    
    for restriction_data in restrictions:
        if not DietaryRestriction.query.filter_by(restriction_key=restriction_data['key']).first():
            restriction = DietaryRestriction(restriction_key=restriction_data['key'])
            db.session.add(restriction)
            db.session.flush()
            
            for lang, label in restriction_data['translations'].items():
                translation = DietaryRestrictionTranslation(
                    dietary_restriction_id=restriction.id,
                    language_code=lang,
                    label=label
                )
                db.session.add(translation)
    
    db.session.commit()

if __name__ == '__main__':
    init_database()
