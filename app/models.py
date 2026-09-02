from app import db
from datetime import datetime


class Invitation(db.Model):
    __tablename__ = 'invitation'

    id = db.Column(db.Integer, primary_key=True)
    invitation_code = db.Column(db.Text, nullable=False, unique=True)
    country_code = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Text, nullable=False, default=lambda: datetime.utcnow().isoformat())

    guests = db.relationship('Guest', backref='invitation', lazy=True, cascade='all, delete-orphan')


class Guest(db.Model):
    __tablename__ = 'guest'

    id = db.Column(db.Integer, primary_key=True)
    invitation_id = db.Column(db.Integer, db.ForeignKey('invitation.id'), nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text)
    is_primary_guest = db.Column(db.Integer, nullable=False, default=0)
    is_vegetarian = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text)  # free-text: accommodation, children info, other notes

    rsvp = db.relationship('GuestRSVP', backref='guest', uselist=False, cascade='all, delete-orphan')
    menu_choice = db.relationship('GuestMenuChoice', backref='guest', uselist=False, cascade='all, delete-orphan')
    dietary_restrictions = db.relationship('GuestDietaryRestriction', backref='guest', cascade='all, delete-orphan')


class RSVPStatus(db.Model):
    __tablename__ = 'rsvp_status'

    id = db.Column(db.Integer, primary_key=True)
    status_key = db.Column(db.Text, nullable=False, unique=True)

    translations = db.relationship('RSVPStatusTranslation', backref='status', cascade='all, delete-orphan')

    def label(self, lang):
        for t in self.translations:
            if t.language_code == lang:
                return t.label
        return self.status_key


class RSVPStatusTranslation(db.Model):
    __tablename__ = 'rsvp_status_translation'

    rsvp_status_id = db.Column(db.Integer, db.ForeignKey('rsvp_status.id'), primary_key=True)
    language_code = db.Column(db.Text, primary_key=True)
    label = db.Column(db.Text, nullable=False)


class GuestRSVP(db.Model):
    __tablename__ = 'guest_rsvp'

    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), primary_key=True)
    rsvp_status_id = db.Column(db.Integer, db.ForeignKey('rsvp_status.id'), nullable=False)
    responded_at = db.Column(db.Text)

    status = db.relationship('RSVPStatus', backref='guest_rsvps')


class MenuItem(db.Model):
    __tablename__ = 'menu_item'

    id = db.Column(db.Integer, primary_key=True)
    menu_key = db.Column(db.Text, nullable=False, unique=True)

    translations = db.relationship('MenuItemTranslation', backref='menu_item', cascade='all, delete-orphan')

    def name(self, lang):
        for t in self.translations:
            if t.language_code == lang:
                return t.name
        return self.menu_key

    def description(self, lang):
        for t in self.translations:
            if t.language_code == lang:
                return t.description
        return None


class MenuItemTranslation(db.Model):
    __tablename__ = 'menu_item_translation'

    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), primary_key=True)
    language_code = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)


class GuestMenuChoice(db.Model):
    __tablename__ = 'guest_menu_choice'

    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)

    menu_item = db.relationship('MenuItem', backref='guest_choices')


class DietaryRestriction(db.Model):
    __tablename__ = 'dietary_restriction'

    id = db.Column(db.Integer, primary_key=True)
    restriction_key = db.Column(db.Text, nullable=False, unique=True)

    translations = db.relationship('DietaryRestrictionTranslation', backref='restriction', cascade='all, delete-orphan')

    def label(self, lang):
        for t in self.translations:
            if t.language_code == lang:
                return t.label
        return self.restriction_key


class DietaryRestrictionTranslation(db.Model):
    __tablename__ = 'dietary_restriction_translation'

    dietary_restriction_id = db.Column(db.Integer, db.ForeignKey('dietary_restriction.id'), primary_key=True)
    language_code = db.Column(db.Text, primary_key=True)
    label = db.Column(db.Text, nullable=False)


class GuestDietaryRestriction(db.Model):
    __tablename__ = 'guest_dietary_restriction'

    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'), primary_key=True)
    dietary_restriction_id = db.Column(db.Integer, db.ForeignKey('dietary_restriction.id'), primary_key=True)

    restriction = db.relationship('DietaryRestriction', backref='guest_links')  # <-- new

class Photo(db.Model):
    __tablename__ = 'photo'

    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.Text, nullable=False)
    uploaded_by_guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'))
    is_professional = db.Column(db.Integer, nullable=False, default=0)
    uploaded_at = db.Column(db.Text, nullable=False, default=lambda: datetime.utcnow().isoformat())

    uploaded_by = db.relationship('Guest', backref='uploaded_photos')