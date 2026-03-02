# Feature Specification: Tagging System

## Overview

The tagging system allows users to attach descriptive tags to prompts for flexible categorization beyond the single-collection hierarchy. Tags are short labels (e.g., "python", "code-review", "marketing") that can be freely assigned to any prompt. Users can filter and search prompts by one or more tags, enabling cross-collection discovery.

While collections provide a single hierarchical grouping, tags provide a flat, many-to-many labeling system that supports overlapping categories.

---

## User Stories

### US-1: Add Tags When Creating a Prompt

**As** a prompt engineer,
**I want** to assign tags to a prompt when I create it,
**so that** I can categorize it from the start.

**Acceptance Criteria:**
- The POST `/prompts` endpoint accepts an optional `tags` field (list of strings).
- Tags are stored as lowercase, trimmed strings.
- Duplicate tags in the input are deduplicated automatically.
- Empty strings and whitespace-only strings are rejected.
- Each tag must be 1–50 characters and contain only alphanumeric characters, hyphens, and underscores.
- A prompt can have a maximum of 10 tags.

### US-2: Update Tags on a Prompt

**As** a prompt engineer,
**I want** to add or remove tags from an existing prompt,
**so that** I can recategorize it as my needs change.

**Acceptance Criteria:**
- The PUT endpoint replaces all tags with the provided list.
- The PATCH endpoint updates tags only if the `tags` field is included in the request body.
- Setting `tags` to an empty list `[]` removes all tags from the prompt.
- The same validation rules apply (lowercase, deduplicated, max 10, valid format).

### US-3: Filter Prompts by Tag

**As** a prompt engineer,
**I want** to filter prompts by one or more tags,
**so that** I can find all prompts in a specific category.

**Acceptance Criteria:**
- The GET `/prompts` endpoint accepts a `tags` query parameter.
- Multiple tags can be specified as a comma-separated list: `?tags=python,code-review`.
- Filtering returns prompts that have **all** specified tags (AND logic).
- Tag filtering can be combined with the existing `collection_id` and `search` parameters.
- Tag matching is case-insensitive.

### US-4: List All Tags

**As** a prompt engineer,
**I want** to see all tags that are currently in use,
**so that** I can discover existing categories and avoid creating duplicates.

**Acceptance Criteria:**
- A GET endpoint returns all unique tags across all prompts.
- Each tag entry includes the tag name and the count of prompts using it.
- Tags are sorted alphabetically.
- Tags that are no longer used by any prompt are not included.

### US-5: View Tags on a Prompt

**As** a prompt engineer,
**I want** to see the tags on any prompt I view,
**so that** I understand how it's categorized.

**Acceptance Criteria:**
- The `tags` field is included in all prompt responses (GET single, GET list, POST, PUT, PATCH).
- Tags are returned as a sorted list of strings.

---

## Data Model Changes

### Prompt Model Updates

Add a `tags` field to the prompt models:

```python
class PromptBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list, max_length=10)
```

```python
class PromptUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None
    tags: Optional[List[str]] = None
```

### New Response Model

```python
class TagInfo(BaseModel):
    """A single tag with its usage count."""

    name: str
    count: int


class TagList(BaseModel):
    """Response wrapper for a list of tags."""

    tags: List[TagInfo]
    total: int
```

### Tag Validation

Add a validator to normalize and validate tags:

```python
from pydantic import field_validator

@field_validator("tags", mode="before")
@classmethod
def validate_tags(cls, v: List[str]) -> List[str]:
    """Normalize and validate tag list.

    - Strips whitespace and converts to lowercase.
    - Removes duplicates while preserving order.
    - Validates each tag is 1-50 chars, alphanumeric/hyphens/underscores only.
    - Limits to 10 tags maximum.
    """
```

### Storage Changes

Add to the `Storage` class:

```python
def get_all_tags(self) -> List[TagInfo]
    # Aggregate tags across all prompts, return with counts

def get_prompts_by_tags(self, tags: List[str]) -> List[Prompt]
    # Return prompts that contain ALL specified tags
```

### Impact on Existing Code

- `PromptBase` gains a `tags` field — all existing prompts default to `[]`.
- `PromptUpdate` gains an optional `tags` field for PUT/PATCH support.
- The `Prompt` response model automatically inherits `tags` from `PromptBase`.
- The `list_prompts` handler gains a `tags` query parameter.
- No changes to the Collection models.

---

## API Endpoint Specifications

### Create Prompt with Tags

```
POST /prompts
```

**Request Body:**
```json
{
  "title": "Python Code Review",
  "content": "Review this {{language}} code:\n\n{{code}}",
  "description": "Code review assistant",
  "tags": ["python", "code-review", "development"]
}
```

**Response:** `201 Created`
```json
{
  "id": "prompt-uuid",
  "title": "Python Code Review",
  "content": "Review this {{language}} code:\n\n{{code}}",
  "description": "Code review assistant",
  "collection_id": null,
  "tags": ["code-review", "development", "python"],
  "created_at": "2026-03-02T12:00:00.000000",
  "updated_at": "2026-03-02T12:00:00.000000"
}
```

### Filter Prompts by Tags

```
GET /prompts?tags=python,code-review
```

**Processing Order:** filter by collection → filter by tags → search → sort.

**Response:** `200 OK` — returns only prompts that have both "python" AND "code-review" tags.

### Update Tags via PATCH

```
PATCH /prompts/{prompt_id}
```

**Request Body:**
```json
{
  "tags": ["python", "security"]
}
```

Only the `tags` field is updated; all other fields remain unchanged.

### List All Tags

```
GET /tags
```

**Response:** `200 OK`
```json
{
  "tags": [
    { "name": "code-review", "count": 5 },
    { "name": "development", "count": 3 },
    { "name": "marketing", "count": 2 },
    { "name": "python", "count": 4 }
  ],
  "total": 4
}
```

---

## Search/Filter Requirements

### Tag Filtering Logic

- **AND logic:** `?tags=python,code-review` returns prompts that have both tags.
- **Case-insensitive:** Tags are stored and matched in lowercase.
- **Composable with existing filters:**

| Query | Behavior |
|-------|----------|
| `?tags=python` | All prompts tagged "python" |
| `?tags=python,security` | Prompts with both "python" AND "security" |
| `?tags=python&collection_id=abc` | Prompts tagged "python" in collection "abc" |
| `?tags=python&search=review` | Prompts tagged "python" matching "review" in title/description |
| `?tags=python&collection_id=abc&search=review` | All three filters combined |

### Processing Pipeline

The `list_prompts` handler applies filters in this order:

1. Filter by `collection_id` (if provided)
2. Filter by `tags` (if provided) — AND logic
3. Filter by `search` query (if provided) — substring match
4. Sort by `created_at` (newest first)

### Utility Function

Add to `app/utils.py`:

```python
def filter_prompts_by_tags(prompts: List[Prompt], tags: List[str]) -> List[Prompt]:
    """Filter prompts to those containing all specified tags.

    Args:
        prompts: The list of prompts to filter.
        tags: The tag names to match (case-insensitive, AND logic).

    Returns:
        A list of prompts that contain every tag in the input list.

    Example:
        >>> filtered = filter_prompts_by_tags(prompts, ["python", "security"])
        >>> all({"python", "security"}.issubset(set(p.tags)) for p in filtered)
        True
    """
    tags_lower = {t.lower() for t in tags}
    return [p for p in prompts if tags_lower.issubset(set(p.tags))]
```

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No tags provided on create | Prompt is created with `tags: []` |
| Duplicate tags in input (`["python", "Python", "PYTHON"]`) | Deduplicated to `["python"]` after lowercasing |
| More than 10 tags | Return `422` validation error |
| Tag with invalid characters (`"c++ code"`) | Return `422` — only alphanumeric, hyphens, and underscores allowed |
| Empty string tag (`""`) | Return `422` — minimum 1 character |
| Tag longer than 50 characters | Return `422` — exceeds max length |
| Filter by tag that no prompt has | Return empty list with `total: 0` |
| Delete a prompt that has tags | Tags are removed with the prompt; tag counts update accordingly |
| PATCH with `tags: []` | Removes all tags from the prompt |
| PATCH without `tags` field | Tags remain unchanged |
| GET `/tags` when no prompts have tags | Return empty list with `total: 0` |
