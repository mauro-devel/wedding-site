# wedding-site
A Flask-based wedding website with a complete RSVP management system using SQLite database.

## Features

- 🎊 Beautiful wedding website with countdown timer
- 📝 RSVP system with invitation code verification
- 🍽️ Menu selection for guests
- 🥗 Dietary restrictions tracking
- 🌍 Multi-language support (EN, ES, PT)
- 📊 Admin dashboard for managing RSVPs
- 💾 SQLite database for data persistence

## Project Structure

```
wedding-website/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── init_db.py             # Database initialization script
├── app/
│   └── models.py          # SQLAlchemy models
├── templates/
│   └── wedding_site.html  # Main wedding website
├── data/
│   └── wedding.db         # SQLite database (created automatically)
└── schema/
    └── wedding_schema.sql # Database schema
```

## Fonts:
- Creato display:
- Altone
- Australia Costom
- 
- 

## Setup Instructions

### 1. Install Pyenv

```bash
$ sudo apt update
$ sudo apt install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev \
xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```
### 2. Create virtual environment

```bash
$ peynv install 3.13.11
$ pyenv virtualenv 3.13.11 wedding-site-3.13
$ pyenv local wedding-site-3.13
```

### 3. Install dependencies

```bash
pip install -r requirements
```

### 4. Initialize the database

```bash
python init_db.py
```

## TODO
- [ ] Refine .gitignore

### On the server
- [ ] Disable SSH login (key-only). Install fail2ban.
- [ ] Configure firewall with ufw 
- [ ] Install Docker 
- [ ] Clone the repo in /opt/wedding-site
- [ ] Create .env file with SECRET_KEY and URL_DATABASE.

