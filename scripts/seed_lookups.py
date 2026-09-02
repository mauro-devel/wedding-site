"""
Seed lookup tables: RSVPStatus, MenuItem, DietaryRestriction and their
es / pt_PT translations.

Run once (safe to re-run — it upserts by key):

    python -m scripts.seed_lookups

Requires app context, so run from project root with app/ importable.
"""
from app import create_app, db
from app.models import (
    RSVPStatus, RSVPStatusTranslation,
    MenuItem, MenuItemTranslation,
    DietaryRestriction, DietaryRestrictionTranslation,
)

RSVP_STATUSES = {
    'ACCEPTED': {'es': 'Confirmado', 'pt_PT': 'Confirmado'},
    'DECLINED': {'es': 'Rechazado', 'pt_PT': 'Recusado'},
    'PENDING':  {'es': 'Pendiente', 'pt_PT': 'Pendente'},
}

MENU_ITEMS = {
    'MEAT': {
        'es': ('Carne', ''),
        'pt_PT': ('Carne', ''),
    },
    'FISH': {
        'es': ('Pescado', ''),
        'pt_PT': ('Peixe', ''),
    },
    'VEGETARIAN': {
        'es': ('Vegetariano', ''),
        'pt_PT': ('Vegetariano', ''),
    },
    'VEGAN': {
        'es': ('Vegano', ''),
        'pt_PT': ('Vegano', ''),
    },
    'CHILD': {
        'es': ('Menú infantil', ''),
        'pt_PT': ('Menu infantil', ''),
    },
}

DIETARY_RESTRICTIONS = {
    'GLUTEN':  {'es': 'Sin gluten', 'pt_PT': 'Sem glúten'},
    'LACTOSE': {'es': 'Intolerancia a la lactosa', 'pt_PT': 'Intolerância à lactose'},
    'NUTS':    {'es': 'Alergia a frutos secos', 'pt_PT': 'Alergia a frutos secos'},
    'SEAFOOD': {'es': 'Alergia al marisco', 'pt_PT': 'Alergia a marisco'},
    'EGGS':    {'es': 'Alergia al huevo', 'pt_PT': 'Alergia a ovo'},
}


def upsert_status(key, translations):
    status = RSVPStatus.query.filter_by(status_key=key).first()
    if not status:
        status = RSVPStatus(status_key=key)
        db.session.add(status)
        db.session.flush()
    for lang, label in translations.items():
        t = RSVPStatusTranslation.query.filter_by(
            rsvp_status_id=status.id, language_code=lang).first()
        if t:
            t.label = label
        else:
            db.session.add(RSVPStatusTranslation(
                rsvp_status_id=status.id, language_code=lang, label=label))


def upsert_menu_item(key, translations):
    item = MenuItem.query.filter_by(menu_key=key).first()
    if not item:
        item = MenuItem(menu_key=key)
        db.session.add(item)
        db.session.flush()
    for lang, (name, description) in translations.items():
        t = MenuItemTranslation.query.filter_by(
            menu_item_id=item.id, language_code=lang).first()
        if t:
            t.name = name
            t.description = description
        else:
            db.session.add(MenuItemTranslation(
                menu_item_id=item.id, language_code=lang,
                name=name, description=description))


def upsert_dietary_restriction(key, translations):
    restriction = DietaryRestriction.query.filter_by(restriction_key=key).first()
    if not restriction:
        restriction = DietaryRestriction(restriction_key=key)
        db.session.add(restriction)
        db.session.flush()
    for lang, label in translations.items():
        t = DietaryRestrictionTranslation.query.filter_by(
            dietary_restriction_id=restriction.id, language_code=lang).first()
        if t:
            t.label = label
        else:
            db.session.add(DietaryRestrictionTranslation(
                dietary_restriction_id=restriction.id, language_code=lang, label=label))


def run():
    app = create_app()
    with app.app_context():
        for key, translations in RSVP_STATUSES.items():
            upsert_status(key, translations)
        for key, translations in MENU_ITEMS.items():
            upsert_menu_item(key, translations)
        for key, translations in DIETARY_RESTRICTIONS.items():
            upsert_dietary_restriction(key, translations)
        db.session.commit()
        print('Lookup tables seeded successfully.')


if __name__ == '__main__':
    run()