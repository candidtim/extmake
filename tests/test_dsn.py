import pytest

from extmake import dsn


def test_parse():
    assert dsn.parse("") == {}, "empty string"
    assert dsn.parse("foo=bar") == {"foo": "bar"}, "single key-value pair"
    assert dsn.parse("foo=bar;baz=qux") == {
        "foo": "bar",
        "baz": "qux",
    }, "many key-value pairs"
    assert dsn.parse("foo=bar;") == {"foo": "bar"}, "trailing semicolon"
    assert dsn.parse("foo=") == {"foo": ""}, "empty value"
    with pytest.raises(ValueError):
        dsn.parse("lorem ipsum") == {}
