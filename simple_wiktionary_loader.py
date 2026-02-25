"""
Simple English Wiktionary Loader
Loads dictionary from simple-wiktionary.jsonl (Simple English Wiktionary dump)
"""
import json
import os


def _get_blocked_words() -> set:
    """Return the authoritative kid-safe blocklist from AjaSpellBApp.
    Falls back to a minimal inline set if the import is unavailable (e.g. during isolated testing).
    """
    try:
        from AjaSpellBApp import INAPPROPRIATE_WORDS as _IW
        return set(_IW)
    except Exception:
        pass
    return {
        "dam", "dams", "damn", "damned", "hell", "crap", "piss", "shit", "fuck", "bitch", "asshole", "bastard",
        "sex", "porn", "penis", "vagina", "rape", "molest", "abuse", "predator", "grooming",
        "kill", "killing", "killer", "murder", "murderer", "offing", "offed", "shoot", "shooting", "gun", "weapon",
        "suicide", "violent", "violence", "slay", "slaughter", "harm", "harming", "harmful",
        "nigger", "nigga", "faggot", "retard", "cock", "dick", "cunt", "slut", "whore",
        "cocaine", "heroin", "meth", "weed", "drunk", "alcohol", "nazi",
    }


def _contains_blocked_content(text: str) -> bool:
    s = (text or "").strip().lower()
    if not s:
        return False
    if "sex" in s:
        return True
    blocked = _get_blocked_words()
    tokens = []
    token = []
    for ch in s:
        if 'a' <= ch <= 'z':
            token.append(ch)
        elif token:
            tokens.append("".join(token))
            token = []
    if token:
        tokens.append("".join(token))
    for t in tokens:
        if t in blocked:
            return True
    for bad in blocked:
        if len(bad) > 4 and bad in s:
            return True
    return False

def load_simple_wiktionary(jsonl_path="data/simple-wiktionary.jsonl"):
    """
    Load Simple English Wiktionary from JSONL file
    Returns dict: {word_lower: {"definition": str, "example": str}}
    """
    if not os.path.exists(jsonl_path):
        print(f"⚠️ Simple Wiktionary file not found: {jsonl_path}")
        return {}
    
    print(f"📚 Loading Simple English Wiktionary from {jsonl_path}...")
    dictionary = {}
    loaded_count = 0
    skipped_count = 0
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                entry = json.loads(line.strip())
                
                # Extract word (normalize to lowercase)
                word = entry.get("word", "").strip().lower()
                if not word:
                    skipped_count += 1
                    continue

                if _contains_blocked_content(word):
                    skipped_count += 1
                    continue
                
                # Skip if already loaded (keep first definition)
                if word in dictionary:
                    continue
                
                # Extract part of speech
                pos = entry.get("pos", "")
                
                # Extract first sense (definition)
                senses = entry.get("senses", [])
                if not senses:
                    skipped_count += 1
                    continue
                
                first_sense = senses[0]
                glosses = first_sense.get("glosses", [])
                
                if not glosses:
                    skipped_count += 1
                    continue
                
                # Get definition (first gloss)
                definition = glosses[0].strip()
                if _contains_blocked_content(definition):
                    skipped_count += 1
                    continue
                
                # Get example sentence (from first sense examples)
                examples = first_sense.get("examples", [])
                example_sentence = ""
                
                if examples and isinstance(examples, list):
                    for ex in examples:
                        if isinstance(ex, dict):
                            ex_text = ex.get("text", "").strip()
                            if ex_text and word in ex_text.lower():
                                example_sentence = ex_text
                                break

                if _contains_blocked_content(example_sentence):
                    skipped_count += 1
                    continue
                
                # If no example with the word, create one
                if not example_sentence:
                    # Use definition to create example
                    if pos == "noun":
                        example_sentence = f"The {word} is important to understand."
                    elif pos == "verb":
                        example_sentence = f"I {word} every day."
                    elif pos == "adj":
                        example_sentence = f"This is very {word}."
                    else:
                        example_sentence = f"The word {word} is used often."
                
                # Store in dictionary
                dictionary[word] = {
                    "definition": definition,
                    "example": example_sentence,
                    "pos": pos
                }
                loaded_count += 1
                
                # Progress update every 10000 words
                if loaded_count % 10000 == 0:
                    print(f"   Loaded {loaded_count} words...")
                
            except json.JSONDecodeError:
                skipped_count += 1
                continue
            except Exception as e:
                skipped_count += 1
                continue
    
    print(f"✅ Loaded {loaded_count} words from Simple English Wiktionary")
    print(f"   Skipped {skipped_count} entries (no definition or duplicate)")
    return dictionary


def test_loader():
    """Test the loader and show some sample entries"""
    print("\n" + "="*60)
    print("Testing Simple English Wiktionary Loader")
    print("="*60)
    
    dictionary = load_simple_wiktionary()
    
    print(f"\n📊 Dictionary Statistics:")
    print(f"   Total words loaded: {len(dictionary)}")
    
    # Test some common words
    test_words = ["admire", "brisk", "curious", "simple", "word", "dictionary"]
    
    print(f"\n🔍 Testing lookups for: {', '.join(test_words)}")
    print("-"*60)
    
    for word in test_words:
        if word in dictionary:
            entry = dictionary[word]
            print(f"\n✅ {word.upper()}")
            print(f"   Definition: {entry['definition'][:100]}...")
            print(f"   Example: {entry['example'][:100]}...")
        else:
            print(f"\n❌ {word.upper()} - Not found")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_loader()
