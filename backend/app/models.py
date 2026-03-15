"""Pydantic models for PromptLab.

Defines all request/response schemas used by the PromptLab API, including
models for prompts, collections, and standard response wrappers.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import uuid4


def generate_id() -> str:
    """Generate a unique identifier for a resource.

    Returns:
        A UUID4 string to be used as a primary key.

    Example:
        >>> id = generate_id()
        >>> print(id)
        "95958876-49c3-4a93-b254-ccedcc9d5a6f"
    """
    return str(uuid4())


def get_current_time() -> datetime:
    """Get the current UTC timestamp.

    Returns:
        The current datetime in UTC, used for created_at and updated_at fields.

    Example:
        >>> now = get_current_time()
        >>> print(now)
        datetime.datetime(2026, 3, 2, 12, 0, 0, 0)
    """
    return datetime.utcnow()


# ============== Prompt Models ==============

class PromptBase(BaseModel):
    """Base schema for prompt data shared across create and read operations.

    Attributes:
        title: The prompt title. Must be between 1 and 200 characters.
        content: The prompt template body. Supports ``{{variable}}`` placeholders.
            Must be at least 1 character.
        description: An optional short description of the prompt. Max 500 characters.
        collection_id: Optional ID of the collection this prompt belongs to.
    """

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None


class PromptCreate(PromptBase):
    """Schema for creating a new prompt.

    Inherits all fields from PromptBase. The ``id``, ``created_at``, and
    ``updated_at`` fields are generated automatically by the server.
    """

    pass


class PromptUpdate(BaseModel):
    """Schema for updating an existing prompt (used by both PUT and PATCH).

    All fields are optional to support partial updates via PATCH.
    For PUT requests, the API expects all fields to be provided.

    Attributes:
        title: Updated prompt title. Must be between 1 and 200 characters.
        content: Updated prompt template body. Must be at least 1 character.
        description: Updated description. Max 500 characters.
        collection_id: Updated collection assignment.
    """

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, max_length=500)
    collection_id: Optional[str] = None


class Prompt(PromptBase):
    """Full prompt resource returned by the API.

    Extends PromptBase with server-generated fields for identification
    and timestamp tracking.

    Attributes:
        id: Auto-generated UUID4 identifier.
        created_at: UTC timestamp set when the prompt is created.
        updated_at: UTC timestamp updated on every PUT or PATCH operation.
    """

    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)

    class Config:
        """Pydantic configuration for the Prompt model."""

        from_attributes = True


# ============== Collection Models ==============

class CollectionBase(BaseModel):
    """Base schema for collection data shared across create and read operations.

    Attributes:
        name: The collection name. Must be between 1 and 100 characters.
        description: An optional short description of the collection.
            Max 500 characters.
    """

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CollectionCreate(CollectionBase):
    """Schema for creating a new collection.

    Inherits all fields from CollectionBase. The ``id`` and ``created_at``
    fields are generated automatically by the server.
    """

    pass


class Collection(CollectionBase):
    """Full collection resource returned by the API.

    Extends CollectionBase with server-generated fields for identification
    and timestamp tracking.

    Attributes:
        id: Auto-generated UUID4 identifier.
        created_at: UTC timestamp set when the collection is created.
    """

    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=get_current_time)

    class Config:
        """Pydantic configuration for the Collection model."""

        from_attributes = True


# ============== Version Models ==============

class PromptVersion(BaseModel):
    """A historical snapshot of a prompt's state before an update.

    Attributes:
        id: Auto-generated UUID4 identifier for this version.
        prompt_id: The UUID of the parent prompt.
        version_number: Auto-incrementing version number per prompt (1, 2, 3, ...).
        title: The prompt title at this version.
        content: The prompt content at this version.
        description: The prompt description at this version.
        collection_id: The collection assignment at this version.
        created_at: UTC timestamp when this version was saved.
    """

    id: str = Field(default_factory=generate_id)
    prompt_id: str
    version_number: int
    title: str
    content: str
    description: Optional[str] = None
    collection_id: Optional[str] = None
    created_at: datetime = Field(default_factory=get_current_time)


class PromptVersionList(BaseModel):
    """Response wrapper for a list of prompt versions.

    Attributes:
        versions: The list of PromptVersion objects.
        total: The total number of versions.
    """

    versions: List[PromptVersion]
    total: int


# ============== Response Models ==============

class PromptList(BaseModel):
    """Response wrapper for a list of prompts.

    Attributes:
        prompts: The list of Prompt objects matching the query.
        total: The total number of prompts in the response.
    """

    prompts: List[Prompt]
    total: int


class CollectionList(BaseModel):
    """Response wrapper for a list of collections.

    Attributes:
        collections: The list of Collection objects.
        total: The total number of collections in the response.
    """

    collections: List[Collection]
    total: int


class HealthResponse(BaseModel):
    """Response schema for the health check endpoint.

    Attributes:
        status: The API health status (e.g., ``"healthy"``).
        version: The current API version string.
    """

    status: str
    version: str

