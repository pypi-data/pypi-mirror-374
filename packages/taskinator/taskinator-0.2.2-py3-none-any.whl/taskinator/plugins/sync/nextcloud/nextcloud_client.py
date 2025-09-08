"""
NextCloud client for interacting with NextCloud Tasks API.

This module provides a client for interacting with the NextCloud Tasks API
using the CalDAV protocol.
"""

import asyncio
import json
import logging
import os
import random
import time
import uuid
from datetime import date, datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

import caldav
import requests
from caldav.elements import cdav, dav

# Import icalendar components
from icalendar import Calendar, Todo
from icalendar.prop import vCalAddress, vText
from pydantic import BaseModel, ConfigDict, Field, model_validator

# Set up logging
log = logging.getLogger(__name__)

# Define a generic type variable for the return type
T = TypeVar('T')


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message="Nextcloud rate limit exceeded", retry_after=None):
        self.message = message
        self.retry_after = retry_after
        super().__init__(self.message)


def with_retry(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    """Decorator to retry API calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    # Check if it's a rate limit error (429)
                    if e.response is not None and e.response.status_code == 429:
                        retry_after = None
                        # Try to get retry-after header
                        if 'Retry-After' in e.response.headers:
                            try:
                                retry_after = int(e.response.headers['Retry-After'])
                            except ValueError:
                                pass
                            
                        if retries >= max_retries:
                            raise RateLimitExceeded(
                                message=f"Rate limit exceeded after {max_retries} retries",
                                retry_after=retry_after
                            ) from e
                            
                        # Calculate delay with exponential backoff and jitter
                        delay = min(base_delay * (2 ** retries) + random.uniform(0, 1), max_delay)
                        if retry_after is not None:
                            delay = max(delay, float(retry_after))
                            
                        log.warning(
                            f"Rate limit exceeded, retrying in {delay:.2f} seconds "
                            f"(attempt {retries + 1}/{max_retries})"
                        )
                        time.sleep(delay)
                        retries += 1
                    else:
                        # Re-raise other HTTP errors
                        raise
                except (caldav.lib.error.DAVError, requests.exceptions.RequestException) as e:
                    # Handle DAV errors that might be rate-limiting related
                    if retries >= max_retries:
                        raise
                    
                    # Check if this might be a rate limit issue
                    is_rate_limit = False
                    if hasattr(e, 'status') and getattr(e, 'status', 0) == 429:
                        is_rate_limit = True
                    elif hasattr(e, 'reason') and '429' in str(getattr(e, 'reason', '')):
                        is_rate_limit = True
                        
                    if is_rate_limit:
                        delay = min(base_delay * (2 ** retries) + random.uniform(0, 1), max_delay)
                        log.warning(
                            f"Possible rate limit detected, retrying in {delay:.2f} seconds "
                            f"(attempt {retries + 1}/{max_retries})"
                        )
                        time.sleep(delay)
                        retries += 1
                    else:
                        # Re-raise other errors
                        raise
        return cast(Callable[..., T], wrapper)
    return decorator


async def async_with_retry(func, *args, max_retries=3, base_delay=1.0, max_delay=60.0, **kwargs):
    """Asynchronous retry helper for async functions.
    
    Args:
        func: Async function to call
        args: Positional arguments to pass to func
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        kwargs: Keyword arguments to pass to func
        
    Returns:
        The result of the function call
        
    Raises:
        RateLimitExceeded: If rate limit is exceeded after max_retries
    """
    retries = 0
    while True:
        try:
            return await func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            # Check if it's a rate limit error (429)
            if e.response is not None and e.response.status_code == 429:
                retry_after = None
                # Try to get retry-after header
                if 'Retry-After' in e.response.headers:
                    try:
                        retry_after = int(e.response.headers['Retry-After'])
                    except ValueError:
                        pass
                    
                if retries >= max_retries:
                    raise RateLimitExceeded(
                        message=f"Rate limit exceeded after {max_retries} retries",
                        retry_after=retry_after
                    ) from e
                    
                # Calculate delay with exponential backoff and jitter
                delay = min(base_delay * (2 ** retries) + random.uniform(0, 1), max_delay)
                if retry_after is not None:
                    delay = max(delay, float(retry_after))
                    
                log.warning(
                    f"Rate limit exceeded, retrying in {delay:.2f} seconds "
                    f"(attempt {retries + 1}/{max_retries})"
                )
                await asyncio.sleep(delay)
                retries += 1
            else:
                # Re-raise other HTTP errors
                raise
        except (caldav.lib.error.DAVError, requests.exceptions.RequestException) as e:
            # Handle DAV errors that might be rate-limiting related
            if retries >= max_retries:
                raise
            
            # Check if this might be a rate limit issue
            is_rate_limit = False
            if hasattr(e, 'status') and getattr(e, 'status', 0) == 429:
                is_rate_limit = True
            elif hasattr(e, 'reason') and '429' in str(getattr(e, 'reason', '')):
                is_rate_limit = True
                
            if is_rate_limit:
                delay = min(base_delay * (2 ** retries) + random.uniform(0, 1), max_delay)
                log.warning(
                    f"Possible rate limit detected, retrying in {delay:.2f} seconds "
                    f"(attempt {retries + 1}/{max_retries})"
                )
                await asyncio.sleep(delay)
                retries += 1
            else:
                # Re-raise other errors
                raise


class NextCloudTask(BaseModel):
    """NextCloud task data model."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True, json_schema_serialization_defaults_required=True
    )

    id: str
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    priority: Optional[str] = None
    calendar_id: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    etag: Optional[str] = None
    fileid: Optional[str] = None
    subtasks: List[Dict[str, Any]] = Field(default_factory=list)
    parent_id: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_caldav_todo(cls, todo: caldav.Todo) -> "NextCloudTask":
        """Create a NextCloudTask from a CalDAV Todo."""
        # Extract the iCalendar component
        ical = todo.icalendar_component

        # Extract basic properties
        uid = str(ical.get("uid", ""))
        summary = str(ical.get("summary", ""))
        description = str(ical.get("description", ""))

        # Extract status
        status = "pending"
        if ical.get("status") == "COMPLETED":
            status = "done"
        elif ical.get("status") == "IN-PROCESS":
            status = "in_progress"
        elif ical.get("completed"):
            status = "done"

        # Extract due date
        due_date = None
        if ical.get("due"):
            due = ical.get("due").dt
            if isinstance(due, datetime):
                due_date = due.isoformat()
            elif isinstance(due, date):
                due_date = datetime.combine(due, datetime.min.time()).isoformat()

        # Extract created and updated timestamps
        created_at = None
        if ical.get("created"):
            created = ical.get("created").dt
            if isinstance(created, datetime):
                created_at = created.isoformat()

        updated_at = None
        if ical.get("last-modified"):
            updated = ical.get("last-modified").dt
            if isinstance(updated, datetime):
                updated_at = updated.isoformat()

        # Extract priority
        priority_map = {1: "high", 5: "medium", 9: "low"}
        priority = None
        if ical.get("priority"):
            priority_val = int(ical.get("priority"))
            priority = priority_map.get(priority_val, "medium")

        # Extract categories
        categories = []
        if ical.get("categories"):
            categories = [str(cat) for cat in ical.get("categories").cats]

        # Get etag and fileid
        etag = getattr(todo, "etag", None)
        fileid = uid

        # Check for parent task relationship
        parent_id = None
        # First check our custom property
        if ical.get("X-TASKINATOR-PARENT-ID"):
            parent_id = str(ical.get("X-TASKINATOR-PARENT-ID"))
        # Then check the standard related-to field
        elif ical.get("related-to"):
            parent_id = str(ical.get("related-to"))

        # Extract subtasks (if any are defined as RELATED-TO with this task as parent)
        # Note: This would require additional API calls to get the actual subtasks
        # We'll handle this separately when needed
        subtasks = []

        # Get calendar_id as string
        calendar = getattr(todo, "parent", None)
        calendar_id = str(calendar.id) if calendar and hasattr(calendar, "id") else None

        # Extract extra metadata from X-TASKINATOR properties
        extra = {}
        for name, value in ical.items():
            if name.startswith("X-TASKINATOR-") and name != "X-TASKINATOR-PARENT-ID":
                key = name[len("X-TASKINATOR-") :].lower()
                try:
                    # Try to parse as JSON if possible
                    extra[key] = json.loads(str(value))
                except json.JSONDecodeError:
                    # Otherwise store as string
                    extra[key] = str(value)

        return cls(
            id=uid,
            title=summary,
            description=description,
            status=status,
            due_date=due_date,
            created_at=created_at,
            updated_at=updated_at,
            priority=priority,
            calendar_id=calendar_id,
            categories=categories,
            etag=etag,
            fileid=fileid,
            subtasks=subtasks,
            parent_id=parent_id,
            extra=extra,
        )

    def to_caldav_todo(self) -> str:
        """Convert the task to a CalDAV Todo object.

        Returns:
            str: iCalendar string representation of the task
        """
        # Create a new iCalendar
        cal = Calendar()
        cal.add("prodid", "-//Taskinator//EN")
        cal.add("version", "2.0")

        # Create a new VTODO component
        todo = Todo()

        # Add basic properties
        todo.add("uid", self.id)
        todo.add("summary", self.title)

        if self.description:
            todo.add("description", self.description)

        # Add status
        status_map = {
            "pending": "NEEDS-ACTION",
            "in_progress": "IN-PROCESS",
            "done": "COMPLETED",
        }
        todo.add("status", status_map.get(self.status, "NEEDS-ACTION"))

        # Add due date
        if self.due_date:
            try:
                due_date = datetime.fromisoformat(self.due_date)
                todo.add("due", due_date)
            except (ValueError, TypeError):
                pass

        # Add created timestamp
        if self.created_at:
            try:
                created_at = datetime.fromisoformat(self.created_at)
                todo.add("created", created_at)
            except (ValueError, TypeError):
                todo.add("created", datetime.now())
        else:
            todo.add("created", datetime.now())

        # Add updated timestamp
        if self.updated_at:
            try:
                updated_at = datetime.fromisoformat(self.updated_at)
                todo.add("last-modified", updated_at)
            except (ValueError, TypeError):
                todo.add("last-modified", datetime.now())
        else:
            todo.add("last-modified", datetime.now())

        # Add priority
        if self.priority:
            priority_map = {"high": 1, "medium": 5, "low": 9}
            todo.add("priority", priority_map.get(self.priority, 5))

        # Add categories
        if self.categories:
            todo.add("categories", self.categories)

        # Add parent task relationship if needed
        # Nextcloud Tasks uses the RELATED-TO field with a RELTYPE parameter
        if self.parent_id:
            # Add as a raw string in the format required by Nextcloud
            todo.add("related-to", self.parent_id)
            # Add a custom X-property to indicate the relationship type
            todo.add("X-TASKINATOR-PARENT-ID", self.parent_id)

        # Add extra metadata as X-TASKINATOR properties
        if self.extra:
            for key, value in self.extra.items():
                if isinstance(value, (dict, list)):
                    # Convert complex objects to JSON strings
                    todo.add(f"X-TASKINATOR-{key.upper()}", json.dumps(value))
                else:
                    # Store simple values directly
                    todo.add(f"X-TASKINATOR-{key.upper()}", str(value))

        # Add the todo to the calendar
        cal.add_component(todo)

        # Return the iCalendar as a string
        return cal.to_ical().decode("utf-8")

    @classmethod
    def from_json(cls, json_str: str) -> List["NextCloudTask"]:
        """Deserialize a JSON string containing a list of tasks."""
        data = json.loads(json_str)
        return [cls(**task_data) for task_data in data]


class NextCloudClient:
    """Client for interacting with NextCloud Tasks API."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str = None,
        app_token: str = None,
        calendar_id: str = "personal",
    ):
        """Initialize the NextCloud client.

        Args:
            base_url: Base URL of the NextCloud instance
            username: Username for authentication
            password: Password for authentication
            app_token: App token for authentication
            calendar_id: Calendar ID to use for tasks
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.app_token = app_token
        self.calendar_id = calendar_id

        # Ensure base URL ends with a slash
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        # Create CalDAV client
        self._client = None
        self._calendar = None

    @with_retry(max_retries=3, base_delay=1.0, max_delay=10.0)
    def _get_client(self) -> caldav.DAVClient:
        """Get the CalDAV client.

        Returns:
            caldav.DAVClient: CalDAV client
            
        Note:
            This method is decorated with @with_retry to handle rate limiting.
        """
        if self._client is None:
            # Determine authentication method
            if self.app_token:
                auth = (self.username, self.app_token)
            else:
                auth = (self.username, self.password)

            # Create CalDAV client
            self._client = caldav.DAVClient(
                url=f"{self.base_url}remote.php/dav", username=auth[0], password=auth[1]
            )

        return self._client

    @with_retry(max_retries=3, base_delay=1.0, max_delay=10.0)
    def _get_calendar(self, calendar_id: str = None) -> caldav.Calendar:
        """Get the CalDAV calendar.

        Args:
            calendar_id: Calendar ID to use

        Returns:
            caldav.Calendar: CalDAV calendar
            
        Note:
            This method is decorated with @with_retry to handle rate limiting.
        """
        if self._calendar is None or (calendar_id and calendar_id != self.calendar_id):
            # Use provided calendar_id or default
            cal_id = calendar_id or self.calendar_id

            # Get principal
            client = self._get_client()
            principal = client.principal()

            # Get calendars
            calendars = principal.calendars()

            # Find the requested calendar
            for calendar in calendars:
                if cal_id == "personal" and "tasks" in calendar.name.lower():
                    self._calendar = calendar
                    break
                elif (
                    str(calendar.id) == cal_id
                    or calendar.name.lower() == cal_id.lower()
                ):
                    self._calendar = calendar
                    break

            # If calendar not found, use the first one
            if self._calendar is None and calendars:
                self._calendar = calendars[0]
                log.warning(f"Calendar {cal_id} not found, using {self._calendar.name}")

            # If still no calendar, raise an error
            if self._calendar is None:
                raise ValueError(f"No calendars found for user {self.username}")

        return self._calendar

    async def check_connection(self) -> bool:
        """Check if we can connect to the Nextcloud server.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Try to get the principal with retry handling
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                lambda: self._get_client().principal()
            )
            return True
        except (RateLimitExceeded, Exception) as e:
            log.error(f"Failed to connect to Nextcloud: {str(e)}")
            return False

    async def list_calendars(self) -> List[Dict[str, str]]:
        """List all available calendars.

        Returns:
            List[Dict[str, str]]: List of calendars with id and name
        """
        try:
            # Get principal
            client = self._get_client()
            principal = client.principal()

            # Get calendars
            calendars = principal.calendars()

            # Format calendar information
            result = []
            for calendar in calendars:
                result.append({
                    "id": str(calendar.id),
                    "name": calendar.name,
                    "url": calendar.url,
                })

            return result
        except Exception as e:
            log.error(f"Failed to list calendars: {str(e)}")
            return []

    async def verify_calendar(self, calendar_id: str = None) -> Dict[str, Any]:
        """Verify that the specified calendar exists and is accessible.

        Args:
            calendar_id: Calendar ID to verify

        Returns:
            Dict[str, Any]: Dictionary with verification results
        """
        try:
            # Use provided calendar_id or default
            cal_id = calendar_id or self.calendar_id

            # Get all calendars
            calendars = await self.list_calendars()

            # Check if the calendar exists
            calendar_exists = False
            found_calendar = None

            for calendar in calendars:
                if cal_id == "personal" and "tasks" in calendar["name"].lower():
                    calendar_exists = True
                    found_calendar = calendar
                    break
                elif (
                    calendar["id"] == cal_id
                    or calendar["name"].lower() == cal_id.lower()
                ):
                    calendar_exists = True
                    found_calendar = calendar
                    break

            # If calendar not found but others exist, suggest the first one
            suggested_calendar = None
            if not calendar_exists and calendars:
                suggested_calendar = calendars[0]

            return {
                "exists": calendar_exists,
                "calendar": found_calendar,
                "suggested_calendar": suggested_calendar,
                "all_calendars": calendars
            }
        except Exception as e:
            log.error(f"Failed to verify calendar: {str(e)}")
            return {
                "exists": False,
                "error": str(e),
                "all_calendars": []
            }

    async def create_task(self, task_data: Dict[str, Any]) -> NextCloudTask:
        """Create a task in NextCloud using CalDAV.

        Args:
            task_data: Task data

        Returns:
            NextCloudTask: Created task
        """
        try:
            # Create a NextCloudTask object
            task = NextCloudTask(
                id=task_data.get("id") or str(uuid.uuid4()),
                title=task_data["title"],
                description=task_data.get("description"),
                status=task_data.get("status", "pending"),
                due_date=task_data.get("due_date"),
                priority=task_data.get("priority", "medium"),
                categories=task_data.get("categories", []),
                parent_id=task_data.get("parent_id"),
            )

            # Convert to iCalendar format
            ical_data = task.to_caldav_todo()

            # This needs to be run in a thread since caldav is synchronous
            loop = asyncio.get_event_loop()
            todo = await loop.run_in_executor(
                None, lambda: self._create_task_sync(ical_data)
            )

            # Return the created task
            return NextCloudTask.from_caldav_todo(todo)

        except Exception as e:
            log.error(f"Failed to create task: {e}")
            raise

    @with_retry(max_retries=5, base_delay=1.0, max_delay=15.0)
    def _create_task_sync(self, ical_data: str) -> caldav.Todo:
        """Synchronous implementation of create_task.

        Args:
            ical_data: iCalendar data

        Returns:
            caldav.Todo: Created todo
            
        Note:
            This method is decorated with @with_retry to handle rate limiting.
        """
        # Get the calendar
        calendar = self._get_calendar()

        # Create the task
        todo = calendar.save_todo(ical_data)

        return todo

    async def update_task(
        self, task_id: str, task_data: Dict[str, Any]
    ) -> NextCloudTask:
        """Update a task in NextCloud using CalDAV.

        Args:
            task_id: ID of the task to update
            task_data: Updated task data

        Returns:
            NextCloudTask: Updated task
        """
        try:
            # Get the task
            current_task = await self.get_task(task_id)

            # Update the task
            updated_task = NextCloudTask(
                id=task_id,
                title=task_data.get("title", current_task.title),
                description=task_data.get("description", current_task.description),
                status=task_data.get("status", current_task.status),
                due_date=task_data.get("due_date", current_task.due_date),
                priority=task_data.get("priority", current_task.priority),
                categories=task_data.get("categories", current_task.categories),
                parent_id=task_data.get("parent_id", current_task.parent_id),
                calendar_id=current_task.calendar_id,
                etag=current_task.etag,
                fileid=current_task.fileid,
            )

            # Convert to iCalendar format
            ical_data = updated_task.to_caldav_todo()

            # This needs to be run in a thread since caldav is synchronous
            loop = asyncio.get_event_loop()
            todo = await loop.run_in_executor(
                None, lambda: self._update_task_sync(task_id, ical_data)
            )

            # Return the updated task
            return NextCloudTask.from_caldav_todo(todo)

        except Exception as e:
            log.error(f"Failed to update task: {e}")
            raise

    @with_retry(max_retries=5, base_delay=1.0, max_delay=15.0)
    def _update_task_sync(self, task_id: str, ical_data: str) -> caldav.Todo:
        """Synchronous implementation of update_task.

        Args:
            task_id: ID of the task to update
            ical_data: iCalendar data

        Returns:
            caldav.Todo: Updated todo
            
        Note:
            This method is decorated with @with_retry to handle rate limiting.
        """
        # Get the calendar
        calendar = self._get_calendar()

        # Find the task by ID
        todos = calendar.todos()
        todo = None
        for t in todos:
            uid = str(t.icalendar_component.get("uid", ""))
            if uid == task_id:
                todo = t
                break

        if not todo:
            raise ValueError(f"Task with ID {task_id} not found")

        # Update the task
        todo.data = ical_data
        todo.save()

        return todo

    async def delete_task(self, task_id: str) -> None:
        """Delete a task in NextCloud using CalDAV.

        Args:
            task_id: ID of the task to delete
        """
        try:
            # This needs to be run in a thread since caldav is synchronous
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self._delete_task_sync(task_id))

        except Exception as e:
            log.error(f"Failed to delete task: {e}")
            raise

    @with_retry(max_retries=5, base_delay=1.0, max_delay=15.0)
    def _delete_task_sync(self, task_id: str) -> None:
        """Synchronous implementation of delete_task.

        Args:
            task_id: ID of the task to delete
            
        Note:
            This method is decorated with @with_retry to handle rate limiting.
        """
        # Get the calendar
        calendar = self._get_calendar()

        # Find the task by ID
        todos = calendar.todos()
        todo = None
        for t in todos:
            uid = str(t.icalendar_component.get("uid", ""))
            if uid == task_id:
                todo = t
                break

        if not todo:
            raise ValueError(f"Task with ID {task_id} not found")

        # Delete the task
        todo.delete()

    async def get_tasks(self, calendar_id: str = None) -> List[NextCloudTask]:
        """Get tasks from the NextCloud API.

        Args:
            calendar_id: Optional calendar ID to use

        Returns:
            List[NextCloudTask]: List of tasks
        """
        # This needs to be run in a thread since caldav is synchronous
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_tasks_sync, calendar_id)

    @with_retry(max_retries=5, base_delay=1.0, max_delay=15.0)
    def _get_tasks_sync(self, calendar_id: str = None) -> List[NextCloudTask]:
        """Synchronous implementation of get_tasks.

        Args:
            calendar_id: Optional calendar ID to use

        Returns:
            List[NextCloudTask]: List of tasks
            
        Note:
            This method is decorated with @with_retry to handle rate limiting.
        """
        try:
            calendar = self._get_calendar(calendar_id)
            tasks = []

            # Get all todos including completed ones
            # The todos() method should return all todos, but we need to set include_completed=True
            all_todos = calendar.todos(include_completed=True)
            
            # Debug: Print iCalendar data for each todo to understand how completed tasks are represented
            for todo in all_todos:
                ical = todo.icalendar_component
                # Print all properties of the iCalendar component for debugging
                log.info(f"Todo: {ical.get('summary')}")
                log.info(f"  - All properties: {list(ical.keys())}")
                log.info(f"  - percent-complete: {ical.get('percent-complete')}")
                log.info(f"  - status: {ical.get('status')}")
                log.info(f"  - completed: {ical.get('completed')}")
                
                task = NextCloudTask.from_caldav_todo(todo)
                tasks.append(task)

            return tasks

        except Exception as e:
            log.error(f"Failed to get tasks: {e}")
            # Check if this might be a rate limit error
            if "429" in str(e) or "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                raise RateLimitExceeded(f"Rate limit exceeded when getting tasks: {e}") from e
            raise

    async def get_task(self, task_id: str) -> NextCloudTask:
        """Get a specific task from NextCloud using CalDAV.

        Args:
            task_id: ID of the task to get

        Returns:
            NextCloudTask: Task object

        Raises:
            ValueError: If the task is not found
        """
        try:
            # This needs to be run in a thread since caldav is synchronous
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._get_task_sync, task_id)
        except Exception as e:
            log.error(f"Failed to get task {task_id}: {e}")
            raise

    @with_retry(max_retries=5, base_delay=1.0, max_delay=15.0)
    def _get_task_sync(self, task_id: str) -> NextCloudTask:
        """Synchronous implementation of get_task.

        Args:
            task_id: ID of the task to get

        Returns:
            NextCloudTask: Task object

        Raises:
            ValueError: If the task is not found
            
        Note:
            This method is decorated with @with_retry to handle rate limiting.
        """
        # Get the calendar
        calendar = self._get_calendar()

        # Find the task by ID
        todos = calendar.todos()
        for todo in todos:
            uid = str(todo.icalendar_component.get("uid", ""))
            if uid == task_id:
                return NextCloudTask.from_caldav_todo(todo)

        # If we get here, the task was not found
        raise ValueError(f"Task with ID {task_id} not found")

    @classmethod
    def from_env(cls) -> "NextCloudClient":
        """Create a NextCloudClient from environment variables.

        Returns:
            NextCloudClient: Client instance
        """
        base_url = os.environ.get("NEXTCLOUD_HOST")
        username = os.environ.get("NEXTCLOUD_USERNAME")
        password = os.environ.get("NEXTCLOUD_PASSWORD")
        app_token = os.environ.get("NEXTCLOUD_APP_TOKEN")
        calendar_id = os.environ.get("NEXTCLOUD_CALENDAR_ID", "personal")

        if not base_url or not username or (not password and not app_token):
            raise ValueError(
                "Missing required environment variables for NextCloud client"
            )

        return cls(
            base_url=base_url,
            username=username,
            password=password,
            app_token=app_token,
            calendar_id=calendar_id,
        )
