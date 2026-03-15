"""Comprehensive API endpoint tests for PromptLab."""

import time
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Tests for the health check endpoint."""

    def test_health_check(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestPrompts:
    """Tests for prompt CRUD endpoints."""

    # ---- POST /prompts ----

    def test_create_prompt(self, client: TestClient, sample_prompt_data):
        response = client.post("/prompts", json=sample_prompt_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_prompt_data["title"]
        assert data["content"] == sample_prompt_data["content"]
        assert data["description"] == sample_prompt_data["description"]
        assert data["collection_id"] is None
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_prompt_minimal(self, client: TestClient):
        response = client.post("/prompts", json={
            "title": "T",
            "content": "C"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "T"
        assert data["description"] is None

    def test_create_prompt_with_collection(self, client: TestClient, sample_prompt_data, sample_collection_data):
        col = client.post("/collections", json=sample_collection_data).json()
        prompt_data = {**sample_prompt_data, "collection_id": col["id"]}
        response = client.post("/prompts", json=prompt_data)
        assert response.status_code == 201
        assert response.json()["collection_id"] == col["id"]

    def test_create_prompt_invalid_collection(self, client: TestClient, sample_prompt_data):
        prompt_data = {**sample_prompt_data, "collection_id": "nonexistent"}
        response = client.post("/prompts", json=prompt_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Collection not found"

    def test_create_prompt_missing_title(self, client: TestClient):
        response = client.post("/prompts", json={"content": "Some content"})
        assert response.status_code == 422

    def test_create_prompt_missing_content(self, client: TestClient):
        response = client.post("/prompts", json={"title": "A Title"})
        assert response.status_code == 422

    def test_create_prompt_empty_title(self, client: TestClient):
        response = client.post("/prompts", json={"title": "", "content": "Some content"})
        assert response.status_code == 422

    def test_create_prompt_title_too_long(self, client: TestClient):
        response = client.post("/prompts", json={
            "title": "x" * 201,
            "content": "Some content"
        })
        assert response.status_code == 422

    def test_create_prompt_description_too_long(self, client: TestClient):
        response = client.post("/prompts", json={
            "title": "Title",
            "content": "Content",
            "description": "x" * 501
        })
        assert response.status_code == 422

    # ---- GET /prompts ----

    def test_list_prompts_empty(self, client: TestClient):
        response = client.get("/prompts")
        assert response.status_code == 200
        data = response.json()
        assert data["prompts"] == []
        assert data["total"] == 0

    def test_list_prompts(self, client: TestClient, sample_prompt_data):
        client.post("/prompts", json=sample_prompt_data)
        client.post("/prompts", json={**sample_prompt_data, "title": "Second Prompt"})
        response = client.get("/prompts")
        assert response.status_code == 200
        assert response.json()["total"] == 2

    def test_list_prompts_sorted_newest_first(self, client: TestClient):
        client.post("/prompts", json={"title": "First", "content": "content1"})
        time.sleep(0.01)
        client.post("/prompts", json={"title": "Second", "content": "content2"})
        response = client.get("/prompts")
        prompts = response.json()["prompts"]
        assert prompts[0]["title"] == "Second"
        assert prompts[1]["title"] == "First"

    def test_list_prompts_filter_by_collection(self, client: TestClient, sample_prompt_data, sample_collection_data):
        col = client.post("/collections", json=sample_collection_data).json()
        client.post("/prompts", json={**sample_prompt_data, "collection_id": col["id"]})
        client.post("/prompts", json={"title": "Other", "content": "content"})
        response = client.get(f"/prompts?collection_id={col['id']}")
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["collection_id"] == col["id"]

    def test_list_prompts_search(self, client: TestClient, sample_prompt_data):
        client.post("/prompts", json=sample_prompt_data)
        client.post("/prompts", json={"title": "Marketing Email", "content": "content"})
        response = client.get("/prompts?search=review")
        data = response.json()
        assert data["total"] == 1
        assert "Review" in data["prompts"][0]["title"]

    def test_list_prompts_search_case_insensitive(self, client: TestClient, sample_prompt_data):
        client.post("/prompts", json=sample_prompt_data)
        response = client.get("/prompts?search=CODE REVIEW")
        assert response.json()["total"] == 1

    def test_list_prompts_search_in_description(self, client: TestClient):
        client.post("/prompts", json={
            "title": "Generic Title",
            "content": "content",
            "description": "This helps with code review"
        })
        response = client.get("/prompts?search=review")
        assert response.json()["total"] == 1

    def test_list_prompts_search_no_match(self, client: TestClient, sample_prompt_data):
        client.post("/prompts", json=sample_prompt_data)
        response = client.get("/prompts?search=nonexistent")
        assert response.json()["total"] == 0

    def test_list_prompts_combined_filter_and_search(self, client: TestClient, sample_collection_data):
        col = client.post("/collections", json=sample_collection_data).json()
        client.post("/prompts", json={
            "title": "Code Review",
            "content": "content",
            "collection_id": col["id"]
        })
        client.post("/prompts", json={
            "title": "Code Review Other",
            "content": "content"
        })
        response = client.get(f"/prompts?collection_id={col['id']}&search=review")
        data = response.json()
        assert data["total"] == 1
        assert data["prompts"][0]["collection_id"] == col["id"]

    # ---- GET /prompts/{id} ----

    def test_get_prompt(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        response = client.get(f"/prompts/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]
        assert response.json()["title"] == sample_prompt_data["title"]

    def test_get_prompt_not_found(self, client: TestClient):
        response = client.get("/prompts/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Prompt not found"

    # ---- PUT /prompts/{id} ----

    def test_update_prompt(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        update_data = {
            "title": "Updated Title",
            "content": "Updated content",
            "description": "Updated description"
        }
        response = client.put(f"/prompts/{created['id']}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated content"
        assert data["id"] == created["id"]
        assert data["created_at"] == created["created_at"]

    def test_update_prompt_refreshes_timestamp(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        time.sleep(0.01)
        update_data = {"title": "New", "content": "New content"}
        response = client.put(f"/prompts/{created['id']}", json=update_data)
        assert response.json()["updated_at"] != created["updated_at"]

    def test_update_prompt_not_found(self, client: TestClient):
        response = client.put("/prompts/nonexistent", json={
            "title": "T", "content": "C"
        })
        assert response.status_code == 404

    def test_update_prompt_invalid_collection(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        response = client.put(f"/prompts/{created['id']}", json={
            "title": "T",
            "content": "C",
            "collection_id": "bad-id"
        })
        assert response.status_code == 400

    # ---- PATCH /prompts/{id} ----

    def test_patch_prompt(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        response = client.patch(f"/prompts/{created['id']}", json={
            "title": "Partially Updated Title"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Partially Updated Title"
        assert data["content"] == sample_prompt_data["content"]

    def test_patch_prompt_refreshes_timestamp(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        time.sleep(0.01)
        response = client.patch(f"/prompts/{created['id']}", json={"title": "New"})
        assert response.json()["updated_at"] != created["updated_at"]

    def test_patch_prompt_not_found(self, client: TestClient):
        response = client.patch("/prompts/nonexistent", json={"title": "X"})
        assert response.status_code == 404

    def test_patch_prompt_update_content_only(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        response = client.patch(f"/prompts/{created['id']}", json={
            "content": "Brand new content"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Brand new content"
        assert data["title"] == sample_prompt_data["title"]

    # ---- DELETE /prompts/{id} ----

    def test_delete_prompt(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        response = client.delete(f"/prompts/{created['id']}")
        assert response.status_code == 204
        # Verify it's gone
        get_response = client.get(f"/prompts/{created['id']}")
        assert get_response.status_code == 404

    def test_delete_prompt_not_found(self, client: TestClient):
        response = client.delete("/prompts/nonexistent-id")
        assert response.status_code == 404


class TestCollections:
    """Tests for collection CRUD endpoints."""

    # ---- POST /collections ----

    def test_create_collection(self, client: TestClient, sample_collection_data):
        response = client.post("/collections", json=sample_collection_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_collection_data["name"]
        assert data["description"] == sample_collection_data["description"]
        assert "id" in data
        assert "created_at" in data

    def test_create_collection_minimal(self, client: TestClient):
        response = client.post("/collections", json={"name": "N"})
        assert response.status_code == 201
        assert response.json()["description"] is None

    def test_create_collection_missing_name(self, client: TestClient):
        response = client.post("/collections", json={"description": "desc"})
        assert response.status_code == 422

    def test_create_collection_empty_name(self, client: TestClient):
        response = client.post("/collections", json={"name": ""})
        assert response.status_code == 422

    def test_create_collection_name_too_long(self, client: TestClient):
        response = client.post("/collections", json={"name": "x" * 101})
        assert response.status_code == 422

    def test_create_collection_description_too_long(self, client: TestClient):
        response = client.post("/collections", json={
            "name": "Valid",
            "description": "x" * 501
        })
        assert response.status_code == 422

    # ---- GET /collections ----

    def test_list_collections_empty(self, client: TestClient):
        response = client.get("/collections")
        assert response.status_code == 200
        data = response.json()
        assert data["collections"] == []
        assert data["total"] == 0

    def test_list_collections(self, client: TestClient, sample_collection_data):
        client.post("/collections", json=sample_collection_data)
        client.post("/collections", json={"name": "Second"})
        response = client.get("/collections")
        assert response.status_code == 200
        assert response.json()["total"] == 2

    # ---- GET /collections/{id} ----

    def test_get_collection(self, client: TestClient, sample_collection_data):
        created = client.post("/collections", json=sample_collection_data).json()
        response = client.get(f"/collections/{created['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == sample_collection_data["name"]

    def test_get_collection_not_found(self, client: TestClient):
        response = client.get("/collections/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["detail"] == "Collection not found"

    # ---- DELETE /collections/{id} ----

    def test_delete_collection(self, client: TestClient, sample_collection_data):
        created = client.post("/collections", json=sample_collection_data).json()
        response = client.delete(f"/collections/{created['id']}")
        assert response.status_code == 204
        get_response = client.get(f"/collections/{created['id']}")
        assert get_response.status_code == 404

    def test_delete_collection_not_found(self, client: TestClient):
        response = client.delete("/collections/nonexistent-id")
        assert response.status_code == 404

    def test_delete_collection_with_prompts(self, client: TestClient, sample_collection_data, sample_prompt_data):
        col = client.post("/collections", json=sample_collection_data).json()
        client.post("/prompts", json={**sample_prompt_data, "collection_id": col["id"]})
        response = client.delete(f"/collections/{col['id']}")
        assert response.status_code == 400
        assert response.json()["detail"] == "Collection cannot be deleted. It has associated prompts."
        # Collection should still exist
        assert client.get(f"/collections/{col['id']}").status_code == 200
