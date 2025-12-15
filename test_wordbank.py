import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from AjaSpellBApp import app, get_wordbank, set_wordbank, init_quiz_state
    print("Successfully imported AjaSpellBApp")
    
    with app.app_context():
        print("Testing get_wordbank()...")
        words = get_wordbank()
        print(f"get_wordbank() returned {len(words)} words")
        
        if len(words) == 0:
            print("Wordbank is empty. Attempting to set sample words...")
            sample_words = [{'word': 'test', 'sentence': 'This is a test.', 'hint': 't_st'}]
            set_wordbank(sample_words, is_user_upload=True)
            print("Set sample words.")
            
            words = get_wordbank()
            print(f"get_wordbank() now returned {len(words)} words")
            
            if len(words) > 0:
                print("SUCCESS: Wordbank operations are working.")
            else:
                print("FAILURE: Wordbank is still empty after set.")
        else:
            print("SUCCESS: Wordbank has words.")
            
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
