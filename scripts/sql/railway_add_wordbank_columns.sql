-- BeeSmart Spelling Bee App — Railway migration: add wordbank persistence columns to users table
-- Safe to run multiple times; uses IF NOT EXISTS

BEGIN;

-- Add UUID pointer for server-side WORD_STORAGE and disk cache
ALTER TABLE IF EXISTS users
    ADD COLUMN IF NOT EXISTS wordbank_storage_id VARCHAR(36);

-- Add last-updated timestamp for wordbank
ALTER TABLE IF EXISTS users
    ADD COLUMN IF NOT EXISTS wordbank_last_updated TIMESTAMPTZ;

-- Indexes to speed lookups and recovery flows
CREATE INDEX IF NOT EXISTS idx_users_wordbank_storage_id ON users (wordbank_storage_id);

COMMIT;
