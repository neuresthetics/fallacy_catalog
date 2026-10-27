"""Idea-level fallacy detection. The checker, not the extractor, issues verdicts."""

from idea_detection.check import check_passage, load_catalog, load_patterns

__all__ = ["check_passage", "load_catalog", "load_patterns"]
