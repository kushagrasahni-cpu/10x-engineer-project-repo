"""FastAPI routes for PromptLab.

Defines all API endpoints for managing prompts and collections,
including CRUD operations, search, filtering, and health checking.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models import (
    Prompt, PromptCreate, PromptUpdate,
    Collection, CollectionCreate,
    PromptList, CollectionList, HealthResponse,
    get_current_time
)
from app.storage import storage
from app.utils import sort_prompts_by_date, filter_prompts_by_collection, search_prompts
from app import __version__


app = FastAPI(
    title="PromptLab API",
    description="AI Prompt Engineering Platform",
    version=__version__
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Check the health status of the API.

    Returns:
        HealthResponse: JSON object with ``status`` and ``version`` fields.
    """
    return HealthResponse(status="healthy", version=__version__)


# ============== Prompt Endpoints ==============

@app.get("/prompts", response_model=PromptList)
def list_prompts(
    collection_id: Optional[str] = None,
    search: Optional[str] = None
):
    """List all prompts with optional filtering, search, and sorting.

    Prompts are filtered by collection, then searched by query, then
    sorted by creation date (newest first).

    Args:
        collection_id: Optional collection ID to filter prompts by.
        search: Optional case-insensitive search query matched against
            prompt title and description.

    Returns:
        PromptList: JSON object containing the list of matching prompts
            and a total count.
    """
    prompts = storage.get_all_prompts()
    
    # Filter by collection if specified
    if collection_id:
        prompts = filter_prompts_by_collection(prompts, collection_id)
    
    # Search if query provided
    if search:
        prompts = search_prompts(prompts, search)
    
    # Sort by date (newest first)
    # Note: There might be an issue with the sorting...
    prompts = sort_prompts_by_date(prompts, descending=True)
    
    return PromptList(prompts=prompts, total=len(prompts))


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    """Retrieve a single prompt by its unique identifier.

    Args:
        prompt_id: The UUID of the prompt to retrieve.

    Returns:
        Prompt: The matching prompt object.

    Raises:
        HTTPException: 404 if no prompt exists with the given ID.
    """
    prompt = storage.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt
    

@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate):
    """Create a new prompt.

    Generates a UUID and timestamps automatically. If a ``collection_id``
    is provided, validates that the collection exists before creating.

    Args:
        prompt_data: The prompt fields (title, content, description,
            collection_id).

    Returns:
        Prompt: The newly created prompt with generated id and timestamps.

    Raises:
        HTTPException: 400 if the referenced collection does not exist.
    """
    # Validate collection exists if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    prompt = Prompt(**prompt_data.model_dump())
    return storage.create_prompt(prompt)


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Fully update an existing prompt, replacing all mutable fields.

    Preserves the original ``id`` and ``created_at`` values. The
    ``updated_at`` timestamp is refreshed to the current time.

    Args:
        prompt_id: The UUID of the prompt to update.
        prompt_data: The complete set of updated fields.

    Returns:
        Prompt: The updated prompt object.

    Raises:
        HTTPException: 404 if no prompt exists with the given ID.
        HTTPException: 400 if the referenced collection does not exist.
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Validate collection if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    # Correctly update the updated_at timestamp
    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        collection_id=prompt_data.collection_id,
        created_at=existing.created_at,
        updated_at=get_current_time()  # Updated line to fix the timestamp
    )
    
    return storage.update_prompt(prompt_id, updated_prompt)


@app.patch("/prompts/{prompt_id}", response_model=Prompt)
def patch_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Partially update an existing prompt.

    Only the fields included in the request body are modified; all other
    fields are preserved. The ``updated_at`` timestamp is refreshed
    to the current time.

    Args:
        prompt_id: The UUID of the prompt to update.
        prompt_data: The fields to update. Omitted fields remain unchanged.

    Returns:
        Prompt: The updated prompt object with all fields.

    Raises:
        HTTPException: 404 if no prompt exists with the given ID.
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Update only the fields provided
    updated_fields = prompt_data.dict(exclude_unset=True)
    for field, value in updated_fields.items():
        setattr(existing, field, value)

    # Update the timestamp
    existing.updated_at = get_current_time()

    return storage.update_prompt(prompt_id, existing)


@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str):
    """Delete a prompt by its unique identifier.

    Args:
        prompt_id: The UUID of the prompt to delete.

    Returns:
        None: Returns no content on success (HTTP 204).

    Raises:
        HTTPException: 404 if no prompt exists with the given ID.
    """
    if not storage.delete_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Prompt not found")
    return None


# ============== Collection Endpoints ==============

@app.get("/collections", response_model=CollectionList)
def list_collections():
    """List all collections.

    Returns:
        CollectionList: JSON object containing the list of all collections
            and a total count.
    """
    collections = storage.get_all_collections()
    return CollectionList(collections=collections, total=len(collections))


@app.get("/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    """Retrieve a single collection by its unique identifier.

    Args:
        collection_id: The UUID of the collection to retrieve.

    Returns:
        Collection: The matching collection object.

    Raises:
        HTTPException: 404 if no collection exists with the given ID.
    """
    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection
    

@app.post("/collections", response_model=Collection, status_code=201)
def create_collection(collection_data: CollectionCreate):
    """Create a new collection.

    Generates a UUID and creation timestamp automatically.

    Args:
        collection_data: The collection fields (name, description).

    Returns:
        Collection: The newly created collection with generated id and
            timestamp.
    """
    collection = Collection(**collection_data.model_dump())
    return storage.create_collection(collection)


@app.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str):
    """Delete a collection by its unique identifier.

    Deletion is blocked if any prompts are still associated with the
    collection, preventing orphaned prompt references.

    Args:
        collection_id: The UUID of the collection to delete.

    Returns:
        None: Returns no content on success (HTTP 204).

    Raises:
        HTTPException: 400 if the collection still has associated prompts.
        HTTPException: 404 if no collection exists with the given ID.
    """
    # Check if there are prompts associated with this collection
    associated_prompts = storage.get_prompts_by_collection(collection_id)
    if associated_prompts:
        raise HTTPException(status_code=400, detail="Collection cannot be deleted. It has associated prompts.")
    if not storage.delete_collection(collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")
    
    return None

