"""TDD tests for Prompt Version Tracking feature."""

import time
from fastapi.testclient import TestClient


class TestListVersions:
    """Tests for GET /prompts/{prompt_id}/versions."""

    def test_no_versions_initially(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        response = client.get(f"/prompts/{created['id']}/versions")
        assert response.status_code == 200
        data = response.json()
        assert data["versions"] == []
        assert data["total"] == 0

    def test_version_created_on_put(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        client.put(f"/prompts/{created['id']}", json={
            "title": "Updated", "content": "New content"
        })
        response = client.get(f"/prompts/{created['id']}/versions")
        data = response.json()
        assert data["total"] == 1
        version = data["versions"][0]
        assert version["version_number"] == 1
        assert version["title"] == sample_prompt_data["title"]
        assert version["content"] == sample_prompt_data["content"]
        assert version["prompt_id"] == created["id"]

    def test_version_created_on_patch(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        client.patch(f"/prompts/{created['id']}", json={"title": "Patched"})
        response = client.get(f"/prompts/{created['id']}/versions")
        data = response.json()
        assert data["total"] == 1
        assert data["versions"][0]["title"] == sample_prompt_data["title"]

    def test_multiple_versions(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        client.put(f"/prompts/{created['id']}", json={
            "title": "V2", "content": "Content v2"
        })
        client.put(f"/prompts/{created['id']}", json={
            "title": "V3", "content": "Content v3"
        })
        response = client.get(f"/prompts/{created['id']}/versions")
        data = response.json()
        assert data["total"] == 2
        # Newest first
        assert data["versions"][0]["version_number"] == 2
        assert data["versions"][0]["title"] == "V2"
        assert data["versions"][1]["version_number"] == 1
        assert data["versions"][1]["title"] == sample_prompt_data["title"]

    def test_versions_newest_first(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        client.patch(f"/prompts/{created['id']}", json={"title": "Second"})
        time.sleep(0.01)
        client.patch(f"/prompts/{created['id']}", json={"title": "Third"})
        response = client.get(f"/prompts/{created['id']}/versions")
        versions = response.json()["versions"]
        assert versions[0]["version_number"] > versions[1]["version_number"]

    def test_list_versions_prompt_not_found(self, client: TestClient):
        response = client.get("/prompts/nonexistent/versions")
        assert response.status_code == 404


class TestGetSpecificVersion:
    """Tests for GET /prompts/{prompt_id}/versions/{version_number}."""

    def test_get_version(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        client.put(f"/prompts/{created['id']}", json={
            "title": "Updated", "content": "New content"
        })
        response = client.get(f"/prompts/{created['id']}/versions/1")
        assert response.status_code == 200
        data = response.json()
        assert data["version_number"] == 1
        assert data["title"] == sample_prompt_data["title"]
        assert data["content"] == sample_prompt_data["content"]
        assert data["prompt_id"] == created["id"]

    def test_get_version_prompt_not_found(self, client: TestClient):
        response = client.get("/prompts/nonexistent/versions/1")
        assert response.status_code == 404

    def test_get_version_not_found(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        response = client.get(f"/prompts/{created['id']}/versions/999")
        assert response.status_code == 404

    def test_get_version_includes_all_fields(self, client: TestClient):
        created = client.post("/prompts", json={
            "title": "Original",
            "content": "Original content",
            "description": "Original desc"
        }).json()
        client.patch(f"/prompts/{created['id']}", json={"title": "Changed"})
        response = client.get(f"/prompts/{created['id']}/versions/1")
        data = response.json()
        assert data["title"] == "Original"
        assert data["content"] == "Original content"
        assert data["description"] == "Original desc"
        assert "id" in data
        assert "created_at" in data


class TestRestoreVersion:
    """Tests for POST /prompts/{prompt_id}/versions/{version_number}/restore."""

    def test_restore_version(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        client.put(f"/prompts/{created['id']}", json={
            "title": "Changed", "content": "Changed content"
        })
        response = client.post(f"/prompts/{created['id']}/versions/1/restore")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_prompt_data["title"]
        assert data["content"] == sample_prompt_data["content"]
        assert data["id"] == created["id"]
        assert data["created_at"] == created["created_at"]

    def test_restore_refreshes_updated_at(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        client.put(f"/prompts/{created['id']}", json={
            "title": "Changed", "content": "Changed content"
        })
        time.sleep(0.01)
        response = client.post(f"/prompts/{created['id']}/versions/1/restore")
        assert response.json()["updated_at"] != created["updated_at"]

    def test_restore_creates_version_of_current_state(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        client.put(f"/prompts/{created['id']}", json={
            "title": "Changed", "content": "Changed content"
        })
        # Before restore: 1 version (original state)
        versions_before = client.get(f"/prompts/{created['id']}/versions").json()
        assert versions_before["total"] == 1

        # Restore version 1
        client.post(f"/prompts/{created['id']}/versions/1/restore")

        # After restore: 2 versions (original + pre-restore "Changed" state)
        versions_after = client.get(f"/prompts/{created['id']}/versions").json()
        assert versions_after["total"] == 2
        # The newest version should be the "Changed" state saved before restore
        assert versions_after["versions"][0]["title"] == "Changed"

    def test_restore_prompt_not_found(self, client: TestClient):
        response = client.post("/prompts/nonexistent/versions/1/restore")
        assert response.status_code == 404

    def test_restore_version_not_found(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        response = client.post(f"/prompts/{created['id']}/versions/999/restore")
        assert response.status_code == 404


class TestVersionCleanup:
    """Tests for version deletion when a prompt is deleted."""

    def test_versions_deleted_with_prompt(self, client: TestClient, sample_prompt_data):
        created = client.post("/prompts", json=sample_prompt_data).json()
        client.put(f"/prompts/{created['id']}", json={
            "title": "V2", "content": "C2"
        })
        # Verify versions exist
        assert client.get(f"/prompts/{created['id']}/versions").json()["total"] == 1
        # Delete prompt
        client.delete(f"/prompts/{created['id']}")
        # Versions endpoint should return 404 since prompt is gone
        response = client.get(f"/prompts/{created['id']}/versions")
        assert response.status_code == 404


class TestVersionStorage:
    """Unit tests for version storage operations."""

    def test_create_and_get_versions(self):
        from app.storage import Storage
        from app.models import Prompt, PromptVersion

        store = Storage()
        prompt = Prompt(title="T", content="C")
        store.create_prompt(prompt)

        version = PromptVersion(
            prompt_id=prompt.id,
            version_number=1,
            title="T",
            content="C"
        )
        store.create_version(prompt.id, version)
        versions = store.get_versions(prompt.id)
        assert len(versions) == 1
        assert versions[0].version_number == 1

    def test_get_specific_version(self):
        from app.storage import Storage
        from app.models import Prompt, PromptVersion

        store = Storage()
        prompt = Prompt(title="T", content="C")
        store.create_prompt(prompt)

        v1 = PromptVersion(prompt_id=prompt.id, version_number=1, title="V1", content="C1")
        v2 = PromptVersion(prompt_id=prompt.id, version_number=2, title="V2", content="C2")
        store.create_version(prompt.id, v1)
        store.create_version(prompt.id, v2)

        result = store.get_version(prompt.id, 2)
        assert result is not None
        assert result.title == "V2"

    def test_get_version_not_found(self):
        from app.storage import Storage

        store = Storage()
        assert store.get_version("nonexistent", 1) is None

    def test_delete_versions(self):
        from app.storage import Storage
        from app.models import Prompt, PromptVersion

        store = Storage()
        prompt = Prompt(title="T", content="C")
        store.create_prompt(prompt)
        store.create_version(prompt.id, PromptVersion(
            prompt_id=prompt.id, version_number=1, title="T", content="C"
        ))
        assert store.delete_versions(prompt.id) is True
        assert store.get_versions(prompt.id) == []

    def test_delete_versions_none_exist(self):
        from app.storage import Storage

        store = Storage()
        assert store.delete_versions("nonexistent") is False

    def test_clear_also_clears_versions(self):
        from app.storage import Storage
        from app.models import Prompt, PromptVersion

        store = Storage()
        prompt = Prompt(title="T", content="C")
        store.create_prompt(prompt)
        store.create_version(prompt.id, PromptVersion(
            prompt_id=prompt.id, version_number=1, title="T", content="C"
        ))
        store.clear()
        assert store.get_versions(prompt.id) == []
