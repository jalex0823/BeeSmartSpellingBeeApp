#!/usr/bin/env python3
"""
Kid-Safe Content Filter with Guardian Reporting System

This module implements comprehensive content filtering for the BeeSmart Spelling Bee app
with progressive warnings and guardian notification for inappropriate content attempts.

Features:
1. Multi-tier inappropriate content detection
2. Progressive warning system (warning → final warning → report)
3. Session tracking of violations
4. Guardian notification system
5. Kid-friendly explanations

Usage: Import and integrate into word upload/paste functionality
"""

import re
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path

class ContentViolationTracker:
    """Tracks content violations per session for progressive enforcement"""
    
    def __init__(self):
        # In-memory tracking (could be moved to database for persistence)
        self.session_violations: Dict[str, List[Dict]] = {}
        self.violation_log_file = Path("data/content_violations.json")
        self.violation_log_file.parent.mkdir(exist_ok=True)
    
    def get_session_id(self, request_or_session):
        """Generate consistent session ID for tracking"""
        # Use session ID if available, otherwise IP hash
        if hasattr(request_or_session, 'remote_addr'):
            # Flask request object
            ip_hash = hashlib.md5(request_or_session.remote_addr.encode()).hexdigest()[:8]
            return f"session_{ip_hash}"
        elif isinstance(request_or_session, dict) and 'session_id' in request_or_session:
            return request_or_session['session_id']
        else:
            return "session_unknown"
    
    def record_violation(self, session_id: str, word: str, violation_type: str, severity: str):
        """Record a content violation for tracking"""
        if session_id not in self.session_violations:
            self.session_violations[session_id] = []
        
        violation = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'word': word,
            'violation_type': violation_type,
            'severity': severity,
            'session_id': session_id
        }
        
        self.session_violations[session_id].append(violation)
        
        # Log to file for persistence
        self._log_violation_to_file(violation)
    
    def get_violation_count(self, session_id: str, time_window_hours: int = 24) -> int:
        """Get violation count for session within time window"""
        if session_id not in self.session_violations:
            return 0

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        recent_violations = [
            v for v in self.session_violations[session_id]
            if datetime.fromisoformat(v['timestamp']) > cutoff_time
        ]
        return len(recent_violations)
    
    def should_report_to_guardian(self, session_id: str) -> bool:
        """Determine if violations warrant guardian notification"""
        violations_24h = self.get_violation_count(session_id, 24)
        return violations_24h >= 3  # Report after 3 violations in 24 hours
    
    def _log_violation_to_file(self, violation):
        """Log violation to persistent file"""
        try:
            # Read existing log
            if self.violation_log_file.exists():
                with open(self.violation_log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = {'violations': []}
            
            # Add new violation
            log_data['violations'].append(violation)
            
            # Keep only last 1000 violations
            log_data['violations'] = log_data['violations'][-1000:]
            
            # Write back to file
            with open(self.violation_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Could not log violation to file: {e}")

# Enhanced inappropriate words list with categories
ENHANCED_INAPPROPRIATE_WORDS = {
    'profanity': {
        "dam", "dams", "damn", "damned", "hell", "hells", "crap", "crappy", "sucks", "piss", "pissed",
        "shit", "shits", "shitty", "bullshit",
        "fuck", "fucks", "fucker", "fuckers", "fucked", "fucking", "fuckhead", "fuckheads",
        "motherfucker", "motherfuckers", "motherfucking",
        "bitch", "bitches", "bitchy",
        "ass", "asses", "asshole", "assholes", "jackass", "smartass", "dumbass", "dumbasses",
        "bastard", "bastards",
        "dick", "dicks", "cock", "cocks", "prick", "pricks",
        "cunt", "cunts", "twat", "twats",
        "slut", "sluts", "slutty", "whore", "whores", "whorish",
        "boob", "boobs", "tit", "tits", "titty", "titties",
        "arse", "arses",
        "douche", "douchebag", "douchebags",
        "turd", "turds", "fart", "farts",
        "screw", "screwed", "screwing",
    },
    'sexual_content': {
        "sex", "sexy", "porn", "pornography", "pornographic",
        "orgasm", "orgasms", "penis", "vagina", "vulva",
        "breast", "breasts", "nipple", "nipples",
        "ejaculation", "ejaculations", "erection", "masturbate", "masturbation",
        "prostitute", "prostitution", "prostitutes",
        "nude", "nudity", "naked",
        "horny", "arousal", "aroused", "climax",
        "intercourse", "erotic", "erotica",
        "sexuality", "genitals", "genital",
        "lust", "lustful", "lusty",
        "fetish", "fetishes", "pervert", "perverts", "perverted",
        "fornicate", "fornication",
        "seduce", "seduction", "seducing",
        "obscene", "obscenity",
        "sexting",
        # Child safety terms
        "pedophile", "pedophiles", "pedophilia", "pedophilic", "paedophile", "paedophiles", "paedophilia",
        "molest", "molestation", "molester", "molesting", "molesters",
        "rape", "rapist", "rapists", "raping", "rapes", "raped",
        "incest", "incestuous",
        "abuse", "abuser", "abusers", "abusive", "abusing",
        "predator", "predators",
        "groom", "grooming", "groomer", "groomers",
        "statutory", "underage", "preteen", "preteens", "tweener", "tweeners",
        "victim", "victims",
        "exploit", "exploitation", "exploiting", "exploiter", "exploiters",
    },
    'violence': {
        "kill", "killing", "killer", "killers",
        "murder", "murderer", "murderers", "murdering",
        "suicide", "suicidal",
        "weapon", "weapons",
        "gun", "guns", "rifle", "rifles", "pistol", "pistols", "shotgun", "shotguns",
        "shoot", "shooting", "shootings", "shooter", "shooters",
        "stab", "stabbing", "stabbings", "stabbed",
        "knife", "knives",
        "bomb", "bombs", "bombing", "bombings", "explosive", "explosives",
        "grenade", "grenades",
        "offing", "offed",
        "violent", "violence",
        "slay", "slaying", "slayings", "slaughter", "slaughtered", "slaughtering",
        "harm", "harming", "harmful",
        "torture", "torturing", "tortured", "torturous",
        "massacre", "massacred", "massacring",
        "execute", "execution", "executions", "executing",
        "behead", "beheading", "beheadings",
        "mutilate", "mutilation", "mutilating",
        "decapitate", "decapitation",
        "strangle", "strangling", "strangled",
        "terrorism", "terrorist", "terrorists",
        "hostage", "hostages",
        "genocide",
        "assault", "assaults", "assaulting", "assaulted",
        "harass", "harassment", "harassing", "harasser",
    },
    'drugs_alcohol': {
        "drug", "drugs",
        "cocaine", "coke",
        "marijuana", "cannabis",
        "heroin", "meth", "methamphetamine",
        "weed", "pot",
        "stoned", "overdose", "overdosed", "overdosing",
        "addiction", "addicted", "addictive",
        "hallucinate", "hallucination", "hallucinations",
        "drunk", "drunken", "drunkenness",
        "alcohol", "alcoholic", "alcoholism",
        "beer", "liquor", "whiskey", "vodka", "tequila",
        "cigarette", "cigarettes", "smoking", "smoked",
        "tobacco",
        "vape", "vaping", "vaper",
        "narcotic", "narcotics",
        "opium", "opioid", "opioids",
        "crack",
        "ecstasy",
        "lsd", "acid",
    },
    'hate_speech': {
        "racist", "racism",
        "sexist", "sexism",
        "nazi", "nazis",
        "hate",
        "nigger", "niggers", "nigga", "niggas",
        "chink", "chinks",
        "spic", "spics",
        "kike", "kikes",
        "gook", "gooks",
        "wetback", "wetbacks",
        "cracker",
        "honky", "honkies",
        "fag", "fags", "faggot", "faggots",
        "dyke", "dykes",
        "retard", "retards", "retarded",
        "moron", "morons",
        "idiot", "idiots",
        "imbecile", "imbeciles",
        "cripple", "cripples",
        "bigot", "bigots", "bigoted", "bigotry",
        "extremist", "extremists", "extremism",
        "supremacist", "supremacists",
        "homophobic", "homophobia",
        "transphobic", "transphobia",
        "xenophobic", "xenophobia",
    },
    'disturbing_content': {
        "death", "die", "dying",
        "blood", "bloody", "bloodshed",
        "corpse", "corpses",
        "skull", "skulls",
        "sadism", "sadist", "sadistic",
        "gore", "gory",
        "cannibal", "cannibalism",
        "necrophilia",
        "self-harm", "selfharm", "cutting",
    },
    'spam_patterns': {
        "wtf", "stfu", "gtfo", "omfg",
        "thot",
        "simp",
    },
}

# Flatten all inappropriate words from the categories above
ALL_INAPPROPRIATE_WORDS = set()
for category_words in ENHANCED_INAPPROPRIATE_WORDS.values():
    ALL_INAPPROPRIATE_WORDS.update(category_words)

# Also merge from AjaSpellBApp authoritative list when available
try:
    from AjaSpellBApp import INAPPROPRIATE_WORDS as _APP_WORDS
    ALL_INAPPROPRIATE_WORDS.update({str(w).strip().lower() for w in _APP_WORDS if str(w or '').strip()})
except Exception:
    pass

# Global violation tracker instance
violation_tracker = ContentViolationTracker()

def detect_inappropriate_content(word: str) -> Tuple[bool, str, str]:
    """
    Enhanced inappropriate content detection
    Returns: (is_inappropriate, category, reason)
    """
    word_lower = word.lower().strip()
    
    # Direct word match
    for category, words in ENHANCED_INAPPROPRIATE_WORDS.items():
        if word_lower in words:
            return True, category, f"contains inappropriate {category.replace('_', ' ')}"
    
    # Partial match for longer inappropriate words
    for category, words in ENHANCED_INAPPROPRIATE_WORDS.items():
        for inappropriate in words:
            if len(inappropriate) > 4 and inappropriate in word_lower:
                return True, category, f"contains inappropriate {category.replace('_', ' ')}"
    
    # Pattern-based detection
    # Leetspeak variations (e.g., "sh1t", "f*ck")
    leetspeak_patterns = {
        '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '0': 'o',
        '@': 'a', '$': 's', '*': '', '#': ''
    }
    
    # Convert leetspeak to normal letters
    converted_word = word_lower
    for leet, normal in leetspeak_patterns.items():
        converted_word = converted_word.replace(leet, normal)
    
    # Check converted word against inappropriate list
    for category, words in ENHANCED_INAPPROPRIATE_WORDS.items():
        if converted_word in words:
            return True, category, f"uses inappropriate characters to spell {category.replace('_', ' ')}"
    
    # Check for excessive repeated characters (spam pattern)
    if re.search(r'(.)\1{4,}', word_lower):
        return True, 'spam_patterns', "uses excessive repeated characters"
    
    # Check for mixed numbers and letters (often spam)
    if re.search(r'\d.*[a-z]|[a-z].*\d', word_lower) and len(word_lower) > 3:
        return True, 'spam_patterns', "mixes numbers and letters inappropriately"
    
    return False, '', ''

def get_kid_friendly_violation_message(word: str, category: str, violation_count: int) -> str:
    """Generate age-appropriate explanation of content violation"""
    
    category_explanations = {
        'profanity': "uses words that aren't polite or respectful",
        'sexual_content': "includes grown-up topics not suitable for kids",
        'violence': "describes harmful or scary things",
        'drugs_alcohol': "mentions substances that aren't healthy for children",
        'hate_speech': "contains mean or hurtful language",
        'disturbing_content': "includes topics that might be scary or upsetting",
        'spam_patterns': "looks like random letters or spam"
    }
    
    explanation = category_explanations.get(category, "isn't appropriate for our spelling bee")
    
    # Progressive message severity
    if violation_count == 1:
        return f"""
🐝 Oops! Our bee scouts noticed that "{word}" {explanation}.

📚 BeeSmart is a safe learning space for kids! Let's choose educational words that help everyone learn and have fun.

💡 Try using words from school subjects like science, nature, or your favorite books instead!
"""
    
    elif violation_count == 2:
        return f"""
🚨 Warning from the Queen Bee! 

This is your second attempt to use inappropriate content ("{word}" {explanation}). 

📖 BeeSmart is designed to be a safe, educational space for young learners. Continued attempts to use inappropriate words may result in a report being sent to your parent or guardian.

🌟 Let's focus on learning awesome vocabulary words that will help you become a spelling champion!
"""
    
    else:  # 3rd+ violation
        return f"""
🚫 FINAL WARNING from the Hive! 

You have repeatedly tried to use inappropriate words ("{word}" {explanation}). 

📧 A report about these attempts has been sent to your parent or guardian. They will be notified about the inappropriate content attempts during this spelling session.

🐝 BeeSmart is committed to providing a safe, educational environment. Please use appropriate vocabulary words for learning.

⭐ Let's get back to learning amazing words that will make you a better speller!
"""

def generate_guardian_report(session_id: str, violations: List[Dict]) -> str:
    """Generate report for parent/guardian about content violations"""

    report = f"""
🐝 BeeSmart Spelling Bee - Guardian Notification Report

📅 Date: {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}
👤 Session ID: {session_id}
🚨 Violation Count: {len(violations)}

📋 INCIDENT SUMMARY:
Your child attempted to use inappropriate content multiple times while using the BeeSmart Spelling Bee educational app. Our content filter successfully blocked these attempts to maintain a safe learning environment.

📝 VIOLATION DETAILS:
"""

    for i, violation in enumerate(violations, 1):
        timestamp = datetime.fromisoformat(violation['timestamp']).strftime('%I:%M %p UTC')
        report += f"""
{i}. Time: {timestamp}
   Word Attempted: "{violation['word']}"
   Issue: {violation['violation_type'].replace('_', ' ').title()}
   Severity: {violation['severity']}
"""

    report += f"""

🛡️ SAFETY MEASURES TAKEN:
• All inappropriate content was automatically blocked
• No inappropriate words were added to spelling lists
• Educational content remained safe and age-appropriate
• Progressive warnings were displayed to encourage better choices

📚 EDUCATIONAL FOCUS:
BeeSmart is designed to help children (ages 6-14) improve their spelling skills using educational, age-appropriate vocabulary. Our content filter ensures a safe learning environment by blocking profanity, adult content, violence references, and other inappropriate material.

💡 RECOMMENDATIONS:
• Discuss appropriate online behavior and language with your child
• Encourage focus on educational vocabulary from school subjects
• Consider supervised usage if inappropriate attempts continue
• Contact us at support@beesmart.com if you have concerns

🐝 Thank you for supporting your child's educational journey with BeeSmart!

---
This is an automated safety report from BeeSmart Spelling Bee
Generated: {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}
"""

    return report

def _safe_print(text: str):
    """Print text safely even if console encoding can't handle emoji on Windows."""
    import sys
    try:
        print(text)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, 'encoding', None) or 'utf-8'
        try:
            sys.stdout.write(text.encode(enc, errors='replace').decode(enc, errors='replace'))
            sys.stdout.write("\n")
        except Exception:
            # Final fallback without emojis
            ascii_text = text.encode('ascii', errors='ignore').decode('ascii')
            print(ascii_text)

def filter_content_with_tracking(words: List[str], session_context) -> Tuple[List[str], List[str], List[Dict]]:
    """
    Filter word list with violation tracking and progressive warnings
    
    Args:
        words: List of words to filter
        session_context: Flask session or request object for tracking
    
    Returns:
        (filtered_words, blocked_words, violation_messages)
    """
    session_id = violation_tracker.get_session_id(session_context)
    
    filtered_words = []
    blocked_words = []
    violation_messages = []
    
    for word in words:
        is_inappropriate, category, reason = detect_inappropriate_content(word)
        
        if is_inappropriate:
            # Record the violation
            violation_tracker.record_violation(
                session_id=session_id,
                word=word,
                violation_type=category,
                severity='high' if category in ['sexual_content', 'hate_speech'] else 'medium'
            )
            
            blocked_words.append(word)
            
            # Get current violation count
            violation_count = violation_tracker.get_violation_count(session_id)
            
            # Generate appropriate message
            message = get_kid_friendly_violation_message(word, category, violation_count)
            violation_messages.append({
                'word': word,
                'message': message,
                'violation_count': violation_count,
                'should_report': violation_tracker.should_report_to_guardian(session_id)
            })
            
            # Generate guardian report if threshold reached
            if violation_tracker.should_report_to_guardian(session_id):
                violations = violation_tracker.session_violations.get(session_id, [])
                guardian_report = generate_guardian_report(session_id, violations)
                
                # In production, this would email the report to parents
                # For now, we'll log it
                _safe_print(f"📧 GUARDIAN REPORT GENERATED for session {session_id}")
                _safe_print(guardian_report)
                
                # Save report to file
                report_file = Path(f"data/guardian_reports/report_{session_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.txt")
                report_file.parent.mkdir(exist_ok=True, parents=True)
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(guardian_report)
        
        else:
            # Word is appropriate
            filtered_words.append(word)
    
    return filtered_words, blocked_words, violation_messages

def get_content_filter_status(session_context) -> Dict:
    """Get current content filter status for session"""
    session_id = violation_tracker.get_session_id(session_context)
    violation_count = violation_tracker.get_violation_count(session_id)
    
    return {
        'session_id': session_id,
        'violation_count_24h': violation_count,
        'warning_level': 'green' if violation_count == 0 else 'yellow' if violation_count < 3 else 'red',
        'guardian_notification_triggered': violation_tracker.should_report_to_guardian(session_id)
    }

# Test function for development
if __name__ == "__main__":
    # Test the content filtering system
    test_words = [
        "apple", "banana", "damn", "hello", "shit", "education", "f*ck", 
        "learning", "wtf123", "sunshine", "kill", "mathematics"
    ]
    
    print("🧪 Testing Content Filter System")
    print("=" * 50)
    
    # Simulate session
    mock_session = {'session_id': 'test_session_001'}
    
    filtered, blocked, messages = filter_content_with_tracking(test_words, mock_session)
    
    print(f"✅ Filtered words: {filtered}")
    print(f"❌ Blocked words: {blocked}")
    print(f"📝 Violation messages: {len(messages)}")
    
    for msg in messages:
        print(f"\n{msg['message']}")