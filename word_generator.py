"""
BeeSmart Spelling App - Word Generation System
Auto-generates spelling words by difficulty level for speed rounds
CRITICAL: All generated words MUST pass kid-friendly filter
"""

import random


def _is_word_safe(word):
    """
    Check if word is kid-friendly.
    Delegates to the authoritative is_kid_friendly() in AjaSpellBApp.
    Falls back to a minimal inline check if the import fails (e.g. circular import at startup).
    """
    word_lower = word.lower().strip()

    # Fast-path: always block "sex" substring
    if "sex" in word_lower:
        return False, f"Word '{word}' contains restricted substring 'sex'"

    try:
        from AjaSpellBApp import is_kid_friendly as _ikf
        return _ikf(word)
    except Exception:
        pass

    # Minimal fallback blocklist (only used if import fails)
    _FALLBACK_BLOCKED = {
        "kill", "murder", "suicide", "rape", "porn", "fuck", "shit", "damn",
        "hell", "crap", "bitch", "cock", "dick", "cunt", "ass", "slut", "whore",
        "cocaine", "heroin", "meth", "weed", "drunk", "alcohol", "nazi",
        "nigger", "nigga", "faggot", "retard",
    }
    if word_lower in _FALLBACK_BLOCKED:
        return False, f"Word '{word}' is not appropriate for children"
    for bad in _FALLBACK_BLOCKED:
        if len(bad) > 4 and bad in word_lower:
            return False, f"Word '{word}' contains inappropriate content"
    return True, "OK"


# ── Tier 1: Kindergarten ─────────────────────────────────────────────────────
# Dolch Pre-K & Kindergarten sight words + simple CVC words (2-3 letters)
GRADE_K_WORDS = [
    "an", "at", "be", "by", "do", "go", "he", "if", "in", "is", "it",
    "me", "my", "no", "of", "on", "or", "so", "to", "up", "us", "we",
    "am", "are", "as", "big", "box", "boy", "but", "can", "cat", "cow",
    "cup", "dad", "day", "did", "dig", "dog", "dot", "egg", "end", "far",
    "fat", "few", "fig", "fit", "fly", "for", "fox", "fun", "get", "got",
    "had", "has", "hat", "hen", "her", "him", "his", "hit", "hop", "hot",
    "how", "hug", "hut", "jam", "jar", "jet", "job", "jog", "joy", "jump",
    "lap", "leg", "let", "lid", "lip", "log", "lot", "mad", "man", "map",
    "mat", "mix", "mob", "mom", "mop", "mud", "mug", "nap", "net", "new",
    "not", "now", "nut", "oak", "odd", "off", "old", "one", "our", "out",
    "own", "pan", "pat", "paw", "pay", "peg", "pen", "pet", "pig", "pin",
    "pit", "pod", "pot", "pub", "pun", "pup", "put", "ran", "rat", "red",
    "rid", "rim", "rip", "rob", "rod", "rot", "row", "rub", "rug", "run",
    "sad", "sat", "saw", "say", "set", "sit", "six", "ski", "sky", "sob",
    "sub", "sum", "sun", "tab", "tan", "tap", "tar", "ten", "the", "tip",
    "top", "toy", "try", "tub", "two", "van", "vat", "vet", "vow", "wag",
    "war", "was", "wax", "way", "web", "wet", "who", "why", "win", "wit",
    "wok", "wot", "yes", "yet", "yew", "you", "zap", "zip", "zoo",
]

# ── Tier 2: Grades 1-2 ───────────────────────────────────────────────────────
# Fry words 101-300 + Dolch Grade 1-2 + common 4-5 letter phonetic words
GRADE_1_2_WORDS = [
    "able", "also", "area", "away", "back", "ball", "band", "barn", "base",
    "bath", "bear", "beat", "been", "bell", "best", "bill", "bird", "bite",
    "blue", "boat", "body", "bold", "bone", "book", "born", "both", "bull",
    "burn", "busy", "call", "calm", "came", "camp", "card", "care", "cart",
    "case", "cash", "cast", "cave", "chef", "chin", "chip", "city", "clam",
    "clap", "clay", "clip", "club", "clue", "coal", "coat", "code", "coin",
    "cold", "come", "cook", "cool", "copy", "corn", "cost", "cozy", "crab",
    "crew", "crop", "crow", "curb", "cure", "cute", "dale", "dame", "dare",
    "dark", "date", "dawn", "dead", "deaf", "deal", "dear", "deck", "deed",
    "deem", "deep", "deer", "dent", "desk", "dew", "dice", "diet", "dime",
    "dirt", "dish", "disk", "dive", "dock", "does", "doll", "done", "door",
    "dose", "down", "drag", "draw", "drew", "drip", "drop", "drum", "dryer",
    "duck", "dull", "dump", "dune", "dust", "each", "earn", "east", "easy",
    "edge", "else", "even", "ever", "evil", "exam", "face", "fact", "fail",
    "fair", "fall", "fame", "farm", "fast", "fate", "feed", "feel", "feet",
    "fell", "felt", "fern", "fill", "film", "find", "fine", "fire", "fish",
    "fist", "five", "flag", "flat", "flaw", "fled", "flew", "flip", "flock",
    "flow", "foam", "fold", "folk", "fond", "food", "fool", "foot", "ford",
    "fore", "fork", "form", "fort", "four", "free", "from", "full", "fume",
    "fuse", "gale", "game", "gang", "gave", "gaze", "gear", "glow", "glue",
    "goat", "gold", "golf", "good", "grab", "gram", "gray", "grid", "grin",
    "grip", "grit", "grow", "gulf", "gust", "guts", "guys", "hack", "hail",
    "half", "hall", "halt", "hand", "hang", "hard", "hare", "harm", "harp",
    "hate", "have", "hawk", "heal", "heap", "hear", "heat", "heel", "held",
    "help", "here", "hide", "high", "hike", "hill", "hint", "hire", "hold",
    "hole", "home", "hood", "hook", "hope", "horn", "hose", "host", "huge",
    "hull", "hunt", "hurt", "inch", "into", "iron", "isle", "jail", "jerk",
    "join", "joke", "just", "keen", "keep", "kick", "kind", "king", "kite",
    "knew", "knob", "knot", "know", "lace", "laid", "lake", "lamb", "lamp",
    "land", "lane", "last", "late", "lawn", "lazy", "lead", "leaf", "lean",
    "left", "lend", "less", "lift", "like", "lime", "line", "link", "lion",
    "list", "live", "load", "loan", "lock", "loft", "lone", "long", "look",
    "loop", "lord", "lore", "lose", "loss", "loud", "love", "luck", "lump",
    "lung", "made", "mail", "main", "make", "male", "mall", "mane", "many",
    "mark", "mars", "mast", "math", "maze", "meal", "mean", "meat", "meet",
    "melt", "menu", "mesh", "mild", "mile", "milk", "mill", "mind", "mine",
    "mint", "mist", "mode", "mole", "more", "most", "move", "much", "mule",
    "must", "myth", "nail", "name", "near", "neck", "need", "next", "nice",
    "nine",    "node", "none", "noon", "norm", "nose", "note", "noun",
    "null", "obey", "once", "only", "open", "oral", "oval", "oven", "over",
    "owed", "pack", "paid", "pain", "pair", "pale", "park", "part", "pass",
    "past", "path", "peak", "peel", "peer", "pick", "pile", "pine", "pink",
    "pipe", "plan", "play", "plot", "plow", "plug", "plum", "plus", "poem",
    "poll", "polo", "pond", "pool", "poor", "pore", "port", "pose", "post",
    "pour", "pray", "prey", "prop", "pull", "pure", "push", "quiz", "race",
    "rack", "rage", "raid", "rail", "rain", "rake", "ramp", "rang", "rank",
    "rare", "rate", "read", "real", "reap", "reel", "reef", "rein", "rely",
    "rent", "rest", "rice", "rich", "ride", "ring", "rink", "riot", "rise",
    "risk", "road", "roam", "roar", "robe", "rock", "role", "roll", "roof",
    "room", "root", "rope", "rose", "rude", "rule", "rush", "rust", "safe",
    "sage", "sail", "sake", "sale", "salt", "same", "sand", "sang", "sank",
    "sash", "save", "scan", "scar", "seal", "seam", "seat", "seed", "seek",
    "seem", "seep", "self", "sell", "send", "sewn", "shed", "shin", "ship",
    "shoe", "shop", "shot", "show", "shut", "sick", "side", "sigh", "sign",
    "silk", "sill", "silo", "sing", "sink", "site", "size", "skin", "slab",
    "slam", "slap", "sled", "slim", "slip", "slot", "slow", "slug", "snag",
    "snap", "snip", "snow", "soak", "soap", "soar", "sock", "soil", "sold",
    "sole", "some", "song", "soot", "sore", "sort", "soul", "soup", "sour",
    "span", "spar", "spec", "sped", "spin", "spit", "spot", "spun", "star",
    "stay", "stem", "step", "stew", "stir", "stop", "stub", "stun", "such",
    "suit", "sung", "sunk", "sure", "surf", "swam", "swan", "swap", "swat",
    "sway", "swim", "swum", "tack", "tail", "tale", "tall", "tame", "tank",
    "tape", "task", "teal", "team", "tear", "teem", "tell", "term", "text",
    "than", "that", "them", "then", "they", "thin", "this", "thus", "tick",
    "tide", "tied", "till", "time", "tiny", "tire", "toad", "told", "toll",
    "tome", "tone", "tong", "took", "tool", "torn", "toss", "town", "trap",
    "tree", "trim", "trip", "true", "tube", "tuck", "tune", "turf", "turn",
    "tusk", "type", "ugly", "upon", "urge", "used", "vale", "vary", "vast",
    "veil", "vein", "very", "vice", "view", "vine", "vise", "vote", "wade",
    "wake", "walk", "wall", "want", "warm", "warn", "warp", "wash", "wave",
    "weak", "weal", "wean", "weed", "week", "well", "went", "were", "west",
    "what", "when", "whim", "whip", "wide", "wild", "will", "wimp", "wind",
    "wine", "wing", "wink", "wire", "wise", "wish", "with", "woke", "wolf",
    "wood", "wool", "word", "wore", "work", "worm", "wrap", "wren", "writ",
    "yard", "year", "yell", "your", "zone",
]

# ── Tier 3: Grades 3-4 ───────────────────────────────────────────────────────
# Fry words 301-600 + Common Core Grade 3-4 + consonant blends/digraphs
GRADE_3_4_WORDS = [
    "about", "above", "ached", "acres", "acted", "added", "admit",
    "adopt", "adult", "after", "again", "agent", "agree", "ahead", "aided",
    "aimed", "aired", "alarm", "album", "alert", "alike", "align", "alive",
    "alley", "allow", "alone", "along", "aloud", "alpha", "alter", "angel",
    "anger", "angle", "angry", "anime", "annex", "apply", "arena", "argue",
    "arise", "array", "arrow", "aside", "asked", "atlas", "atoms", "attic",
    "audio", "audit", "avoid", "awake", "aware", "awful", "badge", "badly",
    "baker", "bases", "basic", "basin", "basis", "batch", "beach", "began",
    "begin", "being", "below", "bench", "berry", "bible", "bikes", "black",
    "blade", "blame", "bland", "blank", "blast", "blaze", "bleed", "blend",
    "bless", "blind", "blink", "block", "blood", "bloom", "blown", "blown",
    "board", "bonus", "bored", "bound", "brace", "brain", "brake", "brand",
    "brave", "bread", "break", "breed", "brick", "bride", "brief", "brine",
    "bring", "brisk", "broad", "broke", "brook", "brown", "brush", "buddy",
    "build", "built", "bunch", "burst", "buyer", "cabin", "cable", "candy",
    "carry", "catch", "cause", "chain", "chair", "chalk", "chaos", "cheap",
    "check", "cheek", "cheer", "chess", "chest", "chick", "chief", "child",
    "china", "choir", "chord", "chose", "civic", "civil", "claim", "clash",
    "class", "clean", "clear", "clerk", "click", "cliff", "cling", "clock",
    "clone", "close", "cloth", "cloud", "clown", "coach", "coast", "cocoa",
    "color", "comic", "coral", "could", "count", "court", "cover", "craft",
    "crane", "crash", "crazy", "cream", "creek", "crime", "cross", "crowd",
    "crown", "crush", "crust", "curly", "cycle", "daily", "dance", "dated",
    "delay", "depot", "depth", "derby", "devil", "digit", "diner", "dirty",
    "disco", "ditch", "dizzy", "dodge", "domed", "donor", "doubt", "dough",
    "draft", "drain", "drama", "drank", "drape", "drawn", "dread", "dream",
    "dress", "drift", "drink", "drive", "drone", "drove", "drown", "dryer",
    "dully", "dunce", "dwarf", "dwell", "earth", "eight", "elect", "email",
    "ember", "empty", "enact", "enter", "entry", "equal", "error", "essay",
    "event", "every", "exact", "exist", "extra", "fable", "faced", "faint",
    "faith", "fancy", "fault", "feast", "fence", "fever", "field", "fifth",
    "fifty", "fight", "final", "first", "fixed", "flame", "flare", "flash",
    "fleet", "flesh", "float", "flood", "floor", "flour", "flute", "focus",
    "force", "forge", "found", "frame", "frank", "fraud", "fresh", "front",
    "frost", "fruit", "fully", "funny", "giant", "given", "gland", "glare",
    "glass", "gleam", "globe", "gloom", "glove", "grace", "grade", "grain",
    "grand", "grant", "graph", "grasp", "grave", "great", "greed", "green",
    "greet", "grief", "grind", "groan", "group", "grove", "guard", "guide",
    "guild", "guise", "gusto", "happy", "harsh", "heart", "hedge", "hello",
    "hence", "herbs", "hinge", "hippo", "hoist", "honor", "horse", "hotel",
    "house", "human", "humid", "humor", "hurry", "ideal", "image", "imply",
    "index", "indie", "infer", "inner", "issue", "ivory", "judge", "juice",
    "juicy", "keen", "knack", "kneel", "knife", "knock", "known", "labor",
    "large", "laser", "later", "laugh", "layer", "learn", "lease", "leave",
    "level", "light", "limit", "lined", "liner", "liver", "local", "lodge",
    "logic", "loose", "lower", "lucky", "lunch", "lying", "magic", "major",
    "maple", "march", "match", "mayor", "media", "mercy", "merit", "metal",
    "meter", "midst", "might", "minor", "minus", "model", "money", "month",
    "moral", "motor", "mount", "mouse", "mouth", "moved", "movie", "muddy",
    "music", "naive", "nerve", "never", "night", "noble", "noise", "north",
    "noted", "novel", "nurse", "nylon", "ocean", "offer", "often", "olive",
    "onset", "opera", "orbit", "order", "organ", "other", "outer", "oxide",
    "ozone", "paint", "panel", "panic", "paper", "patch", "pause", "peace",
    "pearl", "pedal", "penny", "perch", "phase", "phone", "photo", "piano",
    "pilot", "pixel", "pizza", "place", "plain", "plane", "plant", "plate",
    "plaza", "plead", "pluck", "plunge", "point", "polar", "porch", "pound",
    "power", "press", "price", "pride", "prime", "print", "prize", "probe",
    "proof", "prose", "proud", "prove", "prowl", "puppy", "queen", "query",
    "quest", "queue", "quick", "quiet", "quota", "quote", "radix", "raise",
    "rally", "ranch", "range", "rapid", "reach", "realm", "rebel", "refer",
    "reign", "relax", "repay", "reply", "rider", "ridge", "right", "rigid",
    "risky", "rival", "river", "robin", "robot", "rocky", "rouge", "rough",
    "round", "route", "rover", "royal", "rugby", "ruler", "rural", "sadly",
    "saint", "salad", "sauce", "scale", "scene", "scent", "scope", "score",
    "scout", "scrap", "screw", "sedan", "serve", "seven", "sever", "shade",
    "shake", "shall", "shame", "shape", "share", "shark", "sharp", "shave",
    "sheep", "sheer", "shelf", "shell", "shift", "shine", "shirt", "shock",
    "short", "shout", "shrug", "sight", "since", "sixth", "sixty", "sized",
    "skill", "skull", "skunk", "slate", "slave", "sleep", "sleet", "slice",
    "slide", "slope", "smoke", "snail", "snake", "solar", "solve", "sorry",
    "south", "space", "spare", "spark", "spawn", "speak", "spear", "speed",
    "spend", "spent", "spice", "spine", "spoke", "spoon", "spray", "squad",
    "squat", "squid", "stack", "staff", "stage", "stain", "stake", "stale",
    "stall", "stamp", "stand", "stark", "start", "state", "steam", "steel",
    "steep", "steer", "stick", "stiff", "still", "sting", "stock", "stone",
    "stood", "store", "storm", "story", "stove", "strap", "straw", "stray",
    "strip", "stuck", "study", "stump", "style", "sugar", "suite", "sunny",
    "super", "surge", "swear", "sweat", "sweep", "sweet", "swept", "swift",
    "sword", "sworn", "table", "taste", "taxed", "teach", "teeth", "their",
    "theme", "there", "these", "thick", "thing", "think", "third", "thorn",
    "those", "three", "threw", "throw", "thumb", "tiger", "tight", "timer",
    "tired", "title", "today", "token", "torch", "total", "touch", "tough",
    "tower", "track", "trade", "trail", "train", "trait", "tramp", "trash",
    "tray", "trend", "trial", "tribe", "trick", "tried", "troop", "trout",
    "truck", "truly", "trump", "trunk", "trust", "truth", "tuner", "twist",
    "ulcer", "uncut", "under", "unfit", "union", "unite", "unity", "until",
    "upper", "upset", "urban", "usage", "usher", "usual", "utter", "vague",
    "valid", "value", "valve", "vapor", "vault", "verse", "video", "vigil",
    "vigor", "villa", "viral", "virus", "visit", "visor", "vista", "vital",
    "vivid", "vocal", "voice", "voter", "vowel", "vying", "wagon", "waste",
    "watch", "water", "weary", "weave", "wedge", "weigh", "whale", "wheat",
    "wheel", "where", "which", "while", "white", "whole", "whose", "wider",
    "width", "witch", "woman", "women", "world", "worry", "worse", "worst",
    "worth", "would", "wound", "wrath", "write", "wrote", "yacht", "yield",
    "young", "youth", "zebra",
]

# ── Tier 4: Grades 5-6 ───────────────────────────────────────────────────────
# Common Core Grade 5-6 academic vocab + Fry 601-1000 multisyllabic
GRADE_5_6_WORDS = [
    "abolish", "absence", "absolve", "abstain", "achieve", "acquire",
    "address", "advance", "adviser", "ailment", "alarmed",
    "allergy", "altered", "ancient", "anxiety", "anxious", "approve",
    "arrange", "attract", "average", "awkward", "balance", "bandage",
    "barrier", "bearing", "because", "becomes", "benefit", "between",
    "biology", "blossom", "booklet", "borough", "boycott", "breathe",
    "briefly", "cabinet", "caliber", "capable", "capital", "captain",
    "capture", "catalog", "chapter", "charity", "circuit", "citizen",
    "climate", "cluster", "coastal", "college", "combine", "command",
    "compare", "compass", "compete", "concept", "concern", "conduct",
    "connect", "consist", "consume", "contact", "content", "context",
    "control", "convert", "correct", "costume", "counsel", "country",
    "courage", "covered", "creates", "culture", "curious", "current",
    "declare", "default", "defense", "defined", "deposit", "destiny",
    "destroy", "develop", "diagram", "digital", "dilemma", "discuss",
    "disease", "dismiss", "display", "dispute", "disturb", "divided",
    "dormant", "dynamic", "ecology", "edition", "element", "engaged",
    "enhance", "ensures", "examine", "example", "exhaust", "exhibit",
    "explore", "express", "extreme", "feature", "fiction", "formula",
    "fortune", "freedom", "general", "genuine", "graphic", "gravity",
    "habitat", "harvest", "healthy", "hearing", "history", "honored",
    "horizon", "hostile", "however", "imagine", "immense", "improve",
    "include", "involve", "isolate", "journal", "justice", "kitchen",
    "knowing", "knowing", "knowing", "lacking", "leading", "lecture",
    "linking", "literal", "located", "machine", "managed", "meaning",
    "measure", "mention", "message", "methods", "mission", "mixture",
    "monarch", "morning", "natural", "network", "neutral", "notable",
    "nucleus", "observe", "obvious", "opinion", "outcome", "outline",
    "overall", "partial", "pattern", "percent", "perfect", "perform",
    "perhaps", "permits", "persist", "picture", "pioneer", "planner",
    "portion", "possess", "pottery", "precise", "prevent", "primary",
    "process", "produce", "program", "project", "promote", "protect",
    "provide", "purpose", "quality", "rapidly", "reached", "realize",
    "receive", "reflect", "regions", "release", "require", "resolve",
    "respect", "respond", "restore", "results", "revenue", "segment",
    "sensory", "serious", "service", "similar", "society", "soldier",
    "species", "subject", "succeed", "suggest", "support", "survive",
    "sustain", "tension", "thermal", "through", "tonight", "trading",
    "trouble", "typical", "uncover", "unknown", "unusual", "upgrade",
    "venture", "version", "village", "visible", "whether", "witness",
]

# ── Tier 5: Grades 7-8 ───────────────────────────────────────────────────────
# Common Core Grade 7-8 + Tier 2 academic vocabulary (Beck/McKeon/Kucan)
GRADE_7_8_WORDS = [
    "absolute", "abstract", "accurate", "adequate", "adjacent", "advocate",
    "allocate", "ambition", "analysis", "annotate", "apparent", "appetite",
    "approach", "aptitude", "argument", "assembly", "audience", "backbone",
    "balanced", "behavior", "boundary", "bulletin", "campaign", "capacity",
    "category", "caution", "coherent", "collapse", "communal", "complete",
    "compound", "comprise", "conflict", "congress", "constant", "consumer",
    "contrast", "convince", "creative", "critique", "cultural", "deadline",
    "decrease", "delegate", "depicted", "describe", "dialogue", "discover",
    "document", "dominant", "dramatic", "duration", "economic", "editions",
    "elevated", "eloquent", "emphasis", "enduring", "enormous", "evaluate",
    "evidence", "exchange", "excluded", "explicit", "exposure", "extended",
    "familiar", "feasible", "feedback", "flexible", "focusing", "forecast",
    "fraction", "frequent", "function", "generate", "historic", "homeless",
    "identity", "ideology", "impartial", "implicit", "incident", "indicate",
    "indirect", "inferred", "informed", "initiate", "innocent", "innovate",
    "instance", "integral", "interact", "invasive", "investor", "involved",
    "judgment", "landmark", "language", "latitude", "leverage", "lifetime",
    "literacy", "maintain", "marginal", "maximize", "minimize", "momentum",
    "multiple", "negative", "observer", "obstacle", "occupied", "offering",
    "opposite", "organize", "outbreak", "overlook", "override", "paradigm",
    "parallel", "partisan", "peculiar", "persuade", "physical", "platform",
    "positive", "practice", "premise", "preserve", "priority", "probable",
    "profound", "progress", "prohibit", "prolific", "property", "proposal",
    "province", "rational", "reaction", "reckless", "recovery", "relative",
    "relevant", "reliable", "reluctant", "renewal", "restrict", "rhetoric",
    "rigorous", "schedule", "security", "sequence", "shifting", "signify",
    "situated", "skeletal", "spectrum", "standard", "strategy", "strength",
    "suitable", "superior", "suppress", "symbolic", "systemic", "tangible",
    "temporal", "tendency", "terminal", "transfer", "ultimate", "undermine",
    "validate", "variable", "vertical", "vibrant", "volatile", "voluntary",
]

# ── Tier 6: Grades 9-10 ──────────────────────────────────────────────────────
# Academic Word List (AWL) Sublists 1-5 + Common Core 9-10
GRADE_9_10_WORDS = [
    "abridged", "absurdity", "accentuate", "accessible", "accomplish",
    "accordance", "accumulate", "accusation", "adaptation", "additional",
    "administer", "adolescent", "aesthetic", "affiliation", "aggravate",
    "allegiance", "alliterate", "alteration", "ambiguity", "ameliorate",
    "analytical", "annotating", "antagonist", "antiquated", "applicable",
    "appreciable", "archetypal", "assertion", "assimulate", "assumption",
    "attributed", "authentic", "bibliographic", "calculated", "calibrate",
    "categorical", "chronology", "circumstance", "clarifying", "collaborate",
    "commentary", "competence", "conceptual", "connotation", "consistent",
    "consortium", "constitute", "conveyance", "correlation", "credibility",
    "culminating", "deliberate", "democratic", "dependable", "derivative",
    "designated", "determined", "differentiate", "discrepancy", "disparity",
    "distinctive", "divergence", "documented", "ecological", "economical",
    "elaborating", "empowerment", "encouraged", "enterprise", "entitlement",
    "equivalence", "established", "estimation", "evaluation", "eventually",
    "exceptional", "exclusively", "exemplified", "exhaustive", "exposition",
    "extensively", "facilitate", "factitious", "formulated", "foundation",
    "functional", "fundamental", "generalize", "geographical", "governance",
    "hierarchical", "highlighted", "hypothesis", "identified", "illuminate",
    "illustrate", "implication", "incentive", "incidentally", "incorporated",
    "independent", "indigenous", "inevitable", "infallible", "influenced",
    "inherently", "initiation", "innovative", "inspection", "integration",
    "intentional", "interdependent", "intricate", "invaluable", "investigate",
    "justification", "legislative", "likelihood", "marginalize", "methodology",
    "meticulous", "modification", "nonetheless", "obligations", "observable",
    "occupation", "occurrence", "oppression", "optimistic", "oscillating",
    "parameters", "participation", "perception", "periodical", "persistence",
    "perspective", "pertaining", "phenomenal", "plagiarism", "plausible",
    "precedence", "presumably", "proficiency", "propaganda", "prosecution",
    "provisional", "rationalize", "reciprocal", "recognition", "redundancy",
    "reformation", "refutation", "reinforce", "relevance", "repetition",
    "reproduction", "resilience", "resolution", "responsible", "revolutionary",
    "sophisticated", "specifically", "speculation", "standardize", "stereotype",
    "subordinate", "substantial", "sufficiency", "summarizing", "supplement",
    "sustainable", "synthesize", "tentatively", "theoretical", "traditional",
    "transforming", "transparent", "typicality", "ubiquitous", "uncertainty",
    "undermining", "universally", "utilization", "verification", "vulnerability",
]

# ── Tier 7: Grades 11-12 ─────────────────────────────────────────────────────
# AWL Sublists 6-10 + AP Language & Composition vocabulary
GRADE_11_12_WORDS = [
    "abdication", "abhorrence", "abnormality", "abomination", "abstraction",
    "acrimonious", "admonition", "affectation", "aggrandize", "alacrity",
    "allegory", "ameliorate", "anachronism", "anecdotal", "anomalous",
    "antagonism", "anthropological", "antipathy", "aphorism", "apprehensive",
    "archaic", "arduous", "articulate", "ascendancy", "aspiration",
    "assiduous", "astute", "atrocity", "audacity", "authoritarian",
    "autonomy", "aversion", "banality", "benevolence", "bias",
    "blatant", "brevity", "cacophony", "candor", "capricious",
    "catharsis", "caustic", "circumspect", "clandestine", "coalesce",
    "coercion", "coherence", "complacent", "complicity", "condescending",
    "conducive", "connotative", "contentious", "contrite", "conviction",
    "copious", "corroborate", "cosmopolitan", "culmination", "cynical",
    "deferential", "demagogue", "deprecate", "desolation", "determinism",
    "didactic", "diffidence", "digression", "diligence", "discern",
    "disdain", "dissonance", "dogmatic", "ebullient", "egregious",
    "eminent", "empirical", "enthralled", "ephemeral", "equivocal",
    "erudition", "esoteric", "euphemism", "exacerbate", "expedient",
    "exuberant", "fallacious", "fanaticism", "fatalistic", "fervent",
    "flamboyant", "fortuitous", "grandiloquent", "hegemony", "hubris",
    "hypocritical", "idiosyncratic", "ignominious", "imperious", "impetuous",
    "implacable", "incisive", "incongruous", "indignation", "indolent",
    "indulgent", "infallible", "ingenious", "inimical", "insidious",
    "intransigent", "irrefutable", "juxtapose", "laconic", "loquacious",
    "lucid", "magnanimous", "malevolent", "malleable", "mendacious",
    "mercurial", "meticulous", "misanthropic", "mitigate", "nihilism",
    "nonchalant", "obfuscate", "oblique", "obstinate", "ominous",
    "omnipotent", "opportunist", "ostracize", "paternalistic", "pedantic",
    "perfidious", "perilous", "philanthropic", "polemical", "pragmatic",
    "presuppose", "prevaricate", "prodigal", "profligate", "proliferate",
    "propitious", "querulous", "recalcitrant", "reclusive", "reprehensible",
    "resilient", "reticent", "sanctimonious", "sardonic", "scrupulous",
    "serendipity", "solipsism", "specious", "superfluous", "surreptitious",
    "sycophant", "tenacious", "trepidation", "truculent", "tyrannical",
    "unequivocal", "vacuous", "vehement", "venerate", "verisimilitude",
    "vindictive", "vitriolic", "whimsical", "zealous",
]

# ── Tier 8: SAT / College Prep ───────────────────────────────────────────────
# Official SAT high-frequency words + GRE overlap (public domain research lists)
SAT_WORDS = [
    "abjure", "abrogate", "abscond", "abstemious", "accolade", "acerbic",
    "acquiesce", "acrimony", "adulation", "adumbrate", "aesthetic", "affable",
    "aggrandize", "alacrity", "alleviate", "altruism", "ambivalence", "ameliorate",
    "amenable", "amorphous", "anachronistic", "analogous", "anarchy", "anomaly",
    "antagonize", "antipathy", "appease", "apposite", "approbation", "arbitrary",
    "archaic", "ardent", "arduous", "ascetic", "assiduous", "assuage",
    "astute", "atrophy", "audacious", "austere", "avarice", "axiomatic",
    "bellicose", "belligerent", "belie", "beguile", "beneficent", "bombastic",
    "boorish", "burgeon", "cacophony", "capricious", "castigate", "catalyst",
    "caustic", "censure", "chicanery", "circumlocution", "circumspect", "clandestine",
    "coalesce", "cogent", "commensurate", "compunction", "conciliatory", "condone",
    "confound", "congenial", "conjecture", "conscientious", "conspicuous", "contemptuous",
    "contentious", "contrite", "convoluted", "copious", "corroborate", "credulous",
    "culpable", "cupidity", "cursory", "dauntless", "debacle", "decorum",
    "deferential", "demagogue", "denounce", "deprecate", "deride", "desiccate",
    "desultory", "deterrent", "devious", "didactic", "diffidence", "dilettante",
    "dispassionate", "dissemble", "dissimulate", "dogmatic", "dubious", "ebullient",
    "eccentric", "effusive", "egregious", "eloquence", "embroil", "empirical",
    "enervate", "enigmatic", "ephemeral", "equanimity", "equivocate", "erudite",
    "esoteric", "euphemism", "exacerbate", "excoriate", "exemplary", "exhaustive",
    "expedient", "explicit", "expunge", "extol", "extraneous", "exuberant",
    "fallacious", "fatuous", "fervent", "flippant", "forbearance", "frugality",
    "garrulous", "gratuitous", "gregarious", "guile", "hackneyed", "harangue",
    "hegemony", "heresy", "hubris", "hyperbole", "ignominious", "immutable",
    "impartial", "impetuous", "implacable", "implicit", "inadvertent", "incisive",
    "incongruous", "incredulous", "indolent", "ineffable", "inimical", "insipid",
    "instigated", "intransigent", "inveterate", "irascible", "jettison", "judicious",
    "juxtapose", "laconic", "lethargic", "levity", "loquacious", "lucid",
    "magnanimous", "malevolent", "malleable", "mendacious", "mercurial", "misanthrope",
    "mitigate", "mollify", "munificent", "nefarious", "nonchalant", "obdurate",
    "obfuscate", "obsequious", "obstinate", "obtuse", "ominous", "onerous",
    "opaque", "opprobrium", "ostracize", "paternalistic", "pedantic", "penchant",
    "perfidious", "perfunctory", "perspicacious", "perturb", "phlegmatic", "placate",
    "platitude", "plausible", "polemic", "pragmatic", "precarious", "precipitate",
    "predilection", "presumptuous", "prevaricate", "probity", "proclivity", "prodigal",
    "profligate", "proliferate", "propitious", "provincial", "querulous", "quixotic",
    "rancor", "recalcitrant", "reclusive", "reconcile", "redolent", "remonstrate",
    "reprehensible", "repudiate", "reticent", "reverence", "rhetoric", "rigorous",
    "sanctimonious", "sardonic", "scrupulous", "serendipity", "skepticism", "solipsism",
    "soporific", "specious", "spurious", "stoicism", "stolid", "stringent",
    "subjugate", "superfluous", "surreptitious", "sycophant", "taciturn", "temperate",
    "tenacious", "terse", "timorous", "torpor", "tractable", "transient",
    "trepidation", "truculent", "tyrannical", "unequivocal", "vacuous", "vehement",
    "venerate", "verisimilitude", "vindictive", "vitiate", "vitriolic", "volatile",
    "voracious", "whimsical", "zealot", "zealous",
]


def generate_words_by_difficulty(difficulty_level, count=20, exclude_words=None):
    """
    Generate a list of words for the specified difficulty level.
    CRITICAL: All words are filtered through kid-friendly content filter.

    Args:
        difficulty_level (str): One of 'grade_k', 'grade_1_2', 'grade_3_4',
                               'grade_5_6', 'grade_7_8', 'grade_9_10',
                               'grade_11_12', 'sat'
                               Legacy keys 'middle_school' and 'high_school'
                               are still accepted for backwards compatibility.
        count (int): Number of words to generate
        exclude_words (list): Words to exclude from selection

    Returns:
        list: List of filtered, kid-friendly word strings
    """
    word_pools = {
        # Current 8-tier grade-aligned system
        'grade_k':       GRADE_K_WORDS,
        'grade_1_2':     GRADE_1_2_WORDS,
        'grade_3_4':     GRADE_3_4_WORDS,
        'grade_5_6':     GRADE_5_6_WORDS,
        'grade_7_8':     GRADE_7_8_WORDS,
        'grade_9_10':    GRADE_9_10_WORDS,
        'grade_11_12':   GRADE_11_12_WORDS,
        'sat':           SAT_WORDS,
        # Legacy keys (backwards compatibility)
        'middle_school': GRADE_7_8_WORDS,
        'high_school':   GRADE_11_12_WORDS,
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
        'grade_k':     0.5,
        'grade_1_2':   1.0,
        'grade_3_4':   1.5,
        'grade_5_6':   2.0,
        'grade_7_8':   2.5,
        'grade_9_10':  3.0,
        'grade_11_12': 3.5,
        'sat':         4.0,
        # Legacy keys
        'middle_school': 2.5,
        'high_school':   3.5,
    }
    return multipliers.get(difficulty_level, 1.5)


def get_difficulty_name(difficulty_level):
    """Get human-readable difficulty name"""
    names = {
        'grade_k':     'Kindergarten',
        'grade_1_2':   'Grades 1-2 (Early Reader)',
        'grade_3_4':   'Grades 3-4 (Elementary)',
        'grade_5_6':   'Grades 5-6 (Intermediate)',
        'grade_7_8':   'Grades 7-8 (Middle School)',
        'grade_9_10':  'Grades 9-10 (High School)',
        'grade_11_12': 'Grades 11-12 (Advanced)',
        'sat':         'SAT / College Prep',
        # Legacy keys
        'middle_school': 'Grades 7-8 (Middle School)',
        'high_school':   'Grades 11-12 (Advanced)',
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
        GRADE_K_WORDS +
        GRADE_1_2_WORDS +
        GRADE_3_4_WORDS +
        GRADE_5_6_WORDS +
        GRADE_7_8_WORDS +
        GRADE_9_10_WORDS +
        GRADE_11_12_WORDS +
        SAT_WORDS
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
    
    for level in ['grade_k', 'grade_1_2', 'grade_3_4', 'grade_5_6', 'grade_7_8', 'grade_9_10', 'grade_11_12', 'sat']:
        words = generate_words_by_difficulty(level, count=5)
        print(f"{get_difficulty_name(level)} (×{get_difficulty_multiplier(level)}):")
        print(f"  {', '.join(words)}\n")
    
    print("Mixed Challenge:")
    mixed = generate_mixed_words(count=10)
    print(f"  {', '.join(mixed)}")
