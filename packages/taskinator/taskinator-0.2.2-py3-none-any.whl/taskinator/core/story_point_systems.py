"""
Story point systems for Taskinator.

This module defines different story point systems and scaling logic for task planning.
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple


class PointSystemType(str, Enum):
    """Enumeration of supported story point systems."""

    FIBONACCI = "fibonacci"  # 1, 2, 3, 5, 8, 13, 21, ...
    POWERS_OF_TWO = "powers_of_two"  # 1, 2, 4, 8, 16, 32, ...
    LINEAR = "linear"  # 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    TSHIRT = "tshirt"  # XS, S, M, L, XL, XXL
    MODIFIED_FIBONACCI = "modified_fibonacci"  # 0, 0.5, 1, 2, 3, 5, 8, 13, 20, 40, 100
    CUSTOM = "custom"  # User-defined scale


# Define standard point values for each system
POINT_SYSTEMS = {
    PointSystemType.FIBONACCI: [1, 2, 3, 5, 8, 13, 21, 34],
    PointSystemType.POWERS_OF_TWO: [1, 2, 4, 8, 16, 32],
    PointSystemType.LINEAR: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    PointSystemType.TSHIRT: ["XS", "S", "M", "L", "XL", "XXL"],
    PointSystemType.MODIFIED_FIBONACCI: [0, 0.5, 1, 2, 3, 5, 8, 13, 20, 40, 100],
}


# Numeric equivalents for T-shirt sizes or other non-numeric scales
TSHIRT_SIZE_VALUES = {
    "XS": 1,
    "S": 2,
    "M": 3,
    "L": 5,
    "XL": 8,
    "XXL": 13,
}


class StoryPointSystem:
    """
    Represents a story point estimation system.

    This class handles conversion and interpretation of story points
    across different estimation systems.
    """

    def __init__(
        self,
        system_type: Union[str, PointSystemType] = PointSystemType.FIBONACCI,
        custom_values: Optional[List[Union[int, float, str]]] = None,
    ):
        """
        Initialize a story point system.

        Args:
            system_type: The type of point system to use
            custom_values: Custom point values if using a custom system
        """
        if isinstance(system_type, str):
            try:
                self.system_type = PointSystemType(system_type.lower())
            except ValueError:
                self.system_type = PointSystemType.CUSTOM
                if not custom_values:
                    raise ValueError(f"Custom system type requires custom_values")
        else:
            self.system_type = system_type

        self.custom_values = custom_values

        # Set values based on system type
        if self.system_type == PointSystemType.CUSTOM:
            if not custom_values:
                raise ValueError("Custom point system requires custom_values")
            self.values = custom_values
        else:
            self.values = POINT_SYSTEMS[self.system_type]

    def get_numeric_value(self, point_value: Union[int, float, str]) -> float:
        """
        Convert any point value to its numeric equivalent.

        Args:
            point_value: The story point value to convert

        Returns:
            float: Numeric equivalent
        """
        if isinstance(point_value, (int, float)):
            return float(point_value)

        if isinstance(point_value, str):
            # Try T-shirt size conversion
            if point_value in TSHIRT_SIZE_VALUES:
                return float(TSHIRT_SIZE_VALUES[point_value])

            # Try numeric conversion
            try:
                return float(point_value)
            except ValueError:
                raise ValueError(f"Cannot convert '{point_value}' to numeric value")

        return 0.0

    def get_complexity_level(self, point_value: Union[int, float, str]) -> str:
        """
        Determine the complexity level based on story points.

        Args:
            point_value: The story point value

        Returns:
            str: Complexity level (trivial, simple, moderate, complex, very_complex)
        """
        numeric_value = self.get_numeric_value(point_value)

        # Scale complexity based on the system's range
        if self.system_type == PointSystemType.TSHIRT:
            if point_value == "XS":
                return "trivial"
            elif point_value == "S":
                return "simple"
            elif point_value == "M":
                return "moderate"
            elif point_value == "L":
                return "complex"
            elif point_value in ("XL", "XXL"):
                return "very_complex"
            else:
                return "unknown"

        # For numeric systems
        numeric_values = [
            self.get_numeric_value(v)
            for v in self.values
            if isinstance(v, (int, float, str))
        ]
        max_value = max(numeric_values) if numeric_values else 10

        # Scale based on percentage of max value
        percentage = (numeric_value / max_value) * 100

        if percentage <= 10:
            return "trivial"
        elif percentage <= 25:
            return "simple"
        elif percentage <= 50:
            return "moderate"
        elif percentage <= 75:
            return "complex"
        else:
            return "very_complex"

    def get_recommended_subtask_count(self, point_value: Union[int, float, str]) -> int:
        """
        Get recommended number of subtasks based on story points.

        Args:
            point_value: The story point value

        Returns:
            int: Recommended number of subtasks
        """
        complexity = self.get_complexity_level(point_value)

        # Map complexity to subtask count
        subtask_map = {
            "trivial": 0,  # No subtasks needed
            "simple": 2,  # 1-2 subtasks
            "moderate": 4,  # 3-5 subtasks
            "complex": 7,  # 5-8 subtasks
            "very_complex": 10,  # 8+ subtasks
        }

        return subtask_map.get(complexity, 5)  # Default to 5 if unknown

    def get_recommended_task_depth(self, point_value: Union[int, float, str]) -> int:
        """
        Get recommended task hierarchy depth based on story points.

        Args:
            point_value: The story point value

        Returns:
            int: Recommended depth for task hierarchy
        """
        complexity = self.get_complexity_level(point_value)

        # Map complexity to hierarchy depth
        depth_map = {
            "trivial": 1,  # Just the task itself
            "simple": 1,  # Task + subtasks
            "moderate": 2,  # Task + subtasks + sub-subtasks
            "complex": 2,  # Task + subtasks + sub-subtasks
            "very_complex": 3,  # Deep hierarchical breakdown
        }

        return depth_map.get(complexity, 2)  # Default to 2 if unknown

    def get_recommended_research_level(
        self, point_value: Union[int, float, str]
    ) -> str:
        """
        Get recommended research level based on story points.

        Args:
            point_value: The story point value

        Returns:
            str: Research level (none, minimal, moderate, extensive)
        """
        complexity = self.get_complexity_level(point_value)

        # Map complexity to research level
        research_map = {
            "trivial": "none",
            "simple": "minimal",
            "moderate": "moderate",
            "complex": "extensive",
            "very_complex": "extensive",
        }

        return research_map.get(
            complexity, "moderate"
        )  # Default to moderate if unknown

    def get_detail_level(self, point_value: Union[int, float, str]) -> str:
        """
        Get recommended detail level for task descriptions.

        Args:
            point_value: The story point value

        Returns:
            str: Detail level (minimal, moderate, detailed, comprehensive)
        """
        complexity = self.get_complexity_level(point_value)

        # Map complexity to detail level
        detail_map = {
            "trivial": "minimal",
            "simple": "moderate",
            "moderate": "detailed",
            "complex": "comprehensive",
            "very_complex": "comprehensive",
        }

        return detail_map.get(complexity, "detailed")  # Default to detailed if unknown


def get_story_point_system(
    system_type: str = "fibonacci",
    custom_values: Optional[List[Union[int, float, str]]] = None,
) -> StoryPointSystem:
    """
    Factory function to create a story point system.

    Args:
        system_type: The type of point system to use
        custom_values: Custom point values if using a custom system

    Returns:
        StoryPointSystem: Initialized story point system
    """
    return StoryPointSystem(system_type, custom_values)
