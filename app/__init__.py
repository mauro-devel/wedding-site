from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
babel = Babel()

def get_locale():
    """Determine the best locale for the user."""
    # Try to get from session first
    if 'language' in session:
        return session['language']
    
    # Try to get from URL parameter
    lang = request.args.get('lang')
    if lang in ['es', 'pt_PT']:
        session['language'] = lang
        return lang
    # Fall back to browser preference
    return request.accept_languages.best_match(['es', 'pt_PT']) or 'es'

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load config
    if config_name == 'development':
        from app.config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'production':
        from app.config import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from app.config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Babel with locale selector
    babel.init_app(app, locale_selector=get_locale)
    
    # Make get_locale available in templates
    @app.context_processor
    def inject_locale():
        return dict(
            get_locale=lambda: get_locale(),
            current_locale=get_locale()
        )
    
    # Register blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Register CLI commands (if you created them)
    try:
        from app import cli
        cli.init_app(app)
    except ImportError:
        pass
    
    return app

# Create default app instance for Flask CLI
app = create_app()