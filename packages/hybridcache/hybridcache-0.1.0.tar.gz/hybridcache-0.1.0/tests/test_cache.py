from hybridcache import Cache
import pytest
def test_cache_basic_operations():
    cache = Cache(3)
    cache.put_data("A", 1)
    cache.put_data("B", 2)
    cache.put_data("C", 3)

    # Test retrieval increases freq
    assert cache.get_data("A") == 1

    # Now adding D should evict B (lowest freq + oldest)
    cache.put_data("D", 4)

    keys = [list(entry.keys())[0] for entry in cache.arr]
    assert "B" not in keys
    assert "A" in keys
    assert "C" in keys
    assert "D" in keys

def test_update_existing_key():
    cache = Cache(2)
    cache.put_data("X", 100)
    cache.put_data("X", 200)

    value = cache.get_data("X")
    assert value == 200
