"""Quick performance profiling for dictionary enrichment.
Run locally: python speed_profile_dictionary.py
Outputs timing stats comparing single get_word_info calls vs bulk_word_info.
"""
from time import perf_counter
from statistics import mean
from AjaSpellBApp import get_word_info, bulk_word_info, ensure_simple_wiktionary_loaded

SAMPLE_WORDS = [
    "example", "practice", "difficult", "challenge", "adaptive", "learning",
    "buzz", "honey", "flower", "pollinate", "nectar", "brilliant", "future",
    "robot", "knight", "super", "dragon", "franken", "spark", "wizard"
]

REPEATS = 3

def time_single(words):
    timings = []
    for _ in range(REPEATS):
        start = perf_counter()
        for w in words:
            _ = get_word_info(w)
        timings.append(perf_counter() - start)
    return timings


def time_bulk(words):
    timings = []
    for _ in range(REPEATS):
        start = perf_counter()
        _ = bulk_word_info(words)
        timings.append(perf_counter() - start)
    return timings


def main():
    ensure_simple_wiktionary_loaded()
    single_timings = time_single(SAMPLE_WORDS)
    bulk_timings = time_bulk(SAMPLE_WORDS)

    print("Dictionary Enrichment Performance (seconds)")
    print("Words count:", len(SAMPLE_WORDS))
    print(f"Single loop timings: {single_timings} (avg={mean(single_timings):.4f}s)")
    print(f"Bulk timings:        {bulk_timings} (avg={mean(bulk_timings):.4f}s)")
    speedup = mean(single_timings) / max(mean(bulk_timings), 1e-9)
    print(f"Estimated speedup (single vs bulk): {speedup:.2f}x")

if __name__ == "__main__":
    main()
