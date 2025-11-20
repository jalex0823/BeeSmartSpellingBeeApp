-- Manual Railway PostgreSQL Migration for Buzz Dust System
-- Run this directly in Railway's PostgreSQL console

-- Add total_buzz_dust column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='total_buzz_dust'
    ) THEN
        ALTER TABLE users ADD COLUMN total_buzz_dust INTEGER DEFAULT 0;
        CREATE INDEX IF NOT EXISTS ix_users_total_buzz_dust ON users(total_buzz_dust);
        RAISE NOTICE 'Added total_buzz_dust column';
    ELSE
        RAISE NOTICE 'total_buzz_dust column already exists';
    END IF;
END $$;

-- Add bee_class column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='bee_class'
    ) THEN
        ALTER TABLE users ADD COLUMN bee_class VARCHAR(20) DEFAULT 'Novice Bee';
        CREATE INDEX IF NOT EXISTS ix_users_bee_class ON users(bee_class);
        RAISE NOTICE 'Added bee_class column';
    ELSE
        RAISE NOTICE 'bee_class column already exists';
    END IF;
END $$;

-- Add last_rank_up_at column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='last_rank_up_at'
    ) THEN
        ALTER TABLE users ADD COLUMN last_rank_up_at TIMESTAMP;
        RAISE NOTICE 'Added last_rank_up_at column';
    ELSE
        RAISE NOTICE 'last_rank_up_at column already exists';
    END IF;
END $$;

-- Add current_streak column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='current_streak'
    ) THEN
        ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0;
        RAISE NOTICE 'Added current_streak column';
    ELSE
        RAISE NOTICE 'current_streak column already exists';
    END IF;
END $$;

-- Add longest_streak column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='users' AND column_name='longest_streak'
    ) THEN
        ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0;
        RAISE NOTICE 'Added longest_streak column';
    ELSE
        RAISE NOTICE 'longest_streak column already exists';
    END IF;
END $$;

-- Verify all columns exist
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND column_name IN ('total_buzz_dust', 'bee_class', 'last_rank_up_at', 'current_streak', 'longest_streak')
ORDER BY column_name;
