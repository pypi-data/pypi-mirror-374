import pytest
from Phashcat import hashcat, flags

def test_none_to_numeric_is_ignored_or_raises():
    # Our builder rejects wrong type where appropriate:
    with pytest.raises(TypeError):
        hashcat().hash_type(None)  # must be numeric

def test_boolean_switch_false_not_emitted():
    argv = hashcat().set(flags.STATUS, False).value()
    assert flags.STATUS not in argv

def test_charset_requires_string_like():
    # We allow any str-able — numbers pass through (stringified).
    b = hashcat().cs1(123)
    argv = b.value()
    assert flags.CUSTOM_CHARSET1 in argv
    assert argv[argv.index(flags.CUSTOM_CHARSET1) + 1] == "123"

def test_separator_char_kind_is_stringlike():
    b = hashcat().set(flags.SEPARATOR, ":")
    argv = b.value()
    assert flags.SEPARATOR in argv and argv[argv.index(flags.SEPARATOR) + 1] == ":"
