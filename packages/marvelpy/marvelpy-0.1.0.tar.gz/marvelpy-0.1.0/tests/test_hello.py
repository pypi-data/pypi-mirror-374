"""Tests for the hello module."""

from marvelpy.hello import hello_world


def test_hello_world():
    """Test the hello_world function."""
    result = hello_world()
    assert result == "Hello from Marvelpy!"
    assert isinstance(result, str)


def test_hello_world_returns_string():
    """Test that hello_world returns a string type."""
    result = hello_world()
    assert isinstance(result, str)
    assert len(result) > 0


def test_hello_world_contains_marvelpy():
    """Test that hello_world contains the package name."""
    result = hello_world()
    assert "Marvelpy" in result
