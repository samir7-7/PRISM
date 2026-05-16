"""Tests for the validation helpers in ``cli.utils``."""

from __future__ import annotations

import pytest

from cli.utils import (
    extract_pr_number,
    get_repository_display_name,
    is_valid_url,
    normalize_backend_url,
    normalize_pr_identifier,
    parse_repository_url,
    sanitize_filename,
    truncate_text,
    validate_port,
    validate_positive_integer,
    validate_pr_identifier,
    validate_repository_url,
)


# --------------------------------------------------------------------- #
# PR identifier
# --------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "value",
    ["123", "#123", "pr-123", "PR-123", "pull-123", "PULL-123", "  42  "],
)
def test_validate_pr_identifier_accepts_known_formats(value):
    assert validate_pr_identifier(value) is True


@pytest.mark.parametrize("value", ["", "abc", "pr-", "pr-abc", None, "#"])
def test_validate_pr_identifier_rejects_garbage(value):
    assert validate_pr_identifier(value) is False


@pytest.mark.parametrize(
    "raw, expected",
    [("#123", "123"), ("pr-456", "456"), ("PULL-7", "7"), ("9", "9")],
)
def test_normalize_pr_identifier(raw, expected):
    assert normalize_pr_identifier(raw) == expected


def test_normalize_pr_identifier_raises_on_invalid():
    with pytest.raises(ValueError):
        normalize_pr_identifier("not-a-pr")


def test_extract_pr_number_returns_int():
    assert extract_pr_number("pr-99") == 99


# --------------------------------------------------------------------- #
# Repository URL
# --------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "value",
    [
        "https://github.com/owner/repo",
        "https://github.com/owner/repo.git",
        "owner/repo",
        "git@github.com:owner/repo.git",
        "https://gitlab.com/owner/repo",
    ],
)
def test_validate_repository_url_accepts(value):
    assert validate_repository_url(value) is True


@pytest.mark.parametrize("value", ["", "invalid", "github.com/owner/repo", None])
def test_validate_repository_url_rejects(value):
    assert validate_repository_url(value) is False


def test_parse_repository_url_short_form():
    parsed = parse_repository_url("owner/repo")
    assert parsed["owner"] == "owner"
    assert parsed["repo"] == "repo"
    assert parsed["platform"] == "github"
    assert parsed["url"] == "https://github.com/owner/repo"


def test_parse_repository_url_https():
    parsed = parse_repository_url("https://github.com/anthropics/sdk")
    assert parsed["owner"] == "anthropics"
    assert parsed["repo"] == "sdk"


def test_parse_repository_url_ssh():
    parsed = parse_repository_url("git@github.com:owner/repo.git")
    assert parsed["owner"] == "owner"
    assert parsed["repo"] == "repo"


def test_get_repository_display_name_falls_back_to_input():
    # Invalid input → return as-is rather than raising.
    assert get_repository_display_name("not a url") == "not a url"


# --------------------------------------------------------------------- #
# URL helpers
# --------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "url, ok",
    [
        ("http://localhost:8000", True),
        ("https://api.example.com", True),
        ("not a url", False),
        ("", False),
    ],
)
def test_is_valid_url(url, ok):
    assert is_valid_url(url) is ok


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("http://localhost:8000/", "http://localhost:8000"),
        ("localhost:8000", "http://localhost:8000"),
        ("  https://api.example.com  ", "https://api.example.com"),
    ],
)
def test_normalize_backend_url(raw, expected):
    assert normalize_backend_url(raw) == expected


# --------------------------------------------------------------------- #
# String / number helpers
# --------------------------------------------------------------------- #
def test_truncate_text_short_passes_through():
    assert truncate_text("hello", 10) == "hello"


def test_truncate_text_long_gets_suffix():
    assert truncate_text("This is a very long text", 10) == "This is..."


def test_sanitize_filename_replaces_invalid_chars():
    assert sanitize_filename("my/file:name.txt") == "my_file_name.txt"


def test_validate_positive_integer_accepts():
    assert validate_positive_integer("123", "timeout") == 123


@pytest.mark.parametrize("bad", ["0", "-1", "abc"])
def test_validate_positive_integer_rejects(bad):
    with pytest.raises(ValueError):
        validate_positive_integer(bad, "timeout")


@pytest.mark.parametrize("port", ["1", "8000", "65535"])
def test_validate_port_accepts(port):
    assert validate_port(port) == int(port)


@pytest.mark.parametrize("port", ["0", "70000", "abc"])
def test_validate_port_rejects(port):
    with pytest.raises(ValueError):
        validate_port(port)
