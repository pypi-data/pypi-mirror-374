"""
Sprint data models for Taskinator.

This module defines the data models for sprint management in Taskinator.
"""

import json
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from taskinator.models.task import DateTimeEncoder


class SprintStatus(str, Enum):
    """Sprint status enumeration."""
    PLANNED = "planned"
    ACTIVE = "active" 
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DailyProgress(BaseModel):
    """Daily progress tracking for burndown charts."""
    
    date: Annotated[Union[datetime, date], Field(description="Date of the progress entry")]
    remaining_points: float = Field(0.0, description="Remaining story points")
    completed_points: float = Field(0.0, description="Completed story points")
    added_points: float = Field(0.0, description="Story points added during sprint")
    notes: Optional[str] = Field(None, description="Daily notes")
    
    model_config = ConfigDict(
        extra="ignore"  # Allow extra fields for forward compatibility
    )
    
    def model_dump(self) -> Dict[str, Any]:
        """Generate a dictionary representation of the model."""
        progress_date = None
        if isinstance(self.date, datetime):
            progress_date = self.date.date().isoformat()
        elif isinstance(self.date, date):
            progress_date = self.date.isoformat()
            
        return {
            "date": progress_date,
            "remaining_points": self.remaining_points,
            "completed_points": self.completed_points,
            "added_points": self.added_points,
            "notes": self.notes,
        }


class Sprint(BaseModel):
    """Sprint model for agile management."""
    
    id: str = Field(..., description="Sprint ID (e.g., 'sprint-1')")
    name: str = Field(..., description="Sprint name")
    goal: str = Field("", description="Sprint goal")
    start_date: Optional[datetime] = Field(None, description="Sprint start date")
    end_date: Optional[datetime] = Field(None, description="Sprint end date")
    status: SprintStatus = Field(SprintStatus.PLANNED, description="Sprint status")
    capacity: Optional[float] = Field(None, description="Team capacity in story points")
    retrospective: Optional[str] = Field(None, description="Sprint retrospective notes")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    progress: List[DailyProgress] = Field(default_factory=list, description="Daily progress tracking")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    
    model_config = ConfigDict(
        extra="ignore",  # Allow extra fields for forward compatibility
        use_enum_values=True  # Use enum values instead of Enum objects in export
    )
    
    @field_validator("status")
    def validate_status(cls, v: Union[str, SprintStatus]) -> SprintStatus:
        """Validate status field."""
        if isinstance(v, SprintStatus):
            return v
            
        # Convert string to enum if needed
        if isinstance(v, str) and v in [status.value for status in SprintStatus]:
            return SprintStatus(v)
            
        # Raise error for invalid status
        valid_statuses = [status.value for status in SprintStatus]
        raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
    
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
        """Generate a JSON representation of the model."""
        return json.dumps(self.model_dump(), cls=DateTimeEncoder, indent=2)
    
    def json(self, **kwargs) -> str:
        """Generate a JSON representation of the model (for backward compatibility)."""
        return self.model_dump_json(**kwargs)
    
    def model_dump(self) -> Dict[str, Any]:
        """Generate a dictionary representation of the model."""
        return {
            "id": self.id,
            "name": self.name,
            "goal": self.goal,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "status": self.status.value if isinstance(self.status, SprintStatus) else self.status,
            "capacity": self.capacity,
            "retrospective": self.retrospective,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "progress": [p.model_dump() for p in self.progress],
            "metadata": self.metadata,
        }
    
    def dict(self) -> Dict[str, Any]:
        """Generate a dictionary representation of the model (for backward compatibility)."""
        return self.model_dump()
    
    def add_progress(self, date_value: Union[datetime, date], remaining_points: float, 
                    completed_points: float = 0.0, added_points: float = 0.0, 
                    notes: Optional[str] = None) -> None:
        """
        Add a daily progress entry.
        
        Args:
            date_value: Date of the progress entry
            remaining_points: Remaining story points
            completed_points: Completed story points
            added_points: Story points added during sprint
            notes: Daily notes
        """
        # Check if entry for this date already exists
        existing_entry = next((p for p in self.progress if (p.date.date() == date_value.date() 
                             if isinstance(p.date, datetime) else p.date == date_value)), None)
        
        # If entry exists, update it
        if existing_entry:
            existing_entry.remaining_points = remaining_points
            existing_entry.completed_points = completed_points
            existing_entry.added_points = added_points
            if notes:
                existing_entry.notes = notes
        else:
            # Create new entry
            progress_entry = DailyProgress(
                date=date_value,
                remaining_points=remaining_points,
                completed_points=completed_points,
                added_points=added_points,
                notes=notes
            )
            self.progress.append(progress_entry)


class SprintCollection(BaseModel):
    """Collection of sprints."""
    
    sprints: List[Sprint] = Field(default_factory=list, description="List of sprints")
    metadata: Dict[str, Any] = Field(
        default_factory=lambda: {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "0.1.0",
        },
        description="Metadata about the sprint collection",
    )
    
    model_config = ConfigDict()
    
    @model_validator(mode="before")
    def ensure_metadata(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure metadata is present and has required fields."""
        # If metadata is not provided, create it
        if "metadata" not in values or not values["metadata"]:
            values["metadata"] = {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "0.1.0",
            }
        else:
            # Ensure required fields are present
            metadata = values["metadata"]
            if "created_at" not in metadata:
                metadata["created_at"] = datetime.now().isoformat()
            if "updated_at" not in metadata:
                metadata["updated_at"] = datetime.now().isoformat()
            if "version" not in metadata:
                metadata["version"] = "0.1.0"
        
        return values
    
    def model_dump_json(self, **kwargs) -> str:
        """Generate a JSON representation of the model."""
        return json.dumps(self.model_dump(), cls=DateTimeEncoder, indent=2)
    
    def json(self, **kwargs) -> str:
        """Generate a JSON representation of the model (for backward compatibility)."""
        return self.model_dump_json(**kwargs)
    
    def model_dump(self) -> Dict[str, Any]:
        """Generate a dictionary representation of the model."""
        return {
            "sprints": [sprint.model_dump() for sprint in self.sprints],
            "metadata": self.metadata,
        }
    
    def dict(self) -> Dict[str, Any]:
        """Generate a dictionary representation of the model (for backward compatibility)."""
        return self.model_dump()
    
    def get_sprint(self, sprint_id: str) -> Optional[Sprint]:
        """Get a sprint by ID."""
        return next((sprint for sprint in self.sprints if sprint.id == sprint_id), None)
    
    def add_sprint(self, sprint: Sprint) -> bool:
        """Add a sprint to the collection."""
        # Check if sprint with this ID already exists
        if self.get_sprint(sprint.id):
            return False
            
        self.sprints.append(sprint)
        return True
    
    def update_sprint(self, sprint: Sprint) -> bool:
        """Update an existing sprint in the collection."""
        # Find sprint by ID
        for i, existing_sprint in enumerate(self.sprints):
            if existing_sprint.id == sprint.id:
                self.sprints[i] = sprint
                return True
                
        return False
    
    def remove_sprint(self, sprint_id: str) -> bool:
        """Remove a sprint from the collection."""
        for i, sprint in enumerate(self.sprints):
            if sprint.id == sprint_id:
                self.sprints.pop(i)
                return True
                
        return False
    
    def get_active_sprint(self) -> Optional[Sprint]:
        """Get the currently active sprint."""
        active_sprints = [sprint for sprint in self.sprints if sprint.status == SprintStatus.ACTIVE]
        if not active_sprints:
            return None
            
        # If multiple active sprints (should not happen), return the one ending soonest
        if len(active_sprints) > 1:
            return sorted(active_sprints, key=lambda s: s.end_date or datetime.max)[0]
            
        return active_sprints[0]