# -*- coding: utf-8 -*-

"""
common type aliases and constants
"""

from collections.abc import Iterator
from typing import Any, TypeAlias


ScalarType: TypeAlias = str | int | float | bool | None
CollectionType: TypeAlias = dict | list
ValueType: TypeAlias = ScalarType | CollectionType

SegmentsTuple: TypeAlias = tuple[ScalarType, ...]
IndexType: TypeAlias = str | SegmentsTuple


COMMA_BLANK = ", "
DOT = "."
EMPTY = ""
DOUBLE_QUOTE = '"'
SLASH = "/"


def assured_collection(
    original: Any,
    error_message: str = "Expected a collection (ie. a dict or a list",
) -> CollectionType:
    """assure the original is a dict or a list"""
    if isinstance(original, (dict, list)):
        return original
    #
    raise TypeError(error_message)


def assured_number(
    original: Any, error_message: str = "Expected a number (float or int, not bool)"
) -> float | int:
    """assure the original is a int or float"""
    if not isinstance(original, bool) and isinstance(original, (float, int)):
        return original
    #
    raise TypeError(error_message)


def assured_scalar(
    original: Any,
    error_message: str = "Expected a scalar (ie. a string, an int, a float,"
    " or a bool), or None",
) -> ScalarType:
    """assure the original is a scalar"""
    if isinstance(original, (str, int, float, bool)) or original is None:
        return original
    #
    raise TypeError(error_message)


def assured_dict(original: Any, error_message: str = "Expected a dict") -> dict:
    """assure the original is a dict"""
    if isinstance(original, dict):
        return original
    #
    raise TypeError(error_message)


def assured_float(original: Any, error_message: str = "Expected a float") -> float:
    """assure the original is a float"""
    if isinstance(original, float):
        return original
    #
    raise TypeError(error_message)


def assured_int(
    original: Any, error_message: str = "Expected an int (not bool)"
) -> int:
    """assure the original is an int"""
    if not isinstance(original, bool) and isinstance(original, int):
        return original
    #
    raise TypeError(error_message)


def assured_str(original: Any, error_message: str = "Expected a string") -> str:
    """assure the original is a str"""
    if isinstance(original, str):
        return original
    #
    raise TypeError(error_message)


def assured_list(original: Any, error_message: str = "Expected a list") -> list:
    """assure the original is a list"""
    if isinstance(original, list):
        return original
    #
    raise TypeError(error_message)


def to_text(
    original: Any,
    error_message: str = "Expected a string or bytes",
    encoding: str = "utf-8",
) -> str:
    """Return a str from original.
    If the error message is left blank, convert any type to str
    """
    if isinstance(original, str):
        return original
    #
    if isinstance(original, (bytes, bytearray)):
        return original.decode(encoding)
    #
    if error_message:
        raise TypeError(error_message)
    #
    return str(original)


def partial_traverse(
    start: ValueType,
    segments: SegmentsTuple,
    min_remaining_segments: int = 0,
    fail_on_missing_keys: bool = True,
) -> tuple[ValueType, SegmentsTuple]:
    """Traverse through a data structure starting at the start node,
    until minimum min_remaining_segments of the path are left
    """
    if min_remaining_segments < 0:
        raise ValueError("No negative value allowed here")
    #
    pointer = start
    remaining_segments = list(segments)
    while len(remaining_segments) > min_remaining_segments:
        key = remaining_segments.pop(0)
        try:
            pointer = assured_collection(
                pointer,
                error_message=f"Cannot walk through {pointer!r} using {key!r}",
            )[key]  # type: ignore[index]
        except (IndexError, KeyError) as error:
            if fail_on_missing_keys:
                raise error from error
            #
            return pointer, (key, *remaining_segments)
        #
    #
    return pointer, tuple(remaining_segments)


def full_traverse(
    start: ValueType,
    segments: SegmentsTuple,
) -> ValueType:
    """Traverse through a data structure starting at the start node"""
    return partial_traverse(
        start,
        segments,
        min_remaining_segments=0,
        fail_on_missing_keys=True,
    )[0]


def traverse_with_default(
    start: ValueType,
    segments: SegmentsTuple,
    default: ValueType = None,
) -> ValueType:
    """Traverse through a data structure starting at the start node
    and return the result or the default
    """
    try:
        return full_traverse(start, segments)
    except (KeyError, IndexError):
        return default
    #


def iter_paths(
    start: ValueType,
    previous_segments: SegmentsTuple = (),
) -> Iterator[SegmentsTuple]:
    """Return an iterator over all endpoint paths in the data structure"""
    subitems: list[tuple[ScalarType, ValueType]] = []
    if isinstance(start, dict):
        subitems = list(start.items())
    elif isinstance(start, list):
        subitems = list(enumerate(start))
    #
    for key, value in subitems:
        current_segments: SegmentsTuple = (*previous_segments, key)
        if value and isinstance(value, (dict, list)):
            yield from iter_paths(value, previous_segments=current_segments)
        else:
            yield current_segments
        #
    #


# vim: fileencoding=utf-8 ts=4 sts=4 sw=4 autoindent expandtab syntax=python:
