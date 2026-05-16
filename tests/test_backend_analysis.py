"""Unit tests for :mod:`backend.analysis`.

Pure math + GitHub-fetch stubs. No FastAPI involvement — that lives in
``test_backend_app.py``.
"""

from __future__ import annotations

import httpx
import pytest

from backend.analysis import (
    DEMO_RESPONSE,
    analyze,
    fetch_pr_files,
    heuristic_from_pr_number,
    is_demo,
    label_for,
    make_report_id,
    score_from_files,
)
from cli.demo_fixture import DEMO_PR_ID, DEMO_REPO_URL


# --------------------------------------------------------------------- #
# is_demo
# --------------------------------------------------------------------- #
def test_is_demo_exact_match():
    assert is_demo(DEMO_PR_ID, DEMO_REPO_URL) is True


def test_is_demo_short_form_repo():
    # Equivalent short form should still match the canonical URL.
    assert is_demo(DEMO_PR_ID, "prism-demo/payment-service") is True


def test_is_demo_wrong_pr():
    assert is_demo("pr-1", DEMO_REPO_URL) is False


def test_is_demo_wrong_repo():
    assert is_demo(DEMO_PR_ID, "https://github.com/other/repo") is False


def test_is_demo_unparseable_repo():
    assert is_demo(DEMO_PR_ID, "not a url at all") is False


# --------------------------------------------------------------------- #
# label_for
# --------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "score, expected",
    [
        (0, "LOW"),
        (33, "LOW"),
        (34, "MEDIUM"),
        (66, "MEDIUM"),
        (67, "HIGH"),
        (100, "HIGH"),
    ],
)
def test_label_thresholds(score, expected):
    assert label_for(score) == expected


# --------------------------------------------------------------------- #
# make_report_id
# --------------------------------------------------------------------- #
def test_report_id_deterministic():
    a = make_report_id("pr-1", "https://github.com/owner/repo")
    b = make_report_id("pr-1", "https://github.com/owner/repo")
    assert a == b
    assert len(a) == 8


def test_report_id_changes_with_inputs():
    a = make_report_id("pr-1", "https://github.com/owner/repo")
    b = make_report_id("pr-2", "https://github.com/owner/repo")
    c = make_report_id("pr-1", "https://github.com/other/repo")
    assert a != b
    assert a != c


# --------------------------------------------------------------------- #
# score_from_files
# --------------------------------------------------------------------- #
def test_score_empty_files():
    assert score_from_files([]) == (0, 0)


def test_score_basic_math():
    files = [
        {"additions": 10, "deletions": 5},
        {"additions": 0, "deletions": 0},
    ]
    # 5*2 + 0.05*15 = 10.75 -> 10
    score, impacted = score_from_files(files)
    assert score == 10
    assert impacted == 2


def test_score_caps_at_100():
    # 100 files × 5 = 500 base, well over the cap.
    files = [{"additions": 1, "deletions": 0}] * 100
    score, impacted = score_from_files(files)
    assert score == 100
    assert impacted == 100


def test_score_handles_missing_additions_field():
    # Defensive: GitHub *always* returns these, but bad fixtures shouldn't crash.
    score, _ = score_from_files([{}])
    assert score == 5


# --------------------------------------------------------------------- #
# heuristic_from_pr_number
# --------------------------------------------------------------------- #
def test_heuristic_deterministic():
    assert heuristic_from_pr_number(7) == heuristic_from_pr_number(7)


def test_heuristic_in_range():
    for pr in (1, 42, 142, 9999):
        score, impacted = heuristic_from_pr_number(pr)
        assert 0 <= score < 100
        assert 1 <= impacted <= 12


# --------------------------------------------------------------------- #
# fetch_pr_files
# --------------------------------------------------------------------- #
def _client_returning(status: int, body):
    """Build an ``httpx.Client`` whose transport returns the given response."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_fetch_pr_files_happy():
    body = [{"filename": "a.py", "additions": 3, "deletions": 1}]
    files = fetch_pr_files("owner", "repo", 1, None, client=_client_returning(200, body))
    assert files == body


def test_fetch_pr_files_raises_on_401():
    client = _client_returning(401, {"message": "Bad credentials"})
    with pytest.raises(httpx.HTTPError):
        fetch_pr_files("owner", "repo", 1, None, client=client)


def test_fetch_pr_files_raises_on_non_list_body():
    client = _client_returning(200, {"oops": "object not list"})
    with pytest.raises(httpx.HTTPError):
        fetch_pr_files("owner", "repo", 1, None, client=client)


def test_fetch_pr_files_sets_auth_header():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["auth"] = request.headers.get("authorization")
        return httpx.Response(200, json=[])

    client = httpx.Client(transport=httpx.MockTransport(handler))
    fetch_pr_files("owner", "repo", 1, "ghp_secret", client=client)
    assert captured["auth"] == "Bearer ghp_secret"


# --------------------------------------------------------------------- #
# analyze (top-level cascade)
# --------------------------------------------------------------------- #
def test_analyze_demo_passthrough():
    result = analyze(DEMO_PR_ID, DEMO_REPO_URL)
    assert result == DEMO_RESPONSE


def test_analyze_complete_path():
    files = [{"additions": 20, "deletions": 0}, {"additions": 5, "deletions": 5}]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=files)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    result = analyze("pr-7", "https://github.com/owner/repo", http_client=client)
    assert result["status"] == "COMPLETE"
    assert result["impacted_node_count"] == 2
    assert result["risk_score"] == 11  # 5*2 + 0.05*30 = 11.5 -> 11
    assert result["risk_label"] == "LOW"
    # report_id must be derived from inputs, not the random.
    assert result["report_id"] == make_report_id("pr-7", "https://github.com/owner/repo")
    assert result["dashboard_url"].endswith(result["report_id"])


def test_analyze_falls_back_to_partial_on_github_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"message": "rate limited"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    result = analyze("pr-42", "https://github.com/owner/repo", http_client=client)
    assert result["status"] == "PARTIAL"
    # Risk score must come from the deterministic heuristic.
    assert result["risk_score"] == heuristic_from_pr_number(42)[0]
    assert result["impacted_node_count"] == heuristic_from_pr_number(42)[1]
