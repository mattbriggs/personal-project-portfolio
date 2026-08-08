"""Domain unit tests for slug generation."""

import pytest

from portfolio_manager.domain.slug import slugify


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("My Novel", "my-novel"),
        ("  Spaced  Out  ", "spaced-out"),
        ("Punctuation! & Symbols?", "punctuation-symbols"),
        ("under_score", "under-score"),
        ("CAPS Lock", "caps-lock"),
    ],
)
def test_slugify(name: str, expected: str) -> None:
    assert slugify(name) == expected
