"""
Task data models for Taskinator.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

T = TypeVar('T')

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat() if obj else None
        return super().default(obj)

class Subtask(BaseModel):
    """Subtask model."""

    id: Union[int, str] = Field(..., description="Subtask ID (e.g., '1.1')")
    title: str = Field(..., description="Subtask title")
    description: Optional[str] = Field(None, description="Subtask description")
    status: str = Field("pending", description="Subtask status")
    dependencies: List[str] = Field(
        default_factory=list, description="List of dependency IDs"
    )
    details: Optional[str] = Field(None, description="Detailed implementation notes")
    test_strategy: Optional[str] = Field(None, description="Test strategy")
    priority: Optional[str] = Field(None, description="Priority (high, medium, low)")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Define model configuration without using deprecated json_encoders
    model_config = ConfigDict(
        extra="ignore"  # Allow extra fields for forward compatibility
    )

    @field_validator("status")
    def validate_status(cls, v: str) -> str:
        """Validate status field."""
        valid_statuses = [
            "pending",
            "in-progress",
            "done",
            "blocked",
            "deferred",
            "cancelled",
        ]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v.lower()

    @field_validator("dependencies", mode="before")
    def normalize_dependencies(cls, v: List[Union[int, str]]) -> List[str]:
        """Normalize dependencies to strings."""
        return [str(dep) for dep in v]

    @model_validator(mode="before")
    def set_timestamps(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set timestamps if not provided."""
        now = datetime.now()
        if "created_at" not in values or not values["created_at"]:
            values["created_at"] = now
        if "updated_at" not in values or not values["updated_at"]:
            values["updated_at"] = now
        return values

    def model_dump_json(self, **kwargs) -> str:
        """
        Generate a JSON representation of the model.

        This method is used for Pydantic v2 compatibility.

        Returns:
            str: JSON string
        """
        return json.dumps(self.model_dump(), cls=DateTimeEncoder, indent=2)

    def json(self, **kwargs) -> str:
        """
        Generate a JSON representation of the model.

        This method is for backward compatibility with Pydantic v1.

        Returns:
            str: JSON string
        """
        return self.model_dump_json(**kwargs)

    def model_dump(self) -> Dict[str, Any]:
        """
        Generate a dictionary representation of the model.

        This method is used for Pydantic v2 compatibility.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "dependencies": self.dependencies,
            "details": self.details,
            "test_strategy": self.test_strategy,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def dict(self) -> Dict[str, Any]:
        """
        Generate a dictionary representation of the model.

        This method is for backward compatibility with Pydantic v1.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return self.model_dump()


class Task(BaseModel):
    """Task model."""

    id: Union[int, str] = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    status: str = Field("pending", description="Task status")
    priority: str = Field("medium", description="Task priority")
    dependencies: List[str] = Field(
        default_factory=list, description="List of dependency IDs"
    )
    subtasks: List[Subtask] = Field(default_factory=list, description="List of subtasks")
    details: Optional[str] = Field(None, description="Detailed implementation notes")
    test_strategy: Optional[str] = Field(None, description="Test strategy")
    story_points: Optional[float] = Field(None, description="Story points estimation")
    sprint_id: Optional[str] = Field(None, description="ID of the sprint this task belongs to")
    acceptance_criteria: List[str] = Field(default_factory=list, description="List of acceptance criteria")
    task_type: Optional[str] = Field(None, description="Task type (user story, bug, tech debt, etc.)")
    assignee: Optional[str] = Field(None, description="Assigned team member")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    source: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Source document information (type, document, section)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    # Define model configuration without using deprecated json_encoders
    model_config = ConfigDict(
        extra="ignore"  # Allow extra fields for forward compatibility
    )

    @field_validator("status")
    def validate_status(cls, v: str) -> str:
        """Validate status field."""
        valid_statuses = [
            "pending",
            "in-progress",
            "done",
            "blocked",
            "deferred",
            "cancelled",
        ]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v.lower()

    @field_validator("priority")
    def validate_priority(cls, v: str) -> str:
        """Validate priority field."""
        valid_priorities = ["high", "medium", "low"]
        if v.lower() not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
        return v.lower()

    @field_validator("dependencies", mode="before")
    def normalize_dependencies(cls, v: List[Union[int, str]]) -> List[str]:
        """Normalize dependencies to strings."""
        return [str(dep) for dep in v]

    @model_validator(mode="before")
    def set_timestamps(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set timestamps if not provided."""
        now = datetime.now()
        if "created_at" not in values or not values["created_at"]:
            values["created_at"] = now
        if "updated_at" not in values or not values["updated_at"]:
            values["updated_at"] = now
        return values

    def model_dump_json(self, **kwargs) -> str:
        """
        Generate a JSON representation of the model.

        This method is used for Pydantic v2 compatibility.

        Returns:
            str: JSON string
        """
        return json.dumps(self.model_dump(), cls=DateTimeEncoder, indent=2)

    def json(self, **kwargs) -> str:
        """
        Generate a JSON representation of the model.

        This method is for backward compatibility with Pydantic v1.

        Returns:
            str: JSON string
        """
        return self.model_dump_json(**kwargs)

    def model_dump(self) -> Dict[str, Any]:
        """
        Generate a dictionary representation of the model.

        This method is used for Pydantic v2 compatibility.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "dependencies": self.dependencies,
            "subtasks": [
                subtask.model_dump() if hasattr(subtask, "model_dump") else subtask.dict()
                for subtask in self.subtasks
            ],
            "details": self.details,
            "test_strategy": self.test_strategy,
            "story_points": self.story_points,
            "sprint_id": self.sprint_id,
            "acceptance_criteria": self.acceptance_criteria,
            "task_type": self.task_type,
            "assignee": self.assignee,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "source": self.source,
            "metadata": self.metadata,
        }

    def dict(self) -> Dict[str, Any]:
        """
        Generate a dictionary representation of the model.

        This method is for backward compatibility with Pydantic v1.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return self.model_dump()


class TaskCollection(BaseModel):
    """Collection of tasks."""

    tasks: List[Task] = Field(default_factory=list, description="List of tasks")
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "project_name": "Taskinator",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "0.1.0",
        },
        description="Metadata about the task collection",
    )

    # Define model configuration without using deprecated json_encoders
    model_config = ConfigDict()

    @model_validator(mode="before")
    def ensure_metadata(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure metadata is present and has required fields."""
        # If metadata is not provided, create it
        if "metadata" not in values or not values["metadata"]:
            values["metadata"] = {
                "project_name": "Taskinator",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "0.1.0",
            }
        else:
            # Ensure required fields are present
            metadata = values["metadata"]
            if "project_name" not in metadata:
                metadata["project_name"] = "Taskinator"
            if "created_at" not in metadata:
                metadata["created_at"] = datetime.now().isoformat()
            if "updated_at" not in metadata:
                metadata["updated_at"] = datetime.now().isoformat()
            if "version" not in metadata:
                metadata["version"] = "0.1.0"

        return values

    def get_next_id(self) -> int:
        """
        Get the next available task ID.

        Returns:
            int: Next available task ID
        """
        if not self.tasks:
            return 1

        # Try to find the highest numeric ID
        numeric_ids = []
        for task in self.tasks:
            try:
                if isinstance(task.id, int) or (
                    isinstance(task.id, str) and task.id.isdigit()
                ):
                    numeric_ids.append(int(task.id))
            except (ValueError, TypeError):
                continue

        return max(numeric_ids, default=0) + 1

    def model_dump_json(self, **kwargs) -> str:
        """
        Generate a JSON representation of the model.

        This method is used for Pydantic v2 compatibility.

        Returns:
            str: JSON string
        """
        return json.dumps(self.model_dump(), cls=DateTimeEncoder, indent=2)

    def json(self, **kwargs) -> str:
        """
        Generate a JSON representation of the model.

        This method is for backward compatibility with Pydantic v1.

        Returns:
            str: JSON string
        """
        return self.model_dump_json(**kwargs)

    def model_dump(self) -> Dict[str, Any]:
        """
        Generate a dictionary representation of the model.

        This method is used for Pydantic v2 compatibility.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "tasks": [
                task.model_dump() if hasattr(task, "model_dump") else task.dict()
                for task in self.tasks
            ],
            "metadata": self.metadata,
        }

    def dict(self) -> Dict[str, Any]:
        """
        Generate a dictionary representation of the model.

        This method is for backward compatibility with Pydantic v1.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return self.model_dump()

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by its ID.

        This method searches through all tasks and subtasks to find a task with the given ID.

        Args:
            task_id: ID of the task to find

        Returns:
            The task if found, None otherwise
        """
        # First check main tasks
        for task in self.tasks:
            if str(task.id) == str(task_id):
                return task

            # Check subtasks if present
            if hasattr(task, "subtasks") and task.subtasks:
                for subtask in task.subtasks:
                    if str(subtask.id) == str(task_id):
                        return subtask

        return None
