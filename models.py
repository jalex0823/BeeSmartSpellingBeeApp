"""
BeeSmart Spelling Bee App - Database Models
SQLAlchemy ORM models for user management, quiz tracking, and progress analytics
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.types import TypeDecorator
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import random
import string

db = SQLAlchemy()


class JSONListCoerce(TypeDecorator):
    """JSON type that tolerates legacy TEXT storage.

    Some historical schemas stored JSON arrays as TEXT like "[]".
    MutableList requires the ORM value to be a real Python list; if it sees a
    string, it raises. This decorator coerces strings into lists on both bind and
    fetch so the rest of the app can treat these fields as ``list[str]``.
    """

    impl = db.JSON
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return []
            # Best effort parse, otherwise drop to empty
            try:
                import json

                parsed = json.loads(s)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
        # Any other unexpected type: make it safe for JSON
        return []

    def process_result_value(self, value, dialect):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return []
            try:
                import json

                parsed = json.loads(s)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
        return []


class User(UserMixin, db.Model):
    """User account model for students, teachers, parents, and admins"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student', index=True)  # student, teacher, parent, admin
    teacher_key = db.Column(db.String(50), unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(45))
    profile_picture = db.Column(db.Text)
    grade_level = db.Column(db.String(20))
    school_name = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    preferences = db.Column(db.JSON, default=dict)  # User settings as JSON
    total_lifetime_points = db.Column(db.Integer, default=0)
    total_quizzes_completed = db.Column(db.Integer, default=0)
    account_level = db.Column(db.Integer, default=1)
    
    # 🐝 3D Avatar System
    avatar_id = db.Column(db.String(50), default='cool-bee', index=True)  # e.g., 'explorer-bee', 'rockstar-bee'
    avatar_variant = db.Column(db.String(10), default='default')  # All avatars use 'default' variant
    avatar_locked = db.Column(db.Boolean, default=False)  # Parental control lock
    avatar_last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 🍯 Monetization System (Honey Points & IAP)
    honey_points = db.Column(db.Integer, default=0, index=True)  # Earned in-game currency
    # IMPORTANT: use MutableList so in-place mutations (append/extend) persist.
    purchased_avatars = db.Column(MutableList.as_mutable(JSONListCoerce), default=list)  # List of avatar IDs purchased via IAP
    purchased_bundles = db.Column(MutableList.as_mutable(JSONListCoerce), default=list)  # List of bundle IDs purchased
    premium_member = db.Column(db.Boolean, default=False)  # Premium membership flag
    admin_all_access = db.Column(db.Boolean, default=False)  # Admin key: bypass all monetization
    
    # 📱 App Store Subscription System (nullable until migration)
    # subscription_type = db.Column(db.String(50), nullable=True, index=True)  # 'monthly', 'yearly', 'family', or None
    # subscription_product_id = db.Column(db.String(100), nullable=True)  # e.g., 'beesmart.premium.monthly'
    # subscription_status = db.Column(db.String(20), nullable=True, default='none')  # 'active', 'grace_period', 'expired', 'canceled', 'none'
    # subscription_expires_at = db.Column(db.DateTime, nullable=True, index=True)  # When current subscription period ends
    # subscription_auto_renew = db.Column(db.Boolean, nullable=True, default=True)  # Whether auto-renewal is enabled
    # original_transaction_id = db.Column(db.String(100), nullable=True, unique=True, index=True)  # Apple's unique transaction ID
    # latest_receipt_data = db.Column(db.Text, nullable=True)  # Latest App Store receipt (base64)
    # subscription_started_at = db.Column(db.DateTime, nullable=True)  # When subscription first started
    # subscription_canceled_at = db.Column(db.DateTime, nullable=True)  # When user canceled (still has access until expires_at)
    # family_shared_from = db.Column(db.String(100), nullable=True)  # If using family sharing, original subscriber's transaction ID
    
    # �📊 GPA Tracking
    cumulative_gpa = db.Column(db.Numeric(3, 2), default=0.0)  # 0.00 to 4.00 scale
    average_accuracy = db.Column(db.Numeric(5, 2), default=0.0)  # 0.00 to 100.00%
    best_grade = db.Column(db.String(5))  # A+, A, A-, B+, etc.
    best_streak = db.Column(db.Integer, default=0)
    
    # ✨ Buzz Dust & Ranking System (Gamification)
    total_buzz_dust = db.Column(db.Integer, default=0, nullable=True, index=True)  # Cumulative XP for ranking
    bee_class = db.Column(db.String(20), default='novice', nullable=True, index=True)  # Current rank: novice, apprentice, scholar, elite, magistrate, master
    last_rank_up_at = db.Column(db.DateTime, nullable=True)  # When user last achieved a new rank
    current_streak = db.Column(db.Integer, default=0, nullable=True)  # Current consecutive correct answers
    longest_streak = db.Column(db.Integer, default=0, nullable=True)  # All-time longest streak
    
    # 📚 Wordbank Session Persistence (Fix for session loss issues)
    wordbank_storage_id = db.Column(db.String(36), nullable=True, index=True)  # UUID pointer to WORD_STORAGE and disk cache
    wordbank_last_updated = db.Column(db.DateTime, nullable=True)  # Track when wordbank was last modified
    
    # Relationships
    quiz_sessions = db.relationship('QuizSession', backref='user', lazy=True, cascade='all, delete-orphan')
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True, cascade='all, delete-orphan')
    word_mastery = db.relationship('WordMastery', backref='user', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', backref='user', lazy=True, cascade='all, delete-orphan')
    purchase_records = db.relationship('PurchaseRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def generate_teacher_key(self):
        """Generate unique teacher key like BEE-2025-SMITH-7A3B"""
        year = datetime.now().year
        name_part = self.display_name.split()[0].upper()[:5] if self.display_name else 'TEACH'
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.teacher_key = f"BEE-{year}-{name_part}-{random_part}"
        return self.teacher_key
    
    def update_avatar(self, avatar_id, variant='default'):
        """Update user's 3D avatar selection"""
        if self.avatar_locked:
            return False, "Avatar changes are locked by parental controls"
        
        # Validate avatar exists in database
        avatar = Avatar.get_by_slug(avatar_id)
        
        if not avatar:
            return False, f"Invalid avatar ID: {avatar_id}"
        
        # All our avatars use 'default' variant
        variant = 'default'
        
        self.avatar_id = avatar_id
        self.avatar_variant = variant
        self.avatar_last_updated = datetime.utcnow()
        # Mark that the user explicitly selected an avatar (used to switch from mascot → avatar)
        try:
            prefs = self.preferences or {}
            prefs['avatar_selected'] = True
            self.preferences = prefs
        except Exception:
            # Non-fatal; preferences JSON will remain unchanged if not writable
            pass
        
        return True, "Avatar updated successfully"
    
    def get_avatar_data(self):
        """Get complete avatar data for rendering (with stable `urls` shape)"""
        # Query database for avatar
        avatar = Avatar.get_by_slug(self.avatar_id)
        
        # Fallback to cool-bee if avatar not found
        if not avatar:
            avatar = Avatar.get_by_slug('cool-bee')
        
        if not avatar:
            # Ultimate fallback - GLB format only
            return {
                'id': 'mascot-bee',
                'name': 'Mascot Bee Avatar',
                'variant': 'default',
                'urls': {
                    'glb': '/static/assets/avatars/glb_files/MascotBee.glb',
                    'thumbnail': '/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png',
                    'preview': '/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png',
                }
            }
        
        # Build avatar info from database
        # NOTE: ALL avatars are GLB format now. Database field 'obj_file' is legacy naming (contains GLB filename)
        # Path structure: /static/assets/avatars/glb_files/{GLB_FILE}
        # Thumbnail structure: /static/assets/avatars/glb_files/AvatarThumbnails/{GLB_BASENAME}!.png
        
        base_path = "/static/assets/avatars/glb_files"
        
        # Get GLB filename from obj_file field (legacy naming)
        glb_filename = avatar.obj_file if avatar.obj_file else "MascotBee.glb"
        
        # Force .glb extension if it's .obj (fix for legacy database values)
        if glb_filename and glb_filename.lower().endswith('.obj'):
            glb_filename = glb_filename[:-4] + '.glb'
            
        model_path = f"{base_path}/{glb_filename}"
        
        # Derive thumbnail from GLB filename (database thumbnail_file is outdated)
        import os
        glb_basename = os.path.splitext(os.path.basename(glb_filename))[0]
        thumbnail_path = f"{base_path}/AvatarThumbnails/{glb_basename}!.png"
        
        info = {
            'id': avatar.slug,
            'name': avatar.name,
            'description': avatar.description,
            'variant': self.avatar_variant,
            'category': avatar.category,
            'thumbnail_url': thumbnail_path,
            'preview_url': thumbnail_path,
            'model_file_url': model_path,
            'fallback_url': "/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png"
        }
        
        # Build URLs dict - GLB format (all avatars are GLB now)
        urls = {
            'thumbnail': info.get('thumbnail_url'),
            'preview': info.get('preview_url'),
            'glb': info.get('model_file_url'),  # PRIMARY: GLB file path
            'fallback': info.get('fallback_url'),
        }
        
        # Back-compat top-level fields some templates/tools may still reference
        return {
            'avatar_id': self.avatar_id or 'mascot-bee',
            'variant': (self.avatar_variant or 'default'),
            'name': info.get('name'),
            'thumbnail_url': urls['thumbnail'],
            'model_url': urls['glb'],  # NOW RETURNS GLB PATH
            'last_updated': self.avatar_last_updated.isoformat() if self.avatar_last_updated else None,
            'locked': self.avatar_locked,
            'urls': urls,
        }

    def has_selected_avatar(self) -> bool:
        """Return True if the user has explicitly selected an avatar (non-default profile state)."""
        try:
            prefs = self.preferences or {}
            # FIXED: Primarily check the explicit flag; only fallback to checking non-default
            # This ensures that users who pick "Cool Bee Avatar" from picker are counted as having selected
            explicit = bool(prefs.get('avatar_selected'))
            if explicit:
                return True
            # Fallback: check if a specific avatar_id is set (any value means selected)
            has_avatar = bool(self.avatar_id)
            return has_avatar
        except Exception:
            return bool(self.avatar_id)
    
    # 🍯 Monetization Helper Methods
    
    def is_admin_or_premium(self) -> bool:
        """Check if user has admin access or premium membership (bypasses monetization)"""
        return (
            self.role == 'admin' or 
            self.admin_all_access or 
            self.premium_member
        )

    def has_admin_avatar_bypass(self) -> bool:
        """Avatar entitlement bypass: ONLY admins/admin_all_access.

        Business rule (Jan 2026):
        - Admin is the only role that has *all avatars unlocked by default*.
        - `premium_member` is a subscription/feature flag and must NOT bypass avatar locks.
        """
        return bool(self.role == 'admin' or self.admin_all_access)
    
    def has_avatar_access(self, avatar_id: str) -> tuple[bool, str]:
        """
        Check if user can access a specific avatar.
        
        Returns:
            tuple: (can_access: bool, reason: str)
        """
        from avatar_catalog import check_avatar_unlocked
        
        # Admin users bypass all restrictions (avatars only)
        if self.has_admin_avatar_bypass():
            return True, "Admin access"
        
        # Check via monetization system
        result = check_avatar_unlocked(
            avatar_id=avatar_id,
            user_honey_points=self.honey_points or 0,
            purchased_avatars=self.purchased_avatars or []
        )
        
        return result["unlocked"], result["reason"]
    
    def award_honey_points(self, points: int, reason: str = ""):
        """Award Honey Points to user"""
        if points > 0:
            self.honey_points = (self.honey_points or 0) + points
            # Optional: Log the transaction (could add HoneyPointTransaction model later)
            return True
        return False
    
    def purchase_avatar(self, avatar_id: str) -> tuple[bool, str]:
        """
        Mark an avatar as purchased via IAP.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.purchased_avatars:
            self.purchased_avatars = []
        
        if avatar_id in self.purchased_avatars:
            return False, "Avatar already purchased"
        
        self.purchased_avatars.append(avatar_id)
        return True, f"Avatar {avatar_id} purchased successfully"
    
    # 📱 Subscription Helper Methods
    
    def is_premium_active(self) -> bool:
        """
        Check if user has active premium subscription.
        
        Returns True if:
        - Admin/admin_all_access (bypass)
        - Active subscription that hasn't expired
        - Subscription in grace period (billing issue)
        """
        # Admin bypass
        if self.role == 'admin' or self.admin_all_access:
            return True
        
        # Legacy premium_member flag (backward compatibility)
        if self.premium_member:
            return True
        
        # Check if subscription columns exist (migration check)
        if not hasattr(self, 'subscription_status'):
            return False
        
        # Check subscription status
        if not self.subscription_status or self.subscription_status == 'none':
            return False
        
        # Active subscription or grace period
        if self.subscription_status in ['active', 'grace_period']:
            # Verify not expired
            if hasattr(self, 'subscription_expires_at') and self.subscription_expires_at:
                return datetime.utcnow() < self.subscription_expires_at
            return True  # Active status but no expiration means lifetime
        
        return False
    
    def get_subscription_status(self) -> dict:
        """
        Get comprehensive subscription status information.
        
        Returns:
            dict: Subscription details including type, status, expiration, auto-renew
        """
        # Check if subscription columns exist (migration check)
        if not hasattr(self, 'subscription_status'):
            return {
                'is_premium': self.premium_member or False,
                'subscription_type': 'none',
                'product_id': None,
                'status': 'none',
                'expires_at': None,
                'auto_renew': False,
                'started_at': None,
                'canceled_at': None,
                'family_shared': False,
                'days_remaining': 0
            }
        
        return {
            'is_premium': self.is_premium_active(),
            'subscription_type': getattr(self, 'subscription_type', None),
            'product_id': getattr(self, 'subscription_product_id', None),
            'status': getattr(self, 'subscription_status', 'none') or 'none',
            'expires_at': self.subscription_expires_at.isoformat() if hasattr(self, 'subscription_expires_at') and self.subscription_expires_at else None,
            'auto_renew': getattr(self, 'subscription_auto_renew', False),
            'started_at': self.subscription_started_at.isoformat() if hasattr(self, 'subscription_started_at') and self.subscription_started_at else None,
            'canceled_at': self.subscription_canceled_at.isoformat() if hasattr(self, 'subscription_canceled_at') and self.subscription_canceled_at else None,
            'family_shared': bool(getattr(self, 'family_shared_from', None)),
            'days_remaining': (self.subscription_expires_at - datetime.utcnow()).days if hasattr(self, 'subscription_expires_at') and self.subscription_expires_at and self.subscription_expires_at > datetime.utcnow() else 0
        }
    
    def update_subscription(self, receipt_data: dict) -> bool:
        """
        Update subscription status from App Store receipt data.
        
        Args:
            receipt_data: Decoded receipt from Apple's verification response
        
        Returns:
            bool: True if subscription updated successfully
        """
        try:
            from datetime import datetime, timezone
            
            # Extract subscription info from latest_receipt_info
            latest_info = receipt_data.get('latest_receipt_info', [{}])[0]
            
            self.subscription_product_id = latest_info.get('product_id')
            self.original_transaction_id = latest_info.get('original_transaction_id')
            
            # Determine subscription type from product ID
            if 'monthly' in self.subscription_product_id:
                self.subscription_type = 'family' if 'family' in self.subscription_product_id else 'monthly'
            elif 'yearly' in self.subscription_product_id:
                self.subscription_type = 'yearly'
            
            # Parse expiration date (Apple sends milliseconds since epoch)
            expires_ms = int(latest_info.get('expires_date_ms', 0))
            if expires_ms:
                self.subscription_expires_at = datetime.fromtimestamp(expires_ms / 1000, tz=timezone.utc).replace(tzinfo=None)
            
            # Set subscription start date if first time
            if not self.subscription_started_at:
                purchase_ms = int(latest_info.get('purchase_date_ms', 0))
                if purchase_ms:
                    self.subscription_started_at = datetime.fromtimestamp(purchase_ms / 1000, tz=timezone.utc).replace(tzinfo=None)
            
            # Check auto-renew status
            pending_renewal = receipt_data.get('pending_renewal_info', [{}])[0]
            self.subscription_auto_renew = pending_renewal.get('auto_renew_status') == '1'
            
            # Determine status
            if self.subscription_expires_at and datetime.utcnow() < self.subscription_expires_at:
                # Check if in billing retry (grace period)
                is_in_billing_retry = pending_renewal.get('is_in_billing_retry_period') == '1'
                self.subscription_status = 'grace_period' if is_in_billing_retry else 'active'
            else:
                self.subscription_status = 'expired'
            
            # Store latest receipt for future validation
            self.latest_receipt_data = receipt_data.get('latest_receipt')
            
            # Update legacy premium_member flag for backward compatibility
            self.premium_member = self.is_premium_active()
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating subscription: {e}")
            return False
        return True, f"Avatar {avatar_id} purchased successfully"
    
    def purchase_bundle(self, bundle_id: str, included_avatars: list) -> tuple[bool, str]:
        """
        Purchase a bundle and unlock all included avatars.
        
        Args:
            bundle_id: Bundle identifier (e.g., 'top_bee_bundle')
            included_avatars: List of avatar IDs to unlock
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.purchased_bundles:
            self.purchased_bundles = []
        
        if bundle_id in self.purchased_bundles:
            return False, "Bundle already purchased"
        
        # Add bundle to purchased list
        self.purchased_bundles.append(bundle_id)
        
        # Unlock all avatars in bundle
        if not self.purchased_avatars:
            self.purchased_avatars = []
        
        new_avatars = [a for a in included_avatars if a not in self.purchased_avatars]
        self.purchased_avatars.extend(new_avatars)
        
        return True, f"Bundle '{bundle_id}' purchased! Unlocked {len(new_avatars)} new avatars"
    
    def get_unlocked_avatars(self) -> list:
        """
        Get list of all avatar IDs the user has access to.
        
        Returns:
            list: Avatar IDs user can use
        """
        from avatar_catalog import AVATAR_CATALOG, get_free_avatars
        
        # Admin gets everything (avatars only)
        if self.has_admin_avatar_bypass():
            return [a["id"] for a in AVATAR_CATALOG]
        
        # Start with free avatars
        unlocked = [a["id"] for a in get_free_avatars()]
        
        # Add purchased avatars
        if self.purchased_avatars:
            unlocked.extend(self.purchased_avatars)

        # Add avatars unlocked by server-granted entitlements (e.g., Coloring Book reward)
        try:
            ents = UserEntitlement.query.filter_by(user_id=self.id, entitlement_type='avatar').all()
            for e in (ents or []):
                k = str(getattr(e, 'entitlement_key', '') or '').strip()
                if k.startswith('avatar.'):
                    unlocked.append(k[len('avatar.'):].replace('_', '-'))
        except Exception:
            pass
        
        # Add avatars unlocked via Honey Points
        honey_points = self.honey_points or 0
        for avatar in AVATAR_CATALOG:
            avatar_id = avatar["id"]
            if avatar_id not in unlocked:
                required_points = avatar.get("unlock_points", 0)
                if honey_points >= required_points and not avatar.get("is_default_free", False):
                    unlocked.append(avatar_id)
        
        return list(set(unlocked))  # Remove duplicates
    
    def update_last_login(self, ip_address=None):
        """Update last login timestamp and IP"""
        self.last_login = datetime.utcnow()
        if ip_address:
            self.last_login_ip = ip_address
    
    def add_points(self, points):
        """Add points to lifetime total"""
        # Defensive: legacy rows/migrations may have NULL counters.
        self.total_lifetime_points = int(self.total_lifetime_points or 0) + int(points or 0)

    def credit_session_points(self, points: int) -> None:
        """
        Credit points from an in-progress quiz session to the user without incrementing
        quiz count or recalculating GPA/accuracy. Used by partial progress saving.
        """
        if points and int(points) > 0:
            self.total_lifetime_points = int(self.total_lifetime_points or 0) + int(points)
    
    def increment_quizzes(self):
        """Increment total quizzes completed"""
        # Defensive: legacy rows/migrations may have NULL counters.
        self.total_quizzes_completed = int(self.total_quizzes_completed or 0) + 1
    
    def update_gpa_and_accuracy(self):
        """
        Calculate and update cumulative GPA and average accuracy from all completed activities.
        Includes: standard QuizSession records and SpeedRoundScore results.
        GPA Scale: A+ = 4.0, A = 4.0, A- = 3.7, B+ = 3.3, B = 3.0, B- = 2.7,
                   C+ = 2.3, C = 2.0, C- = 1.7, D+ = 1.3, D = 1.0, D- = 0.7, F = 0.0
        """
        # Collect completed quiz sessions
        completed_sessions = QuizSession.query.filter_by(
            user_id=self.id,
            completed=True
        ).all()

        # Collect in-progress (incomplete) quiz sessions with some activity
        try:
            incomplete_sessions = QuizSession.query.filter_by(
                user_id=self.id,
                completed=False
            ).all()
        except Exception:
            incomplete_sessions = []

        # Collect speed round scores (treated as sessions for GPA/accuracy)
        try:
            speed_scores = SpeedRoundScore.query.filter_by(user_id=self.id).all()
        except Exception:
            speed_scores = []

        # Grade to GPA mapping
        grade_to_gpa = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0
        }

        def grade_from_accuracy(acc: float) -> str:
            acc_val = acc or 0.0
            if acc_val >= 97:
                return 'A+'
            elif acc_val >= 93:
                return 'A'
            elif acc_val >= 90:
                return 'A-'
            elif acc_val >= 87:
                return 'B+'
            elif acc_val >= 83:
                return 'B'
            elif acc_val >= 80:
                return 'B-'
            elif acc_val >= 77:
                return 'C+'
            elif acc_val >= 73:
                return 'C'
            elif acc_val >= 70:
                return 'C-'
            elif acc_val >= 67:
                return 'D+'
            elif acc_val >= 63:
                return 'D'
            elif acc_val >= 60:
                return 'D-'
            else:
                return 'F'

        total_gpa_points = 0.0
        total_accuracy = 0.0
        valid_activities = 0
        best_gpa = -1.0

        # Fold in standard quiz sessions (completed)
        for session in completed_sessions:
            if session.accuracy_percentage is not None:
                acc = float(session.accuracy_percentage)
                total_accuracy += acc
            if session.grade:
                gpa_value = grade_to_gpa.get(session.grade, 0.0)
            else:
                # Derive from accuracy if grade missing
                acc = float(session.accuracy_percentage or 0.0)
                gpa_value = grade_to_gpa.get(grade_from_accuracy(acc), 0.0)
            total_gpa_points += gpa_value
            valid_activities += 1
            if gpa_value > best_gpa:
                best_gpa = gpa_value
                self.best_grade = session.grade or grade_from_accuracy(float(session.accuracy_percentage or 0.0))

        # Fold in in-progress sessions (derive provisional accuracy/grade)
        for s in incomplete_sessions:
            # Determine attempted words (exclude skipped by default)
            try:
                correct = int(s.correct_count or 0)
                incorrect = int(s.incorrect_count or 0)
                attempted = correct + incorrect
            except Exception:
                correct = 0
                attempted = 0
            if attempted <= 0:
                # If no real attempts yet, skip from GPA/accuracy aggregation
                continue
            acc = round((correct / attempted) * 100.0, 2)
            total_accuracy += acc
            letter = grade_from_accuracy(acc)
            gpa_value = grade_to_gpa.get(letter, 0.0)
            total_gpa_points += gpa_value
            valid_activities += 1
            if gpa_value > best_gpa:
                best_gpa = gpa_value
                # best_grade can come from provisional too
                self.best_grade = letter

        # Fold in speed round scores
        for sr in speed_scores:
            acc = sr.accuracy_percentage or 0.0
            total_accuracy += float(acc)
            letter = grade_from_accuracy(float(acc))
            gpa_value = grade_to_gpa.get(letter, 0.0)
            total_gpa_points += gpa_value
            valid_activities += 1
            if gpa_value > best_gpa:
                best_gpa = gpa_value
                self.best_grade = letter

        # Calculate averages
        if valid_activities > 0:
            self.cumulative_gpa = round(total_gpa_points / valid_activities, 2)
            self.average_accuracy = round(total_accuracy / valid_activities, 2)
        else:
            self.cumulative_gpa = 0.0
            self.average_accuracy = 0.0

        # CRITICAL: Update total_quizzes_completed to reflect actual count of completed activities
        # This ensures Speed Round scores are included in the quiz count
        # Count = completed QuizSession + SpeedRoundScore records
        total_completed_activities = len(completed_sessions) + len(speed_scores)
        self.total_quizzes_completed = total_completed_activities

        # Update best streak across completed, in-progress, and speed rounds
        session_streaks = [s.max_streak for s in completed_sessions if getattr(s, 'max_streak', None)]
        session_streaks += [s.max_streak for s in incomplete_sessions if getattr(s, 'max_streak', None)]
        speed_streaks = [s.longest_streak for s in speed_scores if getattr(s, 'longest_streak', None)]
        all_streaks = session_streaks + speed_streaks
        if all_streaks:
            self.best_streak = max(all_streaks)

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def generate_teacher_key(self) -> str:
        """
        Generate a unique teacher key using the current year, the first five characters
        of the display name, and a random alphanumeric string.
        Example: BEE-2025-SMITH-7A3B
        """
        year = datetime.now().year
        name_part = self.display_name.split()[0].upper()[:5] if self.display_name else 'TEACH'
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        self.teacher_key = f"BEE-{year}-{name_part}-{random_part}"
        return self.teacher_key

    def update_avatar(self, avatar_id: str, variant: str = 'default') -> tuple[bool, str]:
        """
        Update the user's avatar selection. Returns (success, message).
        Avatar changes respect the parental control lock and only succeed if the
        specified avatar exists.
        """
        if self.avatar_locked:
            return False, "Avatar changes are locked by parental controls"
        avatar = Avatar.get_by_slug(avatar_id)
        if not avatar:
            return False, f"Invalid avatar ID: {avatar_id}"
        variant = 'default'
        self.avatar_id = avatar_id
        self.avatar_variant = variant
        self.avatar_last_updated = datetime.utcnow()
        try:
            prefs = self.preferences or {}
            prefs['avatar_selected'] = True
            self.preferences = prefs
        except Exception:
            pass
        return True, "Avatar updated successfully"

    def get_avatar_data(self) -> dict:
        """
        Return a dict of avatar metadata for rendering, including URLs to the model
        and thumbnail files. Falls back to default avatars if needed.
        """
        avatar = Avatar.get_by_slug(self.avatar_id)
        if not avatar:
            avatar = Avatar.get_by_slug('cool-bee')
        if not avatar:
            return {
                'id': 'mascot-bee',
                'name': 'Mascot Bee Avatar',
                'variant': 'default',
                'urls': {
                    'glb': '/static/assets/avatars/glb_files/MascotBee.glb',
                    'thumbnail': '/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png',
                    'preview': '/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png',
                }
            }
        base_path = "/static/assets/avatars/glb_files"
        glb_filename = avatar.obj_file if avatar.obj_file else "MascotBee.glb"
        if glb_filename.lower().endswith('.obj'):
            glb_filename = glb_filename[:-4] + '.glb'
        model_path = f"{base_path}/{glb_filename}"
        import os
        glb_basename = os.path.splitext(os.path.basename(glb_filename))[0]
        thumbnail_path = f"{base_path}/AvatarThumbnails/{glb_basename}!.png"
        info = {
            'id': avatar.slug,
            'name': avatar.name,
            'description': avatar.description,
            'variant': self.avatar_variant,
            'category': avatar.category,
            'thumbnail_url': thumbnail_path,
            'preview_url': thumbnail_path,
            'model_file_url': model_path,
            'fallback_url': "/static/assets/avatars/glb_files/AvatarThumbnails/MascotBee!.png",
        }
        urls = {
            'thumbnail': info.get('thumbnail_url'),
            'preview': info.get('preview_url'),
            'glb': info.get('model_file_url'),
            'fallback': info.get('fallback_url'),
        }
        return {
            'avatar_id': self.avatar_id or 'mascot-bee',
            'variant': (self.avatar_variant or 'default'),
            'name': info.get('name'),
            'thumbnail_url': urls['thumbnail'],
            'model_url': urls['glb'],
            'last_updated': self.avatar_last_updated.isoformat() if self.avatar_last_updated else None,
            'locked': self.avatar_locked,
            'urls': urls,
        }

    def has_selected_avatar(self) -> bool:
        """
        Return True if the user has explicitly selected an avatar (non-default profile state).
        Checks a preference flag first, then falls back to the presence of avatar_id.
        """
        try:
            prefs = self.preferences or {}
            explicit = bool(prefs.get('avatar_selected'))
            if explicit:
                return True
            return bool(self.avatar_id)
        except Exception:
            return bool(self.avatar_id)

    # 🍯 Monetization Helper Methods
    def is_admin_or_premium(self) -> bool:
        """Return True if the user has admin privileges or premium membership."""
        return bool(self.role == 'admin' or self.admin_all_access or self.premium_member)

    def has_avatar_access(self, avatar_id: str) -> tuple[bool, str]:
        """
        Determine whether the user can access a specific avatar.
        Returns (can_access, reason).
        """
        from avatar_catalog import check_avatar_unlocked
        if self.is_admin_or_premium():
            return True, "Admin/Premium access"
        result = check_avatar_unlocked(
            avatar_id=avatar_id,
            user_honey_points=self.honey_points or 0,
            purchased_avatars=self.purchased_avatars or []
        )
        return result["unlocked"], result["reason"]

    def award_honey_points(self, points: int, reason: str = "") -> bool:
        """Award Honey Points to the user. Returns True if points were added."""
        if points and points > 0:
            self.honey_points = (self.honey_points or 0) + points
            return True
        return False

    def purchase_avatar(self, avatar_id: str) -> tuple[bool, str]:
        """
        Mark an avatar as purchased via in-app purchase. Returns (success, message).
        """
        if not self.purchased_avatars:
            self.purchased_avatars = []
        if avatar_id in self.purchased_avatars:
            return False, "Avatar already purchased"
        self.purchased_avatars.append(avatar_id)
        return True, f"Avatar {avatar_id} purchased successfully"

    # 📱 Subscription Helper Methods
    def is_premium_active(self) -> bool:
        """
        Return True if the user has an active premium subscription. Admins and
        accounts with admin_all_access bypass the check. Legacy premium_member flag
        is also honoured for backward compatibility.
        """
        if self.role == 'admin' or self.admin_all_access:
            return True
        if self.premium_member:
            return True
        if not hasattr(self, 'subscription_status'):
            return False
        if not self.subscription_status or self.subscription_status == 'none':
            return False
        if self.subscription_status in ['active', 'grace_period']:
            if hasattr(self, 'subscription_expires_at') and self.subscription_expires_at:
                return datetime.utcnow() < self.subscription_expires_at
            return True
        return False

    def get_subscription_status(self) -> dict:
        """
        Return a dictionary describing the user's subscription status.
        """
        if not hasattr(self, 'subscription_status'):
            return {
                'is_premium': bool(self.premium_member),
                'subscription_type': 'none',
                'subscription_status': 'none',
                'subscription_expires_at': None,
                'subscription_auto_renew': None,
            }
        return {
            'is_premium': self.is_premium_active(),
            'subscription_type': getattr(self, 'subscription_type', 'none'),
            'subscription_status': getattr(self, 'subscription_status', 'none'),
            'subscription_expires_at': getattr(self, 'subscription_expires_at', None),
            'subscription_auto_renew': getattr(self, 'subscription_auto_renew', None),
        }
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class QuizSession(db.Model):
    """Quiz session tracking - one record per quiz attempt"""
    __tablename__ = 'quiz_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # Null when roster_student_id set
    roster_student_id = db.Column(db.Integer, db.ForeignKey('roster_students.id'), nullable=True, index=True)  # Managed roster (no User)
    teacher_key = db.Column(db.String(50), index=True)  # Links to teacher for reporting
    session_start = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    session_end = db.Column(db.DateTime)
    total_words = db.Column(db.Integer, nullable=False)
    correct_count = db.Column(db.Integer, default=0)
    incorrect_count = db.Column(db.Integer, default=0)
    skipped_count = db.Column(db.Integer, default=0)
    total_points = db.Column(db.Integer, default=0)  # Deprecated - use points_earned instead
    points_earned = db.Column(db.Integer, default=0)  # Total session points (word points + bonuses + badges)
    badge_bonus_points = db.Column(db.Integer, default=0)  # Points from badges only
    extra_points = db.Column(db.Integer, default=0)  # Additional bonus points (achievements, special events)
    max_streak = db.Column(db.Integer, default=0)
    accuracy_percentage = db.Column(db.Numeric(5, 2))
    difficulty_level = db.Column(db.String(20), default='normal')  # easy, normal, challenge, mixed
    word_list_name = db.Column(db.String(200))
    word_list_source = db.Column(db.String(50), default='upload')  # upload, default, teacher_assigned
    time_spent_seconds = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False, index=True)
    grade = db.Column(db.String(5))  # A+, A, A-, B+, etc.
    quiz_mode = db.Column(db.String(20), default='standard')  # standard, battle, timed_challenge
    device_type = db.Column(db.String(20))  # desktop, tablet, mobile
    browser_info = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    notes = db.Column(db.Text)
    # Track whether points from this session have already been applied to the user's lifetime points
    points_applied = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # Relationships
    results = db.relationship('QuizResult', backref='session', lazy=True, cascade='all, delete-orphan')
    roster_student = db.relationship('RosterStudent', backref=db.backref('quiz_sessions', lazy=True))
    
    def calculate_accuracy(self):
        """Calculate and update accuracy percentage"""
        if self.total_words > 0:
            self.accuracy_percentage = round((self.correct_count / self.total_words) * 100, 2)
        else:
            self.accuracy_percentage = 0.0
        return self.accuracy_percentage
    
    def calculate_grade(self):
        """Calculate letter grade based on accuracy"""
        accuracy = self.accuracy_percentage or 0
        
        if accuracy >= 97:
            grade = 'A+'
        elif accuracy >= 93:
            grade = 'A'
        elif accuracy >= 90:
            grade = 'A-'
        elif accuracy >= 87:
            grade = 'B+'
        elif accuracy >= 83:
            grade = 'B'
        elif accuracy >= 80:
            grade = 'B-'
        elif accuracy >= 77:
            grade = 'C+'
        elif accuracy >= 73:
            grade = 'C'
        elif accuracy >= 70:
            grade = 'C-'
        elif accuracy >= 67:
            grade = 'D+'
        elif accuracy >= 63:
            grade = 'D'
        elif accuracy >= 60:
            grade = 'D-'
        else:
            grade = 'F'
        
        self.grade = grade
        return grade
    
    def apply_points_if_needed(self) -> int:
        """
        Apply session points to the user's lifetime total if they haven't already been applied.
        Returns the number of points credited to the user.
        """
        if self.points_applied:
            return 0
        total_points = (self.points_earned or 0) \
                       + (self.badge_bonus_points or 0) \
                       + (self.extra_points or 0)
        if self.user is not None:
            self.user.credit_session_points(total_points)
        self.points_applied = True
        db.session.flush()
        return total_points

    def complete_session(self) -> int:
        """
        Mark the session as completed, apply any remaining points, increment the user's quiz count,
        and update their GPA and accuracy. Returns the number of points awarded (not previously applied).
        """
        self.session_end = datetime.utcnow()
        self.completed = True
        # Calculate final accuracy and grade
        self.calculate_accuracy()
        self.calculate_grade()
        # Apply points if not yet applied
        points_awarded = self.apply_points_if_needed()
        if self.user is not None:
            self.user.increment_quizzes()
            self.user.update_gpa_and_accuracy()
            db.session.flush()
        return points_awarded
    
    def __repr__(self):
        return f'<QuizSession {self.id} - User {self.user_id} ({self.grade})>'


class QuizResult(db.Model):
    """Individual word results - one record per word attempt"""
    __tablename__ = 'quiz_results'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    session_id = db.Column(db.Integer, db.ForeignKey('quiz_sessions.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # Null when roster_student_id set
    roster_student_id = db.Column(db.Integer, db.ForeignKey('roster_students.id'), nullable=True, index=True)
    word = db.Column(db.String(100), nullable=False, index=True)
    word_length = db.Column(db.Integer)
    word_difficulty = db.Column(db.String(20))  # short, medium, long, very_long
    is_correct = db.Column(db.Boolean, nullable=False, index=True)
    user_answer = db.Column(db.Text)
    correct_spelling = db.Column(db.String(100))
    time_taken_seconds = db.Column(db.Numeric(6, 2))
    time_remaining_seconds = db.Column(db.Numeric(6, 2))
    points_earned = db.Column(db.Integer, default=0)
    base_points = db.Column(db.Integer, default=100)
    time_bonus = db.Column(db.Integer, default=0)
    difficulty_multiplier = db.Column(db.Numeric(3, 2), default=1.00)
    streak_bonus = db.Column(db.Integer, default=0)
    first_attempt_bonus = db.Column(db.Integer, default=0)
    no_hints_bonus = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    hint_type = db.Column(db.String(50))  # definition, phonetic, sentence
    attempts = db.Column(db.Integer, default=1)
    input_method = db.Column(db.String(20))  # keyboard, voice
    voice_confidence = db.Column(db.Numeric(5, 4))  # For voice input accuracy
    question_number = db.Column(db.Integer)  # Position in quiz
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def calculate_difficulty(self):
        """Auto-calculate word difficulty based on length"""
        length = len(self.word) if self.word else 0
        self.word_length = length
        
        if length <= 5:
            self.word_difficulty = 'short'
            self.difficulty_multiplier = 1.0
        elif length <= 8:
            self.word_difficulty = 'medium'
            self.difficulty_multiplier = 1.5
        elif length <= 12:
            self.word_difficulty = 'long'
            self.difficulty_multiplier = 2.0
        else:
            self.word_difficulty = 'very_long'
            self.difficulty_multiplier = 2.5
        
        return self.word_difficulty
    
    def __repr__(self):
        return f'<QuizResult {self.word} - {"✓" if self.is_correct else "✗"}>'


class WordMastery(db.Model):
    """Track individual word mastery per user"""
    __tablename__ = 'word_mastery'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    word = db.Column(db.String(100), nullable=False, index=True)
    times_seen = db.Column(db.Integer, default=0)
    times_correct = db.Column(db.Integer, default=0)
    times_incorrect = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Numeric(5, 2), default=0.0)
    mastery_level = db.Column(db.String(20), default='learning', index=True)
    # Levels: learning (0-50%), practicing (50-80%), proficient (80-95%), mastered (95-100%)
    first_attempt_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_attempt_date = db.Column(db.DateTime, default=datetime.utcnow)
    average_time_seconds = db.Column(db.Numeric(6, 2))
    fastest_time_seconds = db.Column(db.Numeric(6, 2))
    needs_review = db.Column(db.Boolean, default=False, index=True)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'word', name='unique_user_word'),)
    
    def update_stats(self, is_correct, time_taken=None):
        """Update mastery stats after attempt"""
        # Defensive: older rows or legacy migrations may have NULL counters.
        self.times_seen = int(self.times_seen or 0) + 1
        
        if is_correct:
            self.times_correct = int(self.times_correct or 0) + 1
        else:
            self.times_incorrect = int(self.times_incorrect or 0) + 1
        
        # Calculate success rate
        seen = max(int(self.times_seen or 0), 1)
        correct = int(self.times_correct or 0)
        self.success_rate = round((correct / seen) * 100, 2)
        
        # Update mastery level
        if self.success_rate >= 95:
            self.mastery_level = 'mastered'
            self.needs_review = False
        elif self.success_rate >= 80:
            self.mastery_level = 'proficient'
            self.needs_review = False
        elif self.success_rate >= 50:
            self.mastery_level = 'practicing'
            self.needs_review = self.success_rate < 70
        else:
            self.mastery_level = 'learning'
            self.needs_review = True
        
        # Update timing stats
        if time_taken is not None:
            try:
                t = float(time_taken)
            except Exception:
                t = None

            if t is not None:
                if self.average_time_seconds is not None:
                    # Running average
                    total_time = float(self.average_time_seconds) * (seen - 1)
                    self.average_time_seconds = round((total_time + t) / seen, 2)
                else:
                    self.average_time_seconds = t

                if self.fastest_time_seconds is None or t < float(self.fastest_time_seconds):
                    self.fastest_time_seconds = t
        
        self.last_attempt_date = datetime.utcnow()
    
    def __repr__(self):
        return f'<WordMastery {self.word} - {self.mastery_level} ({self.success_rate}%)>'


class Class(db.Model):
    """
    Class (tenant) for Teacher Key → managed roster.
    Teacher Key is stored here as the join key; one class per teacher initially.
    """
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, default='Default Class')
    teacher_key = db.Column(db.String(50), unique=True, nullable=False, index=True)  # Class code (BEE-2026-TEACH-XXXX)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref=db.backref('classes', lazy=True))
    roster_students = db.relationship('RosterStudent', backref='class_ref', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Class {self.name} ({self.teacher_key})>'


class RosterStudent(db.Model):
    """
    Managed student profile. Teacher creates these; each can have an auto-created
    User account (user_id) so the student can log in; linked to teacher via TeacherStudent.
    """
    __tablename__ = 'roster_students'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # Auto-created login account
    display_name = db.Column(db.String(200), nullable=False)
    external_student_id = db.Column(db.String(100), nullable=True, index=True)  # From import sheet
    grade_level = db.Column(db.String(20), nullable=True)
    pin_hash = db.Column(db.String(255), nullable=True)  # 4-digit PIN hashed
    status = db.Column(db.String(20), nullable=False, default='ACTIVE', index=True)  # ACTIVE | ARCHIVED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.Index('ix_roster_students_class_status', 'class_id', 'status'),)
    
    # Relationship to User when account is auto-created
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('roster_profile', uselist=False))
    
    def set_pin(self, pin: str) -> None:
        """Store hashed 4-digit PIN."""
        if pin and len(pin) == 4 and pin.isdigit():
            self.pin_hash = generate_password_hash(pin, method='pbkdf2:sha256', salt_length=8)
    
    def check_pin(self, pin: str) -> bool:
        """Verify 4-digit PIN."""
        if not self.pin_hash:
            return True
        return pin and check_password_hash(self.pin_hash, pin)
    
    @property
    def pin_required(self) -> bool:
        return bool(self.pin_hash)
    
    def __repr__(self):
        return f'<RosterStudent {self.display_name} ({self.status})>'


class TeacherStudent(db.Model):
    """Links teachers to their students (registered User accounts)"""
    __tablename__ = 'teacher_students'
    
    id = db.Column(db.Integer, primary_key=True)
    teacher_key = db.Column(db.String(50), nullable=False, index=True)
    teacher_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    relationship_type = db.Column(db.String(20), default='teacher')  # teacher, parent, tutor
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    __table_args__ = (db.UniqueConstraint('teacher_key', 'student_id', name='unique_teacher_student'),)
    
    # Relationships
    teacher = db.relationship('User', foreign_keys=[teacher_user_id])
    student = db.relationship('User', foreign_keys=[student_id])
    
    def __repr__(self):
        return f'<TeacherStudent {self.teacher_key} -> Student {self.student_id}>'


class WordList(db.Model):
    """Teacher-created word lists"""
    __tablename__ = 'word_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    list_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    grade_level = db.Column(db.String(20))
    difficulty_level = db.Column(db.String(20))
    word_count = db.Column(db.Integer, default=0)
    is_public = db.Column(db.Boolean, default=False, index=True)
    is_favorite = db.Column(db.Boolean, default=False, index=True)  # Pin/favorite lists
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    times_used = db.Column(db.Integer, default=0)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by_user_id], backref='created_word_lists')
    items = db.relationship('WordListItem', foreign_keys='WordListItem.word_list_id', backref='word_list', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<WordList "{self.list_name}" ({self.word_count} words)>'


class WordListItem(db.Model):
    """Individual words in a word list"""
    __tablename__ = 'word_list_items'
    
    id = db.Column(db.Integer, primary_key=True)
    word_list_id = db.Column(db.Integer, db.ForeignKey('word_lists.id'), nullable=False, index=True)
    word = db.Column(db.String(100), nullable=False, index=True)
    sentence = db.Column(db.Text)
    hint = db.Column(db.Text)
    difficulty_override = db.Column(db.String(20))
    position = db.Column(db.Integer)  # Order in list
    
    def __repr__(self):
        return f'<WordListItem {self.word}>'


class Achievement(db.Model):
    """User achievements and badges"""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    achievement_type = db.Column(db.String(50), nullable=False, index=True)
    # Types: perfect_quiz, streak_10, streak_25, streak_50,
    #        points_1000, points_5000, points_10000,
    #        speed_demon, word_master, 100_quizzes, etc.
    achievement_name = db.Column(db.String(100))
    achievement_description = db.Column(db.Text)
    earned_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    points_bonus = db.Column(db.Integer, default=0)
    achievement_metadata = db.Column(db.JSON, default=dict)  # Additional context (renamed from metadata to avoid SQLAlchemy conflict)
    
    def __repr__(self):
        return f'<Achievement {self.achievement_name} - User {self.user_id}>'


class SessionLog(db.Model):
    """Audit trail for user actions"""
    __tablename__ = 'session_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    # Actions: login, logout, quiz_start, quiz_complete, upload_words, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    additional_data = db.Column(db.JSON, default=dict)
    
    def __repr__(self):
        return f'<SessionLog {self.action} - User {self.user_id} at {self.timestamp}>'


class PasswordResetToken(db.Model):
    """Password reset tokens stored hashed for security"""
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    token_hash = db.Column(db.String(255), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    used_at = db.Column(db.DateTime)
    request_ip = db.Column(db.String(45))
    user_agent = db.Column(db.Text)

    # Relationship
    user = db.relationship('User', backref='password_reset_tokens')

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() >= (self.expires_at or datetime.utcnow())

    def mark_used(self):
        self.used_at = datetime.utcnow()

    def __repr__(self):
        status = 'used' if self.is_used else ('expired' if self.is_expired else 'active')
        return f'<PasswordResetToken user={self.user_id} {status}>'

class ExportRequest(db.Model):
    """Track report generation requests"""
    __tablename__ = 'export_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    requested_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    export_type = db.Column(db.String(50), index=True)  # student_report, class_report, csv_export, pdf_report
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # If exporting specific student
    date_range_start = db.Column(db.DateTime)
    date_range_end = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, processing, completed, failed
    file_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    requester = db.relationship('User', foreign_keys=[requested_by_user_id])
    target = db.relationship('User', foreign_keys=[target_user_id])
    
    def __repr__(self):
        return f'<ExportRequest {self.export_type} - Status: {self.status}>'


# Database initialization and utility functions
class SpeedRoundConfig(db.Model):
    """Configuration for speed round challenges"""
    __tablename__ = 'speed_round_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Quick Fire", "Marathon Mode"
    time_per_word = db.Column(db.Integer, nullable=False)  # seconds per word
    total_duration = db.Column(db.Integer)  # total seconds (optional, for timed rounds)
    difficulty_level = db.Column(db.String(50), nullable=False)  # grade_1_2, grade_3_4, etc.
    word_source = db.Column(db.String(50), default='auto')  # 'auto', 'uploaded', 'mixed'
    word_count = db.Column(db.Integer, default=20)  # number of words in round
    bonus_multiplier = db.Column(db.Float, default=1.0)  # difficulty multiplier
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_public = db.Column(db.Boolean, default=False)  # shareable with other users
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    scores = db.relationship('SpeedRoundScore', backref='config', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SpeedRoundConfig {self.name}>'


class SpeedRoundScore(db.Model):
    """Score record for completed speed rounds"""
    __tablename__ = 'speed_round_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    config_id = db.Column(db.Integer, db.ForeignKey('speed_round_configs.id'), index=True)
    
    # Performance metrics
    words_attempted = db.Column(db.Integer, nullable=False)
    words_correct = db.Column(db.Integer, nullable=False)
    total_time = db.Column(db.Float, nullable=False)  # total seconds taken
    honey_points_earned = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    average_time_per_word = db.Column(db.Float)
    fastest_word_time = db.Column(db.Float)  # fastest correct answer in seconds
    speed_bonuses_earned = db.Column(db.Integer, default=0)  # count of speed bonuses
    
    # Detailed breakdown (JSON)
    word_details = db.Column(db.JSON)  # [{word, correct, time_taken, points_earned}, ...]
    
    # Metadata
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    difficulty_level = db.Column(db.String(50))  # cached from config
    
    # Relationships
    user = db.relationship('User', backref='speed_round_scores')
    
    @property
    def accuracy_percentage(self):
        """Calculate accuracy as percentage"""
        if self.words_attempted == 0:
            return 0.0
        return round((self.words_correct / self.words_attempted) * 100, 1)
    
    def __repr__(self):
        return f'<SpeedRoundScore user_id={self.user_id} score={self.honey_points_earned}>'


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")


def create_test_data(app):
    """Create test data for development"""
    with app.app_context():
        # Create admin user
        admin = User(
            username='admin',
            display_name='Administrator',
            email='admin@beesmart.app',
            role='admin'
        )
        admin.set_password('admin123')
        admin.generate_teacher_key()
        
        # Create test teacher
        teacher = User(
            username='teacher_smith',
            display_name='Mrs. Smith',
            email='smith@school.edu',
            role='teacher',
            school_name='Example Elementary'
        )
        teacher.set_password('teacher123')
        teacher.generate_teacher_key()
        
        # Create test student
        student = User(
            username='alex_student',
            display_name='Alex Johnson',
            email='alex@example.com',
            role='student',
            grade_level='5th Grade'
        )
        student.set_password('student123')
        
        db.session.add_all([admin, teacher, student])
        db.session.commit()
        
        # Link teacher to student
        link = TeacherStudent(
            teacher_key=teacher.teacher_key,
            teacher_user_id=teacher.id,
            student_id=student.id
        )
        db.session.add(link)
        db.session.commit()
        
        print(f"✅ Test data created!")
        print(f"   Admin: admin / admin123")
        print(f"   Teacher: teacher_smith / teacher123 (Key: {teacher.teacher_key})")
        print(f"   Student: alex_student / student123")


# ============================================================================
# BATTLE OF THE BEES - MULTIPLAYER BATTLE SYSTEM
# ============================================================================

class BattleSession(db.Model):
    """Live multiplayer spelling battle sessions"""
    __tablename__ = "battle_sessions"
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), unique=True, index=True, nullable=False)
    status = db.Column(db.Enum("waiting", "in_progress", "ended", name="battle_status"), 
                      index=True, default="waiting")
    is_public = db.Column(db.Boolean, default=True, index=True)
    allow_guests = db.Column(db.Boolean, default=True)
    max_players = db.Column(db.Integer, default=20)
    grade_range = db.Column(db.String(16))
    mode = db.Column(db.String(24))  # 'speed', 'accuracy', 'streak', 'custom'
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    started_at = db.Column(db.DateTime)
    ends_at = db.Column(db.DateTime)
    wordset_name = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    players = db.relationship("BattlePlayer", backref="session", cascade="all, delete-orphan")
    creator = db.relationship("User", foreign_keys=[created_by])
    
    @property
    def current_players(self):
        """Count of active players (not left)"""
        return len([p for p in self.players if not p.left_at])
    
    @property 
    def player_names(self):
        """List of active player display names"""
        return [p.display_name for p in self.players if not p.left_at]
    
    def generate_battle_code(self):
        """Generate unique 6-character battle code"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not BattleSession.query.filter_by(code=code).first():
                return code
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.code:
            self.code = self.generate_battle_code()


class BattlePlayer(db.Model):
    """Players participating in battle sessions"""
    __tablename__ = "battle_players"
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("battle_sessions.id"), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # NULL for guests
    display_name = db.Column(db.String(40), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    left_at = db.Column(db.DateTime, nullable=True)
    
    # Battle performance stats
    words_attempted = db.Column(db.Integer, default=0)
    words_correct = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    max_streak = db.Column(db.Integer, default=0)
    total_points = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship("User", foreign_keys=[user_id])
    
    @property
    def accuracy(self):
        """Calculate accuracy percentage"""
        if self.words_attempted == 0:
            return 0.0
        return round((self.words_correct / self.words_attempted) * 100, 1)
    
    @property
    def is_active(self):
        """Check if player is still in battle"""
        return self.left_at is None


class Avatar(db.Model):
    """3D Avatar catalog with file associations and metadata"""
    __tablename__ = 'avatars'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)  # e.g., 'cool-bee', 'explorer-bee'
    name = db.Column(db.String(100), nullable=False, index=True)  # Display name: "Cool Bee", "Explorer Bee" - indexed for search
    description = db.Column(db.Text, index=True)  # Kid-friendly description - indexed for search
    category = db.Column(db.String(50), default='classic', index=True)  # classic, adventure, sports, etc.
    
    # File paths (relative to static/assets/avatars/)
    folder_path = db.Column(db.String(200), nullable=False)  # e.g., 'glb_files'
    obj_file = db.Column(db.String(200), nullable=False)  # LEGACY FIELD NAME - Contains GLB filename e.g., 'CoolBee.glb' (NOT .obj)
    mtl_file = db.Column(db.String(200))  # Deprecated - kept for backward compatibility
    texture_file = db.Column(db.String(200))  # Deprecated - kept for backward compatibility
    thumbnail_file = db.Column(db.String(200))  # Deprecated - now auto-derived from GLB filename
    
    # Binary file data (stored directly in database for cloud deployment)
    obj_data = db.Column(db.LargeBinary)  # Deprecated - GLB files only now
    mtl_data = db.Column(db.LargeBinary)  # Deprecated - GLB files only now
    texture_data = db.Column(db.LargeBinary)  # Deprecated - GLB files only now
    thumbnail_data = db.Column(db.LargeBinary)  # Thumbnail PNG file content
    glb_data = db.Column(db.LargeBinary)  # PRIMARY - GLB file binary data (only format used)
    glb_file_size = db.Column(db.Integer)  # Size in bytes for monitoring
    
    # Metadata
    unlock_level = db.Column(db.Integer, default=1)  # Minimum level to unlock (1 = always available)
    points_required = db.Column(db.Integer, default=0)  # Points needed to unlock
    is_premium = db.Column(db.Boolean, default=False)  # Premium/paid avatars
    sort_order = db.Column(db.Integer, default=0, index=True)  # Display order in picker - indexed for sorting
    is_active = db.Column(db.Boolean, default=True, index=True)  # Can be selected by users - indexed for filtering
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite index for common query pattern: active avatars ordered by sort_order and name
    __table_args__ = (
        db.Index('idx_active_sorted', 'is_active', 'sort_order', 'name'),
        db.Index('idx_category_active', 'category', 'is_active'),
    )
    
    # Relationship (users who have selected this avatar)
    users = db.relationship('User', backref='avatar', lazy='dynamic',
                           primaryjoin='Avatar.slug == foreign(User.avatar_id)')
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.slug,  # Keep 'id' as slug for backward compatibility with frontend
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'folder': self.folder_path,
            'obj_file': self.obj_file,
            'mtl_file': self.mtl_file,
            'texture_file': self.texture_file,
            'thumbnail_file': self.thumbnail_file,
            'unlock_level': self.unlock_level,
            'points_required': self.points_required,
            'is_premium': self.is_premium,
            'is_active': self.is_active
        }
    
    @staticmethod
    def get_by_slug(slug):
        """Get avatar by slug (e.g., 'cool-bee') with request-level caching"""
        from flask import g
        
        # Initialize cache if not exists
        if not hasattr(g, '_avatar_cache'):
            g._avatar_cache = {}
        
        # Return cached result if available
        if slug in g._avatar_cache:
            return g._avatar_cache[slug]
        
        # Query database and cache result
        avatar = Avatar.query.filter_by(slug=slug, is_active=True).first()
        g._avatar_cache[slug] = avatar
        return avatar
    
    @staticmethod
    def get_all_active(category=None):
        """Get all active avatars, optionally filtered by category"""
        query = Avatar.query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        return query.order_by(Avatar.sort_order, Avatar.name).all()


class BadgeAsset(db.Model):
    """Store 3D badge GLB files in database for CDN-free deployment"""
    __tablename__ = 'badge_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    badge_name = db.Column(db.String(100), unique=True, nullable=False, index=True)  # e.g., 'Novice', 'Scholar'
    file_name = db.Column(db.String(200), nullable=False)  # Original filename: 'Novice.glb'
    file_data = db.Column(db.LargeBinary, nullable=False)  # Binary GLB data
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100), default='model/gltf-binary')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_accessed = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<BadgeAsset {self.badge_name} - {self.file_size} bytes>'
    
    def to_dict(self):
        """Convert to dictionary for API responses (excluding binary data)"""
        return {
            'badge_name': self.badge_name,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class PurchaseRecord(db.Model):
    """IAP purchase log for Apple/Google/Web verifications"""
    __tablename__ = 'purchase_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False)

    platform = db.Column(db.String(20), index=True)  # 'apple' | 'google' | 'web'
    product_id = db.Column(db.String(150), index=True, nullable=False)
    status = db.Column(db.String(30), index=True, default='pending')  # pending|verified|failed|refunded

    transaction_id = db.Column(db.String(200), index=True)
    purchase_token = db.Column(db.String(300), index=True)

    raw_payload = db.Column(db.JSON, default=dict)

    purchased_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<PurchaseRecord user={self.user_id} product={self.product_id} platform={self.platform} status={self.status}>"


class AnonPurchaseOwnership(db.Model):
    """Device-scoped (cookie-based) ownership records for guest restore.

    This supports Apple guideline-compliant restore without forcing account creation.
    It also helps when the native IAP bridge is temporarily unavailable in TestFlight:
    the server can still remember an anonymous restore attempt across sessions.
    """
    __tablename__ = 'anon_purchase_ownership'

    id = db.Column(db.Integer, primary_key=True)
    anon_restore_id = db.Column(db.String(64), index=True, nullable=False)

    platform = db.Column(db.String(20), index=True)  # 'apple' | 'google' | 'web'
    product_id = db.Column(db.String(150), index=True, nullable=False)
    status = db.Column(db.String(30), index=True, default='verified')  # verified|restore_error
    raw_payload = db.Column(db.JSON, default=dict)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('anon_restore_id', 'product_id', name='uq_anon_purchase_ownership_restore_product'),
    )

    @staticmethod
    def upsert(anon_restore_id: str, platform: str, product_id: str, status: str = 'verified', raw_payload=None):
        """
        Upsert AnonPurchaseOwnership record with race condition prevention.
        Uses database-level locking to prevent concurrent insert conflicts.
        """
        from sqlalchemy.orm import with_for_update
        
        # Use row-level lock to prevent race conditions
        rec = AnonPurchaseOwnership.query.with_for_update(
            skip_locked=True  # Skip if another transaction has lock (prevents deadlocks)
        ).filter_by(
            anon_restore_id=anon_restore_id,
            product_id=product_id
        ).first()
        
        if rec is None:
            # Safe to create - we have the lock, no race condition
            rec = AnonPurchaseOwnership(
                anon_restore_id=anon_restore_id,
                platform=platform,
                product_id=product_id,
                status=status,
                raw_payload=raw_payload or {}
            )
            db.session.add(rec)
        else:
            # Update existing record
            rec.platform = platform
            rec.status = status
            rec.raw_payload = raw_payload or rec.raw_payload or {}
            rec.updated_at = datetime.utcnow()
        return rec


class AnonInstallLink(db.Model):
        """Optional bridge between a stable native install identifier and anon_restore_id.

        Why this exists:
        - The cookie-based anon_restore_id works well across sessions, but is lost on
            app reinstall or data deletion.
        - Native wrappers can provide a stable keychain-backed install id that
            survives reinstalls. When available, we can map that to the existing
            anon_restore_id so a restored guest can regain entitlements.

        Privacy note:
        - This is an app-scoped random identifier, not a device fingerprint.
        - We do not attempt to derive it from hardware identifiers.
        """
        __tablename__ = 'anon_install_links'

        id = db.Column(db.Integer, primary_key=True)
        install_id = db.Column(db.String(128), unique=True, index=True, nullable=False)
        anon_restore_id = db.Column(db.String(64), index=True, nullable=False)

        created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        @staticmethod
        def upsert(install_id: str, anon_restore_id: str):
                install_id = (install_id or '').strip()
                anon_restore_id = (anon_restore_id or '').strip()
                if not install_id or not anon_restore_id:
                        return None
                rec = AnonInstallLink.query.filter_by(install_id=install_id).first()
                if rec is None:
                        rec = AnonInstallLink(install_id=install_id, anon_restore_id=anon_restore_id)
                        db.session.add(rec)
                else:
                        rec.anon_restore_id = anon_restore_id
                return rec


class BundleKey(db.Model):
    """Database-managed avatar bundle distribution keys.

    Allows admin to issue time/usage-limited bundle keys that unlock bundles.
    Supersedes static dev keys in avatar_bundles.py when present.
    """
    __tablename__ = 'bundle_keys'

    id = db.Column(db.Integer, primary_key=True)
    key_raw = db.Column(db.String(80), nullable=False)  # Original form with dashes
    key_norm = db.Column(db.String(80), nullable=False, unique=True, index=True)  # Uppercase, no spaces
    bundle_id = db.Column(db.String(100), nullable=False, index=True)

    max_uses = db.Column(db.Integer, default=1)  # 1 = single-use; >1 multi-use classroom key
    uses_count = db.Column(db.Integer, default=0)

    expires_at = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(20), default='active', index=True)  # active|revoked|expired|exhausted

    issued_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)  # Admin who created
    redeemed_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)  # Last user who redeemed (single-use)
    redeemed_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_expired(self):
        return bool(self.expires_at and datetime.utcnow() > self.expires_at)

    def can_redeem(self):
        if self.status != 'active':
            return False, 'status_not_active'
        if self.is_expired():
            return False, 'expired'
        if self.uses_count >= (self.max_uses or 1):
            return False, 'key_exhausted'
        return True, 'ok'

    def apply_use(self, user_id: int):
        self.uses_count = (self.uses_count or 0) + 1
        self.redeemed_by = user_id
        self.redeemed_at = datetime.utcnow()
        # Transition status if single-use exhausted
        if self.uses_count >= (self.max_uses or 1):
            self.status = 'exhausted'

    @staticmethod
    def normalize(raw: str) -> str:
        return (raw or '').replace(' ', '').upper()

    @staticmethod
    def generate(bundle_id: str, prefix: str = 'BEE') -> tuple[str, str]:
        """Generate a human-readable key and its normalized form."""
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        year = datetime.utcnow().year
        key_raw = f"{prefix}-{bundle_id[:6].upper()}-{year}-{rand}".replace('--', '-')
        return key_raw, BundleKey.normalize(key_raw)

    def to_dict(self):
        return {
            'id': self.id,
            'key_raw': self.key_raw,
            'bundle_id': self.bundle_id,
            'max_uses': self.max_uses,
            'uses_count': self.uses_count,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'status': self.status,
            'redeemed_by': self.redeemed_by,
            'redeemed_at': self.redeemed_at.isoformat() if self.redeemed_at else None,
        }

    def __repr__(self):
        return f"<BundleKey {self.key_raw} bundle={self.bundle_id} status={self.status} uses={self.uses_count}/{self.max_uses}>"


class DynamicBundle(db.Model):
    """Admin-defined dynamic bundles (BeeKey packs) linking a generated bundle_id to avatar list."""
    __tablename__ = 'dynamic_bundles'

    id = db.Column(db.Integer, primary_key=True)
    bundle_id = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    avatars = db.Column(db.JSON, default=list)  # list of avatar slugs
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    def to_dict(self):
        return {
            'bundle_id': self.bundle_id,
            'name': self.name,
            'avatars': self.avatars or [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<DynamicBundle {self.bundle_id} avatars={len(self.avatars or [])}>"


class BundleKeyRedemption(db.Model):
    """Trace each redemption event for auditing and analytics."""
    __tablename__ = 'bundle_key_redemptions'

    id = db.Column(db.Integer, primary_key=True)
    bundle_key_id = db.Column(db.Integer, db.ForeignKey('bundle_keys.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    bundle_id = db.Column(db.String(120), index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(300))
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'bundle_key_id': self.bundle_key_id,
            'user_id': self.user_id,
            'bundle_id': self.bundle_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'redeemed_at': self.redeemed_at.isoformat() if self.redeemed_at else None
        }

    def __repr__(self):
        return f"<BundleKeyRedemption key={self.bundle_key_id} user={self.user_id} bundle={self.bundle_id}>"


class WordBankStorage(db.Model):
    """
    Database-backed wordbank persistence for Railway deployment.
    Solves the ephemeral filesystem problem where data/wordbanks/ files get deleted on restart.
    Stores wordbanks in PostgreSQL for durability across container restarts and multi-instance deployments.
    """
    __tablename__ = 'wordbank_storage'
    
    id = db.Column(db.Integer, primary_key=True)
    storage_id = db.Column(db.String(36), unique=True, nullable=False, index=True)  # UUID matching session storage_id
    words_data = db.Column(db.JSON, nullable=False)  # Array of {word, sentence, hint} objects
    word_count = db.Column(db.Integer, nullable=False, index=True)  # Quick count without parsing JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Optional: link to user for cleanup (nullable for guest users)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    
    def __repr__(self):
        return f"<WordBankStorage storage_id={self.storage_id} words={self.word_count}>"
    
    @classmethod
    def save_wordbank(cls, storage_id: str, words: list, user_id: int = None):
        """Save or update wordbank in database"""
        existing = cls.query.filter_by(storage_id=storage_id).first()
        
        if existing:
            existing.words_data = words
            existing.word_count = len(words)
            existing.updated_at = datetime.utcnow()
            existing.last_accessed = datetime.utcnow()
            if user_id:
                existing.user_id = user_id
        else:
            new_storage = cls(
                storage_id=storage_id,
                words_data=words,
                word_count=len(words),
                user_id=user_id
            )
            db.session.add(new_storage)
        
        db.session.commit()
        return True
    
    @classmethod
    def load_wordbank(cls, storage_id: str):
        """Load wordbank from database and update last_accessed timestamp"""
        storage = cls.query.filter_by(storage_id=storage_id).first()
        if storage:
            storage.last_accessed = datetime.utcnow()
            db.session.commit()
            return storage.words_data
        return None
    
    @classmethod
    def delete_wordbank(cls, storage_id: str):
        """Delete wordbank from database"""
        storage = cls.query.filter_by(storage_id=storage_id).first()
        if storage:
            db.session.delete(storage)
            db.session.commit()
            return True
        return False


class UserEntitlement(db.Model):
    __tablename__ = 'user_entitlements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    entitlement_type = db.Column(db.String(50), nullable=False, index=True)
    entitlement_key = db.Column(db.String(200), nullable=False, index=True)
    source = db.Column(db.String(100), nullable=True, index=True)
    source_id = db.Column(db.String(100), nullable=True)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'entitlement_type', 'entitlement_key', name='uq_user_entitlements_user_type_key'),
    )


class WordSet(db.Model):
    __tablename__ = 'word_sets'

    set_id = db.Column(db.String(50), primary_key=True)
    letter = db.Column(db.String(2), nullable=False, index=True)
    words_json = db.Column(db.JSON, nullable=False, default=list)
    active = db.Column(db.Boolean, default=True, index=True)


class ColoringBookList(db.Model):
    __tablename__ = 'coloring_book_lists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    source_set_id = db.Column(db.String(50), db.ForeignKey('word_sets.set_id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='active', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime)

    __table_args__ = (
        UniqueConstraint('user_id', 'source_set_id', name='uq_coloring_book_lists_user_set'),
    )


class ColoringBookListItem(db.Model):
    __tablename__ = 'coloring_book_list_items'

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('coloring_book_lists.id'), nullable=False, index=True)
    word = db.Column(db.String(100), nullable=False, index=True)
    is_completed = db.Column(db.Boolean, default=False, index=True)
    completed_at = db.Column(db.DateTime)

    __table_args__ = (
        UniqueConstraint('list_id', 'word', name='uq_coloring_book_list_items_list_word'),
    )
