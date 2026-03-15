"""Tests for Pydantic model validation and serialization."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models import (
    PromptBase,
    PromptCreate,
    PromptUpdate,
    Prompt,
    CollectionBase,
    CollectionCreate,
    Collection,
    PromptList,
    CollectionList,
    HealthResponse,
    generate_id,
    get_current_time,
)


class TestGenerateId:
    """Tests for the generate_id helper."""

    def test_returns_string(self):
        assert isinstance(generate_id(), str)

    def test_unique(self):
        assert generate_id() != generate_id()


class TestGetCurrentTime:
    """Tests for the get_current_time helper."""

    def test_returns_datetime(self):
        assert isinstance(get_current_time(), datetime)


class TestPromptModels:
    """Tests for Prompt-related Pydantic models."""

    def test_prompt_create_valid(self):
        p = PromptCreate(title="Title", content="Content")
        assert p.title == "Title"
        assert p.description is None
        assert p.collection_id is None

    def test_prompt_create_all_fields(self):
        p = PromptCreate(
            title="T",
            content="C",
            description="D",
            collection_id="col-1"
        )
        assert p.description == "D"
        assert p.collection_id == "col-1"

    def test_prompt_create_missing_title(self):
        with pytest.raises(ValidationError):
            PromptCreate(content="C")

    def test_prompt_create_missing_content(self):
        with pytest.raises(ValidationError):
            PromptCreate(title="T")

    def test_prompt_create_empty_title(self):
        with pytest.raises(ValidationError):
            PromptCreate(title="", content="C")

    def test_prompt_create_title_max_length(self):
        p = PromptCreate(title="x" * 200, content="C")
        assert len(p.title) == 200

    def test_prompt_create_title_too_long(self):
        with pytest.raises(ValidationError):
            PromptCreate(title="x" * 201, content="C")

    def test_prompt_create_description_max_length(self):
        p = PromptCreate(title="T", content="C", description="x" * 500)
        assert len(p.description) == 500

    def test_prompt_create_description_too_long(self):
        with pytest.raises(ValidationError):
            PromptCreate(title="T", content="C", description="x" * 501)

    def test_prompt_auto_generated_fields(self):
        p = Prompt(title="T", content="C")
        assert p.id is not None
        assert isinstance(p.created_at, datetime)
        assert isinstance(p.updated_at, datetime)

    def test_prompt_unique_ids(self):
        p1 = Prompt(title="T1", content="C1")
        p2 = Prompt(title="T2", content="C2")
        assert p1.id != p2.id

    def test_prompt_update_all_optional(self):
        u = PromptUpdate()
        assert u.title is None
        assert u.content is None
        assert u.description is None
        assert u.collection_id is None

    def test_prompt_update_partial(self):
        u = PromptUpdate(title="New Title")
        assert u.title == "New Title"
        assert u.content is None

    def test_prompt_update_title_validation(self):
        with pytest.raises(ValidationError):
            PromptUpdate(title="")

    def test_prompt_serialization(self):
        p = Prompt(title="T", content="C", description="D")
        data = p.model_dump()
        assert data["title"] == "T"
        assert data["content"] == "C"
        assert data["description"] == "D"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data


class TestCollectionModels:
    """Tests for Collection-related Pydantic models."""

    def test_collection_create_valid(self):
        c = CollectionCreate(name="Dev")
        assert c.name == "Dev"
        assert c.description is None

    def test_collection_create_missing_name(self):
        with pytest.raises(ValidationError):
            CollectionCreate()

    def test_collection_create_empty_name(self):
        with pytest.raises(ValidationError):
            CollectionCreate(name="")

    def test_collection_create_name_max_length(self):
        c = CollectionCreate(name="x" * 100)
        assert len(c.name) == 100

    def test_collection_create_name_too_long(self):
        with pytest.raises(ValidationError):
            CollectionCreate(name="x" * 101)

    def test_collection_create_description_too_long(self):
        with pytest.raises(ValidationError):
            CollectionCreate(name="N", description="x" * 501)

    def test_collection_auto_generated_fields(self):
        c = Collection(name="Dev")
        assert c.id is not None
        assert isinstance(c.created_at, datetime)

    def test_collection_serialization(self):
        c = Collection(name="Dev", description="Desc")
        data = c.model_dump()
        assert data["name"] == "Dev"
        assert data["description"] == "Desc"
        assert "id" in data
        assert "created_at" in data


class TestResponseModels:
    """Tests for response wrapper models."""

    def test_prompt_list(self):
        p = Prompt(title="T", content="C")
        pl = PromptList(prompts=[p], total=1)
        assert pl.total == 1
        assert len(pl.prompts) == 1

    def test_prompt_list_empty(self):
        pl = PromptList(prompts=[], total=0)
        assert pl.total == 0

    def test_collection_list(self):
        c = Collection(name="N")
        cl = CollectionList(collections=[c], total=1)
        assert cl.total == 1

    def test_health_response(self):
        h = HealthResponse(status="healthy", version="0.1.0")
        assert h.status == "healthy"
        assert h.version == "0.1.0"
