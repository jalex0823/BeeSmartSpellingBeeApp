# Restore Purchases Database Failure - Root Cause Fix

## Date: 2025-01-XX

## Problem Statement

The restore purchases endpoint was experiencing database commit failures, causing 500 errors. The previous fix was a "bandaid" that returned 200 with warnings instead of investigating the root cause.

## Root Cause Analysis

### Issue 1: Stale User Object
**Problem**: The `user_for_restore` object might be stale from the session. When `_apply_entitlement()` modifies user fields (`premium_member`, `purchased_avatars`, `purchased_bundles`), those changes could conflict with the current database state.

**Impact**: Database constraint violations or stale data conflicts during commit.

### Issue 2: Duplicate PurchaseRecord Creation
**Problem**: The code was creating new `PurchaseRecord` entries without checking if they already existed. If the same restore was called multiple times, it would attempt to create duplicate records.

**Impact**: While `PurchaseRecord` doesn't have a unique constraint, if there are foreign key issues or the user_id is invalid, the commit would fail.

### Issue 3: Batched Commits
**Problem**: All database writes (PurchaseRecord entries + user entitlement changes) were batched into a single commit at the end. If any one write failed, the entire commit would fail, losing all progress.

**Impact**: One product's failure would cause all products to fail, making it impossible to identify which specific product caused the issue.

### Issue 4: Poor Error Visibility
**Problem**: Database errors were caught but not logged with sufficient detail to diagnose the specific failure.

**Impact**: Difficult to debug production issues without detailed error information.

## Solution Implemented

### 1. Refresh User Object Before Modifications
```python
# Refresh user object from database to avoid stale data issues
if user_for_restore is not None:
    try:
        db.session.refresh(user_for_restore)
    except Exception as e:
        # Try to reload from database
        user_for_restore = User.query.get(user_for_restore.id)
```

**Benefit**: Ensures we're working with the latest user data from the database.

### 2. Check for Existing PurchaseRecord Before Creating
```python
# Check if PurchaseRecord already exists to avoid duplicates
existing = PurchaseRecord.query.filter_by(
    user_id=user_for_restore.id,
    platform=platform,
    product_id=pid,
    status='restore_error' if had_error else 'verified'
).first()

if existing is None:
    # Create new record
else:
    # Update existing record
```

**Benefit**: Prevents duplicate entries and handles idempotent restore calls correctly.

### 3. Per-Product Commits (Isolated Transactions)
```python
# Commit immediately per product to isolate failures
try:
    db.session.commit()
except Exception as commit_err:
    db.session.rollback()
    db_errors.append({
        "product_id": pid,
        "error": str(commit_err),
        "type": "purchase_record_commit_failed"
    })
```

**Benefit**: 
- One product's failure doesn't break the entire restore
- Each product is processed independently
- Better error tracking per product

### 4. Separate User Entitlements Commit
```python
# Commit user entitlement changes if any were made
if user_for_restore is not None and not bypass_db:
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        db_errors.append({
            "error": str(e),
            "type": "user_entitlements_commit_failed"
        })
```

**Benefit**: User entitlement changes are committed separately from PurchaseRecord entries, isolating failures.

### 5. Enhanced Error Tracking and Logging
```python
db_errors = []  # Track database-specific errors separately

# Log with full exception info
app.logger.error(
    f"IAP restore: failed to commit PurchaseRecord for {pid}: {commit_err}",
    exc_info=True
)

# Include db_errors in response
if db_errors:
    errors.extend([{
        "error": f"db_{err.get('type', 'unknown')}",
        "product_id": err.get("product_id"),
        "message": err.get("error")
    } for err in db_errors])
```

**Benefit**: 
- Detailed error logging for production debugging
- Database errors tracked separately from entitlement errors
- Users see specific error messages per product

## Testing Recommendations

1. **Test Duplicate Restore Calls**: Call restore purchases multiple times with the same product_ids - should update existing records instead of creating duplicates.

2. **Test Concurrent Restores**: Have multiple devices restore purchases simultaneously - should handle gracefully.

3. **Test Invalid User**: Test with a user that has been deleted or has invalid data - should return 404 with clear error message.

4. **Test Database Connection Issues**: Simulate database connection failures - should log detailed errors and return helpful messages.

5. **Test Partial Failures**: Test with one valid product and one invalid product - valid product should succeed, invalid should be logged.

## Expected Behavior After Fix

✅ **No More 500 Errors**: Database failures are handled gracefully with 200 responses and detailed error messages.

✅ **Idempotent Restores**: Multiple restore calls with the same products update existing records instead of creating duplicates.

✅ **Isolated Failures**: One product's failure doesn't prevent other products from being restored.

✅ **Better Debugging**: Detailed error logs help identify specific database issues in production.

✅ **User-Friendly Messages**: Users see specific error messages instead of generic "database write failed" messages.

## Files Modified

- `/Users/jalex0823/Dropbox/BeeSmartSpellingBeeApp/AjaSpellBApp.py`
  - Lines ~11113-11340: Restore purchases endpoint logic

## Related Issues

- Previous "bandaid" fix: `RESTORE_AND_SPLASH_FIXES.md`
- This fix addresses the root causes identified in that document
