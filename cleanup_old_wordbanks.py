"""
Cleanup script for old, unused wordbank records in Railway PostgreSQL.
Deletes wordbank_storage records that haven't been accessed in 5+ days.

Usage:
    python cleanup_old_wordbanks.py

This script is safe to run repeatedly and can be scheduled as a cron job.
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AjaSpellBApp import app, db
from models import WordBankStorage

def cleanup_old_wordbanks(days_threshold=5, dry_run=False):
    """
    Delete wordbank records that haven't been accessed in X days.
    
    Args:
        days_threshold: Number of days of inactivity before deletion (default: 5)
        dry_run: If True, only show what would be deleted without actually deleting
    
    Returns:
        tuple: (deleted_count, total_size_saved)
    """
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
        
        print(f"{'='*70}")
        print(f"🧹 Wordbank Cleanup Script")
        print(f"{'='*70}")
        print(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Threshold: {days_threshold} days of inactivity")
        print(f"Mode: {'DRY RUN (no deletions)' if dry_run else 'LIVE (will delete)'}")
        print(f"{'='*70}\n")
        
        # Find old records
        old_records = WordBankStorage.query.filter(
            WordBankStorage.last_accessed < cutoff_date
        ).all()
        
        if not old_records:
            print("✅ No old wordbank records found. Database is clean!")
            return 0, 0
        
        print(f"Found {len(old_records)} old wordbank record(s):\n")
        
        deleted_count = 0
        total_words_removed = 0
        
        for record in old_records:
            word_count = record.word_count or 0
            total_words_removed += word_count
            
            days_old = (datetime.utcnow() - record.last_accessed).days
            
            print(f"  📦 ID: {record.id}")
            print(f"     Storage ID: {record.storage_id[:20]}...")
            print(f"     Words: {word_count}")
            print(f"     User ID: {record.user_id or 'guest'}")
            print(f"     Created: {record.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"     Last accessed: {record.last_accessed.strftime('%Y-%m-%d %H:%M')} ({days_old} days ago)")
            
            if not dry_run:
                try:
                    db.session.delete(record)
                    deleted_count += 1
                    print(f"     ✅ Deleted")
                except Exception as e:
                    print(f"     ❌ Error deleting: {e}")
                    db.session.rollback()
            else:
                print(f"     🔍 Would be deleted (dry run)")
                deleted_count += 1
            
            print()
        
        if not dry_run:
            try:
                db.session.commit()
                print(f"{'='*70}")
                print(f"✅ Cleanup completed successfully!")
                print(f"   Deleted: {deleted_count} record(s)")
                print(f"   Total words removed: {total_words_removed}")
                print(f"{'='*70}")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error committing deletions: {e}")
                return 0, 0
        else:
            print(f"{'='*70}")
            print(f"🔍 DRY RUN SUMMARY:")
            print(f"   Would delete: {deleted_count} record(s)")
            print(f"   Total words that would be removed: {total_words_removed}")
            print(f"   Run without --dry-run to perform actual deletion")
            print(f"{'='*70}")
        
        return deleted_count, total_words_removed

def show_wordbank_stats():
    """Display statistics about current wordbank storage."""
    with app.app_context():
        total_records = WordBankStorage.query.count()
        total_words = db.session.query(
            db.func.sum(WordBankStorage.word_count)
        ).scalar() or 0
        
        # Count by age
        now = datetime.utcnow()
        age_ranges = [
            ("< 1 day", 1),
            ("1-2 days", 2),
            ("2-5 days", 5),
            ("5-7 days", 7),
            ("7-14 days", 14),
            ("> 14 days", 999)
        ]
        
        print(f"\n{'='*70}")
        print(f"📊 Wordbank Storage Statistics")
        print(f"{'='*70}")
        print(f"Total records: {total_records}")
        print(f"Total words stored: {total_words}")
        print(f"\nAge distribution:")
        
        prev_days = 0
        for label, days in age_ranges:
            cutoff = now - timedelta(days=days)
            prev_cutoff = now - timedelta(days=prev_days)
            
            count = WordBankStorage.query.filter(
                WordBankStorage.last_accessed >= cutoff,
                WordBankStorage.last_accessed < prev_cutoff
            ).count()
            
            print(f"  {label:12} {count:4} record(s)")
            prev_days = days
        
        print(f"{'='*70}\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up old wordbank records from Railway database")
    parser.add_argument("--days", type=int, default=5, help="Delete records older than X days (default: 5)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without actually deleting")
    parser.add_argument("--stats", action="store_true", help="Show wordbank statistics only (no cleanup)")
    
    args = parser.parse_args()
    
    if args.stats:
        show_wordbank_stats()
    else:
        # Show stats first
        show_wordbank_stats()
        
        # Then run cleanup
        deleted, words_removed = cleanup_old_wordbanks(
            days_threshold=args.days,
            dry_run=args.dry_run
        )
        
        if deleted > 0 and not args.dry_run:
            print(f"\n💡 Tip: Schedule this script to run daily with:")
            print(f"   python cleanup_old_wordbanks.py --days 5")
