"""
Quick script to check buzz dust ranking logic
"""
from buzz_dust_helpers import get_bee_class, get_rank_progress, BEE_CLASSES

# Print all rank thresholds
print("=" * 60)
print("BUZZ DUST RANKING THRESHOLDS")
print("=" * 60)
for rank in BEE_CLASSES:
    print(f"{rank['label']:20} - {rank['min_buzz_dust']:>8,} Buzz Dust")
print("=" * 60)

# Test different buzz dust amounts
test_amounts = [0, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 75000, 100000, 150000]

print("\nTEST CASES:")
print("-" * 60)
for amount in test_amounts:
    rank = get_bee_class(amount)
    progress = get_rank_progress(amount)
    next_rank = progress['next_class']
    
    print(f"\nBuzz Dust: {amount:>8,}")
    print(f"  Rank: {rank['label']}")
    if next_rank:
        print(f"  Next: {next_rank['label']} (need {progress['dust_needed']:,} more)")
        print(f"  Progress: {progress['progress_percent']}%")
    else:
        print(f"  Status: MAX RANK!")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
