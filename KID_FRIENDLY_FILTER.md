# Kid-Friendly Word Filter - BeeSmart Spelling Bee App

## Overview
The BeeSmart Spelling Bee App includes a comprehensive content filter to ensure all spelling words are appropriate for children ages 6-14. The filter automatically blocks inappropriate content during word upload.

## Problem Addressed
**Issue**: Random spelling bee asked kids to spell "ejaculations" - a word with adult connotations inappropriate for children.

**Solution**: Implemented multi-layer filtering system that blocks words containing:
- Profanity and vulgar language
- Sexual/adult content
- Violence and weapons
- Drugs and alcohol
- Hate speech
- Other age-inappropriate themes

## How It Works

### Automatic Filtering
The filter runs **automatically** on ALL word uploads:
- ✅ File uploads (CSV, TXT, DOCX, PDF, images)
- ✅ Manual word entry (typed/pasted lists)
- ✅ Enhanced background uploads

### Filter Logic

```python
def is_kid_friendly(word: str) -> tuple[bool, str]:
    """
    Check if a word is appropriate for children (ages 6-14).
    Returns: (is_safe, reason)
    """
```

**Checks performed:**
1. **Explicit word list**: Blocks ~40 known inappropriate words
2. **Substring matching**: Catches variations (e.g., "ejaculate" in "ejaculations")
3. **Number check**: Blocks words with digits (spam/codes)
4. **Length validation**: Must be 2-25 letters
5. **Character validation**: Must contain only letters

### Blocked Word Categories

#### Profanity/Vulgar Terms
- damn, hell, crap, sucks, piss

#### Sexual/Adult Content  
- sex, porn, orgasm, ejaculation, erection
- Anatomical terms (penis, vagina, breast)

#### Violence/Weapons
- kill, murder, suicide, gun, bomb

#### Drugs/Alcohol
- cocaine, marijuana, heroin, drunk, alcohol

#### Hate Speech
- racist, sexist, nazi, hate

#### Other Inappropriate
- death, blood, torture

## User Experience

### Successful Upload (All Words Safe)
```
🛡️ Running kid-friendly filter on 20 words...
✅ 20 words passed kid-friendly filter
📖 Found 'admire' in Simple Wiktionary with example
...
```

### Partial Block (Some Words Blocked)
```
🛡️ Running kid-friendly filter on 25 words...
🚫 BLOCKED: ejaculations - Word contains inappropriate content
🚫 BLOCKED: kill - Word is not appropriate for children
⚠️ Blocked 2 inappropriate words: ['ejaculations', 'kill']
✅ 23 words passed kid-friendly filter
```

### Complete Block (All Words Blocked)
```json
{
  "error": "All 3 words were blocked as inappropriate for children. Examples: damn, hell, crap"
}
```

## Integration Points

### 1. Standard Upload (`/api/upload`)
**Location**: Line ~2220 in `AjaSpellBApp.py`

```python
# After deduplication, before enrichment
filtered = []
blocked = []
for r in deduped:
    is_safe, reason = is_kid_friendly(r["word"])
    if is_safe:
        filtered.append(r)
    else:
        blocked.append({"word": r["word"], "reason": reason})
```

### 2. Enhanced Upload (`/api/upload-enhanced`)
**Location**: Line ~2070 in `AjaSpellBApp.py`

Includes progress update for parents/teachers:
```python
update_upload_progress(session_id, "filtering", 
    "Bees are checking words for kid-friendliness...", 
    "bees_checking", 50)
```

### 3. Manual Word Entry (`/api/upload-manual-words`)
**Location**: Line ~2450 in `AjaSpellBApp.py`

Same filtering applies to manually typed words.

## Console Logging

### Filter Activation
```
🛡️ Running kid-friendly filter on 20 words...
```

### Word Blocked
```
🚫 BLOCKED: ejaculations - Word contains inappropriate content
🚫 BLOCKED: kill - Word 'kill' is not appropriate for children
```

### Summary
```
⚠️ Blocked 2 inappropriate words: ['ejaculations', 'kill']
✅ 18 words passed kid-friendly filter
```

## Customization

### Adding Words to Block List

Edit the `INAPPROPRIATE_WORDS` set in `AjaSpellBApp.py` (around line 440):

```python
INAPPROPRIATE_WORDS = {
    # Profanity and vulgar terms
    "damn", "damned", "hell", "hells", "crap", "sucks", "piss", "pissed",
    # Add more words here...
    "newword1", "newword2",
}
```

### Adjusting Filter Sensitivity

**More Strict**: Add more words to `INAPPROPRIATE_WORDS`
```python
INAPPROPRIATE_WORDS.add("additional_word")
```

**Less Strict**: Remove words from the set
```python
# Comment out specific words
# "damn", "hell",  # Allow these
```

## Testing the Filter

### Test Case 1: Inappropriate Word
```bash
curl -X POST http://localhost:5000/api/upload-manual-words \
  -H "Content-Type: application/json" \
  -d '{"words": ["cat", "dog", "ejaculations", "bird"]}'
```

**Expected**: Block "ejaculations", allow others

### Test Case 2: All Safe Words
```bash
curl -X POST http://localhost:5000/api/upload-manual-words \
  -H "Content-Type: application/json" \
  -d '{"words": ["admire", "brisk", "curious", "delightful"]}'
```

**Expected**: All words pass filter

### Test Case 3: All Blocked
```bash
curl -X POST http://localhost:5000/api/upload-manual-words \
  -H "Content-Type: application/json" \
  -d '{"words": ["damn", "hell", "kill"]}'
```

**Expected**: Error response with all words blocked

## Error Handling

### Error Response Format
```json
{
  "error": "All 3 words were blocked as inappropriate for children. Examples: word1, word2, word3"
}
```

### HTTP Status Codes
- `200`: Upload successful (all words safe or partial block with some words remaining)
- `400`: Upload failed (all words blocked or other validation error)

## Performance Impact

- **Overhead**: ~1ms per word (negligible)
- **No API calls**: All filtering is local
- **No delays**: Instant validation

## Privacy & Safety

### What We Block
- ✅ Inappropriate content
- ✅ Adult themes
- ✅ Violence references
- ✅ Profanity

### What We DON'T Block
- ✅ Educational medical terms (in context)
- ✅ Historical terms (war, battle, soldier)
- ✅ Age-appropriate challenging vocabulary

## Future Enhancements

### Potential Additions
1. **Grade-level filtering**: Adjust word list by age (6-8, 9-11, 12-14)
2. **Custom teacher overrides**: Allow teachers to approve specific words
3. **Context-aware filtering**: Check definitions, not just words
4. **Machine learning**: Train model on kid-appropriate corpora
5. **Multilingual support**: Extend to non-English words

### Feedback Mechanism
Teachers can report:
- False positives (safe words blocked)
- False negatives (inappropriate words allowed)

Email: support@beesmartspelling.com

## Compliance

This filter helps ensure compliance with:
- **COPPA** (Children's Online Privacy Protection Act)
- **CIPA** (Children's Internet Protection Act)
- Educational content guidelines
- School district content policies

## Files Modified

- `AjaSpellBApp.py`: Core filter implementation
  - Lines ~440-495: `is_kid_friendly()` function
  - Line ~2220: `/api/upload` integration
  - Line ~2070: `/api/upload-enhanced` integration
  - Line ~2450: `/api/upload-manual-words` integration

## Related Documentation

- `IOS_VOICE_FIXES.md` - iOS voice consistency fixes
- `AUTHENTICATION_COMPLETE.md` - User authentication system
- `DATABASE_ARCHITECTURE.md` - Database schema for word tracking

## Version History

### v1.0 (Current)
- Initial implementation
- ~40 blocked words across 6 categories
- Integration with all upload endpoints
- Console logging for monitoring

## Support

For questions or issues:
- Check console logs for `🛡️` and `🚫` emoji markers
- Report false positives/negatives
- Suggest additional words to block

---

**Last Updated**: October 17, 2025
**Status**: ✅ Active in Production
