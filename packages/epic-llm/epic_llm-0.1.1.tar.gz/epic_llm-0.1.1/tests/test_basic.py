"""Simple test to verify test framework is working."""

import pytest


def test_basic_functionality():
    """Test that basic pytest functionality works."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations."""
    test_string = "llm-api-gw"
    assert "api" in test_string
    assert test_string.startswith("llm")


class TestBasicMath:
    """Test class for basic mathematical operations."""

    def test_addition(self):
        """Test addition."""
        assert 2 + 3 == 5

    def test_multiplication(self):
        """Test multiplication."""
        assert 4 * 5 == 20

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (1, 2, 3),
            (5, 10, 15),
            (0, 0, 0),
            (-1, 1, 0),
        ],
    )
    def test_addition_parametrized(self, a, b, expected):
        """Test addition with multiple inputs."""
        assert a + b == expected


@pytest.mark.asyncio
async def test_async_functionality():
    """Test async functionality works."""

    async def async_add(a, b):
        return a + b

    result = await async_add(3, 4)
    assert result == 7
