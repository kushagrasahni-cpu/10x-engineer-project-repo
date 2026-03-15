"""Tests for utility functions."""

from app.models import Prompt
from app.utils import (
    sort_prompts_by_date,
    filter_prompts_by_collection,
    search_prompts,
    validate_prompt_content,
    extract_variables,
)
import time


class TestSortPromptsByDate:
    """Tests for sort_prompts_by_date."""

    def test_sort_descending(self):
        p1 = Prompt(title="First", content="C")
        time.sleep(0.01)
        p2 = Prompt(title="Second", content="C")
        result = sort_prompts_by_date([p1, p2], descending=True)
        assert result[0].title == "Second"
        assert result[1].title == "First"

    def test_sort_ascending(self):
        p1 = Prompt(title="First", content="C")
        time.sleep(0.01)
        p2 = Prompt(title="Second", content="C")
        result = sort_prompts_by_date([p1, p2], descending=False)
        assert result[0].title == "First"
        assert result[1].title == "Second"

    def test_sort_empty_list(self):
        assert sort_prompts_by_date([], descending=True) == []

    def test_sort_single_item(self):
        p = Prompt(title="Only", content="C")
        result = sort_prompts_by_date([p])
        assert len(result) == 1
        assert result[0].title == "Only"


class TestFilterPromptsByCollection:
    """Tests for filter_prompts_by_collection."""

    def test_filter_matching(self):
        p1 = Prompt(title="A", content="C", collection_id="col-1")
        p2 = Prompt(title="B", content="C", collection_id="col-2")
        result = filter_prompts_by_collection([p1, p2], "col-1")
        assert len(result) == 1
        assert result[0].title == "A"

    def test_filter_no_match(self):
        p1 = Prompt(title="A", content="C", collection_id="col-1")
        result = filter_prompts_by_collection([p1], "col-999")
        assert result == []

    def test_filter_empty_list(self):
        assert filter_prompts_by_collection([], "col-1") == []

    def test_filter_none_collection_id(self):
        p1 = Prompt(title="A", content="C")
        result = filter_prompts_by_collection([p1], "col-1")
        assert result == []


class TestSearchPrompts:
    """Tests for search_prompts."""

    def test_search_by_title(self):
        p1 = Prompt(title="Code Review", content="C")
        p2 = Prompt(title="Marketing", content="C")
        result = search_prompts([p1, p2], "review")
        assert len(result) == 1
        assert result[0].title == "Code Review"

    def test_search_by_description(self):
        p = Prompt(title="Generic", content="C", description="Helps with code review")
        result = search_prompts([p], "review")
        assert len(result) == 1

    def test_search_case_insensitive(self):
        p = Prompt(title="Code Review", content="C")
        result = search_prompts([p], "CODE REVIEW")
        assert len(result) == 1

    def test_search_substring(self):
        p = Prompt(title="Code Review Assistant", content="C")
        result = search_prompts([p], "rev")
        assert len(result) == 1

    def test_search_no_match(self):
        p = Prompt(title="Code Review", content="C")
        result = search_prompts([p], "marketing")
        assert result == []

    def test_search_empty_list(self):
        assert search_prompts([], "query") == []

    def test_search_no_description(self):
        p = Prompt(title="Title", content="C", description=None)
        result = search_prompts([p], "nonexistent")
        assert result == []


class TestValidatePromptContent:
    """Tests for validate_prompt_content."""

    def test_valid_content(self):
        assert validate_prompt_content("This is valid content") is True

    def test_exactly_ten_chars(self):
        assert validate_prompt_content("1234567890") is True

    def test_too_short(self):
        assert validate_prompt_content("Short") is False

    def test_empty_string(self):
        assert validate_prompt_content("") is False

    def test_whitespace_only(self):
        assert validate_prompt_content("   ") is False

    def test_whitespace_padded_short(self):
        assert validate_prompt_content("   Hi   ") is False

    def test_whitespace_padded_valid(self):
        assert validate_prompt_content("   1234567890   ") is True


class TestExtractVariables:
    """Tests for extract_variables."""

    def test_multiple_variables(self):
        result = extract_variables("Hello {{name}}, welcome to {{place}}")
        assert result == ["name", "place"]

    def test_no_variables(self):
        assert extract_variables("No variables here") == []

    def test_single_variable(self):
        result = extract_variables("Summarize {{document}}")
        assert result == ["document"]

    def test_duplicate_variables(self):
        result = extract_variables("{{name}} and {{name}} again")
        assert result == ["name", "name"]

    def test_empty_string(self):
        assert extract_variables("") == []

    def test_incomplete_braces(self):
        assert extract_variables("Hello {name}") == []
        assert extract_variables("Hello {{name}") == []

    def test_variable_with_underscores(self):
        result = extract_variables("{{my_var}}")
        assert result == ["my_var"]
