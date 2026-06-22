import pytest

from scyther.routing.parser import ParsedCommand, Parser


def test_simple_slash_command():
    result = Parser.parse("/help")
    assert result.name == "/help"
    assert result.args == ()
    assert result.raw == "/help"


def test_command_with_single_arg():
    result = Parser.parse("/tree 2")
    assert result.name == "/tree"
    assert result.args == ("2",)


def test_command_with_multiple_args():
    result = Parser.parse("/open path/to/README.md")
    assert result.name == "/open"
    assert result.args == ("path/to/README.md",)


def test_command_with_spaced_filename():
    result = Parser.parse("/find config.py")
    assert result.name == "/find"
    assert result.args == ("config.py",)


def test_empty_input_returns_empty_name():
    result = Parser.parse("")
    assert result.name == ""
    assert result.args == ()


def test_whitespace_only_returns_empty_name():
    result = Parser.parse("   ")
    assert result.name == ""
    assert result.args == ()


def test_command_name_is_lowercased():
    result = Parser.parse("/HELP")
    assert result.name == "/help"


def test_mixed_case_command_is_lowercased():
    result = Parser.parse("/Tree 3")
    assert result.name == "/tree"
    assert result.args == ("3",)


def test_extra_surrounding_whitespace_is_stripped():
    result = Parser.parse("  /tree  3  ")
    assert result.name == "/tree"
    assert result.args == ("3",)


def test_raw_preserves_original_input():
    raw = "  /tree  3  "
    result = Parser.parse(raw)
    assert result.raw == raw


def test_parsed_command_is_immutable():
    result = Parser.parse("/help")
    with pytest.raises((AttributeError, TypeError)):
        result.name = "/other"  # type: ignore[misc]


def test_plain_text_input_has_no_slash_prefix():
    result = Parser.parse("show tree")
    assert result.name == "show"
    assert result.args == ("tree",)


def test_quoted_arguments():
    result = Parser.parse('/replace README.md "hello world" "goodbye world"')
    assert result.name == "/replace"
    assert result.args == ("README.md", "hello world", "goodbye world")


def test_escaped_quotes():
    result = Parser.parse('/write file.txt "hello \\"world\\""')
    assert result.name == "/write"
    assert result.args == ("file.txt", 'hello "world"')


def test_unmatched_quote_raises_value_error():
    with pytest.raises(ValueError):
        Parser.parse('/write file.txt "hello world')
