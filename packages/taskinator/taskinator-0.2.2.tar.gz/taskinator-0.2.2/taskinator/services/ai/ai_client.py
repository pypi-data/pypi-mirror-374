"""
Generic AI client for Taskinator using LiteLLM.
Supports any model that LiteLLM supports including Anthropic, OpenAI, Bedrock, Azure, etc.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from rich.console import Console

from taskinator.utils.config import get_config

console = Console()
config = get_config()

# Default model configuration
DEFAULT_MODEL_CONFIG = {
    "model": "anthropic/claude-3-7-sonnet-20250219",
    "max_tokens": 64000,
    "temperature": 0.2,
}


def get_ai_client():
    """
    Get LiteLLM client for AI operations.

    Returns:
        litellm module: LiteLLM module (required dependency)
    """
    import litellm
    return litellm


def is_ai_available() -> bool:
    """
    Check if AI functionality is available.
    
    Returns:
        bool: True if AI is available, False otherwise
    """
    # Check if litellm is available
    try:
        import litellm
    except ImportError:
        return False
    
    # For LiteLLM, we'll let it handle the credential validation
    # This allows support for any model that LiteLLM supports
    model = os.environ.get("MODEL", DEFAULT_MODEL_CONFIG["model"])
    
    # Common credential checks for major providers
    if model.startswith("bedrock/"):
        # AWS Bedrock
        return (
            os.environ.get("AWS_ACCESS_KEY_ID") is not None or
            os.environ.get("AWS_PROFILE") is not None
        )
    elif model.startswith("anthropic/") or "claude" in model.lower():
        # Anthropic direct
        return os.environ.get("ANTHROPIC_API_KEY") is not None
    elif model.startswith("openai/") or model.startswith("gpt-"):
        # OpenAI
        return os.environ.get("OPENAI_API_KEY") is not None
    elif model.startswith("azure/"):
        # Azure OpenAI
        return (
            os.environ.get("AZURE_API_KEY") is not None or
            os.environ.get("AZURE_OPENAI_API_KEY") is not None
        )
    elif model.startswith("vertex_ai/"):
        # Google Vertex AI
        return (
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") is not None or
            os.environ.get("VERTEX_PROJECT") is not None
        )
    elif model.startswith("cohere/"):
        # Cohere
        return os.environ.get("COHERE_API_KEY") is not None
    else:
        # For other models, assume they're configured properly
        # LiteLLM will handle the actual validation
        return True


def get_model_config() -> Dict[str, Any]:
    """
    Get model configuration from environment variables or fall back to defaults.

    Returns:
        Dict[str, Any]: Model configuration with model, max_tokens, and temperature
    """
    return {
        "model": os.environ.get("MODEL", DEFAULT_MODEL_CONFIG["model"]),
        "max_tokens": int(
            os.environ.get("MAX_TOKENS", DEFAULT_MODEL_CONFIG["max_tokens"])
        ),
        "temperature": float(
            os.environ.get("TEMPERATURE", DEFAULT_MODEL_CONFIG["temperature"])
        ),
    }


async def generate_tasks_from_prd(
    prd_content: str, num_tasks: int
) -> List[Dict[str, Any]]:
    """
    Generate tasks from a PRD using any LiteLLM-supported model.

    Args:
        prd_content (str): PRD content
        num_tasks (int): Number of tasks to generate

    Returns:
        List[Dict[str, Any]]: Generated tasks
    """
    try:
        # Check if LiteLLM is available
        if not get_ai_client():
            return []

        # Check if AI is available with proper credentials
        if not is_ai_available():
            return []

        # Import litellm here to avoid import errors if it's not installed
        import litellm
        from litellm import completion

        model_config = get_model_config()

        console.print("[INFO] Calling AI model to generate tasks from PRD...")

        # Create system and user prompts
        system_prompt = f"""You are a task breakdown assistant that helps software engineers break down project requirements into clear, actionable tasks.

Given a Product Requirements Document (PRD), your job is to:
1. Analyze the requirements thoroughly
2. Break them down into {num_tasks} well-defined tasks
3. Provide each task with a clear title, description, and implementation details.
4. Identify dependencies between tasks
5. Assign appropriate priorities (high, medium, low)
6. Return the tasks in JSON format

Focus on creating tasks that:
- Are clear and actionable
- Have appropriate granularity (not too broad or too narrow)
- Cover all key requirements in the PRD
- Have logical dependencies and sequencing
- Include APPROPRIATE implementation guidance in the "details" field. Scale level of detail to match the complexity of the task.
- Include APPROPRIATE test criteria in the "test_strategy" field. Scale level of detail to match the complexity of the task.
- Be proportionate to the complexity of the task. Don't overcomplicate or implement enterprise-level features unless requested in the PRD. 
- Testing and reliability are important but don't overcomplicate. Test the fundamentals.

Each task should be self-contained with enough detail that a developer could implement it without referring back to the PRD.

The tasks should be returned as a JSON array with each task having the following structure:
{{
  "id": "1", // Sequential numeric ID
  "title": "Short descriptive title",
  "description": "Brief summary of what the task involves",
  "status": "pending", // Always set to "pending"
  "priority": "high|medium|low", // Based on importance and urgency
  "dependencies": [], // Array of task IDs this task depends on
  "details": "Implementation notes including technical approach and considerations. Scale level of detail to match the complexity of the task and include specific implementation guidance. Do not overcomplicate.",
  "test_strategy": "How to verify this task is complete and working correctly. Scale level of detail to match the complexity of the task. Do not overcomplicate."
}}

Ensure your response contains ONLY valid JSON that can be parsed programmatically."""

        user_prompt = f"""Here is the Product Requirements Document (PRD) to break down into {num_tasks} tasks:

{prd_content}

Please analyze this PRD and generate exactly {num_tasks} tasks in the JSON format specified."""

        # Call AI model via LiteLLM
        try:
            console.print(f"[INFO] Sending request to {model_config['model']}...")

            response = completion(
                model=model_config["model"],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=model_config["max_tokens"],
                temperature=model_config["temperature"],
            )

            # Extract the response content
            response_text = response.choices[0].message.content

        except Exception as e:
            console.print(
                f"[ERROR] Error calling AI model: {str(e)}", style="bold red"
            )
            if "401" in str(e) or "authentication" in str(e).lower():
                console.print(
                    "[ERROR] Authentication error. Your credentials may be invalid.",
                    style="bold red",
                )
                console.print(
                    "[INFO] Please check your model configuration and credentials.",
                    style="bold yellow",
                )
            return []

        # Parse the JSON response
        try:
            # Try to find JSON in code blocks
            json_match = None
            if "```json" in response_text:
                json_parts = response_text.split("```json")
                if len(json_parts) > 1:
                    json_content = json_parts[1].split("```")[0].strip()
                    json_match = json_content
            elif "```" in response_text:
                json_parts = response_text.split("```")
                if len(json_parts) > 1:
                    json_content = json_parts[1].strip()
                    json_match = json_content

            # If no code blocks, try to find array directly
            if not json_match:
                start_idx = response_text.find("[")
                end_idx = response_text.rfind("]")
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_match = response_text[start_idx : end_idx + 1]

            # Parse the JSON
            if json_match:
                tasks = json.loads(json_match)
            else:
                # Last resort: try to parse the whole response
                tasks = json.loads(response_text)

            # Validate it's an array
            if not isinstance(tasks, list):
                raise ValueError("Parsed content is not a valid task array")

            return tasks
        except Exception as e:
            console.print(
                f"[ERROR] Failed to parse tasks from AI response: {str(e)}",
                style="bold red",
            )
            return []

    except Exception as e:
        console.print(
            f"[ERROR] Error generating tasks with AI model: {str(e)}", style="bold red"
        )
        return []
