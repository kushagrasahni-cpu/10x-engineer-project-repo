"""Tests for the in-memory storage layer."""

from app.models import Prompt, Collection
from app.storage import Storage


class TestPromptStorage:
    """Tests for prompt CRUD operations in Storage."""

    def test_create_and_get_prompt(self):
        store = Storage()
        prompt = Prompt(title="Test", content="Content")
        store.create_prompt(prompt)
        retrieved = store.get_prompt(prompt.id)
        assert retrieved is not None
        assert retrieved.id == prompt.id
        assert retrieved.title == "Test"

    def test_get_prompt_not_found(self):
        store = Storage()
        assert store.get_prompt("nonexistent") is None

    def test_get_all_prompts_empty(self):
        store = Storage()
        assert store.get_all_prompts() == []

    def test_get_all_prompts(self):
        store = Storage()
        store.create_prompt(Prompt(title="A", content="C1"))
        store.create_prompt(Prompt(title="B", content="C2"))
        assert len(store.get_all_prompts()) == 2

    def test_update_prompt(self):
        store = Storage()
        prompt = Prompt(title="Original", content="Content")
        store.create_prompt(prompt)
        updated = Prompt(id=prompt.id, title="Updated", content="New content")
        result = store.update_prompt(prompt.id, updated)
        assert result is not None
        assert result.title == "Updated"
        assert store.get_prompt(prompt.id).title == "Updated"

    def test_update_prompt_not_found(self):
        store = Storage()
        prompt = Prompt(title="T", content="C")
        assert store.update_prompt("nonexistent", prompt) is None

    def test_delete_prompt(self):
        store = Storage()
        prompt = Prompt(title="T", content="C")
        store.create_prompt(prompt)
        assert store.delete_prompt(prompt.id) is True
        assert store.get_prompt(prompt.id) is None

    def test_delete_prompt_not_found(self):
        store = Storage()
        assert store.delete_prompt("nonexistent") is False


class TestCollectionStorage:
    """Tests for collection CRUD operations in Storage."""

    def test_create_and_get_collection(self):
        store = Storage()
        col = Collection(name="Dev")
        store.create_collection(col)
        retrieved = store.get_collection(col.id)
        assert retrieved is not None
        assert retrieved.name == "Dev"

    def test_get_collection_not_found(self):
        store = Storage()
        assert store.get_collection("nonexistent") is None

    def test_get_all_collections_empty(self):
        store = Storage()
        assert store.get_all_collections() == []

    def test_get_all_collections(self):
        store = Storage()
        store.create_collection(Collection(name="A"))
        store.create_collection(Collection(name="B"))
        assert len(store.get_all_collections()) == 2

    def test_delete_collection(self):
        store = Storage()
        col = Collection(name="Dev")
        store.create_collection(col)
        assert store.delete_collection(col.id) is True
        assert store.get_collection(col.id) is None

    def test_delete_collection_not_found(self):
        store = Storage()
        assert store.delete_collection("nonexistent") is False

    def test_get_prompts_by_collection(self):
        store = Storage()
        col = Collection(name="Dev")
        store.create_collection(col)
        p1 = Prompt(title="In col", content="C", collection_id=col.id)
        p2 = Prompt(title="No col", content="C")
        store.create_prompt(p1)
        store.create_prompt(p2)
        results = store.get_prompts_by_collection(col.id)
        assert len(results) == 1
        assert results[0].id == p1.id

    def test_get_prompts_by_collection_empty(self):
        store = Storage()
        assert store.get_prompts_by_collection("nonexistent") == []


class TestStorageClear:
    """Tests for the clear utility method."""

    def test_clear(self):
        store = Storage()
        store.create_prompt(Prompt(title="T", content="C"))
        store.create_collection(Collection(name="N"))
        store.clear()
        assert store.get_all_prompts() == []
        assert store.get_all_collections() == []
