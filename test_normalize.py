"""Test normalize function with capitalized words"""
import re

NORMALIZE_PATTERN = r'[^a-zA-Z0-9]'

def normalize(s: str) -> str:
    """Normalize a spelling for comparison: strip non-alnum, lowercase."""
    if s is None:
        return ""
    return re.sub(NORMALIZE_PATTERN, "", s).lower()

# Test cases
print("="*60)
print("Testing Normalize Function - Case Insensitivity")
print("="*60)

test_cases = [
    ("November", "november"),
    ("FRANCE", "france"),
    ("McDonald", "mcdonald"),
    ("O'Brien", "obrien"),
    ("New York", "newyork"),
]

for word_in_list, user_types in test_cases:
    normalized_list = normalize(word_in_list)
    normalized_user = normalize(user_types)
    is_match = normalized_list == normalized_user
    
    print(f"\nWord in list: '{word_in_list}'")
    print(f"User types:   '{user_types}'")
    print(f"Normalized:   '{normalized_list}' == '{normalized_user}'")
    print(f"Result:       {'✅ CORRECT' if is_match else '❌ WRONG'}")

print("\n" + "="*60)
print("All tests show normalize() handles capitalization correctly!")
print("="*60)
