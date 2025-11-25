#!/usr/bin/env python3
"""Test slug generation for avatar IDs"""

import re
from avatar_catalog import NAME_MAP_CAMELCASE

def generate_slug(base: str) -> str:
    """Generate proper slug from CamelCase base name"""
    # Try canonical mapping first
    if base in NAME_MAP_CAMELCASE:
        return NAME_MAP_CAMELCASE[base]
    
    # Fallback: convert CamelCase to hyphenated slug
    name_with_spaces = re.sub(r'(?<!^)([A-Z])', r' \1', base).strip()
    slug = re.sub(r'[^a-z0-9]+', '-', name_with_spaces.lower()).strip('-')
    return slug

# Test cases
test_cases = [
    'AlBee',
    'BrotherBee', 
    'KnightBee',
    'DoctorBee',
    'DivaBee',
    'QueenBee',
    'MascotBee',
    'HoneyComb',
    'FrankenBee',
]

print('✅ Testing slug generation for avatar IDs')
print('=' * 60)

for case in test_cases:
    slug = generate_slug(case)
    source = 'NAME_MAP' if case in NAME_MAP_CAMELCASE else 'FALLBACK'
    print(f'{case:15} → {slug:20} ({source})')

print('=' * 60)
print(f'Total mapped: {len(NAME_MAP_CAMELCASE)} avatars')
