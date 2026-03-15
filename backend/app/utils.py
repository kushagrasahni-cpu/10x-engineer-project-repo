"""Utility functions for PromptLab.

Provides helper functions for sorting, filtering, searching, validating,
and extracting variables from prompts.
"""

import re
from typing import List
from app.models import Prompt


def sort_prompts_by_date(prompts: List[Prompt], descending: bool = True) -> List[Prompt]:
    """Sort prompts by their creation date.

    Args:
        prompts: The list of prompts to sort.
        descending: If True (default), newest prompts appear first.
            If False, oldest prompts appear first.

    Returns:
        A new list of prompts sorted by ``created_at``.

    Example:
        >>> sorted_prompts = sort_prompts_by_date(prompts, descending=True)
        >>> sorted_prompts[0].created_at >= sorted_prompts[-1].created_at
        True
    """
    return sorted(prompts, key=lambda p: p.created_at, reverse=descending)


def filter_prompts_by_collection(prompts: List[Prompt], collection_id: str) -> List[Prompt]:
    """Filter prompts to only those belonging to a specific collection.

    Args:
        prompts: The list of prompts to filter.
        collection_id: The UUID of the collection to match against.

    Returns:
        A list of prompts whose ``collection_id`` matches the given ID.

    Example:
        >>> filtered = filter_prompts_by_collection(prompts, "col-123")
        >>> all(p.collection_id == "col-123" for p in filtered)
        True
    """
    return [p for p in prompts if p.collection_id == collection_id]


def search_prompts(prompts: List[Prompt], query: str) -> List[Prompt]:
    """Search prompts by matching a query against title and description.

    Performs a case-insensitive substring match. A prompt is included
    in the results if the query appears in either its title or description.

    Args:
        prompts: The list of prompts to search.
        query: The search string to match against.

    Returns:
        A list of prompts that match the search query.

    Example:
        >>> results = search_prompts(prompts, "review")
        >>> all("review" in p.title.lower() or
        ...     (p.description and "review" in p.description.lower())
        ...     for p in results)
        True
    """
    query_lower = query.lower()
    return [
        p for p in prompts
        if query_lower in p.title.lower()
        or (p.description and query_lower in p.description.lower())
    ]


def validate_prompt_content(content: str) -> bool:
    """Validate that prompt content meets minimum requirements.

    A valid prompt must not be empty, not be only whitespace, and be
    at least 10 characters long after stripping whitespace.

    Args:
        content: The prompt content string to validate.

    Returns:
        True if the content is valid, False otherwise.

    Example:
        >>> validate_prompt_content("Short")
        False
        >>> validate_prompt_content("This is a valid prompt content")
        True
    """
    if not content or not content.strip():
        return False
    return len(content.strip()) >= 10


def extract_variables(content: str) -> List[str]:
    """Extract template variable names from prompt content.

    Scans the content for Mustache-style ``{{variable_name}}`` placeholders
    and returns the variable names found.

    Args:
        content: The prompt content string to scan for variables.

    Returns:
        A list of variable name strings extracted from the content.

    Example:
        >>> extract_variables("Hello {{name}}, welcome to {{place}}")
        ['name', 'place']
        >>> extract_variables("No variables here")
        []
    """
    pattern = r'\{\{(\w+)\}\}'
    return re.findall(pattern, content)
