from lark import Lark
from typing import Any
from pathlib import Path
from .transformer import MojangsonTransformer


__all__ = (
    "parse",
    "simplify",
    "stringify",
    "normalize"
)


GRAMMAR = (Path(__file__).parent / "GRAMMAR.lark").open().read()
_parser = Lark(GRAMMAR, start="main", parser="lalr", transformer=MojangsonTransformer())


def simplify(node: dict[str, Any]) -> Any:
    """
    Recursively simplify a parsed Mojangson node into a pure Python structure.

    Args:
        node (dict[str, Any]): A Mojangson node with "type" and "value".

    Returns:
        Any: A simplified Python value, such as:
            - dict for compounds
            - list for lists
            - primitive values (int, str, float, etc.)
    """
    def transform(value: Any, typ: str) -> Any:
        if typ == 'compound':
            return {k: simplify(v) for k, v in value.items()}
        if typ == 'list':
            arr = value.get('value')
            if not isinstance(arr, list):
                return []
            t = value.get('type')
            return [transform(v, t) for v in arr]
        return value

    return transform(node['value'], node['type'])


def _normalize_string(s: str) -> str:
    """
    Normalize a string for Mojangson output:
    - Remove surrounding quotes if present.
    - Add quotes if the string contains special characters or is empty.
    - Escape internal quotes if needed.

    Args:
        s (str): The input string.

    Returns:
        str: A normalized Mojangson-safe string.
    """
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    needs_quotes = (
        not s or
        any(c in s for c in "'{}[]:;,()§=") or
        not all(c.isalnum() or c in ('_', ' ') for c in s)
    )
    if needs_quotes:
        s = s.replace('"', '\\"')
        return f'"{s}"'
    return s


def _has_missing(arr: list[Any]) -> bool:
    """
    Check whether a list contains None values.

    Args:
        arr (list[Any]): A list of values.

    Returns:
        bool: True if at least one element is None, False otherwise.
    """
    return any(el is None for el in arr)


def _get_suffix(val: Any, typ: str) -> str:
    """
    Get the Mojangson numeric suffix for a value.

    Args:
        val (Any): The numeric value.
        typ (str): The Mojangson type (e.g., "int", "float", "double").

    Returns:
        str: The appropriate suffix (e.g., 'b', 's', 'l', 'f', 'd', or '').
    """
    if typ == 'double':
        try:
            iv = int(val)
            return 'd' if float(iv) == float(val) else ''
        except Exception:
            return ''
    return {'int': '', 'byte': 'b', 'short': 's', 'float': 'f', 'long': 'l', 'string': ''}.get(typ, '')


def _get_array_prefix(typ: str) -> str:
    """
    Get the Mojangson prefix for an array type.

    Args:
        typ (str): The array type ("byteArray", "intArray", "longArray").

    Returns:
        str: The Mojangson array prefix (e.g., 'B;', 'I;', 'L;').
    """
    return typ[0].upper() + ';'


def _stringify_array_values(payload: dict[str, Any]) -> str:
    """
    Convert an array payload into a Mojangson string representation.

    Args:
        payload (dict[str, Any]): A node with "type" and "value".

    Returns:
        str: The stringified array contents.
    """
    arr = payload['value']
    typ = payload['type']
    missing = _has_missing(arr)
    parts: list[str] = []
    for i, v in enumerate(arr):
        if v is None:
            continue
        curr = stringify({"value": v, "type": typ})
        parts.append(f"{i}:{curr}" if missing else curr)
    return ",".join(parts)


def stringify(node: dict[str, Any]) -> str:
    """
    Convert a parsed Mojangson node into a Mojangson string.

    Args:
        node (dict[str, Any]): A Mojangson node.

    Returns:
        str: A Mojangson string representation of the node.
    """
    typ = node['type']
    val = node['value']
    if typ == 'compound':
        parts: list[str] = []
        for key, child in val.items():
            s = stringify(child)
            if child['type'] == 'string':
                if isinstance(child['value'], str):
                    s = _normalize_string(child['value'])
                else:
                    s = str(child['value'])
            parts.append(f"{key}:{s}")
        return '{' + ','.join(parts) + '}'
    elif typ == 'list':
        if not isinstance(val.get('value'), list):
            return '[]'
        inner = _stringify_array_values(val)
        return '[' + inner + ']'
    elif typ in ('byteArray', 'intArray', 'longArray'):
        prefix = _get_array_prefix(typ)
        inner = _stringify_array_values(val)
        return '[' + prefix + inner + ']'
    else:
        s = f"{val}{_get_suffix(val, typ)}"
        if typ == 'string':
            s = _normalize_string(s)
        return s


def parse(text: str) -> dict[str, Any]:
    """
    Parse a Mojangson string into a structured node tree.

    Args:
        text (str): A Mojangson string.

    Returns:
        dict[str, Any]: The parsed node tree.

    Raises:
        ValueError: If the text cannot be parsed.
    """
    try:
        return _parser.parse(text)
    except Exception as e:
        raise ValueError(f"Error parsing text '{text}'") from e


def normalize(text: str) -> str:
    """
    Normalize a Mojangson string by parsing and re-stringifying it.

    Args:
        text (str): The input Mojangson string.

    Returns:
        str: A normalized Mojangson string.
    """
    return stringify(parse(text))
