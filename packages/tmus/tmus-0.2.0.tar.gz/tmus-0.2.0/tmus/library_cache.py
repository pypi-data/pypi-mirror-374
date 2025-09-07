import os
import json

def get_cache_path(music_dir):
    cache_name = f"library_cache_{os.path.basename(os.path.abspath(music_dir))}.json"
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), cache_name)


def load_library_cache(music_dir):
    cache_path = get_cache_path(music_dir)
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_library_cache(music_dir, library):
    cache_path = get_cache_path(music_dir)
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(library, f, ensure_ascii=False, indent=2)


def update_library_cache(music_dir, scan_func):
    cached = load_library_cache(music_dir)
    current = scan_func(music_dir)
    if cached is None or cached != current:
        save_library_cache(music_dir, current)
        return current
    return cached
