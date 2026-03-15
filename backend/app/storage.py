"""In-memory storage for PromptLab.

Provides a dictionary-based in-memory data store for prompts and
collections. Data does not persist across server restarts. In a
production environment, this would be replaced with a database.
"""

from typing import Dict, List, Optional
from app.models import Prompt, Collection, PromptVersion


class Storage:
    """In-memory storage backend for prompts and collections.

    Uses Python dictionaries keyed by resource UUID for O(1) lookups.
    A single global instance is created at module level and shared
    across the application.

    Attributes:
        _prompts: Internal dictionary mapping prompt IDs to Prompt objects.
        _collections: Internal dictionary mapping collection IDs to
            Collection objects.
    """

    def __init__(self):
        """Initialize an empty storage instance."""
        self._prompts: Dict[str, Prompt] = {}
        self._collections: Dict[str, Collection] = {}
        self._versions: Dict[str, List[PromptVersion]] = {}

    # ============== Prompt Operations ==============

    def create_prompt(self, prompt: Prompt) -> Prompt:
        """Store a new prompt.

        Args:
            prompt: The Prompt object to store. Must have a unique ``id``.

        Returns:
            The stored Prompt object.
        """
        self._prompts[prompt.id] = prompt
        return prompt

    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Retrieve a prompt by its unique identifier.

        Args:
            prompt_id: The UUID of the prompt to retrieve.

        Returns:
            The Prompt object if found, None otherwise.
        """
        return self._prompts.get(prompt_id)

    def get_all_prompts(self) -> List[Prompt]:
        """Retrieve all stored prompts.

        Returns:
            A list of all Prompt objects in storage.
        """
        return list(self._prompts.values())

    def update_prompt(self, prompt_id: str, prompt: Prompt) -> Optional[Prompt]:
        """Replace an existing prompt with updated data.

        Args:
            prompt_id: The UUID of the prompt to update.
            prompt: The new Prompt object to store in its place.

        Returns:
            The updated Prompt object if found, None if the prompt
            does not exist.
        """
        if prompt_id not in self._prompts:
            return None
        self._prompts[prompt_id] = prompt
        return prompt

    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt by its unique identifier.

        Args:
            prompt_id: The UUID of the prompt to delete.

        Returns:
            True if the prompt was found and deleted, False otherwise.
        """
        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            return True
        return False

    # ============== Collection Operations ==============

    def create_collection(self, collection: Collection) -> Collection:
        """Store a new collection.

        Args:
            collection: The Collection object to store. Must have a
                unique ``id``.

        Returns:
            The stored Collection object.
        """
        self._collections[collection.id] = collection
        return collection

    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """Retrieve a collection by its unique identifier.

        Args:
            collection_id: The UUID of the collection to retrieve.

        Returns:
            The Collection object if found, None otherwise.
        """
        return self._collections.get(collection_id)

    def get_all_collections(self) -> List[Collection]:
        """Retrieve all stored collections.

        Returns:
            A list of all Collection objects in storage.
        """
        return list(self._collections.values())

    def delete_collection(self, collection_id: str) -> bool:
        """Delete a collection by its unique identifier.

        Does not check for associated prompts — that validation is
        handled by the API layer before calling this method.

        Args:
            collection_id: The UUID of the collection to delete.

        Returns:
            True if the collection was found and deleted, False otherwise.
        """
        if collection_id in self._collections:
            del self._collections[collection_id]
            return True
        return False

    def get_prompts_by_collection(self, collection_id: str) -> List[Prompt]:
        """Retrieve all prompts belonging to a specific collection.

        Args:
            collection_id: The UUID of the collection to filter by.

        Returns:
            A list of Prompt objects whose ``collection_id`` matches
            the given ID.
        """
        return [p for p in self._prompts.values() if p.collection_id == collection_id]

    # ============== Version Operations ==============

    def create_version(self, prompt_id: str, version: PromptVersion) -> PromptVersion:
        """Store a new version snapshot for a prompt.

        Args:
            prompt_id: The UUID of the parent prompt.
            version: The PromptVersion object to store.

        Returns:
            The stored PromptVersion object.
        """
        if prompt_id not in self._versions:
            self._versions[prompt_id] = []
        self._versions[prompt_id].append(version)
        return version

    def get_versions(self, prompt_id: str) -> List[PromptVersion]:
        """Retrieve all versions for a prompt.

        Args:
            prompt_id: The UUID of the prompt.

        Returns:
            A list of PromptVersion objects, may be empty.
        """
        return list(self._versions.get(prompt_id, []))

    def get_version(self, prompt_id: str, version_number: int) -> Optional[PromptVersion]:
        """Retrieve a specific version by prompt ID and version number.

        Args:
            prompt_id: The UUID of the prompt.
            version_number: The version number to retrieve.

        Returns:
            The PromptVersion if found, None otherwise.
        """
        for v in self._versions.get(prompt_id, []):
            if v.version_number == version_number:
                return v
        return None

    def delete_versions(self, prompt_id: str) -> bool:
        """Delete all versions for a prompt.

        Args:
            prompt_id: The UUID of the prompt.

        Returns:
            True if versions existed and were deleted, False otherwise.
        """
        if prompt_id in self._versions:
            del self._versions[prompt_id]
            return True
        return False

    # ============== Utility ==============

    def clear(self):
        """Remove all prompts, collections, and versions from storage.

        Primarily used in tests to reset state between test cases.
        """
        self._prompts.clear()
        self._collections.clear()
        self._versions.clear()


# Global storage instance
storage = Storage()
