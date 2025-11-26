# Railway SQL Commands to Fix Avatar Paths
# Run these via Railway CLI or Railway Dashboard SQL editor

## Step 1: Check current avatar paths (see what needs fixing)
```sql
SELECT id, name, obj_file 
FROM avatars 
WHERE obj_file LIKE '%.obj'
ORDER BY name;
```

## Step 2: Fix all .obj to .glb paths
```sql
UPDATE avatars 
SET obj_file = REPLACE(obj_file, '.obj', '.glb')
WHERE obj_file LIKE '%.obj';
```

## Step 3: Verify the fix
```sql
SELECT id, name, obj_file 
FROM avatars 
WHERE obj_file LIKE '%.glb'
ORDER BY name;
```

## Step 4: Count fixed avatars
```sql
SELECT 
  COUNT(*) as total_avatars,
  COUNT(CASE WHEN obj_file LIKE '%.glb' THEN 1 END) as glb_avatars,
  COUNT(CASE WHEN obj_file LIKE '%.obj' THEN 1 END) as obj_avatars
FROM avatars;
```

---

## How to run these commands:

### Option A: Railway CLI
```bash
railway login
railway link
railway run psql $DATABASE_URL
# Then paste the SQL commands above
```

### Option B: Railway Dashboard
1. Go to https://railway.app/dashboard
2. Select your BeeSmartSpellingBeeApp project
3. Click on the PostgreSQL service
4. Click "Data" tab
5. Click "Query" button
6. Paste and run SQL commands above

### Option C: Web UI (Already deployed!)
1. Navigate to: https://beesmart.up.railway.app/admin/fix-avatar-glb
2. Login with BigDaddy admin account
3. Click "Fix All Avatar Paths" button

---

## Just the UPDATE command (copy/paste ready):
```sql
UPDATE avatars SET obj_file = REPLACE(obj_file, '.obj', '.glb') WHERE obj_file LIKE '%.obj';
```
