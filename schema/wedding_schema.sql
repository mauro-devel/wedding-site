PRAGMA foreign_keys = ON;

--------------------------------------------------
-- Invitations
--------------------------------------------------

CREATE TABLE invitation (
    id INTEGER PRIMARY KEY,
    invitation_code TEXT NOT NULL UNIQUE,
    country_code TEXT NOT NULL, -- ISO 3166-1 alpha-2 (e.g. ES, PT)
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- Guests
--------------------------------------------------

CREATE TABLE guest (
    id INTEGER PRIMARY KEY,
    invitation_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    is_primary_guest INTEGER NOT NULL DEFAULT 0,
    is_vegetarian INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (invitation_id) REFERENCES invitation(id) ON DELETE CASCADE
);

--------------------------------------------------
-- RSVP Status (i18n)
--------------------------------------------------

CREATE TABLE rsvp_status (
    id INTEGER PRIMARY KEY,
    status_key TEXT NOT NULL UNIQUE -- ACCEPTED, DECLINED, PENDING
);

CREATE TABLE rsvp_status_translation (
    rsvp_status_id INTEGER NOT NULL,
    language_code TEXT NOT NULL, -- 'es', 'pt-PT'
    label TEXT NOT NULL,
    PRIMARY KEY (rsvp_status_id, language_code),
    FOREIGN KEY (rsvp_status_id) REFERENCES rsvp_status(id) ON DELETE CASCADE
);

CREATE TABLE guest_rsvp (
    guest_id INTEGER PRIMARY KEY,
    rsvp_status_id INTEGER NOT NULL,
    responded_at TEXT,
    FOREIGN KEY (guest_id) REFERENCES guest(id) ON DELETE CASCADE,
    FOREIGN KEY (rsvp_status_id) REFERENCES rsvp_status(id)
);

--------------------------------------------------
-- Menu Items (i18n)
--------------------------------------------------

CREATE TABLE menu_item (
    id INTEGER PRIMARY KEY,
    menu_key TEXT NOT NULL UNIQUE -- MEAT, FISH, VEGETARIAN, VEGAN, CHILD
);

CREATE TABLE menu_item_translation (
    menu_item_id INTEGER NOT NULL,
    language_code TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    PRIMARY KEY (menu_item_id, language_code),
    FOREIGN KEY (menu_item_id) REFERENCES menu_item(id) ON DELETE CASCADE
);

CREATE TABLE guest_menu_choice (
    guest_id INTEGER PRIMARY KEY,
    menu_item_id INTEGER NOT NULL,
    FOREIGN KEY (guest_id) REFERENCES guest(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_item(id)
);

--------------------------------------------------
-- Dietary Restrictions (Allergies & Intolerances)
--------------------------------------------------

CREATE TABLE dietary_restriction (
    id INTEGER PRIMARY KEY,
    restriction_key TEXT NOT NULL UNIQUE -- GLUTEN, LACTOSE, NUTS, SEAFOOD, EGGS
);

CREATE TABLE dietary_restriction_translation (
    dietary_restriction_id INTEGER NOT NULL,
    language_code TEXT NOT NULL,
    label TEXT NOT NULL,
    PRIMARY KEY (dietary_restriction_id, language_code),
    FOREIGN KEY (dietary_restriction_id) REFERENCES dietary_restriction(id) ON DELETE CASCADE
);

CREATE TABLE guest_dietary_restriction (
    guest_id INTEGER NOT NULL,
    dietary_restriction_id INTEGER NOT NULL,
    PRIMARY KEY (guest_id, dietary_restriction_id),
    FOREIGN KEY (guest_id) REFERENCES guest(id) ON DELETE CASCADE,
    FOREIGN KEY (dietary_restriction_id) REFERENCES dietary_restriction(id)
);

--------------------------------------------------
-- Photos
--------------------------------------------------

CREATE TABLE photo (
    id INTEGER PRIMARY KEY,
    file_path TEXT NOT NULL,
    uploaded_by_guest_id INTEGER,
    is_professional INTEGER NOT NULL DEFAULT 0,
    uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by_guest_id) REFERENCES guest(id)
);

--------------------------------------------------
-- Optional Indexes (Recommended)
--------------------------------------------------

CREATE INDEX idx_guest_invitation ON guest(invitation_id);
CREATE INDEX idx_guest_email ON guest(email);
CREATE INDEX idx_photo_uploaded_by ON photo(uploaded_by_guest_id);

