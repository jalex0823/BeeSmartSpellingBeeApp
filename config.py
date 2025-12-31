"""
BeeSmart Configuration
Environment-based configuration for development and production
"""

import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv


def _load_env_files() -> None:
    """Load environment variables from dotenv files.

    Priority:
      1) Explicit path via BEESMART_ENV_FILE
      2) Repo-root .env (this file's directory)
      3) A couple common local locations (optional)

    We never fail hard here; missing dotenv files are expected in CI.
    """

    # 1) Explicit override (lets a dev keep their .env outside the repo)
    override = os.environ.get("BEESMART_ENV_FILE")
    if override:
        load_dotenv(dotenv_path=override, override=False)
        return

    # 2) Default: repo root (directory containing this config.py)
    repo_root = Path(__file__).resolve().parent
    load_dotenv(dotenv_path=repo_root / ".env", override=False)

    # 3) Optional fallbacks (best-effort; do not override existing env)
    # Note: None of these should be committed; they're just convenience.
    candidates = [
        repo_root / ".env.local",
        repo_root / "config" / ".env",
        Path.home() / ".config" / "beesmart" / ".env",
    ]
    for p in candidates:
        if p.exists():
            load_dotenv(dotenv_path=p, override=False)


# Load environment variables from dotenv files (best-effort)
_load_env_files()


class Config:
    """Base configuration"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-abc123'
    
    def _normalize_database_url(raw: str) -> str:
        """Normalize DATABASE_URL / DIGITALOCEAN_DATABASE_URL.

        - Accepts Railway-style postgres://
        - Keeps SQLite URLs unchanged
        - DigitalOcean Managed Postgres commonly *requires* SSL; if the URL doesn't
          specify sslmode, we default to sslmode=require.
        """
        if not raw:
            return raw

        # Keep SQLite (and any non-postgres) URLs as-is.
        if raw.startswith('sqlite:'):
            return raw

        # Fix for Railway's postgres:// vs postgresql://
        if raw.startswith('postgres://'):
            raw = raw.replace('postgres://', 'postgresql://', 1)

        if not raw.startswith('postgresql://'):
            return raw

        # Ensure sslmode is present (DigitalOcean typically needs it).
        try:
            parts = urlsplit(raw)
            q = dict(parse_qsl(parts.query, keep_blank_values=True))
            if 'sslmode' not in {k.lower(): v for k, v in q.items()}:
                q['sslmode'] = 'require'
                parts = parts._replace(query=urlencode(q))
                return urlunsplit(parts)
        except Exception:
            # If parsing fails, return raw; SQLAlchemy will raise a helpful error.
            return raw

        return raw

    # Database - Auto-detect from environment or default to SQLite
    # Allow DIGITALOCEAN_DATABASE_URL as a friendly alias during migration.
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get('DATABASE_URL')
        or os.environ.get('DIGITALOCEAN_DATABASE_URL')
        or 'sqlite:///beesmart.db'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for query debugging
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 300,    # Recycle connections after 5 minutes
    }
    
    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = 86400 * 30  # 30 days
    REMEMBER_COOKIE_SECURE = True  # Only send over HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'docx', 'pdf', 'png', 'jpg', 'jpeg'}
    
    # Application settings
    APP_NAME = 'BeeSmart Spelling Bee'
    APP_VERSION = '22'
    
    # Pagination
    STUDENTS_PER_PAGE = 25
    QUIZZES_PER_PAGE = 50
    
    # Email (SMTP) configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # SSL vs TLS
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    # Default port depends on SSL vs TLS if not explicitly set
    _port_env = os.environ.get('MAIL_PORT')
    if _port_env is not None and len(_port_env.strip()) > 0:
        MAIL_PORT = int(_port_env)
    else:
        MAIL_PORT = 465 if MAIL_USE_SSL else 587
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # Prefer explicit default sender; fallback to username if not provided
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME
    # Optional friendly display name (e.g., "BeeSmart Spelling Bee")
    MAIL_FROM_NAME = os.environ.get('MAIL_FROM_NAME') or 'BeeSmart Spelling Bee'

    # Optional: public base URL for absolute links in emails
    APP_BASE_URL = os.environ.get('APP_BASE_URL')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Show SQL queries in console
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    FLASK_ENV = 'production'
    
    # Production security
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    # Prefer real DB in CI/dev when provided (e.g., DigitalOcean Postgres) so
    # tests exercise the actual schema. Falls back to in-memory SQLite.
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or os.environ.get('DIGITALOCEAN_DATABASE_URL')
        or 'sqlite:///:memory:'
    )
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
