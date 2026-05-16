"""Tests for :func:`cli.utils.detect_git_remote`.

The helper shells out to ``git``. We never want a real subprocess in the
test loop — every test monkeypatches ``subprocess.run`` with a tiny stub
that returns a synthesized ``CompletedProcess`` (or raises the failure mode
we want to exercise).
"""

from __future__ import annotations

import subprocess
from types import SimpleNamespace

import pytest

from cli.utils import detect_git_remote


def _completed(stdout: str = "", returncode: int = 0) -> SimpleNamespace:
    """Build a stand-in for ``subprocess.CompletedProcess``."""
    return SimpleNamespace(stdout=stdout, stderr="", returncode=returncode)


def test_returns_normalized_https(monkeypatch):
    monkeypatch.setattr(
        "cli.utils.subprocess.run",
        lambda *a, **k: _completed("https://github.com/owner/repo.git\n"),
    )
    assert detect_git_remote() == "https://github.com/owner/repo"


def test_normalizes_ssh_to_https(monkeypatch):
    monkeypatch.setattr(
        "cli.utils.subprocess.run",
        lambda *a, **k: _completed("git@github.com:owner/repo.git\n"),
    )
    assert detect_git_remote() == "https://github.com/owner/repo"


def test_normalizes_gitlab_ssh(monkeypatch):
    monkeypatch.setattr(
        "cli.utils.subprocess.run",
        lambda *a, **k: _completed("git@gitlab.com:owner/repo.git"),
    )
    assert detect_git_remote() == "https://gitlab.com/owner/repo"


def test_returns_none_when_git_missing(monkeypatch):
    def _raise(*_a, **_k):
        raise FileNotFoundError("no git")

    monkeypatch.setattr("cli.utils.subprocess.run", _raise)
    assert detect_git_remote() is None


def test_returns_none_on_timeout(monkeypatch):
    def _raise(*_a, **_k):
        raise subprocess.TimeoutExpired(cmd="git", timeout=2.0)

    monkeypatch.setattr("cli.utils.subprocess.run", _raise)
    assert detect_git_remote() is None


def test_returns_none_on_os_error(monkeypatch):
    def _raise(*_a, **_k):
        raise OSError("denied")

    monkeypatch.setattr("cli.utils.subprocess.run", _raise)
    assert detect_git_remote() is None


def test_returns_none_on_nonzero_exit(monkeypatch):
    # git remote get-url origin returns 128 when there is no origin.
    monkeypatch.setattr(
        "cli.utils.subprocess.run",
        lambda *a, **k: _completed("", returncode=128),
    )
    assert detect_git_remote() is None


def test_returns_none_on_empty_stdout(monkeypatch):
    monkeypatch.setattr(
        "cli.utils.subprocess.run",
        lambda *a, **k: _completed("   \n"),
    )
    assert detect_git_remote() is None


def test_returns_none_when_url_unparseable(monkeypatch):
    monkeypatch.setattr(
        "cli.utils.subprocess.run",
        lambda *a, **k: _completed("not a url"),
    )
    assert detect_git_remote() is None


def test_passes_cwd_through(monkeypatch, tmp_path):
    captured: dict = {}

    def _spy(cmd, **kwargs):
        captured["cwd"] = kwargs.get("cwd")
        captured["cmd"] = cmd
        return _completed("https://github.com/owner/repo")

    monkeypatch.setattr("cli.utils.subprocess.run", _spy)
    detect_git_remote(cwd=str(tmp_path))
    assert captured["cwd"] == str(tmp_path)
    assert captured["cmd"] == ["git", "remote", "get-url", "origin"]


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("https://github.com/owner/repo", "https://github.com/owner/repo"),
        ("https://github.com/owner/repo.git", "https://github.com/owner/repo"),
        ("owner/repo", "https://github.com/owner/repo"),
    ],
)
def test_various_input_shapes(monkeypatch, raw, expected):
    monkeypatch.setattr(
        "cli.utils.subprocess.run",
        lambda *a, **k: _completed(raw),
    )
    assert detect_git_remote() == expected
