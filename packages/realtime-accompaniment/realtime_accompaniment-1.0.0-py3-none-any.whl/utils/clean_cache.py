# Script to clean the cache given a type of cache
# take in argument while running the script
# user should run python clean_cache.py --cache_type <cache_type> --cache_dir <cache_dir>

# cache_type:
# - eval
#   - smod_eval
#   - stsm_eval
#   - baseline_eval
# - features
#   - chroma_stft_features
#   - chroma_cens_features
#   - chroma_cqt_features
# - tsm
#   - xh
#   - xp

import os
import argparse


def clean_cache(cache_type, cache_dir="cache"):
    """
    Clean the cache for a given cache type.

    Args:
        cache_type: type of cache to clean
        cache_dir: directory to clean
    """
    # check if cache_dir exists
    if not os.path.exists(cache_dir):
        raise FileNotFoundError(f"Cache directory {cache_dir} does not exist")

    # xh and xp are tsm outputs
    if cache_type == "tsm":
        clean_cache("xh", cache_dir)
        clean_cache("xp", cache_dir)

    # find all files in the cache directory that ends with f'{cache_type}.pkl'
    cache_files = [f for f in os.listdir(cache_dir) if f.endswith(f"{cache_type}.pkl")]
    for file in cache_files:
        os.remove(os.path.join(cache_dir, file))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache_type", type=str, required=True)
    parser.add_argument("--cache_dir", type=str, default="cache")
    args = parser.parse_args()
    clean_cache(args.cache_type, args.cache_dir)
