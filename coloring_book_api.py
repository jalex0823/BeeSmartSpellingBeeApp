"""Coloring Book QR Challenge API

Implements server-driven A–Z word list progress and a hidden avatar unlock.
"""

from __future__ import annotations

from flask import Blueprint, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from sqlalchemy import inspect
from datetime import datetime

from models import db, WordSet, ColoringBookList, ColoringBookListItem, UserEntitlement


coloring_book_bp = Blueprint('coloring_book', __name__)
coloring_book_qr_bp = Blueprint('coloring_book_qr', __name__)

# ---------------------------------------------------------------------------
# A–Z word sets (5 kid-friendly words per letter)
# ---------------------------------------------------------------------------
COLORING_BOOK_WORD_SETS = {
    'a': ['ant', 'apple', 'acorn', 'airplane', 'astronaut'],
    'b': ['bear', 'butterfly', 'balloon', 'banana', 'bridge'],
    'c': ['cat', 'cloud', 'candle', 'castle', 'crayon'],
    'd': ['dog', 'dolphin', 'daisy', 'dragon', 'drum'],
    'e': ['eagle', 'elephant', 'egg', 'earth', 'engine'],
    'f': ['frog', 'flower', 'feather', 'fish', 'forest'],
    'g': ['giraffe', 'garden', 'grapes', 'ghost', 'guitar'],
    'h': ['horse', 'honey', 'hammer', 'heart', 'helmet'],
    'i': ['igloo', 'island', 'insect', 'iron', 'ivy'],
    'j': ['jaguar', 'jellyfish', 'jungle', 'jacket', 'jewel'],
    'k': ['kangaroo', 'kite', 'kitten', 'kettle', 'knight'],
    'l': ['lion', 'ladder', 'lantern', 'lemon', 'lighthouse'],
    'm': ['monkey', 'mountain', 'magnet', 'mirror', 'mushroom'],
    'n': ['nest', 'needle', 'notebook', 'narwhal', 'noodle'],
    'o': ['octopus', 'orange', 'otter', 'ocean', 'owl'],
    'p': ['penguin', 'pumpkin', 'parrot', 'planet', 'puzzle'],
    'q': ['queen', 'quilt', 'quail', 'quarter', 'question'],
    'r': ['rabbit', 'rainbow', 'rocket', 'river', 'robot'],
    's': ['snake', 'sunflower', 'starfish', 'spider', 'storm'],
    't': ['tiger', 'turtle', 'tornado', 'telescope', 'trumpet'],
    'u': ['umbrella', 'unicorn', 'universe', 'urchin', 'uniform'],
    'v': ['volcano', 'violin', 'village', 'vulture', 'vine'],
    'w': ['whale', 'wizard', 'waterfall', 'wagon', 'wolf'],
    'x': ['xylophone', 'x-ray', 'xenops', 'xerus', 'xyster'],
    'y': ['yarn', 'yellow', 'yo-yo', 'yacht', 'yardstick'],
    'z': ['zebra', 'zipper', 'zeppelin', 'zinnia', 'zombie'],
}


def seed_word_sets() -> None:
    """Idempotently insert all 26 letter word sets into the word_sets table.

    Safe to call on every startup — skips sets that already exist.
    """
    try:
        _ensure_coloring_book_schema()
        inserted = 0
        for letter, words in COLORING_BOOK_WORD_SETS.items():
            set_id = f'{letter}-set-01'
            if not WordSet.query.filter_by(set_id=set_id).first():
                db.session.add(WordSet(
                    set_id=set_id,
                    letter=letter,
                    words_json=words,
                    active=True,
                ))
                inserted += 1
        if inserted:
            db.session.commit()
            print(f' Coloring Book: seeded {inserted} word set(s)')
        else:
            print(' Coloring Book: all word sets already present')
    except Exception as exc:
        try:
            db.session.rollback()
        except Exception:
            pass
        print(f' Coloring Book seed_word_sets failed: {exc}')


def _ensure_coloring_book_schema() -> bool:
    """Best-effort initializer for Coloring Book tables.

    Safe to call multiple times.
    """
    try:
        insp = inspect(db.engine)
        needed = {'word_sets', 'coloring_book_lists', 'coloring_book_list_items', 'user_entitlements'}
        existing = set(insp.get_table_names() or [])
        if needed.issubset(existing):
            return True
    except Exception:
        pass

    try:
        db.create_all()
        return True
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
        return False


def _extract_set_id_from_qr(raw: str) -> str:
    """Accept either a token like 'a-set-01' or a URL containing it."""
    s = str(raw or '').strip()
    if not s:
        return ''
    try:
        if '://' in s:
            from urllib.parse import urlparse

            p = urlparse(s)
            path = (p.path or '').strip('/')
            if path:
                s = path.split('/')[-1]
    except Exception:
        pass
    return s.strip()


@coloring_book_bp.route('/wordlists/from-set', methods=['POST'])
@login_required
def from_set():
    try:
        _ensure_coloring_book_schema()

        data = request.get_json(silent=True) or {}
        set_id_raw = data.get('set_id') or data.get('qr') or data.get('value')
        set_id = _extract_set_id_from_qr(set_id_raw)
        if not set_id:
            return jsonify({"created": False, "error": "set_id_required"}), 400

        ws = WordSet.query.filter_by(set_id=set_id, active=True).first()
        if not ws:
            return jsonify({"created": False, "error": "set_not_found", "set_id": set_id}), 404

        created = False
        lst = ColoringBookList.query.filter_by(user_id=current_user.id, source_set_id=set_id).first()
        if not lst:
            created = True
            letter = str(getattr(ws, 'letter', '') or '').strip().upper() or set_id[:1].upper()
            title = f"Coloring Book - {letter}"
            lst = ColoringBookList(user_id=current_user.id, source_set_id=set_id, title=title, status='active')
            db.session.add(lst)
            db.session.flush()

            words = getattr(ws, 'words_json', []) or []
            words = [str(w).strip() for w in words if str(w or '').strip()][:5]
            for w in words:
                db.session.add(ColoringBookListItem(list_id=lst.id, word=w, is_completed=False))
            db.session.commit()

        items = (ColoringBookListItem.query
                 .filter_by(list_id=lst.id)
                 .order_by(ColoringBookListItem.id.asc())
                 .all())
        words_out = [it.word for it in (items or [])]

        return jsonify({
            "created": created,
            "list": {
                "list_id": lst.id,
                "title": lst.title,
                "source_set_id": lst.source_set_id,
                "status": lst.status,
            },
            "words": words_out,
        }), 200

    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({"created": False, "error": "server_error", "message": str(e)}), 500


@coloring_book_bp.route('/wordlists/<int:list_id>/words/complete', methods=['POST'])
@login_required
def complete_word(list_id: int):
    try:
        _ensure_coloring_book_schema()

        data = request.get_json(silent=True) or {}
        word_raw = (data.get('word') or '').strip()
        if not word_raw:
            return jsonify({"word_completed": False, "error": "word_required"}), 400

        lst = ColoringBookList.query.filter_by(id=list_id, user_id=current_user.id).first()
        if not lst:
            return jsonify({"word_completed": False, "error": "not_found"}), 404

        items = ColoringBookListItem.query.filter_by(list_id=lst.id).all()
        target = None
        for it in (items or []):
            if str(it.word or '').strip().lower() == word_raw.lower():
                target = it
                break
        if not target:
            return jsonify({"word_completed": False, "error": "word_not_in_list"}), 400

        word_completed = False
        if not bool(getattr(target, 'is_completed', False)):
            target.is_completed = True
            target.completed_at = datetime.utcnow()
            db.session.add(target)
            word_completed = True

        completed_count = ColoringBookListItem.query.filter_by(list_id=lst.id, is_completed=True).count()
        list_completed = False
        if completed_count >= 5 and str(getattr(lst, 'status', '') or '').lower() != 'completed':
            lst.status = 'completed'
            lst.completed_at = datetime.utcnow()
            db.session.add(lst)
            list_completed = True

        db.session.commit()

        completed_lists_count = ColoringBookList.query.filter_by(user_id=current_user.id, status='completed').count()
        alphabet_completed = bool(completed_lists_count >= 26)

        unlocked_avatar = None
        if alphabet_completed:
            key = 'avatar.spelling_champion'
            existing = UserEntitlement.query.filter_by(
                user_id=current_user.id,
                entitlement_type='avatar',
                entitlement_key=key
            ).first()
            if not existing:
                ent = UserEntitlement(
                    user_id=current_user.id,
                    entitlement_type='avatar',
                    entitlement_key=key,
                    source='coloring_book_alphabet',
                    source_id='26of26'
                )
                db.session.add(ent)
                db.session.commit()
                unlocked_avatar = key

        return jsonify({
            "word_completed": bool(word_completed),
            "list_completed": bool(list_completed),
            "completed_lists_count": int(completed_lists_count),
            "alphabet_completed": bool(alphabet_completed),
            "unlocked_avatar": unlocked_avatar,
        }), 200

    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({"word_completed": False, "error": "server_error", "message": str(e)}), 500


@coloring_book_bp.route('/coloring-book/status', methods=['GET'])
@login_required
def status():
    try:
        _ensure_coloring_book_schema()

        completed = ColoringBookList.query.filter_by(user_id=current_user.id, status='completed').all()
        completed_set_ids = [c.source_set_id for c in (completed or []) if getattr(c, 'source_set_id', None)]
        completed_lists_count = len(completed_set_ids)

        key = 'avatar.spelling_champion'
        ent = UserEntitlement.query.filter_by(
            user_id=current_user.id,
            entitlement_type='avatar',
            entitlement_key=key
        ).first()
        unlocked_avatars = [key] if ent else []

        return jsonify({
            "completed_lists_count": int(completed_lists_count),
            "total_lists": 26,
            "completed_set_ids": completed_set_ids,
            "unlocked_avatars": unlocked_avatars,
        }), 200

    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({"error": "server_error", "message": str(e)}), 500


# ---------------------------------------------------------------------------
# QR landing route — GET /q/coloring/<set_id>
# This is the URL embedded in the physical coloring-book QR codes.
# ---------------------------------------------------------------------------
@coloring_book_qr_bp.route('/q/coloring/<set_id>', methods=['GET'])
def qr_landing(set_id: str):
    """Handle a QR-code scan for a coloring-book letter set.

    Flow:
      1. If not logged in → save the set_id in session and redirect to login.
      2. Ensure schema + word sets exist.
      3. Idempotently create (or fetch) the user's word list for this set.
      4. Redirect to /word-lists so the user sees their list immediately.
    """
    clean_set_id = _extract_set_id_from_qr(set_id)
    if not clean_set_id:
        flash('Invalid QR code.', 'error')
        return redirect('/word-lists')

    if not current_user.is_authenticated:
        session['pending_coloring_set_id'] = clean_set_id
        flash('Please log in to save your Coloring Book word list!', 'info')
        return redirect('/login?next=/q/coloring/' + clean_set_id)

    try:
        _ensure_coloring_book_schema()
        seed_word_sets()

        ws = WordSet.query.filter_by(set_id=clean_set_id, active=True).first()
        if not ws:
            flash(f'Word set "{clean_set_id}" not found.', 'error')
            return redirect('/word-lists')

        lst = ColoringBookList.query.filter_by(
            user_id=current_user.id, source_set_id=clean_set_id
        ).first()

        if not lst:
            letter = str(getattr(ws, 'letter', '') or '').strip().upper() or clean_set_id[:1].upper()
            title = f'Coloring Book - {letter}'
            lst = ColoringBookList(
                user_id=current_user.id,
                source_set_id=clean_set_id,
                title=title,
                status='active',
            )
            db.session.add(lst)
            db.session.flush()

            words = getattr(ws, 'words_json', []) or []
            words = [str(w).strip() for w in words if str(w or '').strip()][:5]
            for w in words:
                db.session.add(ColoringBookListItem(list_id=lst.id, word=w, is_completed=False))
            db.session.commit()
            flash(f'Coloring Book - {letter} word list added to your Word Lists!', 'success')
        else:
            letter = str(getattr(ws, 'letter', '') or '').strip().upper() or clean_set_id[:1].upper()
            flash(f'Coloring Book - {letter} is already in your Word Lists.', 'info')

    except Exception as exc:
        try:
            db.session.rollback()
        except Exception:
            pass
        print(f'ERROR /q/coloring/{set_id}: {exc}')
        flash('Something went wrong. Please try again.', 'error')

    return redirect('/word-lists')
