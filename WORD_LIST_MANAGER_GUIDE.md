# Word List Manager - Implementation Guide

## Overview
The Word List Manager is a centralized JavaScript module that manages quiz word lists, ensuring consistency between server-provided lists and client-side state.

## Problem Solved
Previously, the quiz would not consistently use the selected word list. Issues included:
- No tracking of which list was active
- Page reloads would lose list context
- No way to "refresh" and clear the current list
- Confusion when switching between different word lists

## Solution Architecture

### Components

#### 1. **quiz-wordlist.js** (Client-Side Manager)
Location: `static/js/quiz-wordlist.js`

**Responsibilities:**
- Persist active list metadata in localStorage
- Compare server-provided list to stored list on page load
- Override storage when server provides a different list
- Provide public API for getting/clearing lists
- Dispatch events when list changes
- Maintain backward compatibility with existing globals

**Key Classes:**
```javascript
class WordListManager {
    constructor()
    async init(serverProvidedList)
    async setActiveList(listData)
    clearActiveList()
    getCurrentWordList()
    saveToStorage()
    loadFromStorage()
    notifyListChanged()
    async ensureUsingSelectedList(options)
}
```

**Public API:**
```javascript
window.wordListManager            // Global instance
window.getCurrentWordList()       // Get current list
window.clearActiveWordList()      // Clear current list
```

**Events:**
```javascript
// Dispatched when list changes
window.addEventListener('wordlist:changed', (event) => {
    console.log('List changed:', event.detail.list);
    console.log('Words:', event.detail.words);
    console.log('List ID:', event.detail.listId);
});
```

**Backward-Compatible Globals:**
```javascript
window.QUIZ_WORDS            // Array of word objects
window.QUIZ_CURRENT_INDEX    // Current word index (always 0 on list change)
window.QUIZ_ACTIVE_LIST_ID   // Current list ID
window.QUIZ_ACTIVE_LIST_NAME // Current list name
```

#### 2. **quiz.html Template Modifications**

**Data Anchor Element:**
```html
<div id="quiz-root" 
     data-selected-list-id="{{ selected_list.id if selected_list else 'default' }}"
     data-selected-list-name="{{ selected_list.name if selected_list else 'Word List' }}"
     data-words-url="/api/wordbank"
     style="display: none;">
</div>
```

**Refresh Button:**
```html
<button id="refreshWordListBtn" 
        class="action-btn secondary">
    🔄 Refresh List
</button>
```

**Script Inclusion:**
```html
<script src="{{ url_for('static', filename='js/quiz-wordlist.js') }}?v={{ timestamp }}"></script>
<script>
document.addEventListener('DOMContentLoaded', () => {
    const quizRoot = document.getElementById('quiz-root');
    if (quizRoot && window.wordListManager) {
        window.wordListManager.ensureUsingSelectedList({
            selectedListId: quizRoot.dataset.selectedListId,
            selectedListName: quizRoot.dataset.selectedListName,
            wordsUrl: quizRoot.dataset.wordsUrl
        });
    }
});
</script>
```

#### 3. **Flask Backend Modifications**

**Quiz Route (`/quiz`):**
```python
# Generate or retrieve active list metadata
active_list_id = session.get("active_list_id", None)
active_list_name = session.get("active_list_name", "Word List")

if not active_list_id:
    # Create identifier from word hash
    import hashlib
    words_str = "_".join([w.get("word", "") for w in wordbank[:5]])
    word_hash = hashlib.md5(words_str.encode()).hexdigest()[:8]
    active_list_id = f"wordbank_{word_hash}"
    active_list_name = f"Word List ({len(wordbank)} words)"

selected_list = {
    "id": active_list_id,
    "name": active_list_name
}

return render_template("quiz.html", selected_list=selected_list, ...)
```

**Load Saved List (`/api/saved-lists/load`):**
```python
# After loading words into session
session["active_list_id"] = str(wl.id)
session["active_list_name"] = wl.list_name
session.modified = True
```

**Clear List (`/api/clear`):**
```python
# Clear active list metadata
session.pop("active_list_id", None)
session.pop("active_list_name", None)
```

## Usage Scenarios

### Scenario 1: User Loads Quiz with Default Words
1. User navigates to `/quiz`
2. Flask generates a unique ID from word hash
3. Template passes `selected_list` to frontend
4. Word List Manager initializes with server data
5. List metadata saved to localStorage
6. `window.QUIZ_WORDS` populated with words

### Scenario 2: User Loads a Saved List
1. User clicks "Load List" with ID `123`
2. `/api/saved-lists/load` sets `session["active_list_id"] = "123"`
3. User navigates to `/quiz`
4. Flask passes `selected_list.id = "123"`
5. Word List Manager detects new list ID
6. Old list cleared, new list loaded
7. Quiz state reset with new words

### Scenario 3: User Refreshes the List
1. User clicks "Refresh List" button
2. Confirmation dialog appears
3. If confirmed, `clearActiveWordList()` called
4. localStorage cleared
5. `window.QUIZ_WORDS` set to empty array
6. User prompted to select a new list

### Scenario 4: Page Reload
1. User reloads `/quiz` page
2. Word List Manager loads from localStorage
3. Compares stored list ID to server-provided ID
4. If IDs match, keeps current list
5. If IDs differ, overrides with server list
6. Ensures consistency

## Data Flow

```
Server (Flask)
    ↓
[Generates selected_list metadata]
    ↓
Template (quiz.html)
    ↓
[Embeds data in #quiz-root]
    ↓
JavaScript (quiz-wordlist.js)
    ↓
[Compares to localStorage]
    ↓
[Updates globals: QUIZ_WORDS, etc.]
    ↓
[Dispatches wordlist:changed event]
    ↓
QuizManager
    ↓
[Uses window.QUIZ_WORDS]
```

## localStorage Schema

```javascript
{
    "id": "list_123",           // List identifier
    "name": "Science Words",    // Human-readable name
    "words": [...],             // Array of word objects
    "loadedAt": 1699999999999,  // Timestamp
    "version": "1.0"            // Schema version
}
```

Key: `beesmart_active_wordlist`

## Testing

### Unit Tests
Run: `python3 test_wordlist_manager.py`

Tests:
- ✅ Quiz template includes word list manager
- ✅ quiz-wordlist.js has expected content
- ✅ Flask route passes selected_list
- ✅ Saved lists load sets active list
- ✅ Clear API clears active list

### Functional Tests
Run: `python3 test_wordlist_functional.py`

Tests:
- ✅ JavaScript syntax validation
- ✅ Quiz page loads (when Flask app running)

## Acceptance Criteria

✅ **New list selection overrides existing list**
- When server provides a different `selected_list.id`, the stored list is replaced
- Progress resets and `window.QUIZ_WORDS` updated
- `window.QUIZ_CURRENT_INDEX` set to 0

✅ **Refresh button clears active list**
- Clicking "Refresh list" shows confirmation dialog
- If confirmed, localStorage cleared
- `window.QUIZ_WORDS` becomes empty array
- User must select a new list to continue

✅ **Quiz uses selected list across reloads**
- Page reload compares stored list to server-provided list
- If IDs match, quiz continues with stored list
- If IDs differ, quiz switches to server-provided list

✅ **Backward compatibility maintained**
- `window.QUIZ_WORDS` still available for existing code
- `window.QUIZ_CURRENT_INDEX` still works
- No breaking changes to QuizManager

✅ **wordlist:changed event dispatched**
- Event fired whenever list changes
- Contains list data, words array, list ID, and name
- Can be used for UI updates or analytics

## Future Enhancements

### Possible Additions:
1. **List Selector UI** - Dropdown to switch between saved lists
2. **Progress Persistence** - Save quiz progress per list
3. **List Comparison** - Show differences between lists
4. **Auto-sync** - Sync lists across devices for logged-in users
5. **Offline Mode** - Cache lists for offline quiz practice

### API Extensions:
```javascript
// Example future API
window.wordListManager.getAllLists()       // Get all saved lists
window.wordListManager.switchList(id)      // Switch to different list
window.wordListManager.syncWithServer()    // Sync with backend
```

## Troubleshooting

### Issue: List not loading
**Check:**
1. Is `selected_list` passed to template?
2. Is `#quiz-root` element present?
3. Is `quiz-wordlist.js` loaded?
4. Check browser console for errors

### Issue: List not persisting across reloads
**Check:**
1. Is localStorage enabled in browser?
2. Check localStorage quota (might be full)
3. Verify version matches in stored data

### Issue: Refresh button not working
**Check:**
1. Is `#refreshWordListBtn` element present?
2. Is click handler attached?
3. Check browser console for errors

## Maintenance Notes

- **Version updates**: If localStorage schema changes, increment VERSION in quiz-wordlist.js
- **Testing**: Always run tests after modifications
- **Backward compatibility**: Maintain `window.QUIZ_*` globals for existing code
- **Documentation**: Update this guide when adding features

## Related Files

- `static/js/quiz-wordlist.js` - Word List Manager implementation
- `templates/quiz.html` - Quiz template with data anchor and script
- `AjaSpellBApp.py` - Flask routes (`/quiz`, `/api/saved-lists/load`, `/api/clear`)
- `test_wordlist_manager.py` - Unit tests
- `test_wordlist_functional.py` - Functional tests
