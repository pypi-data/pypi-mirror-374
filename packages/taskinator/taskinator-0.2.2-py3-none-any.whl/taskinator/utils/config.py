"""
Configuration utilities for Taskinator.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import dotenv
import httpx
from rich.console import Console

console = Console()

# Global flag to track if the AI credentials warning has been shown
_ai_credentials_warning_shown = False

# Default configuration values
DEFAULT_CONFIG = {
    "tasks_dir": "tasks",
    "tasks_file": "tasks.json",
    "task_complexity_report_file": "task-complexity-report.json",
    "DEFAULT_SUBTASKS": 3,
    "DEFAULT_COMPLEXITY_THRESHOLD": 5,
    "PROJECT_NAME": "Taskinator",
    "MODEL": "claude-3-7-sonnet",
    "MAX_TOKENS": 4000,
    "TEMPERATURE": 0.7,
    "PERPLEXITY_MODEL": "sonar-pro",
    "DEBUG": False,
    "LOG_LEVEL": "info",
    "DEFAULT_PRIORITY": "medium",
    "PRD_PATH": None,
}


def get_project_path() -> str:
    """
    Get the project path from the environment or use the current working directory.

    Returns:
        str: The project path
    """
    return os.environ.get("TASKINATOR_PROJECT_PATH", os.getcwd())


def get_tasks_dir() -> str:
    """
    Get the tasks directory path.

    Returns:
        str: The tasks directory path
    """
    project_path = get_project_path()
    tasks_dir = os.path.join(project_path, DEFAULT_CONFIG["tasks_dir"])
    os.makedirs(tasks_dir, exist_ok=True)
    return tasks_dir


def get_tasks_path() -> str:
    """
    Get the tasks.json file path.

    Returns:
        str: The tasks.json file path
    """
    tasks_dir = get_tasks_dir()
    return os.path.join(tasks_dir, DEFAULT_CONFIG["tasks_file"])


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables and defaults.

    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    # Load environment variables from .env file in the current working directory
    dotenv_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(dotenv_path):
        dotenv.load_dotenv(dotenv_path=dotenv_path, override=True)
    else:
        # Fall back to default dotenv behavior (looking in parent directories)
        dotenv.load_dotenv()

    # Start with default configuration
    config = DEFAULT_CONFIG.copy()

    # Add project path
    config["project_path"] = get_project_path()
    config["tasks_dir_path"] = get_tasks_dir()
    config["tasks_file_path"] = get_tasks_path()
    
    # Set project name to current directory name if not overridden
    if config["PROJECT_NAME"] == "Taskinator" and "PROJECT_NAME" not in os.environ:
        config["PROJECT_NAME"] = os.path.basename(os.getcwd())

    # Override with environment variables
    for key in config.keys():
        if key in os.environ:
            # Convert boolean strings to actual booleans
            if key == "DEBUG":
                config[key] = os.environ[key].lower() in ("true", "1", "yes", "y")
            # Convert numeric values
            elif isinstance(config[key], int):
                try:
                    config[key] = int(os.environ[key])
                except ValueError:
                    console.print(
                        f"[WARNING] Invalid value for {key}: {os.environ[key]}. "
                        f"Using default: {config[key]}",
                        style="bold yellow",
                    )
            # Convert temperature to float
            elif key == "TEMPERATURE":
                try:
                    config[key] = float(os.environ[key])
                except ValueError:
                    console.print(
                        f"[WARNING] Invalid value for {key}: {os.environ[key]}. "
                        f"Using default: {config[key]}",
                        style="bold yellow",
                    )
            else:
                config[key] = os.environ[key]

    # AI credentials will be checked by LiteLLM when needed
    # No need for upfront warnings since LiteLLM handles all providers

    return config


def get_config() -> Dict[str, Any]:
    """
    Get the configuration.

    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    return load_config()


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a configuration value by key.

    Args:
        key (str): Configuration key
        default (Any, optional): Default value if key is not found. Defaults to None.

    Returns:
        Any: Configuration value
    """
    config = get_config()
    return config.get(key, default)


def check_ai_available() -> bool:
    """
    Check if AI functionality is available by testing LiteLLM.
    We need to check if the required AI dependencies are installed and
    that we have API keys configured for the selected model.
    
    Returns:
        bool: True if AI is available, False otherwise
    """
    # Always enable debug output for credential errors
    show_error_info = True
    debug = os.environ.get("DEBUG", "false").lower() in ["true", "1", "yes", "y"]
    
    # Force reload .env file to ensure we have the latest environment variables
    # This is important for commands that are run directly without going through 
    # the main config loading process
    # Explicitly look for .env in the current working directory
    dotenv_path = os.path.join(os.getcwd(), '.env')
    if os.path.exists(dotenv_path):
        if debug:
            console.print(f"[DEBUG] Loading .env from {dotenv_path}")
        dotenv.load_dotenv(dotenv_path=dotenv_path, override=True)
    else:
        if debug:
            console.print(f"[DEBUG] No .env file found at {dotenv_path}")
    
    # First check if litellm is available
    try:
        import litellm
        if debug:
            console.print("[DEBUG] LiteLLM module is available")
    except ImportError:
        if show_error_info:
            console.print("[ERROR] LiteLLM module is not installed. Run 'pip install litellm' to enable AI functionality.", style="bold red")
        return False
    
    # Check for model from different sources, with priority:
    # 1. Environment variables
    # 2. .env file (loaded through dotenv.load_dotenv() earlier)
    # 3. Default value
    model = os.environ.get("MODEL", "anthropic/claude-3-7-sonnet-20250219")
    
    # Check for alternative model environment variables
    if not model or model == "anthropic/claude-3-7-sonnet-20250219":
        claude_model = os.environ.get("CLAUDE_MODEL")
        if claude_model:
            model = claude_model
            if debug:
                console.print(f"[DEBUG] Using model from CLAUDE_MODEL: {model}")
    
    if debug:
        console.print(f"[DEBUG] Selected model: {model}")
    
    # Common credential checks for major providers
    if model.startswith("bedrock/") or "bedrock" in model.lower():
        # AWS Bedrock
        has_aws_creds = (
            os.environ.get("AWS_ACCESS_KEY_ID") is not None or
            os.environ.get("AWS_PROFILE") is not None
        )
        if debug or (show_error_info and not has_aws_creds):
            console.print(f"[INFO] AWS Bedrock model detected: {model}")
            console.print(f"[INFO]   AWS_ACCESS_KEY_ID: {'✓ Set' if os.environ.get('AWS_ACCESS_KEY_ID') else '✗ Not set'}")
            console.print(f"[INFO]   AWS_PROFILE: {'✓ Set' if os.environ.get('AWS_PROFILE') else '✗ Not set'}")
            if not has_aws_creds:
                console.print("[ERROR] Missing AWS credentials. Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or AWS_PROFILE environment variables.", style="bold red")
        return has_aws_creds
        
    elif model.startswith("anthropic/") or "claude" in model.lower():
        # Anthropic direct
        has_anthropic_key = os.environ.get("ANTHROPIC_API_KEY") is not None
        if debug or (show_error_info and not has_anthropic_key):
            console.print(f"[INFO] Anthropic/Claude model detected: {model}")
            console.print(f"[INFO]   ANTHROPIC_API_KEY: {'✓ Set' if has_anthropic_key else '✗ Not set'}")
            if not has_anthropic_key:
                console.print("[ERROR] Missing Anthropic API key. Set ANTHROPIC_API_KEY environment variable.", style="bold red")
        return has_anthropic_key
        
    elif model.startswith("openai/") or model.startswith("gpt-"):
        # OpenAI
        has_openai_key = os.environ.get("OPENAI_API_KEY") is not None
        if debug or (show_error_info and not has_openai_key):
            console.print(f"[INFO] OpenAI model detected: {model}")
            console.print(f"[INFO]   OPENAI_API_KEY: {'✓ Set' if has_openai_key else '✗ Not set'}")
            if not has_openai_key:
                console.print("[ERROR] Missing OpenAI API key. Set OPENAI_API_KEY environment variable.", style="bold red")
        return has_openai_key
        
    elif model.startswith("azure/"):
        # Azure OpenAI
        has_azure_key = (
            os.environ.get("AZURE_API_KEY") is not None or
            os.environ.get("AZURE_OPENAI_API_KEY") is not None
        )
        if debug or (show_error_info and not has_azure_key):
            console.print(f"[INFO] Azure OpenAI model detected: {model}")
            console.print(f"[INFO]   AZURE_API_KEY: {'✓ Set' if os.environ.get('AZURE_API_KEY') else '✗ Not set'}")
            console.print(f"[INFO]   AZURE_OPENAI_API_KEY: {'✓ Set' if os.environ.get('AZURE_OPENAI_API_KEY') else '✗ Not set'}")
            if not has_azure_key:
                console.print("[ERROR] Missing Azure API key. Set AZURE_API_KEY or AZURE_OPENAI_API_KEY environment variable.", style="bold red")
        return has_azure_key
        
    elif model.startswith("vertex_ai/") or "vertex" in model.lower():
        # Google Vertex AI
        has_google_creds = (
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") is not None or
            os.environ.get("VERTEX_PROJECT") is not None
        )
        if debug or (show_error_info and not has_google_creds):
            console.print(f"[INFO] Google Vertex AI model detected: {model}")
            console.print(f"[INFO]   GOOGLE_APPLICATION_CREDENTIALS: {'✓ Set' if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') else '✗ Not set'}")
            console.print(f"[INFO]   VERTEX_PROJECT: {'✓ Set' if os.environ.get('VERTEX_PROJECT') else '✗ Not set'}")
            if not has_google_creds:
                console.print("[ERROR] Missing Google credentials. Set GOOGLE_APPLICATION_CREDENTIALS or VERTEX_PROJECT environment variable.", style="bold red")
        return has_google_creds
        
    elif model.startswith("cohere/"):
        # Cohere
        has_cohere_key = os.environ.get("COHERE_API_KEY") is not None
        if debug or (show_error_info and not has_cohere_key):
            console.print(f"[INFO] Cohere model detected: {model}")
            console.print(f"[INFO]   COHERE_API_KEY: {'✓ Set' if has_cohere_key else '✗ Not set'}")
            if not has_cohere_key:
                console.print("[ERROR] Missing Cohere API key. Set COHERE_API_KEY environment variable.", style="bold red")
        return has_cohere_key
        
    else:
        # For other models, we don't know what credentials are required,
        # provide information but assume they're properly configured if litellm is available
        if debug:
            console.print(f"[INFO] Using model: {model}")
            console.print(f"[INFO] This appears to be a custom or less common model type")
            console.print(f"[INFO] Taskinator will attempt to use LiteLLM's auto-detection for credentials")
            
        # Suggest common environment variables that might be needed
        if show_error_info:
            console.print(f"""
[INFO] Configuration help for model '{model}':
- For AWS models: Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
- For Anthropic: Set ANTHROPIC_API_KEY 
- For OpenAI: Set OPENAI_API_KEY
- For Azure: Set AZURE_API_KEY or AZURE_OPENAI_API_KEY
- For Google: Set GOOGLE_APPLICATION_CREDENTIALS or VERTEX_PROJECT
- For Cohere: Set COHERE_API_KEY
- For other providers, check the LiteLLM documentation
            
To configure models, you can:
1. Set environment variables directly
2. Add them to your .env file
3. For AWS/Google, use profile configurations
""", style="blue")
        return True


def save_config_value(key: str, value: Any) -> None:
    """
    Save a configuration value to environment (in-memory for current session).
    
    Args:
        key (str): Configuration key
        value (Any): Configuration value
    """
    os.environ[key] = str(value)


def show_ai_credentials_info():
    """Show information about AI credentials for LiteLLM."""
    global _ai_credentials_warning_shown

    if not _ai_credentials_warning_shown:
        console.print(
            "[INFO] AI features use LiteLLM. Ensure proper credentials are set for your chosen model.",
            style="blue",
        )
        _ai_credentials_warning_shown = True
