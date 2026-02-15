from fastapi.testclient import TestClient

class TestCollections:
    """Tests for collection endpoints."""

    def test_delete_collection_with_prompts(self, client: TestClient, sample_collection_data, sample_prompt_data):
        """Test deleting a collection that has prompts and should raise error without deletion.
        
        NOTE: Bug #4 - prompts become orphaned after collection deletion.
        This test documents the current (buggy) behavior.
        After fixing, update the test to verify correct behavior.
        """
        # Create collection
        col_response = client.post("/collections", json=sample_collection_data)
        collection_id = col_response.json()["id"]
        
        # Create prompt in collection
        prompt_data = {**sample_prompt_data, "collection_id": collection_id}
        client.post("/prompts", json=prompt_data)  # Corrected indentation

        # Attempt to delete the collection
        del_response = client.delete(f"/collections/{collection_id}")
        
        # The intended behavior should raise error and prevent deletion
        # if the collection has associated prompts.
        assert del_response.status_code == 400
        assert del_response.json()["detail"] == "Collection cannot be deleted. It has associated prompts."

        # Documenting current expectations:
        prompts = client.get("/prompts").json()["prompts"]
        if prompts:
            # Prompt exists with orphaned collection_id
            assert prompts[0]["collection_id"] == collection_id


class TestPrompts:
    def test_patch_prompt(self, client: TestClient, sample_prompt_data):
        # Create a prompt first
        create_response = client.post("/prompts", json=sample_prompt_data)
        prompt_id = create_response.json()["id"]

        # Partially update it
        partial_update_data = {
            "title": "Partially Updated Title"
        }
        response = client.patch(f"/prompts/{prompt_id}", json=partial_update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Partially Updated Title"
        assert data["content"] == sample_prompt_data["content"]

        # Check if the updated_at field is refreshed
        original_updated_at = create_response.json()["updated_at"]
        assert data["updated_at"] != original_updated_at

