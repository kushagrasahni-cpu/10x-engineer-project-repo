# PromptLab — AI Coding Instructions

This file defines the coding standards, conventions, and practices for the PromptLab project. AI assistants should follow these guidelines when generating or modifying code.

---

## Project Overview

PromptLab is a FastAPI-based REST API for managing AI prompt templates and collections. The backend uses in-memory storage, Pydantic models for validation, and pytest for testing.

**Stack:** Python 3.10+, FastAPI 0.109, Pydantic 2.5, Uvicorn 0.27, pytest 7.4

---

## Project Coding Standards

### Python Style

- Follow PEP 8 for all Python code.
- Use 4 spaces for indentation (no tabs).
- Maximum line length: 100 characters.
- Use double quotes for strings in general; single quotes are acceptable for dictionary keys and short identifiers.
- Use type hints on all function signatures (parameters and return types).
- Import ordering: standard library, third-party packages, local modules — separated by blank lines.

### Docstrings

- Use Google-style docstrings on every function, method, and class.
- Required sections: a one-line summary, `Args`, `Returns`, and `Raises` (where applicable).
- Include `Example` sections for utility/helper functions.
- Module-level docstrings should describe the module's purpose in 1–2 sentences.

```python
def get_prompt(prompt_id: str) -> Optional[Prompt]:
    """Retrieve a prompt by its unique identifier.

    Args:
        prompt_id: The UUID of the prompt to retrieve.

    Returns:
        The Prompt object if found, None otherwise.

    Raises:
        HTTPException: 404 if the prompt does not exist.
    """
```

---

## Preferred Patterns and Conventions

### API Endpoints

- Define all routes in `app/api.py`.
- Use FastAPI decorators with explicit `response_model` and `status_code`.
- Use `HTTPException` for all error responses — never return raw error dicts.
- Validate business rules (e.g., collection existence) in the route handler before calling the storage layer.
- Return `201 Created` for POST, `200 OK` for GET/PUT/PATCH, `204 No Content` for DELETE.

```python
@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate):
```

### Data Models

- Define all Pydantic models in `app/models.py`.
- Use a base → create → full pattern: `PromptBase` (shared fields), `PromptCreate` (input), `Prompt` (output with id/timestamps).
- Use `PromptUpdate` with all-optional fields for PUT/PATCH support.
- Use `Field(...)` for required fields with constraints (`min_length`, `max_length`).
- Use `Field(None)` for optional fields.
- Auto-generate `id` with `uuid4` and timestamps with `datetime.utcnow()` via `default_factory`.

### Storage Layer

- All data access goes through the `Storage` class in `app/storage.py`.
- The storage layer should only handle data operations (CRUD) — no business logic or validation.
- Business rule checks (e.g., "does this collection exist?") belong in the API layer.
- Use the global `storage` singleton instance — do not create new `Storage()` instances.

### Utility Functions

- Place reusable helper functions in `app/utils.py`.
- Utility functions should be pure (no side effects, no storage access).
- Accept data as parameters rather than accessing global state.

---

## File Naming Conventions

### Backend

| Path | Purpose |
|------|---------|
| `backend/app/__init__.py` | Package init, version string |
| `backend/app/api.py` | All FastAPI route handlers |
| `backend/app/models.py` | All Pydantic model definitions |
| `backend/app/storage.py` | Storage class and global instance |
| `backend/app/utils.py` | Stateless helper/utility functions |
| `backend/main.py` | Uvicorn entry point |
| `backend/requirements.txt` | Python dependencies with pinned versions |

### Tests

| Path | Purpose |
|------|---------|
| `backend/tests/conftest.py` | Shared fixtures (client, storage reset, sample data) |
| `backend/tests/test_api.py` | API endpoint tests |
| `backend/tests/test_storage.py` | Storage layer unit tests |
| `backend/tests/test_utils.py` | Utility function unit tests |
| `backend/tests/test_models.py` | Model validation tests |

### Documentation

| Path | Purpose |
|------|---------|
| `README.md` | Project overview, setup, and feature docs |
| `docs/API_REFERENCE.md` | Full API endpoint documentation |
| `specs/*.md` | Feature specification documents |

### General Rules

- Use `snake_case` for Python files, functions, variables, and modules.
- Use `PascalCase` for class names.
- Use `UPPER_SNAKE_CASE` for constants.
- Test files must be prefixed with `test_` and mirror the module they test.

---

## Error Handling Approach

### HTTP Status Codes

| Code | When to Use |
|------|-------------|
| `200` | Successful GET, PUT, PATCH |
| `201` | Successful POST (resource created) |
| `204` | Successful DELETE (no response body) |
| `400` | Business rule violation (e.g., invalid collection reference, deleting non-empty collection) |
| `404` | Resource not found by ID |
| `422` | Request body validation failure (handled automatically by Pydantic/FastAPI) |

### Error Patterns

- Always check resource existence before operating on it. Return `404` early.
- Validate referenced resources (e.g., `collection_id`) before creating/updating. Return `400` if invalid.
- Use descriptive error messages in `HTTPException.detail`.
- Never expose internal errors or stack traces to the client.

```python
existing = storage.get_prompt(prompt_id)
if not existing:
    raise HTTPException(status_code=404, detail="Prompt not found")
```

### Deletion Safety

- Before deleting a collection, check for associated prompts. Block deletion with `400` if prompts exist.
- Prompt deletion is straightforward — no cascading checks needed.

---

## Testing Requirements

### Framework and Setup

- Use `pytest` as the test runner.
- Use `FastAPI.TestClient` (from `starlette`) for API integration tests.
- Define shared fixtures in `conftest.py`.
- Use the `clear_storage` autouse fixture to reset state between tests.

### Test Organization

- Group related tests into classes (e.g., `TestPrompts`, `TestCollections`).
- Name test methods descriptively: `test_<action>_<scenario>` (e.g., `test_delete_collection_with_prompts`).
- Each test should be independent — no test should depend on another test's side effects.

### Coverage

- Target 80%+ code coverage.
- Test both happy paths and error paths for every endpoint.
- Test edge cases: empty strings, max-length strings, missing fields, non-existent IDs.
- Test query parameters: search, filtering, sorting.

### Test Patterns

```python
class TestPrompts:
    def test_create_prompt(self, client: TestClient, sample_prompt_data):
        response = client.post("/prompts", json=sample_prompt_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_prompt_data["title"]
        assert "id" in data
        assert "created_at" in data

    def test_get_prompt_not_found(self, client: TestClient):
        response = client.get("/prompts/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Prompt not found"
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```
