# PromptLab

**An AI Prompt Engineering Platform** — a professional workspace for AI engineers to store, organize, and manage their prompts.

---

## Overview

PromptLab is a FastAPI-powered backend application that serves as a "Postman for Prompts." It provides a RESTful API for teams to manage prompt templates with variable support, organize them into collections, and search across their prompt library.

### Key Features

#### Prompt Management (Full CRUD)

Complete lifecycle management for AI prompt templates through RESTful endpoints. Create prompts with a title, content body, optional description, and optional collection assignment. Retrieve individual prompts by UUID or list all prompts at once. Fully replace a prompt's fields with PUT, or selectively update specific fields with PATCH. Delete prompts by ID with proper 404 handling when a prompt doesn't exist.

- Each prompt is assigned a UUID and timestamped (`created_at`, `updated_at`) automatically on creation
- `updated_at` is refreshed on every PUT or PATCH operation
- Titles are capped at 200 characters; descriptions at 500 characters
- Content must be at least 1 character (schema-level) and can optionally be validated for a 10-character minimum via the utility layer

#### Template Variable Extraction

Prompts support `{{variable}}` placeholders using Mustache-style double-brace syntax. The `extract_variables()` utility parses prompt content with a regex pattern (`\{\{(\w+)\}\}`) and returns a list of variable names found. This enables downstream tooling to identify required inputs before a prompt is executed.

```
Content:  "Summarize the following {{document}} in {{language}}"
Extracted: ["document", "language"]
```

#### Collections

Prompts can be organized into named collections (e.g., "Code Review Prompts", "Marketing Templates"). Collections have a name (max 100 characters), an optional description (max 500 characters), and an auto-generated UUID and timestamp.

- A prompt can belong to at most one collection via its `collection_id` field
- When creating or updating a prompt with a `collection_id`, the API validates that the referenced collection exists and returns a `400` error if it doesn't
- Deleting a collection is blocked with a `400` error if any prompts are still associated with it, preventing orphaned references
- Retrieve all prompts within a collection via the `collection_id` query parameter on `GET /prompts`

#### Search

The `GET /prompts` endpoint accepts a `search` query parameter for full-text search across prompts. The search is:

- **Case-insensitive** — searching "Code" matches "code review", "CODE HELPER", etc.
- **Multi-field** — matches against both the prompt `title` and `description`
- **Substring-based** — partial matches work (e.g., "rev" matches "Code Review")
- **Composable** — can be combined with `collection_id` filtering in the same request

```
GET /prompts?search=review                          # search all prompts
GET /prompts?search=review&collection_id=abc-123    # search within a collection
```

#### Filtering & Sorting

Prompts can be filtered and sorted via query parameters on `GET /prompts`:

- **Filter by collection** — `collection_id=<uuid>` returns only prompts belonging to that collection
- **Sort by date** — Results are sorted by `created_at` timestamp, newest first by default
- **Pipeline** — Filtering, searching, and sorting are applied in sequence: filter by collection first, then search, then sort. This allows precise result sets when parameters are combined.

#### Partial Updates (PATCH)

The `PATCH /prompts/{id}` endpoint allows updating individual fields without replacing the entire resource. Only the fields included in the request body are modified; all other fields remain unchanged.

- Supports any combination of `title`, `content`, `description`, and `collection_id`
- Omitted fields are preserved as-is (uses `exclude_unset=True` to distinguish between "not provided" and "set to null")
- `updated_at` is automatically refreshed on every PATCH
- `collection_id` is validated against existing collections if provided
- Returns the full updated prompt object

```json
// Only update the title — everything else stays the same
PATCH /prompts/{id}
{ "title": "New Title" }
```

#### Input Validation

All request and response data is validated through Pydantic v2 schemas with strict type enforcement:

| Field | Constraint |
|-------|-----------|
| `title` | Required, 1–200 characters |
| `content` | Required, minimum 1 character |
| `description` | Optional, max 500 characters |
| `collection_id` | Optional, must reference an existing collection |
| `name` (collection) | Required, 1–100 characters |

- Invalid requests return `422 Unprocessable Entity` with detailed field-level error messages
- Not-found resources return `404` with a descriptive error detail
- Business rule violations (e.g., deleting a non-empty collection) return `400`

#### Health Check & API Documentation

- `GET /health` returns the API status and current version number
- Interactive Swagger UI documentation is auto-generated at `/docs`
- CORS is enabled for all origins, methods, and headers to support frontend clients during development

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | FastAPI | 0.109.0 |
| Server | Uvicorn | 0.27.0 |
| Validation | Pydantic | 2.5.3 |
| Testing | pytest | 7.4.4 |
| Coverage | pytest-cov | 4.1.0 |
| HTTP Client | httpx | 0.26.0 |
| Language | Python | 3.10+ |

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/kushagrasahni/10x-engineer-project-repo.git
cd 10x-engineer-project-repo

# Install dependencies
cd backend
pip install -r requirements.txt

# Start the server
python main.py
```

The API will be available at **http://localhost:8000**

Interactive API docs (Swagger UI) at **http://localhost:8000/docs**

### Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## API Reference

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Returns API health status |

### Prompts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/prompts` | List all prompts |
| GET | `/prompts/{id}` | Get a single prompt by ID |
| POST | `/prompts` | Create a new prompt |
| PUT | `/prompts/{id}` | Full update of a prompt |
| PATCH | `/prompts/{id}` | Partial update of a prompt |
| DELETE | `/prompts/{id}` | Delete a prompt |

**Query Parameters for `GET /prompts`:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search in title and description (case-insensitive) |
| `collection_id` | string | Filter by collection ID |
| `sort` | string | Sort order: `newest` (default) or `oldest` |

### Collections

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/collections` | List all collections |
| GET | `/collections/{id}` | Get a single collection by ID |
| POST | `/collections` | Create a new collection |
| DELETE | `/collections/{id}` | Delete a collection (fails if it contains prompts) |

### Example Usage

**Create a prompt:**
```bash
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Code Review Assistant",
    "content": "Review the following {{language}} code for bugs and improvements:\n\n{{code}}",
    "description": "AI-powered code review prompt"
  }'
```

**Search prompts:**
```bash
curl "http://localhost:8000/prompts?search=review&sort=newest"
```

**Partial update:**
```bash
curl -X PATCH http://localhost:8000/prompts/{id} \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

---

## Project Structure

```
10x-engineer-project-repo/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App metadata (version)
│   │   ├── api.py               # FastAPI route handlers
│   │   ├── models.py            # Pydantic data models
│   │   ├── storage.py           # In-memory storage layer
│   │   └── utils.py             # Helper functions (search, sort, filter, validation)
│   ├── tests/
│   │   ├── conftest.py          # Pytest fixtures
│   │   └── test_api.py          # API endpoint tests
│   ├── main.py                  # Application entry point
│   └── requirements.txt         # Python dependencies
├── frontend/                    # Frontend (planned)
├── specs/                       # Feature specifications (planned)
├── docs/                        # Documentation (planned)
├── PROJECT_BRIEF.md             # Assignment details
└── GRADING_RUBRIC.md            # Evaluation criteria
```

---

## Data Models

### Prompt

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUID) | Auto-generated unique identifier |
| `title` | string | Prompt title |
| `content` | string | Prompt template body (supports `{{variables}}`) |
| `description` | string (optional) | Brief description of the prompt |
| `collection_id` | string (optional) | ID of the parent collection |
| `created_at` | datetime | Auto-generated creation timestamp |
| `updated_at` | datetime | Auto-updated modification timestamp |

### Collection

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUID) | Auto-generated unique identifier |
| `name` | string | Collection name |
| `description` | string (optional) | Brief description of the collection |
| `created_at` | datetime | Auto-generated creation timestamp |

---

## Architecture

```
HTTP Request → FastAPI Router → Pydantic Validation → Storage Layer → Response
```

- **API Layer** (`api.py`) — Route handlers with HTTP status codes and error handling
- **Models** (`models.py`) — Pydantic schemas for request/response validation
- **Storage** (`storage.py`) — In-memory dictionary-based data store
- **Utilities** (`utils.py`) — Sorting, filtering, searching, content validation, and variable extraction

### Storage

The current implementation uses in-memory storage (Python dictionaries). Data resets on server restart. This is suitable for development and testing.

### CORS

CORS is enabled for all origins, methods, and headers to support frontend development.

---

## Development

### Dev Container

A VS Code Dev Container configuration is included for a consistent development environment:

```bash
# Open in VS Code with Dev Containers extension
code .
# Then: Ctrl+Shift+P → "Reopen in Container"
```

### Utility Functions

The `utils.py` module provides:

- `sort_prompts_by_date(prompts, descending)` — Sort by creation date
- `filter_prompts_by_collection(prompts, collection_id)` — Filter by collection
- `search_prompts(prompts, query)` — Case-insensitive title/description search
- `validate_prompt_content(content)` — Validates non-empty, minimum 10 characters
- `extract_variables(content)` — Extracts `{{variable}}` placeholders via regex

---

## Contributing

1. Create a new branch from `main` for your feature or fix.
2. Follow the coding standards defined in [`.github/copilot-instructions.md`](.github/copilot-instructions.md).
3. Add Google-style docstrings to all new functions, methods, and classes.
4. Write tests for new functionality — target 80%+ coverage.
5. Run the test suite before submitting: `pytest tests/ -v`
6. Use clear, descriptive commit messages that explain the "why" behind changes.
7. Open a pull request against `main` with a summary of what changed and why.

---

## License

This project is part of an academic engineering assignment.
