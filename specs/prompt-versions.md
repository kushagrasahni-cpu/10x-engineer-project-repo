# Feature Specification: Prompt Version Tracking

## Overview

Prompt version tracking enables users to maintain a full history of changes made to a prompt over time. Every time a prompt is updated (via PUT or PATCH), the previous state is saved as a version snapshot. Users can list all versions of a prompt, view any past version, and restore a previous version as the current one.

This feature supports iterative prompt engineering workflows where users refine prompts through many revisions and need the ability to compare or roll back changes.

---

## User Stories

### US-1: Automatic Version Creation on Update

**As** a prompt engineer,
**I want** a new version to be saved automatically every time I update a prompt,
**so that** I never lose a previous iteration of my work.

**Acceptance Criteria:**
- When a prompt is updated via PUT, the pre-update state is saved as a new version.
- When a prompt is updated via PATCH, the pre-update state is saved as a new version.
- Each version is assigned an auto-incrementing version number starting at 1.
- The version includes a timestamp recording when it was created.
- The current prompt state is not itself stored as a version — versions represent past states only.

### US-2: List Version History

**As** a prompt engineer,
**I want** to view the full version history of a prompt,
**so that** I can see how it evolved over time.

**Acceptance Criteria:**
- A GET endpoint returns all versions for a given prompt ID.
- Versions are returned in reverse chronological order (newest first).
- Each version entry includes: version number, timestamp, title, content, description, and collection_id.
- The response includes a total count of versions.
- If the prompt has never been updated, the list is empty.

### US-3: View a Specific Version

**As** a prompt engineer,
**I want** to view the full details of a specific past version,
**so that** I can review exactly what a prompt looked like at that point.

**Acceptance Criteria:**
- A GET endpoint returns a single version by prompt ID and version number.
- The response includes all prompt fields as they were at that version.
- Returns 404 if the prompt or version number does not exist.

### US-4: Restore a Previous Version

**As** a prompt engineer,
**I want** to restore a previous version of a prompt as the current state,
**so that** I can revert a bad edit.

**Acceptance Criteria:**
- A POST endpoint restores a specified version number as the current prompt state.
- Restoring creates a new version snapshot of the current state before overwriting (so the restore itself is reversible).
- The prompt's `updated_at` timestamp is refreshed.
- Returns 404 if the prompt or version number does not exist.

---

## Data Model Changes

### New Model: `PromptVersion`

```python
class PromptVersion(BaseModel):
    """A historical snapshot of a prompt's state before an update."""

    id: str = Field(default_factory=generate_id)
    prompt_id: str                          # FK to the parent Prompt
    version_number: int                     # Auto-incrementing per prompt (1, 2, 3, ...)
    title: str
    content: str
    description: Optional[str] = None
    collection_id: Optional[str] = None
    created_at: datetime = Field(default_factory=get_current_time)  # When this version was saved
```

### Response Wrapper

```python
class PromptVersionList(BaseModel):
    """Response wrapper for a list of prompt versions."""

    versions: List[PromptVersion]
    total: int
```

### Storage Changes

Add to the `Storage` class:

```python
_versions: Dict[str, List[PromptVersion]]  # prompt_id -> list of versions

def create_version(self, prompt_id: str, version: PromptVersion) -> PromptVersion
def get_versions(self, prompt_id: str) -> List[PromptVersion]
def get_version(self, prompt_id: str, version_number: int) -> Optional[PromptVersion]
def delete_versions(self, prompt_id: str) -> bool  # called when a prompt is deleted
```

### Impact on Existing Models

- The `Prompt` model itself does not change.
- The PUT and PATCH handlers must be updated to save a version before applying changes.
- The DELETE prompt handler must be updated to also delete associated versions.

---

## API Endpoint Specifications

### List Versions

```
GET /prompts/{prompt_id}/versions
```

**Response:** `200 OK`
```json
{
  "versions": [
    {
      "id": "ver-uuid-1",
      "prompt_id": "prompt-uuid",
      "version_number": 2,
      "title": "Old Title v2",
      "content": "Old content v2",
      "description": "Old description",
      "collection_id": null,
      "created_at": "2026-03-02T12:05:00.000000"
    },
    {
      "id": "ver-uuid-0",
      "prompt_id": "prompt-uuid",
      "version_number": 1,
      "title": "Old Title v1",
      "content": "Old content v1",
      "description": null,
      "collection_id": null,
      "created_at": "2026-03-02T12:00:00.000000"
    }
  ],
  "total": 2
}
```

**Errors:**
- `404` — Prompt not found.

### Get Specific Version

```
GET /prompts/{prompt_id}/versions/{version_number}
```

**Response:** `200 OK`
```json
{
  "id": "ver-uuid-1",
  "prompt_id": "prompt-uuid",
  "version_number": 2,
  "title": "Old Title v2",
  "content": "Old content v2",
  "description": "Old description",
  "collection_id": null,
  "created_at": "2026-03-02T12:05:00.000000"
}
```

**Errors:**
- `404` — Prompt not found or version number does not exist.

### Restore Version

```
POST /prompts/{prompt_id}/versions/{version_number}/restore
```

**Response:** `200 OK` — Returns the updated current prompt (with restored fields and refreshed `updated_at`).

```json
{
  "id": "prompt-uuid",
  "title": "Old Title v2",
  "content": "Old content v2",
  "description": "Old description",
  "collection_id": null,
  "created_at": "2026-03-01T10:00:00.000000",
  "updated_at": "2026-03-02T14:00:00.000000"
}
```

**Errors:**
- `404` — Prompt not found or version number does not exist.

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Prompt has never been updated | `GET /versions` returns an empty list with `total: 0` |
| Version number does not exist | Return `404` with detail "Version not found" |
| Prompt is deleted | All associated versions are also deleted |
| Restore version that references a now-deleted collection | Restore proceeds but `collection_id` becomes an orphaned reference; the API could optionally validate and set it to `null` |
| Multiple rapid updates | Each update creates its own version with the correct sequential number |
| Restore followed by another restore | Each restore saves the current state as a new version first, so the chain is fully reversible |
| PUT with identical data (no actual change) | A version is still created — the system does not diff content |
| Version number is not a positive integer | Return `422` validation error |
| Max versions per prompt | No limit enforced initially; consider adding a configurable cap in the future |
