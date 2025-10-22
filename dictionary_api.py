"""
Dictionary API integration for BeeSmart Spelling App
Handles API lookups with rate limiting, circuit breaker, and kid-friendly normalization
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
import re


class DictionaryAPI:
    def __init__(self):
        self.base_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        self.rate_limit_delay = 0.5  # 500ms between requests
        self.last_request_time = 0
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 300  # 5 minutes
        self.circuit_breaker_last_failure = 0
        
    def reset_circuit_breaker(self):
        """Reset circuit breaker to allow API calls again"""
        self.circuit_breaker_failures = 0
        self.circuit_breaker_last_failure = 0
        print("🔄 Circuit breaker reset - API calls enabled")
        
    def is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open (blocking requests)"""
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            time_since_failure = time.time() - self.circuit_breaker_last_failure
            if time_since_failure < self.circuit_breaker_timeout:
                return True
            else:
                # Reset circuit breaker after timeout
                self.circuit_breaker_failures = 0
        return False
    
    def respect_rate_limit(self):
        """Ensure respectful rate limiting between API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def normalize_for_kids(self, definition: str) -> str:
        """Make definition more kid-friendly"""
        # Remove technical jargon and complex terms
        kid_replacements = {
            r'\b(noun|verb|adjective|adverb|pronoun|preposition|conjunction|interjection)\b': '',
            r'\b(etymology|etymology from)\b.*?\.': '',
            r'\barchaic\b': 'old-fashioned',
            r'\bformal\b': '',
            r'\binformal\b': '',
            r'\btechnical\b': '',
            r'\bliterary\b': 'in stories',
            r'\bcolloq\w*\b': '',
            r'\bslang\b': 'casual word',
            r'\beuphemism\b': 'nice way to say',
        }
        
        result = definition
        for pattern, replacement in kid_replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Clean up extra spaces and punctuation
        result = re.sub(r'\s+', ' ', result).strip()
        result = result.rstrip('.,;:')
        
        # Ensure first letter is capitalized
        if result:
            result = result[0].upper() + result[1:]
            
        return result
    
    def create_example_sentence(self, word: str, definition: str, api_example: Optional[str] = None) -> str:
        """Create a kid-friendly example sentence with blank"""
        word_lower = word.lower()
        
        # Try to use API example first if available and appropriate
        if api_example:
            # Clean up the API example
            example_clean = re.sub(r'["""]', '', api_example).strip()
            if len(example_clean) < 100 and word_lower in example_clean.lower():
                # Replace the word with blank
                example_with_blank = re.sub(
                    r'\b' + re.escape(word) + r'\b', 
                    '_____', 
                    example_clean, 
                    flags=re.IGNORECASE
                )
                if '_____' in example_with_blank:
                    return example_with_blank
        
        # Generate a simple example based on word patterns
        if word_lower.endswith('ing'):
            return f"The children are _____ at the playground"
        elif word_lower.endswith('ed'):
            return f"Yesterday, she _____ her homework carefully"
        elif word_lower.endswith('ly'):
            return f"The student worked very _____ on the project"
        elif word_lower.endswith('tion') or word_lower.endswith('sion'):
            return f"The _____ was announced at the school assembly"
        elif word_lower.endswith('able') or word_lower.endswith('ible'):
            return f"The puzzle was _____ for the smart student"
        else:
            return f"The teacher explained what _____ means to the class"
    
    def lookup_word(self, word: str) -> Optional[Dict]:
        """
        Look up a word using the Free Dictionary API
        Returns dict with definition, example, phonetic if successful
        """
        if self.is_circuit_breaker_open():
            print(f"🚫 Circuit breaker open - skipping API lookup for '{word}' (failures: {self.circuit_breaker_failures})")
            return None
            
        try:
            print(f"🔍 Looking up '{word}' via Free Dictionary API...")
            self.respect_rate_limit()
            
            # Clean the word for API call
            clean_word = re.sub(r'[^a-zA-Z\'-]', '', word.strip().lower())
            if not clean_word:
                print(f"⚠️ Invalid word format: '{word}'")
                return None
                
            url = f"{self.base_url}{clean_word}"
            print(f"📡 API URL: {url}")
            
            response = requests.get(
                url,
                timeout=10,
                headers={'User-Agent': 'BeeSmart-Spelling-App/1.6'}
            )
            
            print(f"📊 API Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Reset circuit breaker on success
                    self.circuit_breaker_failures = 0
                    print(f"✅ API success for '{word}'")
                    
                    # Extract the best definition and example
                    word_data = data[0]  # Use first result
                    
                    # Get phonetic if available
                    phonetic = ""
                    if 'phonetics' in word_data:
                        for phonetic_entry in word_data['phonetics']:
                            if 'text' in phonetic_entry and phonetic_entry['text']:
                                phonetic = phonetic_entry['text']
                                break
                    
                    # Get definition and example
                    definition = ""
                    example = ""
                    pos = ""
                    
                    if 'meanings' in word_data and word_data['meanings']:
                        meaning = word_data['meanings'][0]  # Use first meaning
                        pos = meaning.get('partOfSpeech', '')
                        
                        if 'definitions' in meaning and meaning['definitions']:
                            def_entry = meaning['definitions'][0]  # Use first definition
                            definition = def_entry.get('definition', '')
                            example = def_entry.get('example', '')
                    
                    if definition:
                        # Normalize for kids
                        kid_definition = self.normalize_for_kids(definition)
                        
                        # Create example sentence
                        example_sentence = self.create_example_sentence(word, kid_definition, example)
                        
                        return {
                            'definition': kid_definition,
                            'example': example_sentence,
                            'phonetic': phonetic,
                            'pos': pos,
                            'source': 'api',
                            'created': datetime.now().isoformat()
                        }
            
            elif response.status_code == 404:
                # Word not found - not an error, just return None
                print(f"🔍 Word '{word}' not found in dictionary (404)")
                return None
            else:
                # Other HTTP errors count as failures
                self.circuit_breaker_failures += 1
                self.circuit_breaker_last_failure = time.time()
                print(f"❌ API error {response.status_code} for word '{word}' - Response: {response.text[:200]}")
                
        except requests.RequestException as e:
            self.circuit_breaker_failures += 1
            self.circuit_breaker_last_failure = time.time()
            print(f"🌐 Network error for word '{word}': {e}")
        except Exception as e:
            print(f"💥 Unexpected error during API lookup for word '{word}': {e}")
            import traceback
            traceback.print_exc()
            
        return None


# Global instance
dictionary_api = DictionaryAPI()
