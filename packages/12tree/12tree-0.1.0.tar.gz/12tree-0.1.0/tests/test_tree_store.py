"""Tests for 12Tree"""

import pytest
from twelve_tree import FloatTreeStore


class TestFloatTreeStore:
    """Test cases for FloatTreeStore"""

    def test_insert_and_search(self):
        """Test basic insert and search functionality"""
        store = FloatTreeStore()
        store.insert(3.14, "pi")
        store.insert(2.71, "e")

        assert store.search(3.14) == "pi"
        assert store.search(2.71) == "e"
        assert store.search(1.23) is None

    def test_search_with_tolerance(self):
        """Test search with floating point tolerance"""
        store = FloatTreeStore()
        store.insert(3.14159, "pi")

        # Exact match
        assert store.search(3.14159) == "pi"

        # Within tolerance
        assert store.search(3.14159, tolerance=0.001) == "pi"
        assert store.search(3.14159, tolerance=0.00001) == "pi"

        # Outside tolerance
        assert store.search(3.14, tolerance=0.001) is None

    def test_range_search(self):
        """Test range search functionality"""
        store = FloatTreeStore()
        store.insert(1.0, "one")
        store.insert(2.0, "two")
        store.insert(3.0, "three")
        store.insert(4.0, "four")

        results = store.find_range(1.5, 3.5)
        values = [r["value"] for r in results]
        assert 2.0 in values
        assert 3.0 in values
        assert 1.0 not in values
        assert 4.0 not in values

    def test_get_all_values(self):
        """Test getting all values in sorted order"""
        store = FloatTreeStore()
        store.insert(3.0)
        store.insert(1.0)
        store.insert(2.0)

        values = store.get_all_values()
        assert values == [1.0, 2.0, 3.0]

    def test_size_and_empty(self):
        """Test size and empty functionality"""
        store = FloatTreeStore()

        assert store.size() == 0
        assert store.is_empty() is True

        store.insert(1.0)
        assert store.size() == 1
        assert store.is_empty() is False

        store.clear()
        assert store.size() == 0
        assert store.is_empty() is True

    def test_duplicate_values(self):
        """Test handling of duplicate values"""
        store = FloatTreeStore()
        store.insert(1.0, "first")
        store.insert(1.0, "second")

        # Should find one of the values (implementation dependent)
        result = store.search(1.0)
        assert result in ["first", "second"]
        assert store.size() == 2

    def test_invalid_input(self):
        """Test invalid input handling"""
        store = FloatTreeStore()

        # Non-numeric values should raise ValueError
        with pytest.raises(ValueError):
            store.insert("not a number")

        with pytest.raises(ValueError):
            store.insert(None)


if __name__ == "__main__":
    # Run basic tests
    test_store = TestFloatTreeStore()
    test_store.test_insert_and_search()
    test_store.test_search_with_tolerance()
    test_store.test_range_search()
    test_store.test_get_all_values()
    test_store.test_size_and_empty()
    test_store.test_duplicate_values()

    print("All basic tests passed!")
