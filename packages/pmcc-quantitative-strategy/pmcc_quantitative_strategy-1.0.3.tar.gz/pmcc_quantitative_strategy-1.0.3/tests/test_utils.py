from __future__ import annotations

from pmcc.utils import is_number


def test_is_number_includes_int_float_excludes_bool_and_others():
    assert is_number(0)
    assert is_number(3.14)
    assert not is_number(True)  # bool is subclass of int but should be excluded
    assert not is_number("1")
    assert not is_number(None)
