from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from msl.kcdb.kcdb import to_countries, to_label, to_physics_code
from msl.kcdb.types import Country, ReferenceData, Service

if TYPE_CHECKING:
    from collections.abc import Iterable


def test_to_label_raises() -> None:
    """Test to_label() for an invalid object."""
    with pytest.raises(AttributeError):
        _ = to_label(8)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize(
    ("obj", "expected"),
    [
        ("none", "none"),
        (ReferenceData(id=0, label="lab", value=""), "lab"),
        (Country(id=100, label="100", value="100"), "100"),
    ],
)
def test_to_label(obj: str | ReferenceData, expected: str) -> None:
    """Test to_label() for a valid object."""
    assert to_label(obj) == expected


def test_to_physics_code_raises() -> None:
    """Test to_physics_code() for an invalid object."""
    with pytest.raises(AttributeError):
        _ = to_physics_code(None)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize(
    ("obj", "expected"),
    [
        ("any string", "any string"),
        (Service(id=0, label="", value="", branch=None, physics_code="1"), "1"),  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
    ],
)
def test_to_physics_code(obj: str | Service, expected: str) -> None:
    """Test to_physics_code() for a valid object."""
    assert to_physics_code(obj) == expected


def test_to_countries_raises() -> None:
    """Test to_countries() for an invalid object."""
    with pytest.raises(TypeError):
        _ = to_countries(None)  # type: ignore[arg-type] # pyright: ignore[reportArgumentType]
    with pytest.raises(AttributeError):
        _ = to_countries([1, 2])  # type: ignore[list-item] # pyright: ignore[reportArgumentType]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("any string", ["any string"]),
        (["a", "b", "c"], ["a", "b", "c"]),
        (Country(1, label="a", value="A"), ["a"]),
        ([Country(1, label="a", value="A"), Country(2, label="b", value="B")], ["a", "b"]),
        (("a", Country(2, label="b", value="B"), "c"), ["a", "b", "c"]),
    ],
)
def test_to_countries(value: str | Country | Iterable[str | Country], expected: list[str]) -> None:
    """Test to_countries() for a valid object."""
    assert to_countries(value) == expected
