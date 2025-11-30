"""Tests for fuzzy matching and scoring algorithms."""

from tries.scoring import fuzzy_match, calculate_recency_score, score_directory
from pathlib import Path
import tempfile
import time


def test_exact_match():
    """Exact matches should score highest."""
    score, indices = fuzzy_match("redis", "redis")
    assert score == 1.0
    assert indices == [0, 1, 2, 3, 4]


def test_substring_match():
    """Substring matches should work."""
    score, indices = fuzzy_match("redis", "redis-server")
    assert score > 0.7
    assert indices[:5] == [0, 1, 2, 3, 4]


def test_abbreviation_match():
    """Abbreviations should match."""
    score, indices = fuzzy_match("rds", "redis-server")
    assert score > 0.0
    # r, d, s should be found
    assert len(indices) == 3


def test_case_insensitive():
    """Matching should be case-insensitive."""
    score1, _ = fuzzy_match("Redis", "redis-server")
    score2, _ = fuzzy_match("redis", "redis-server")
    assert score1 == score2


def test_no_match():
    """Non-matching queries should score 0."""
    score, indices = fuzzy_match("xyz", "redis")
    assert score == 0.0
    assert indices == []


def test_empty_query():
    """Empty query should be perfect match."""
    score, indices = fuzzy_match("", "redis")
    assert score == 1.0


def test_contiguous_bonus():
    """Contiguous matches should be detected."""
    # "redis" is contiguous in "redis-server"
    score1, indices1 = fuzzy_match("redis", "redis-server")
    assert indices1 == [0, 1, 2, 3, 4]
    # Matches are found in sequence
    assert score1 == 1.0


def test_recent_directory():
    """Recently modified directories should score high."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        path.touch()
        score = calculate_recency_score(path, max_days=365)
        assert score > 0.9


def test_old_directory():
    """Old directories should score lower than recent ones."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        # Set mtime to 200 days ago (should be < 0.5)
        old_time = time.time() - (200 * 24 * 60 * 60)
        path.touch()
        import os

        os.utime(path, (old_time, old_time))

        score = calculate_recency_score(path, max_days=365)
        assert score < 0.5


def test_nonexistent_path():
    """Non-existent paths should score 0."""
    score = calculate_recency_score(Path("/nonexistent/path"))
    assert score == 0.0


def test_score_combines_metrics():
    """Scoring should combine fuzzy and recency."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "redis-server"
        path.mkdir()

        scored = score_directory("redis", path)

        # Should have some score
        assert scored.score > 0.0
        assert scored.name == "redis-server"
        assert scored.fuzzy_score > 0.0
        assert scored.recency_score > 0.0
