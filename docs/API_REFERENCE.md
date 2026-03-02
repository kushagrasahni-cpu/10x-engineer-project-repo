# PromptLab API Reference

**Base URL:** `http://localhost:8000`

**Version:** `0.1.0`

---

## Authentication

No authentication is currently required. All endpoints are publicly accessible.

> **Note:** Authentication may be added in a future release. When implemented, this section will be updated with token-based auth details.

---

## Common Response Formats

### Success Responses

All successful responses return JSON. The HTTP status code indicates the type of success:

| Status Code | Meaning |
|-------------|---------|
| `200 OK` | Request succeeded (GET, PUT, PATCH) |
| `201 Created` | Resource created successfully (POST) |
| `204 No Content` | Resource deleted successfully (DELETE) |

### Error Responses

All error responses follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| `400 Bad Request` | Business rule violation | Deleting a collection that has prompts; referencing a non-existent collection |
| `404 Not Found` | Resource does not exist | Invalid or non-existent UUID in path |
| `422 Unprocessable Entity` | Validation error | Missing required fields, fields exceeding max length, empty strings |

#### 422 Validation Error Format

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```

---

## Endpoints

### Health Check

#### `GET /health`

Returns the current health status and version of the API.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

### Prompts

#### `GET /prompts`

List all prompts with optional filtering, search, and sorting.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `collection_id` | string | No | — | Filter prompts by collection UUID |
| `search` | string | No | — | Case-insensitive substring search in title and description |

**Processing Order:** filter by collection → search → sort by newest first.

**Request:**
```bash
# List all prompts
curl http://localhost:8000/prompts

# Filter by collection
curl "http://localhost:8000/prompts?collection_id=abc-123"

# Search prompts
curl "http://localhost:8000/prompts?search=review"

# Combine filter and search
curl "http://localhost:8000/prompts?collection_id=abc-123&search=review"
```

**Response:** `200 OK`
```json
{
  "prompts": [
    {
      "id": "95958876-49c3-4a93-b254-ccedcc9d5a6f",
      "title": "Code Review Prompt",
      "content": "Review the following {{language}} code:\n\n{{code}}",
      "description": "AI-powered code review assistant",
      "collection_id": "abc-123",
      "created_at": "2026-03-02T12:00:00.000000",
      "updated_at": "2026-03-02T12:00:00.000000"
    }
  ],
  "total": 1
}
```

---

#### `GET /prompts/{prompt_id}`

Retrieve a single prompt by its UUID.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt_id` | string | Yes | The UUID of the prompt |

**Request:**
```bash
curl http://localhost:8000/prompts/95958876-49c3-4a93-b254-ccedcc9d5a6f
```

**Response:** `200 OK`
```json
{
  "id": "95958876-49c3-4a93-b254-ccedcc9d5a6f",
  "title": "Code Review Prompt",
  "content": "Review the following {{language}} code:\n\n{{code}}",
  "description": "AI-powered code review assistant",
  "collection_id": null,
  "created_at": "2026-03-02T12:00:00.000000",
  "updated_at": "2026-03-02T12:00:00.000000"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Prompt not found"
}
```

---

#### `POST /prompts`

Create a new prompt. The `id`, `created_at`, and `updated_at` fields are generated automatically.

**Request Body:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `title` | string | Yes | 1–200 characters | The prompt title |
| `content` | string | Yes | Min 1 character | The prompt template body |
| `description` | string | No | Max 500 characters | Short description |
| `collection_id` | string | No | Must reference an existing collection | Parent collection UUID |

**Request:**
```bash
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Code Review Prompt",
    "content": "Review the following {{language}} code for bugs:\n\n{{code}}",
    "description": "AI-powered code review assistant",
    "collection_id": null
  }'
```

**Response:** `201 Created`
```json
{
  "id": "95958876-49c3-4a93-b254-ccedcc9d5a6f",
  "title": "Code Review Prompt",
  "content": "Review the following {{language}} code for bugs:\n\n{{code}}",
  "description": "AI-powered code review assistant",
  "collection_id": null,
  "created_at": "2026-03-02T12:00:00.000000",
  "updated_at": "2026-03-02T12:00:00.000000"
}
```

**Error Response:** `400 Bad Request` (invalid collection reference)
```json
{
  "detail": "Collection not found"
}
```

**Error Response:** `422 Unprocessable Entity` (missing required field)
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

---

#### `PUT /prompts/{prompt_id}`

Fully replace all mutable fields of an existing prompt. The `id` and `created_at` are preserved; `updated_at` is refreshed.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt_id` | string | Yes | The UUID of the prompt to update |

**Request Body:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `title` | string | No* | 1–200 characters | Updated title |
| `content` | string | No* | Min 1 character | Updated content |
| `description` | string | No | Max 500 characters | Updated description |
| `collection_id` | string | No | Must reference an existing collection | Updated collection |

> *While the schema allows optional fields, a PUT request should provide all fields to fully replace the resource.

**Request:**
```bash
curl -X PUT http://localhost:8000/prompts/95958876-49c3-4a93-b254-ccedcc9d5a6f \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Code Review Prompt",
    "content": "Review this {{language}} code for security issues:\n\n{{code}}",
    "description": "Security-focused code review",
    "collection_id": null
  }'
```

**Response:** `200 OK`
```json
{
  "id": "95958876-49c3-4a93-b254-ccedcc9d5a6f",
  "title": "Updated Code Review Prompt",
  "content": "Review this {{language}} code for security issues:\n\n{{code}}",
  "description": "Security-focused code review",
  "collection_id": null,
  "created_at": "2026-03-02T12:00:00.000000",
  "updated_at": "2026-03-02T12:05:00.000000"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Prompt not found"
}
```

**Error Response:** `400 Bad Request`
```json
{
  "detail": "Collection not found"
}
```

---

#### `PATCH /prompts/{prompt_id}`

Partially update a prompt. Only the fields included in the request body are modified; all other fields remain unchanged. `updated_at` is refreshed.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt_id` | string | Yes | The UUID of the prompt to update |

**Request Body:**

All fields are optional. Only include fields you want to change.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `title` | string | 1–200 characters | Updated title |
| `content` | string | Min 1 character | Updated content |
| `description` | string | Max 500 characters | Updated description |
| `collection_id` | string | Must reference an existing collection | Updated collection |

**Request:**
```bash
# Update only the title
curl -X PATCH http://localhost:8000/prompts/95958876-49c3-4a93-b254-ccedcc9d5a6f \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Improved Code Review Prompt"
  }'
```

**Response:** `200 OK`
```json
{
  "id": "95958876-49c3-4a93-b254-ccedcc9d5a6f",
  "title": "Improved Code Review Prompt",
  "content": "Review this {{language}} code for security issues:\n\n{{code}}",
  "description": "Security-focused code review",
  "collection_id": null,
  "created_at": "2026-03-02T12:00:00.000000",
  "updated_at": "2026-03-02T12:10:00.000000"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Prompt not found"
}
```

---

#### `DELETE /prompts/{prompt_id}`

Delete a prompt by its UUID.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt_id` | string | Yes | The UUID of the prompt to delete |

**Request:**
```bash
curl -X DELETE http://localhost:8000/prompts/95958876-49c3-4a93-b254-ccedcc9d5a6f
```

**Response:** `204 No Content`

No response body.

**Error Response:** `404 Not Found`
```json
{
  "detail": "Prompt not found"
}
```

---

### Collections

#### `GET /collections`

List all collections.

**Request:**
```bash
curl http://localhost:8000/collections
```

**Response:** `200 OK`
```json
{
  "collections": [
    {
      "id": "col-abc-123",
      "name": "Code Review Prompts",
      "description": "Prompts for automated code review",
      "created_at": "2026-03-02T12:00:00.000000"
    }
  ],
  "total": 1
}
```

---

#### `GET /collections/{collection_id}`

Retrieve a single collection by its UUID.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `collection_id` | string | Yes | The UUID of the collection |

**Request:**
```bash
curl http://localhost:8000/collections/col-abc-123
```

**Response:** `200 OK`
```json
{
  "id": "col-abc-123",
  "name": "Code Review Prompts",
  "description": "Prompts for automated code review",
  "created_at": "2026-03-02T12:00:00.000000"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Collection not found"
}
```

---

#### `POST /collections`

Create a new collection. The `id` and `created_at` fields are generated automatically.

**Request Body:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | string | Yes | 1–100 characters | The collection name |
| `description` | string | No | Max 500 characters | Short description |

**Request:**
```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Code Review Prompts",
    "description": "Prompts for automated code review"
  }'
```

**Response:** `201 Created`
```json
{
  "id": "col-abc-123",
  "name": "Code Review Prompts",
  "description": "Prompts for automated code review",
  "created_at": "2026-03-02T12:00:00.000000"
}
```

**Error Response:** `422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

---

#### `DELETE /collections/{collection_id}`

Delete a collection by its UUID. Deletion is **blocked** if the collection still has associated prompts, to prevent orphaned references.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `collection_id` | string | Yes | The UUID of the collection to delete |

**Request:**
```bash
curl -X DELETE http://localhost:8000/collections/col-abc-123
```

**Response:** `204 No Content`

No response body.

**Error Response:** `400 Bad Request` (collection has associated prompts)
```json
{
  "detail": "Collection cannot be deleted. It has associated prompts."
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Collection not found"
}
```

---

## Data Models

### Prompt

```json
{
  "id": "string (UUID, auto-generated)",
  "title": "string (1-200 chars, required)",
  "content": "string (min 1 char, required)",
  "description": "string (max 500 chars, optional)",
  "collection_id": "string (optional, must reference existing collection)",
  "created_at": "datetime (UTC, auto-generated)",
  "updated_at": "datetime (UTC, auto-updated on PUT/PATCH)"
}
```

### Collection

```json
{
  "id": "string (UUID, auto-generated)",
  "name": "string (1-100 chars, required)",
  "description": "string (max 500 chars, optional)",
  "created_at": "datetime (UTC, auto-generated)"
}
```

---

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These interfaces allow you to explore and test all endpoints directly from the browser.

---

## CORS

Cross-Origin Resource Sharing is enabled with the following configuration:

| Setting | Value |
|---------|-------|
| `allow_origins` | `["*"]` (all origins) |
| `allow_credentials` | `true` |
| `allow_methods` | `["*"]` (all methods) |
| `allow_headers` | `["*"]` (all headers) |

This configuration is intended for development. In production, origins should be restricted to known frontend domains.
