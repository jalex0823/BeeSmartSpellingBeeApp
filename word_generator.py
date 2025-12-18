"""
BeeSmart Spelling App - Word Generation System
Auto-generates spelling words by difficulty level for speed rounds
CRITICAL: All generated words MUST pass kid-friendly filter
"""

import random


def _is_word_safe(word):
    """
    Internal function to check if word is kid-friendly.
    This avoids circular import by duplicating the filter logic.
    """
    # Import the INAPPROPRIATE_WORDS set from AjaSpellBApp
    # This list MUST stay in sync with the main filter
    INAPPROPRIATE_WORDS = {
        # Profanity and vulgar terms
        "damn", "damned", "hell", "hells", "crap", "sucks", "piss", "pissed",
        # Sexual/adult content - CRITICAL: Block all adult/child abuse terms
        "sex", "sexy", "porn", "orgasm", "penis", "vagina", "breast", "breasts",
        "ejaculation", "ejaculations", "erection", "masturbate", "prostitute",
        "pedophile", "pedophiles", "pedophilia", "pedophilic", "paedophile", "paedophilia",
        "molest", "molestation", "molester", "molesting", "molesters",
        "rape", "rapist", "raping", "rapes", "raped",
        "incest", "incestuous", "abuse", "abuser", "abusive", "abusing",
        "predator", "predators", "groom", "grooming", "groomer", "groomers",
        "statutory", "underage", "preteen", "preteens", "tweener", "tweeners",
        "victim", "victims", "exploit", "exploitation", "exploiting",
        "assault", "assaulting", "assaults", "assaulted",
        "harass", "harassment", "harassing",
        "nude", "naked", "horny", "arousal", "climax", "intercourse",
        "erotic", "sexuality", "genitals", "genital",
        # Violence/weapons
        "kill", "killing", "killer", "murder", "murderer", "suicide", "weapon", 
        "gun", "shoot", "shooting", "bomb", "explosive",
        # Drugs/alcohol
        "drug", "drugs", "cocaine", "marijuana", "heroin", "meth", "drunk", "alcohol",
        # Hate speech
        "racist", "sexist", "nazi", "hate",
        # Other inappropriate
        "death", "die", "dying", "blood", "bloody", "torture",
        # Disturbing / age-inappropriate concepts
        "sadism", "sadist", "sadistic"
    }
    
    word_lower = word.lower().strip()
    
    # Check against inappropriate words list
    if word_lower in INAPPROPRIATE_WORDS:
        return False, f"Word '{word}' is not appropriate for children"
    
    # Check for partial matches (longer words containing inappropriate substrings)
    for inappropriate in INAPPROPRIATE_WORDS:
        if len(inappropriate) > 4 and inappropriate in word_lower:
            return False, f"Word '{word}' contains inappropriate content"
    
    # Special rule: block "sex" substring
    if "sex" in word_lower:
        return False, f"Word '{word}' contains restricted substring 'sex'"
    
    return True, "OK"


# Grade 1-2: CVC words, basic sight words
GRADE_1_2_WORDS = [
    "cat", "dog", "run", "sun", "hat", "mat", "rat", "bat", "can", "man",
    "pan", "fan", "sit", "hit", "pit", "kit", "hot", "pot", "got", "not",
    "bed", "red", "led", "fed", "pig", "big", "dig", "fig", "bug", "hug",
    "rug", "mug", "box", "fox", "six", "mix", "top", "mop", "hop", "pop",
    "cup", "pup", "up", "bus", "us", "pen", "hen", "ten", "men", "wet",
    "pet", "net", "get", "set", "let", "the", "and", "for", "are", "but",
    "not", "you", "all", "can", "had", "her", "was", "one", "our", "out",
    "day", "get", "has", "him", "his", "how", "if", "its", "may", "old",
    "see", "two", "way", "who", "boy", "did", "new", "now", "put", "too",
    "fun", "lot", "mom", "dad", "yes", "no", "go", "so", "me", "we"
]

# Grade 3-4: Blends, digraphs, common patterns
GRADE_3_4_WORDS = [
    "black", "block", "brick", "bring", "clock", "crank", "drink", "frank",
    "grand", "plant", "print", "skunk", "spring", "stand", "string", "think",
    "thank", "blank", "blend", "brand", "clamp", "crisp", "draft", "flash",
    "grape", "grass", "grasp", "priest", "shrink", "splash", "strand", "stress",
    "about", "after", "again", "always", "around", "because", "before", "between",
    "could", "every", "first", "friend", "great", "house", "large", "later",
    "learn", "never", "often", "other", "people", "place", "please", "right",
    "school", "should", "small", "start", "still", "study", "their", "there",
    "these", "think", "three", "through", "today", "under", "until", "where",
    "which", "while", "world", "would", "write", "young", "happy", "party",
    "funny", "lucky", "penny", "puppy", "sorry", "story", "study", "carry"
]

# Grade 5-6: Multisyllabic, prefixes/suffixes
GRADE_5_6_WORDS = [
    "adventure", "beautiful", "beginning", "business", "calendar", "character",
    "chocolate", "community", "dangerous", "delicious", "different", "difficult",
    "disappear", "discovery", "emergency", "enormous", "especially", "experiment",
    "favorite", "finally", "furniture", "geography", "government", "hamburger",
    "happiness", "imagine", "important", "impossible", "incredible", "intelligence",
    "interesting", "interrupt", "interview", "invisible", "language", "library",
    "lightning", "literature", "manufacture", "mathematics", "medicine", "mysterious",
    "necessary", "neighborhood", "ordinary", "otherwise", "paragraph", "particular",
    "passenger", "personality", "photograph", "pollution", "popular", "population",
    "possible", "probably", "professor", "recognize", "recommend", "remember",
    "restaurant", "ridiculous", "ScheduleError", "separate", "similar", "skyscraper",
    "stereotype", "substitute", "surprise", "technology", "temperature", "terrible",
    "together", "tomorrow", "treasure", "uncomfortable", "understand", "universe",
    "unnecessary", "unusual", "vacation", "vegetable", "volunteer", "wednesday",
    "wonderful", "yesterday", "accomplishment", "achievement", "advertisement"
]

# Middle School: Academic vocabulary
MIDDLE_SCHOOL_WORDS = [
    "abundance", "accelerate", "accommodate", "accomplish", "accumulate", "achievement",
    "acknowledge", "adolescent", "affectionate", "aggressive", "allergic", "ambassador",
    "analysis", "ancient", "Antarctica", "anxiety", "appreciate", "appropriate",
    "approximate", "argument", "artificial", "assessment", "astronaut", "atmosphere",
    "attendance", "attorney", "audience", "authentic", "authority", "automatic",
    "bankruptcy", "beneficial", "boundary", "calculating", "campaign", "candidate",
    "capacity", "capitalism", "catastrophe", "celebration", "challenge", "chemical",
    "citizen", "civilization", "classify", "colleague", "collision", "column",
    "commercial", "commitment", "communicate", "community", "comparison", "compassion",
    "compatible", "competition", "complement", "complexity", "comprehend", "compromise",
    "concentrate", "conclusion", "condition", "conference", "confidence", "congratulate",
    "conscience", "conscious", "consequence", "conservation", "consideration", "consistent",
    "constitution", "construction", "contemporary", "continent", "continuous", "contribution",
    "controversial", "convenient", "conversation", "cooperation", "coordinate", "correspond",
    "courageous", "criticism", "curiosity", "currency", "curriculum", "cylinder"
]

# High School: Advanced, SAT-level words
HIGH_SCHOOL_WORDS = [
    "abdicate", "aberration", "abhor", "abscond", "abstemious", "accede",
    "accolade", "acquiesce", "acrimonious", "acumen", "adamant", "admonish",
    "adroit", "adverse", "aesthetic", "affable", "aggrandize", "alacrity",
    "alleviate", "altruistic", "ambiguous", "ambivalent", "ameliorate", "amenable",
    "amiable", "amorphous", "anachronistic", "analogous", "anarchy", "anomaly",
    "antagonize", "antecedent", "antipathy", "apathy", "appease", "arbitrary",
    "arcane", "archaic", "ardent", "arduous", "articulate", "ascertain",
    "ascetic", "assuage", "astute", "audacious", "austere", "avarice",
    "banal", "bellicose", "belligerent", "benevolent", "benign", "blatant",
    "bolster", "bombastic", "brusque", "burgeon", "cacophony", "camaraderie",
    "candid", "capricious", "castigate", "catalyst", "caustic", "censure",
    "chastise", "chicanery", "circumspect", "clandestine", "coalesce", "cogent",
    "coherent", "collaborate", "commemorate", "commensurate", "compelling", "complacent",
    "complement", "comprehensive", "comprise", "concede", "conciliatory", "congenial",
    "conscientious", "consensus", "conspicuous", "contemplate", "contentious", "conventional",
    "copious", "corroborate", "cosmopolitan", "covet", "credible", "criterion"
]


def generate_words_by_difficulty(difficulty_level, count=20, exclude_words=None):
    """
    Generate a list of words for the specified difficulty level
    CRITICAL: All words are filtered through kid-friendly content filter
    
    Args:
        difficulty_level (str): One of 'grade_1_2', 'grade_3_4', 'grade_5_6', 
                               'grade_7_8', 'middle_school', 'high_school'
        count (int): Number of words to generate
        exclude_words (list): Words to exclude from selection
    
    Returns:
        list: List of filtered, kid-friendly word strings
    """
    word_pools = {
        'grade_1_2': GRADE_1_2_WORDS,
        'grade_3_4': GRADE_3_4_WORDS,
        'grade_5_6': GRADE_5_6_WORDS,
        'grade_7_8': MIDDLE_SCHOOL_WORDS,  # Map grade_7_8 to middle school
        'middle_school': MIDDLE_SCHOOL_WORDS,
        'high_school': HIGH_SCHOOL_WORDS
    }
    
    if difficulty_level not in word_pools:
        difficulty_level = 'grade_3_4'  # Default fallback
    
    word_pool = word_pools[difficulty_level].copy()
    
    # CRITICAL: Filter out inappropriate words
    filtered_pool = []
    blocked_count = 0
    for word in word_pool:
        is_safe, reason = _is_word_safe(word)
        if is_safe:
            filtered_pool.append(word)
        else:
            blocked_count += 1
            print(f"🛡️ Word generator blocked inappropriate word: '{word}' - {reason}")
    
    if blocked_count > 0:
        print(f"⚠️ Word generator filtered out {blocked_count} inappropriate word(s) from {difficulty_level}")
    
    word_pool = filtered_pool
    
    # Remove excluded words
    if exclude_words:
        word_pool = [w for w in word_pool if w.lower() not in [e.lower() for e in exclude_words]]
    
    # If not enough words, return what we have
    if len(word_pool) <= count:
        random.shuffle(word_pool)
        return word_pool
    
    # Randomly select words
    return random.sample(word_pool, count)


def get_difficulty_multiplier(difficulty_level):
    """Get point multiplier for difficulty level"""
    multipliers = {
        'grade_1_2': 1.0,
        'grade_3_4': 1.5,
        'grade_5_6': 2.0,
        'grade_7_8': 2.5,  # Map grade_7_8 to middle school multiplier
        'middle_school': 2.5,
        'high_school': 3.0
    }
    return multipliers.get(difficulty_level, 1.5)


def get_difficulty_name(difficulty_level):
    """Get human-readable difficulty name"""
    names = {
        'grade_1_2': 'Grade 1-2 (Beginner)',
        'grade_3_4': 'Grade 3-4 (Elementary)',
        'grade_5_6': 'Grade 5-6 (Intermediate)',
        'grade_7_8': 'Grade 7-8 (Middle School)',  # Add grade_7_8 mapping
        'middle_school': 'Middle School',
        'high_school': 'High School (Advanced)'
    }
    return names.get(difficulty_level, 'Unknown')


def generate_mixed_words(count=20, exclude_words=None):
    """
    Generate a mixed difficulty word list for extra challenge
    CRITICAL: All words are filtered through kid-friendly content filter
    
    Args:
        count (int): Number of words to generate
        exclude_words (list): Words to exclude from selection
    
    Returns:
        list: List of filtered, kid-friendly word strings from various difficulty levels
    """
    all_words = (
        GRADE_1_2_WORDS + 
        GRADE_3_4_WORDS + 
        GRADE_5_6_WORDS + 
        MIDDLE_SCHOOL_WORDS + 
        HIGH_SCHOOL_WORDS
    )
    
    # CRITICAL: Filter out inappropriate words
    filtered_words = []
    blocked_count = 0
    for word in all_words:
        is_safe, reason = _is_word_safe(word)
        if is_safe:
            filtered_words.append(word)
        else:
            blocked_count += 1
            print(f"🛡️ Mixed word generator blocked inappropriate word: '{word}' - {reason}")
    
    if blocked_count > 0:
        print(f"⚠️ Mixed word generator filtered out {blocked_count} inappropriate word(s)")
    
    all_words = filtered_words
    
    if exclude_words:
        all_words = [w for w in all_words if w.lower() not in [e.lower() for e in exclude_words]]
    
    return random.sample(all_words, min(count, len(all_words)))


# Test function
if __name__ == '__main__':
    print("🐝 BeeSmart Word Generator Test\n")
    
    for level in ['grade_1_2', 'grade_3_4', 'grade_5_6', 'middle_school', 'high_school']:
        words = generate_words_by_difficulty(level, count=5)
        print(f"{get_difficulty_name(level)} (×{get_difficulty_multiplier(level)}):")
        print(f"  {', '.join(words)}\n")
    
    print("Mixed Challenge:")
    mixed = generate_mixed_words(count=10)
    print(f"  {', '.join(mixed)}")
