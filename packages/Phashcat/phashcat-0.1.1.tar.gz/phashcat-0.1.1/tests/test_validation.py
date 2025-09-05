import pytest
from Phashcat import hashcat, flags

def test_boolean_switch_wrong_type_raises():
    with pytest.raises(TypeError):
        hashcat().set(flags.STATUS, "yes")  # should be bool/None

def test_numeric_flag_wrong_type_raises():
    with pytest.raises(TypeError):
        hashcat().hash_type("zero")  # must be numeric

def test_accepts_numeric_but_not_bool_as_number():
    # bool is subclass of int; builder must reject True for Num
    with pytest.raises(TypeError):
        hashcat().hash_type(True)

def test_generic_string_values_ok_for_str_kinds():
    b = hashcat().set(flags.SESSION, 12345)  # str-able value allowed
    assert b._opts[flags.SESSION] == 12345
