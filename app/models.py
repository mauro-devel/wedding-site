# app/models.py
"""
Database models for the wedding website.
All models use SQLAlchemy ORM with SQLite backend.
"""

from datetime import datetime
from typing import List, Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    Column, Integer, String, Boolean, Text, DateTime, ForeignKey, 
    Table, CheckConstraint, Index, event, DDL, text
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass

# Initialize SQLAlchemy with our custom Base
db = SQLAlchemy(model_class=Base)

# ---------------------------------------------------------------------
# Association Tables (Many-to-Many)
# ---------------------------------------------------------------------

guest_dietary_restriction = Table(
    'guest_dietary_restriction',
    db.metadata,
    Column('guest_id', Integer, ForeignKey('guest.id', ondelete='CASCADE'), primary_key=True),
    Column('dietary_restriction_id', Integer, ForeignKey('dietary_restriction.id'), primary_key=True),
    Column('custom_note', Text, nullable=True),  # For "OTHER" restrictions
    extend_existing=True
)

# ---------------------------------------------------------------------
# Main Models
# ---------------------------------------------------------------------

class Invitation(db.Model):
    """
    Represents a wedding invitation sent to a group of guests.
    Each invitation has a unique code for RSVP access.
    """
    __tablename__ = 'invitation'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invitation_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)  # ISO 3166-1 alpha-2
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    guests: Mapped[List["Guest"]] = relationship(
        'Guest', 
        back_populates='invitation', 
        cascade='all, delete-orphan',
        order_by='Guest.is_primary_guest.desc(), Guest.last_name, Guest.first_name'
    )
    
    # Properties
    @hybrid_property
    def total_guests(self) -> int:
        """Total number of guests in this invitation."""
        return len(self.guests)
    
    @hybrid_property
    def primary_guest(self) -> Optional["Guest"]:
        """Get the primary guest for this invitation."""
        for guest in self.guests:
            if guest.is_primary_guest:
                return guest
        return None
    
    @hybrid_property
    def rsvp_status_summary(self) -> dict:
        """Get RSVP status counts for this invitation."""
        from collections import Counter
        status_counts = Counter()
        for guest in self.guests:
            if guest.rsvp and guest.rsvp.status:
                status_counts[guest.rsvp.status.status_key] += 1
        return dict(status_counts)
    
    def __repr__(self) -> str:
        return f'<Invitation {self.invitation_code} ({self.country_code})>'
    
    def to_dict(self, include_guests: bool = False) -> dict:
        """Convert invitation to dictionary (for API responses)."""
        data = {
            'id': self.id,
            'invitation_code': self.invitation_code,
            'country_code': self.country_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_guests': self.total_guests,
            'primary_guest': self.primary_guest.full_name if self.primary_guest else None
        }
        if include_guests:
            data['guests'] = [guest.to_dict() for guest in self.guests]
        return data


class Guest(db.Model):
    """
    Represents an individual guest.
    Multiple guests can belong to one invitation.
    """
    __tablename__ = 'guest'
    __table_args__ = (
        # Prevent duplicate emails within the same invitation
        db.UniqueConstraint('invitation_id', 'email', name='uq_guest_invitation_email'),
        CheckConstraint('is_primary_guest IN (0, 1)', name='ck_guest_primary'),
        CheckConstraint('is_vegetarian IN (0, 1)', name='ck_guest_vegetarian'),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invitation_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('invitation.id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    is_primary_guest: Mapped[bool] = mapped_column(Boolean, default=False)
    is_vegetarian: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    invitation: Mapped["Invitation"] = relationship('Invitation', back_populates='guests')
    rsvp: Mapped[Optional["GuestRSVP"]] = relationship(
        'GuestRSVP', 
        back_populates='guest', 
        uselist=False, 
        cascade='all, delete-orphan'
    )
    menu_choice: Mapped[Optional["GuestMenuChoice"]] = relationship(
        'GuestMenuChoice', 
        back_populates='guest', 
        uselist=False, 
        cascade='all, delete-orphan'
    )
    dietary_restrictions: Mapped[List["DietaryRestriction"]] = relationship(
        'DietaryRestriction', 
        secondary=guest_dietary_restriction,
        back_populates='guests',
        cascade='all, delete'
    )
    photos: Mapped[List["Photo"]] = relationship(
        'Photo', 
        back_populates='uploaded_by',
        order_by='Photo.uploaded_at.desc()'
    )
    
    # Association proxies for easier access
    dietary_restriction_keys = association_proxy('dietary_restrictions', 'restriction_key')
    
    # Properties
    @hybrid_property
    def full_name(self) -> str:
        """Get guest's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @hybrid_property
    def rsvp_status(self) -> Optional[str]:
        """Get RSVP status key."""
        return self.rsvp.status.status_key if self.rsvp and self.rsvp.status else None
    
    @hybrid_property
    def menu_choice_key(self) -> Optional[str]:
        """Get menu choice key."""
        return self.menu_choice.menu_item.menu_key if self.menu_choice and self.menu_choice.menu_item else None
    
    def __repr__(self) -> str:
        return f'<Guest {self.full_name} (Invitation: {self.invitation_id})>'
    
    def to_dict(self, include_relationships: bool = True) -> dict:
        """Convert guest to dictionary (for API responses)."""
        data = {
            'id': self.id,
            'invitation_id': self.invitation_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'is_primary_guest': self.is_primary_guest,
            'is_vegetarian': self.is_vegetarian,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_relationships:
            data.update({
                'rsvp_status': self.rsvp_status,
                'rsvp_responded_at': self.rsvp.responded_at.isoformat() if self.rsvp and self.rsvp.responded_at else None,
                'menu_choice': self.menu_choice_key,
                'dietary_restrictions': [dr.to_dict() for dr in self.dietary_restrictions]
            })
        
        return data


class RSVPStatus(db.Model):
    """
    RSVP status master table (ACCEPTED, DECLINED, PENDING).
    Uses translations for internationalization.
    """
    __tablename__ = 'rsvp_status'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status_key: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # ACCEPTED, DECLINED, PENDING
    
    # Relationships
    translations: Mapped[List["RSVPStatusTranslation"]] = relationship(
        'RSVPStatusTranslation', 
        back_populates='rsvp_status', 
        cascade='all, delete-orphan'
    )
    guest_rsvps: Mapped[List["GuestRSVP"]] = relationship('GuestRSVP', back_populates='status')
    
    # Properties
    @hybrid_property
    def label(self) -> str:
        """Get English label (default)."""
        for translation in self.translations:
            if translation.language_code == 'en':
                return translation.label
        return self.status_key.title()
    
    def get_label(self, language_code: str = 'en') -> str:
        """Get label for specific language."""
        for translation in self.translations:
            if translation.language_code == language_code:
                return translation.label
        return self.label
    
    def __repr__(self) -> str:
        return f'<RSVPStatus {self.status_key}>'
    
    def to_dict(self, language_code: str = 'en') -> dict:
        """Convert RSVP status to dictionary."""
        return {
            'id': self.id,
            'status_key': self.status_key,
            'label': self.get_label(language_code)
        }


class RSVPStatusTranslation(db.Model):
    """
    Translation table for RSVP status labels.
    """
    __tablename__ = 'rsvp_status_translation'
    __table_args__ = (
        db.PrimaryKeyConstraint('rsvp_status_id', 'language_code'),
    )
    
    rsvp_status_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('rsvp_status.id', ondelete='CASCADE'), 
        primary_key=True
    )
    language_code: Mapped[str] = mapped_column(String(10), primary_key=True)  # 'en', 'es', 'pt-PT'
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationships
    rsvp_status: Mapped["RSVPStatus"] = relationship('RSVPStatus', back_populates='translations')
    
    def __repr__(self) -> str:
        return f'<RSVPStatusTranslation {self.language_code}:{self.label}>'


class GuestRSVP(db.Model):
    """
    RSVP response from a guest.
    """
    __tablename__ = 'guest_rsvp'
    
    guest_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('guest.id', ondelete='CASCADE'), 
        primary_key=True
    )
    rsvp_status_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('rsvp_status.id'), 
        nullable=False, 
        default=1  # Default to PENDING
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    guest: Mapped["Guest"] = relationship('Guest', back_populates='rsvp')
    status: Mapped["RSVPStatus"] = relationship('RSVPStatus', back_populates='guest_rsvps')
    
    def __repr__(self) -> str:
        return f'<GuestRSVP {self.guest_id}:{self.rsvp_status_id}>'
    
    def to_dict(self, language_code: str = 'en') -> dict:
        """Convert guest RSVP to dictionary."""
        return {
            'guest_id': self.guest_id,
            'rsvp_status': self.status.to_dict(language_code) if self.status else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None
        }


class MenuItem(db.Model):
    """
    Menu items available for selection (MEAT, FISH, VEGETARIAN, etc.).
    Uses translations for internationalization.
    """
    __tablename__ = 'menu_item'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    menu_key: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # MEAT, FISH, VEGETARIAN
    
    # Relationships
    translations: Mapped[List["MenuItemTranslation"]] = relationship(
        'MenuItemTranslation', 
        back_populates='menu_item', 
        cascade='all, delete-orphan'
    )
    guest_choices: Mapped[List["GuestMenuChoice"]] = relationship('GuestMenuChoice', back_populates='menu_item')
    
    # Properties
    @hybrid_property
    def name(self) -> str:
        """Get English name (default)."""
        for translation in self.translations:
            if translation.language_code == 'en':
                return translation.name
        return self.menu_key.title()
    
    def get_name(self, language_code: str = 'en') -> str:
        """Get name for specific language."""
        for translation in self.translations:
            if translation.language_code == language_code:
                return translation.name
        return self.name
    
    def get_description(self, language_code: str = 'en') -> Optional[str]:
        """Get description for specific language."""
        for translation in self.translations:
            if translation.language_code == language_code:
                return translation.description
        return None
    
    def __repr__(self) -> str:
        return f'<MenuItem {self.menu_key}>'
    
    def to_dict(self, language_code: str = 'en') -> dict:
        """Convert menu item to dictionary."""
        return {
            'id': self.id,
            'menu_key': self.menu_key,
            'name': self.get_name(language_code),
            'description': self.get_description(language_code)
        }


class MenuItemTranslation(db.Model):
    """
    Translation table for menu items.
    """
    __tablename__ = 'menu_item_translation'
    __table_args__ = (
        db.PrimaryKeyConstraint('menu_item_id', 'language_code'),
    )
    
    menu_item_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('menu_item.id', ondelete='CASCADE'), 
        primary_key=True
    )
    language_code: Mapped[str] = mapped_column(String(10), primary_key=True)  # 'en', 'es', 'pt-PT'
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    menu_item: Mapped["MenuItem"] = relationship('MenuItem', back_populates='translations')
    
    def __repr__(self) -> str:
        return f'<MenuItemTranslation {self.language_code}:{self.name}>'


class GuestMenuChoice(db.Model):
    """
    Menu choice selected by a guest.
    """
    __tablename__ = 'guest_menu_choice'
    
    guest_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('guest.id', ondelete='CASCADE'), 
        primary_key=True
    )
    menu_item_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('menu_item.id'), 
        nullable=False
    )
    
    # Relationships
    guest: Mapped["Guest"] = relationship('Guest', back_populates='menu_choice')
    menu_item: Mapped["MenuItem"] = relationship('MenuItem', back_populates='guest_choices')
    
    def __repr__(self) -> str:
        return f'<GuestMenuChoice {self.guest_id}:{self.menu_item_id}>'
    
    def to_dict(self, language_code: str = 'en') -> dict:
        """Convert guest menu choice to dictionary."""
        return {
            'guest_id': self.guest_id,
            'menu_item': self.menu_item.to_dict(language_code) if self.menu_item else None
        }


class DietaryRestriction(db.Model):
    """
    Dietary restrictions/allergies (GLUTEN, LACTOSE, NUTS, etc.).
    Uses translations for internationalization.
    """
    __tablename__ = 'dietary_restriction'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    restriction_key: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)  # GLUTEN, LACTOSE
    
    # Relationships
    translations: Mapped[List["DietaryRestrictionTranslation"]] = relationship(
        'DietaryRestrictionTranslation', 
        back_populates='dietary_restriction', 
        cascade='all, delete-orphan'
    )
    guests: Mapped[List["Guest"]] = relationship(
        'Guest', 
        secondary=guest_dietary_restriction,
        back_populates='dietary_restrictions'
    )
    
    # Properties
    @hybrid_property
    def label(self) -> str:
        """Get English label (default)."""
        for translation in self.translations:
            if translation.language_code == 'en':
                return translation.label
        return self.restriction_key.title()
    
    def get_label(self, language_code: str = 'en') -> str:
        """Get label for specific language."""
        for translation in self.translations:
            if translation.language_code == language_code:
                return translation.label
        return self.label
    
    def __repr__(self) -> str:
        return f'<DietaryRestriction {self.restriction_key}>'
    
    def to_dict(self, language_code: str = 'en') -> dict:
        """Convert dietary restriction to dictionary."""
        return {
            'id': self.id,
            'restriction_key': self.restriction_key,
            'label': self.get_label(language_code)
        }


class DietaryRestrictionTranslation(db.Model):
    """
    Translation table for dietary restrictions.
    """
    __tablename__ = 'dietary_restriction_translation'
    __table_args__ = (
        db.PrimaryKeyConstraint('dietary_restriction_id', 'language_code'),
    )
    
    dietary_restriction_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey('dietary_restriction.id', ondelete='CASCADE'), 
        primary_key=True
    )
    language_code: Mapped[str] = mapped_column(String(10), primary_key=True)  # 'en', 'es', 'pt-PT'
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationships
    dietary_restriction: Mapped["DietaryRestriction"] = relationship(
        'DietaryRestriction', 
        back_populates='translations'
    )
    
    def __repr__(self) -> str:
        return f'<DietaryRestrictionTranslation {self.language_code}:{self.label}>'


class Photo(db.Model):
    """
    Photos uploaded by guests or professional photographers.
    """
    __tablename__ = 'photo'
    __table_args__ = (
        CheckConstraint('is_professional IN (0, 1)', name='ck_photo_professional'),
        CheckConstraint('is_approved IN (0, 1)', name='ck_photo_approved'),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_path: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # In bytes
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    uploaded_by_guest_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey('guest.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    is_professional: Mapped[bool] = mapped_column(Boolean, default=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)  # Admin approval for user uploads
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    uploaded_by: Mapped[Optional["Guest"]] = relationship('Guest', back_populates='photos')
    
    # Properties
    @hybrid_property
    def url(self) -> str:
        """Get URL for the photo."""
        return f"/static/uploads/{self.file_name}"
    
    @hybrid_property
    def thumbnail_url(self) -> str:
        """Get URL for the thumbnail (assuming naming convention)."""
        name, ext = self.file_name.rsplit('.', 1)
        return f"/static/uploads/thumbnails/{name}_thumb.{ext}"
    
    @hybrid_property
    def file_size_mb(self) -> Optional[float]:
        """Get file size in MB."""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
    
    def __repr__(self) -> str:
        return f'<Photo {self.file_name} ({self.file_size_mb}MB)>'
    
    def to_dict(self) -> dict:
        """Convert photo to dictionary."""
        return {
            'id': self.id,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_size_mb': self.file_size_mb,
            'mime_type': self.mime_type,
            'url': self.url,
            'thumbnail_url': self.thumbnail_url,
            'uploaded_by_guest_id': self.uploaded_by_guest_id,
            'uploaded_by_name': self.uploaded_by.full_name if self.uploaded_by else None,
            'is_professional': self.is_professional,
            'is_approved': self.is_approved,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class AdminUser(db.Model):
    """
    Admin users for managing the wedding site.
    """
    __tablename__ = 'admin_user'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f'<AdminUser {self.username}>'
    
    def to_dict(self) -> dict:
        """Convert admin user to dictionary (without sensitive data)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class AuditLog(db.Model):
    """
    Audit log for tracking changes to the database.
    """
    __tablename__ = 'audit_log'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(20), nullable=False)  # CREATE, UPDATE, DELETE
    table_name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    record_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    old_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    new_values: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    performed_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # admin_user_id or guest_id
    user_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'admin', 'guest'
    performed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # Supports IPv6
    
    def __repr__(self) -> str:
        return f'<AuditLog {self.action} {self.table_name}.{self.record_id}>'
    
    def to_dict(self) -> dict:
        """Convert audit log to dictionary."""
        return {
            'id': self.id,
            'action': self.action,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'performed_by': self.performed_by,
            'user_type': self.user_type,
            'performed_at': self.performed_at.isoformat() if self.performed_at else None,
            'ip_address': self.ip_address
        }


# ---------------------------------------------------------------------
# Database Initialization and Utility Functions
# ---------------------------------------------------------------------

def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create database views if they don't exist
        create_database_views()
        
        # Seed initial data
        seed_initial_data()


def create_database_views():
    """Create database views for reporting."""
    
    # Guest summary view
    guest_summary_view = text("""
        CREATE VIEW IF NOT EXISTS guest_summary AS
        SELECT 
            g.id,
            g.first_name || ' ' || g.last_name as full_name,
            g.email,
            i.invitation_code,
            i.country_code,
            g.is_primary_guest,
            g.is_vegetarian,
            rs.status_key as rsvp_status,
            gr.responded_at as rsvp_date,
            mi.menu_key as menu_choice,
            GROUP_CONCAT(dr.restriction_key, ', ') as dietary_restrictions
        FROM guest g
        JOIN invitation i ON g.invitation_id = i.id
        LEFT JOIN guest_rsvp gr ON g.id = gr.guest_id
        LEFT JOIN rsvp_status rs ON gr.rsvp_status_id = rs.id
        LEFT JOIN guest_menu_choice gmc ON g.id = gmc.guest_id
        LEFT JOIN menu_item mi ON gmc.menu_item_id = mi.id
        LEFT JOIN guest_dietary_restriction gdr ON g.id = gdr.guest_id
        LEFT JOIN dietary_restriction dr ON gdr.dietary_restriction_id = dr.id
        GROUP BY g.id
    """)
    
    # Invitation summary view
    invitation_summary_view = text("""
        CREATE VIEW IF NOT EXISTS invitation_summary AS
        SELECT 
            i.id,
            i.invitation_code,
            i.country_code,
            COUNT(g.id) as total_guests,
            COUNT(CASE WHEN g.is_primary_guest = 1 THEN 1 END) as primary_guests,
            COUNT(CASE WHEN gr.rsvp_status_id = 2 THEN 1 END) as accepted_count,
            COUNT(CASE WHEN gr.rsvp_status_id = 3 THEN 1 END) as declined_count,
            COUNT(CASE WHEN gr.rsvp_status_id = 1 THEN 1 END) as pending_count,
            i.created_at,
            i.updated_at
        FROM invitation i
        LEFT JOIN guest g ON i.id = g.invitation_id
        LEFT JOIN guest_rsvp gr ON g.id = gr.guest_id
        GROUP BY i.id
    """)
    
    try:
        db.session.execute(guest_summary_view)
        db.session.execute(invitation_summary_view)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Warning: Could not create database views: {e}")


def seed_initial_data():
    """Seed the database with initial data."""
    
    # Check if data already exists
    if RSVPStatus.query.first() is not None:
        return  # Data already seeded
    
    # 1. RSVP Statuses
    rsvp_statuses = [
        RSVPStatus(status_key='PENDING'),
        RSVPStatus(status_key='ACCEPTED'),
        RSVPStatus(status_key='DECLINED')
    ]
    
    rsvp_translations = [
        # English translations
        RSVPStatusTranslation(rsvp_status=rsvp_statuses[0], language_code='en', label='Pending'),
        RSVPStatusTranslation(rsvp_status=rsvp_statuses[1], language_code='en', label='Accepted'),
        RSVPStatusTranslation(rsvp_status=rsvp_statuses[2], language_code='en', label='Declined'),
        # Spanish translations
        RSVPStatusTranslation(rsvp_status=rsvp_statuses[0], language_code='es', label='Pendiente'),
        RSVPStatusTranslation(rsvp_status=rsvp_statuses[1], language_code='es', label='Aceptado'),
        RSVPStatusTranslation(rsvp_status=rsvp_statuses[2], language_code='es', label='Rechazado'),
        # Portuguese translations
        RSVPStatusTranslation(rsvp_status=rsvp_statuses[0], language_code='pt', label='Pendente'),
        RSVPStatusTranslation(rsvp_status=rsvp_statuses[1], language_code='pt', label='Aceito'),
        RSVPStatusTranslation(rsvp_status=rsvp_statuses[2], language_code='pt', label='Recusado'),
    ]
    
    # 2. Menu Items
    menu_items = [
        MenuItem(menu_key='MEAT'),
        MenuItem(menu_key='FISH'),
        MenuItem(menu_key='VEGETARIAN'),
        MenuItem(menu_key='VEGAN'),
        MenuItem(menu_key='CHILD')
    ]
    
    menu_translations = [
        # English translations
        MenuItemTranslation(menu_item=menu_items[0], language_code='en', name='Meat', description='Grilled beef with seasonal vegetables'),
        MenuItemTranslation(menu_item=menu_items[1], language_code='en', name='Fish', description='Salmon with lemon butter sauce'),
        MenuItemTranslation(menu_item=menu_items[2], language_code='en', name='Vegetarian', description='Mushroom risotto with truffle oil'),
        MenuItemTranslation(menu_item=menu_items[3], language_code='en', name='Vegan', description='Seasonal vegetable curry'),
        MenuItemTranslation(menu_item=menu_items[4], language_code='en', name='Child', description='Chicken tenders with fries'),
        # Spanish translations
        MenuItemTranslation(menu_item=menu_items[0], language_code='es', name='Carne', description='Ternera a la parrilla con verduras de temporada'),
        MenuItemTranslation(menu_item=menu_items[1], language_code='es', name='Pescado', description='Salmón con salsa de mantequilla y limón'),
        MenuItemTranslation(menu_item=menu_items[2], language_code='es', name='Vegetariano', description='Risotto de setas con aceite de trufa'),
        MenuItemTranslation(menu_item=menu_items[3], language_code='es', name='Vegano', description='Curry de verduras de temporada'),
        MenuItemTranslation(menu_item=menu_items[4], language_code='es', name='Infantil', description='Tiras de pollo con patatas fritas'),
    ]
    
    # 3. Dietary Restrictions
    dietary_restrictions = [
        DietaryRestriction(restriction_key='GLUTEN'),
        DietaryRestriction(restriction_key='LACTOSE'),
        DietaryRestriction(restriction_key='NUTS'),
        DietaryRestriction(restriction_key='SEAFOOD'),
        DietaryRestriction(restriction_key='EGGS'),
        DietaryRestriction(restriction_key='OTHER')
    ]
    
    dietary_translations = [
        # English translations
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[0], language_code='en', label='Gluten'),
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[1], language_code='en', label='Lactose'),
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[2], language_code='en', label='Nuts'),
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[3], language_code='en', label='Seafood'),
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[4], language_code='en', label='Eggs'),
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[5], language_code='en', label='Other'),
        # Spanish translations
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[0], language_code='es', label='Gluten'),
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[1], language_code='es', label='Lactosa'),
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[2], language_code='es', label='Frutos secos'),
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[3], language_code='es', label='Marisco'),
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[4], language_code='es', label='Huevos'),
        DietaryRestrictionTranslation(dietary_restriction=dietary_restrictions[5], language_code='es', label='Otro'),
    ]
    
    # 4. Default Admin User (password will need to be set separately)
    admin_user = AdminUser(
        username='admin',
        password_hash='',  # Should be set via password reset
        email='admin@wedding.com',
        is_active=True
    )
    
    # Add all to session and commit
    try:
        db.session.add_all(rsvp_statuses)
        db.session.add_all(rsvp_translations)
        db.session.add_all(menu_items)
        db.session.add_all(menu_translations)
        db.session.add_all(dietary_restrictions)
        db.session.add_all(dietary_translations)
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Database seeded with initial data")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error seeding database: {e}")


# ---------------------------------------------------------------------
# Event Listeners for Audit Logging
# ---------------------------------------------------------------------

def setup_audit_logging():
    """Setup event listeners for audit logging."""
    
    @event.listens_for(db.session, 'after_flush')
    def receive_after_flush(session, flush_context):
        """Track changes to models for audit logging."""
        for obj in session.new:
            if isinstance(obj, AuditLog):
                continue  # Skip audit log entries themselves
            
            # Log creation
            audit_entry = AuditLog(
                action='CREATE',
                table_name=obj.__tablename__,
                record_id=getattr(obj, 'id', None),
                new_values=str({col: getattr(obj, col) for col in obj.__table__.columns.keys()}),
                performed_by=None,  # Could be set from current user context
                user_type=None
            )
            session.add(audit_entry)
        
        for obj in session.dirty:
            if isinstance(obj, AuditLog):
                continue
            
            # Get changes
            changes = {}
            for attr in db.inspect(obj).attrs:
                if attr.history.has_changes():
                    changes[attr.key] = {
                        'old': attr.history.deleted[0] if attr.history.deleted else None,
                        'new': attr.value
                    }
            
            if changes:
                audit_entry = AuditLog(
                    action='UPDATE',
                    table_name=obj.__tablename__,
                    record_id=getattr(obj, 'id', None),
                    old_values=str({k: v['old'] for k, v in changes.items()}),
                    new_values=str({k: v['new'] for k, v in changes.items()}),
                    performed_by=None,
                    user_type=None
                )
                session.add(audit_entry)
        
        for obj in session.deleted:
            if isinstance(obj, AuditLog):
                continue
            
            audit_entry = AuditLog(
                action='DELETE',
                table_name=obj.__tablename__,
                record_id=getattr(obj, 'id', None),
                old_values=str({col: getattr(obj, col) for col in obj.__table__.columns.keys()}),
                performed_by=None,
                user_type=None
            )
            session.add(audit_entry)
