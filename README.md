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
- 🐳 Docker deployment with Nginx and SSL support

## Project Structure

```
wedding-site/
├── README.md
├── requirements.txt
├── babel.cfg
├── messages.pot
├── wedding_site_template.html
├── Dockerfile
├── Dockerfile.dev
├── docker-compose.yml
├── docker-compose.override.yml
├── .env.example
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration classes
│   ├── models.py            # SQLAlchemy models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── main.py          # Main routes
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   └── uploads/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── rsvp.html
│   │   ├── rsvp_guests.html
│   │   └── rsvp_confirmation.html
│   └── translations/
│       ├── es/
│       │   └── LC_MESSAGES/
│       │       ├── messages.mo
│       │       └── messages.po
│       └── pt_PT/
│           └── LC_MESSAGES/
│               ├── messages.mo
│               └── messages.po
├── docker/
│   └── nginx/
│       └── nginx.conf
├── instance/                # Instance-specific config
├── schema/
│   └── wedding_schema.sql
├── scripts/
│   ├── init_db.py
│   └── create_test_data.py
└── templates/               # Additional templates
```

## Fonts

- Creato Display
- Altone
- Australia Custom

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip
- (Optional) pyenv for version management
- Docker and Docker Compose for deployment

### 1. Clone the repository

```bash
git clone <repo-url>
cd wedding-site
```

### 2. (Optional) Install Pyenv

```bash
sudo apt update
sudo apt install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev \
xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
pyenv install 3.13.11
pyenv virtualenv 3.13.11 wedding-site-3.13
pyenv local wedding-site-3.13
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your settings (SECRET_KEY, DATABASE_URL, etc.)

### 5. Initialize the database

```bash
python scripts/init_db.py
```

To create test data:

```bash
python scripts/create_test_data.py
```

## Running the Application

### Local Development

```bash
flask run
```

The app will be available at http://localhost:5000

### With Docker (Development)

```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
```

### Production Deployment

```bash
docker-compose up --build
```

## Internationalization

The app supports multiple languages. To update translations:

1. Extract messages: `pybabel extract -F babel.cfg -o messages.pot .`
2. Update .po files: `pybabel update -i messages.pot -d app/translations`
3. Compile: `pybabel compile -d app/translations`

## TODO

- [ ] Refine .gitignore
- [ ] Add more tests
- [ ] Improve admin dashboard

### Server Setup

- [ ] Disable SSH password login (key-only). Install fail2ban.
- [ ] Configure firewall with ufw
- [ ] Install Docker
- [ ] Clone the repo in /opt/wedding-site
- [ ] Create .env file with SECRET_KEY and DATABASE_URL
- [ ] Set up SSL certificates with certbot

