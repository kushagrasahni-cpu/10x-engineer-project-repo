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
    client.post("/prompts", json=prompt_data)

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
