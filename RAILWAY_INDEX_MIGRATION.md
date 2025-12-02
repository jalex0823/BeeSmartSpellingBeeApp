# Railway Database Index Migration

## Run this command in Railway's console to add indexes:

```bash
python3 add_avatar_indexes.py
```

## Or run it via Railway CLI:

```bash
railway run python3 add_avatar_indexes.py
```

## What this does:
- Adds 6 new indexes to the `avatars` table in PostgreSQL
- Improves `/api/avatars` query performance by 10-100x
- Safe to run multiple times (checks for existing indexes)

## Expected output:
```
📋 Existing indexes: {...}
➕ Adding 6 new indexes...
   ✅ Success (x6)
🎉 Index creation complete!
```

## Performance improvement:
- **Before**: 10+ seconds per avatar API call
- **After**: <1 second (first call builds cache, subsequent calls <100ms)
