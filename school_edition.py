# School Edition: decorators and helpers (release/school branch only)
# Used only when APP_EDITION=school / REQUIRE_SCHOOL_CONTEXT=true.

import os
from functools import wraps
from flask import session, redirect, url_for, request
from flask_login import current_user


def is_school_edition():
    return os.environ.get('APP_EDITION', '').strip().lower() == 'school'


def require_school_context():
    return os.environ.get('REQUIRE_SCHOOL_CONTEXT', 'false').strip().lower() in ('true', '1', 'yes')


def school_context_required(f):
    """Require authenticated user with school_id and role in session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('school_landing_page', next=request.url))
        if not session.get('school_id'):
            return redirect(url_for('school_landing_page', next=request.url))
        return f(*args, **kwargs)
    return decorated


def require_role(role):
    """Require session role_context to be teacher or student."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('school_landing_page', next=request.url))
            if not session.get('school_id'):
                return redirect(url_for('school_landing_page', next=request.url))
            ctx = (session.get('role_context') or '').strip().lower()
            if ctx != role:
                # Redirect to correct dashboard
                if role == 'teacher':
                    return redirect(url_for('school_teacher_dashboard'))
                return redirect(url_for('school_student_dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator


def get_edition_context():
    """Return dict for templates: edition, role_context, school_mascot_logo_url, school_theme_colors."""
    edition = 'consumer'
    if is_school_edition():
        edition = 'school'
    role_context = (session.get('role_context') or '').strip().lower()
    school_id = session.get('school_id')
    school_mascot_logo_url = None
    school_theme_primary = None
    school_theme_secondary = None
    if school_id:
        try:
            from models import School
            school = School.query.get(school_id)
            if school:
                school_mascot_logo_url = school.mascot_logo_url
                school_theme_primary = school.theme_primary or os.environ.get('SCHOOL_DEFAULT_THEME_PRIMARY', '#E6A800')
                school_theme_secondary = school.theme_secondary or os.environ.get('SCHOOL_DEFAULT_THEME_SECONDARY', '#8B6914')
        except Exception:
            pass
    if not school_theme_primary:
        school_theme_primary = os.environ.get('SCHOOL_DEFAULT_THEME_PRIMARY', '#E6A800')
    if not school_theme_secondary:
        school_theme_secondary = os.environ.get('SCHOOL_DEFAULT_THEME_SECONDARY', '#8B6914')
    return {
        'edition': edition,
        'role_context': role_context,
        'school_mascot_logo_url': school_mascot_logo_url,
        'school_theme_primary': school_theme_primary,
        'school_theme_secondary': school_theme_secondary,
    }
