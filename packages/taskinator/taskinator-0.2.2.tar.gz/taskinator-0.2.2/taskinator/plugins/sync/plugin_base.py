"""
Base class for sync plugins.

This module defines the base classes for sync plugins in Taskinator.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ConfigDict

from taskinator.models.task import Task, TaskCollection


class SyncDirection(str, Enum):
    """Direction of synchronization."""

    LOCAL_TO_REMOTE = "local_to_remote"
    REMOTE_TO_LOCAL = "remote_to_local"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(str, Enum):
    """Synchronization status for tasks."""

    PENDING = "pending"
    SYNCED = "synced"
    CONFLICT = "conflict"
    ERROR = "error"
    DELETED = "deleted"


class SyncMetadata(BaseModel):
    """Base metadata for synchronization."""

    provider: str = Field(..., description="Sync provider name")
    last_sync: Optional[str] = Field(None, description="Last synchronization timestamp")
    sync_status: SyncStatus = Field(
        SyncStatus.PENDING, description="Synchronization status"
    )
    remote_id: Optional[str] = Field(None, description="Remote ID for the task")

    model_config = ConfigDict(
        extra="allow"  # Allow extra fields for forward compatibility
    )


class SyncPlugin(ABC):
    """Base class for sync plugins."""

    name: str = "sync"
    provider: str = "base"

    @abstractmethod
    def setup(self, **kwargs) -> bool:
        """
        Set up the sync plugin.

        Args:
            **kwargs: Additional setup parameters

        Returns:
            bool: True if setup was successful, False otherwise
        """
        pass

    @abstractmethod
    def sync(
        self,
        tasks_path: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Synchronize tasks.

        Args:
            tasks_path: Path to the tasks.json file
            direction: Direction of synchronization
            **kwargs: Additional synchronization parameters

        Returns:
            Dict[str, Any]: Synchronization results
        """
        pass

    @abstractmethod
    def get_status(self, tasks_path: str, **kwargs) -> Dict[str, Any]:
        """
        Get synchronization status.

        Args:
            tasks_path: Path to the tasks.json file
            **kwargs: Additional parameters

        Returns:
            Dict[str, Any]: Synchronization status
        """
        pass

    @abstractmethod
    def resolve_conflicts(
        self, tasks_path: str, task_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Resolve synchronization conflicts.

        Args:
            tasks_path: Path to the tasks.json file
            task_id: Optional task ID to resolve conflicts for
            **kwargs: Additional parameters

        Returns:
            Dict[str, Any]: Conflict resolution results
        """
        pass

    def get_metadata_key(self) -> str:
        """
        Get the metadata key for this sync provider.

        Returns:
            str: Metadata key
        """
        return f"sync_{self.provider}"

    def get_task_metadata(self, task: Task) -> Optional[SyncMetadata]:
        """
        Get synchronization metadata for a task.

        Args:
            task: Task to get metadata for

        Returns:
            Optional[SyncMetadata]: Synchronization metadata
        """
        metadata_key = self.get_metadata_key()

        # Check if task has metadata for this provider
        if hasattr(task, metadata_key) and getattr(task, metadata_key):
            return SyncMetadata.parse_obj(getattr(task, metadata_key))

        # Check if task has metadata in extra fields
        if hasattr(task, "extra") and task.extra and metadata_key in task.extra:
            return SyncMetadata.parse_obj(task.extra[metadata_key])

        return None

    def set_task_metadata(self, task: Task, metadata: SyncMetadata) -> Task:
        """
        Set synchronization metadata for a task.

        Args:
            task: Task to set metadata for
            metadata: Synchronization metadata

        Returns:
            Task: Updated task
        """
        metadata_key = self.get_metadata_key()

        # Initialize extra if needed
        if not hasattr(task, "extra") or task.extra is None:
            task.extra = {}

        # Set metadata in extra fields
        task.extra[metadata_key] = metadata.dict()

        return task
