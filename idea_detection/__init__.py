"""Idea-level fallacy detection. The checker, not the extractor, issues verdicts."""

from idea_detection.check import check_passage, load_catalog, load_patterns
from idea_detection.nested import check_nested

__all__ = ["check_passage", "check_nested", "load_catalog", "load_patterns"]
