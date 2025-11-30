"""Fuzzy matching and scoring algorithm for try experiments."""

import time
from pathlib import Path
from typing import NamedTuple


class ScoredDirectory(NamedTuple):
    """A directory with its score and scoring details."""

    path: Path
    name: str
    score: float
    fuzzy_score: float
    recency_score: float
    matched_indices: list[int]


def fuzzy_match(query: str, target: str) -> tuple[float, list[int]]:
    """Perform fuzzy matching with character sequence matching.

    Scores based on:
    - Contiguous character matches (highest)
    - Consecutive character matches
    - Scattered character matches (lowest)

    Args:
        query: The search query
        target: The string to match against

    Returns:
        Tuple of (score 0-1, list of matched character indices)
    """
    query = query.lower()
    target = target.lower()

    if not query:
        return 1.0, []

    if not target:
        return 0.0, []

    matched_indices = []
    target_idx = 0
    query_idx = 0

    # Find all possible character matches
    while query_idx < len(query) and target_idx < len(target):
        if query[query_idx] == target[target_idx]:
            matched_indices.append(target_idx)
            query_idx += 1
        target_idx += 1

    # If we didn't match all query characters, no match
    if query_idx < len(query):
        return 0.0, []

    # Calculate score based on match quality
    # Start with perfect match score
    score = 1.0

    # Penalty for gaps between matches
    if matched_indices:
        gaps = 0
        for i in range(1, len(matched_indices)):
            gap = matched_indices[i] - matched_indices[i - 1] - 1
            gaps += gap

        # Each gap reduces score by 1-2%
        gap_penalty = min(0.5, gaps * 0.01)
        score -= gap_penalty

    # Bonus for matching at start of string or after separator
    bonus = 0.0
    if matched_indices and matched_indices[0] == 0:
        bonus += 0.1

    # Bonus for contiguous match
    if len(matched_indices) > 1:
        max_contiguous = 1
        current_contiguous = 1
        for i in range(1, len(matched_indices)):
            if matched_indices[i] == matched_indices[i - 1] + 1:
                current_contiguous += 1
                max_contiguous = max(max_contiguous, current_contiguous)
            else:
                current_contiguous = 1

        if max_contiguous >= 3:
            bonus += 0.1

    score = min(1.0, score + bonus)

    return max(0.0, score), matched_indices


def calculate_recency_score(path: Path, max_days: int = 365) -> float:
    """Calculate recency score based on modification time.

    Args:
        path: Path to the directory
        max_days: Maximum days in the recency window

    Returns:
        Score from 0-1, where 1 is most recent
    """
    try:
        mtime = path.stat().st_mtime
    except (OSError, FileNotFoundError):
        return 0.0

    now = time.time()
    seconds_since = now - mtime
    days_since = seconds_since / (24 * 60 * 60)

    if days_since < 0:
        days_since = 0
    if days_since > max_days:
        days_since = max_days

    return 1.0 - (days_since / max_days)


def score_directory(
    query: str,
    path: Path,
    fuzzy_weight: float = 0.7,
    recency_weight: float = 0.3,
) -> ScoredDirectory:
    """Score a directory based on fuzzy match and recency.

    Args:
        query: The search query
        path: The directory path to score
        fuzzy_weight: Weight for fuzzy match score (0-1)
        recency_weight: Weight for recency score (0-1)

    Returns:
        ScoredDirectory with all scoring details
    """
    name = path.name

    fuzzy_score, matched_indices = fuzzy_match(query, name)
    recency_score = calculate_recency_score(path)

    # Name length penalty: shorter names get slight boost (up to 10% bonus)
    name_length_bonus = max(0.0, 0.1 * (1.0 - min(1.0, len(name) / 50.0)))

    final_score = (
        fuzzy_score * fuzzy_weight
        + recency_score * recency_weight
        + name_length_bonus * 0.1
    )
    final_score = min(1.0, final_score)

    return ScoredDirectory(
        path=path,
        name=name,
        score=final_score,
        fuzzy_score=fuzzy_score,
        recency_score=recency_score,
        matched_indices=matched_indices,
    )


def score_directories(
    query: str,
    directories: list[Path],
    min_score: float = 0.0,
) -> list[ScoredDirectory]:
    """Score and sort multiple directories by combined score.

    Args:
        query: The search query
        directories: List of directory paths to score
        min_score: Minimum score to include in results (0-1)

    Returns:
        Sorted list of ScoredDirectory, highest score first
    """
    scored = [score_directory(query, d) for d in directories]

    # Filter by minimum score and sort by score (descending)
    results = [s for s in scored if s.score >= min_score]
    return sorted(results, key=lambda s: s.score, reverse=True)
