"""
Stack management command for discussing and defining technology stack.
"""

import json
import os
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from taskinator.core.file_storage import read_tasks
from taskinator.services.ai.ai_client import get_ai_client, get_model_config, is_ai_available
from taskinator.utils.config import get_config_value

console = Console()


def stack_command(
    action: str = "suggest",
    project_dir: str = None,
    interactive: bool = True,
    prd_file: str = None,
    use_research: bool = False
) -> None:
    """
    Technology stack management interface.

    Args:
        action: Action to perform (suggest, discuss, lock, show, compile)
        project_dir: Project directory (defaults to current directory)
        interactive: Whether to run in interactive mode
        prd_file: Optional PRD file to analyze for stack suggestions
    """
    if project_dir is None:
        project_dir = os.getcwd()

    stack_suggest_path = os.path.join(project_dir, "stack.suggest")
    stack_lock_path = os.path.join(project_dir, "stack.lock")
    tasks_path = os.path.join(project_dir, "tasks", "tasks.json")

    if action == "suggest":
        _handle_stack_suggest(project_dir, stack_suggest_path, tasks_path, prd_file, interactive)
    elif action == "recommend":
        _handle_stack_recommend(project_dir, stack_suggest_path, tasks_path, prd_file, interactive, use_research)
    elif action == "discuss":
        _handle_stack_discuss(project_dir, stack_suggest_path, interactive)
    elif action == "lock" or action == "compile":
        _handle_stack_compile(stack_suggest_path, stack_lock_path, interactive)
    elif action == "show":
        _show_stack_status(stack_suggest_path, stack_lock_path)
    else:
        console.print(f"[ERROR] Unknown action: {action}", style="bold red")
        _show_stack_help()


def _handle_stack_suggest(
    project_dir: str, 
    stack_suggest_path: str, 
    tasks_path: str, 
    prd_file: str = None,
    interactive: bool = True
) -> None:
    """Generate initial stack suggestions based on PRD and tasks."""
    
    # Check if AI is available
    if not is_ai_available():
        console.print(
            "[ERROR] AI functionality is not available. Please check your model configuration and credentials.",
            style="bold red",
        )
        return
    
    # Gather context
    context_parts = []
    
    # Read PRD if provided
    if prd_file and os.path.exists(prd_file):
        with open(prd_file, 'r') as f:
            prd_content = f.read()
            context_parts.append(f"PRD Content:\n{prd_content}")
    
    # Read existing tasks if available
    if os.path.exists(tasks_path):
        try:
            task_collection = read_tasks(tasks_path)
            tasks_summary = []
            for task in task_collection.tasks:
                tasks_summary.append(f"- {task.title}: {task.description}")
            if tasks_summary:
                context_parts.append(f"Existing Tasks:\n" + "\n".join(tasks_summary))
        except Exception as e:
            console.print(f"[WARNING] Could not read tasks: {str(e)}", style="yellow")
    
    # Read existing stack suggestions if available
    existing_suggestions = ""
    if os.path.exists(stack_suggest_path):
        with open(stack_suggest_path, 'r') as f:
            existing_suggestions = f.read()
        context_parts.append(f"Existing Stack Suggestions:\n{existing_suggestions}")
    
    if not context_parts:
        console.print("[ERROR] No context available. Please provide a PRD file or ensure tasks exist.", style="bold red")
        return
    
    console.print(Panel.fit(
        "🔍 [bold cyan]Technology Stack Analysis[/bold cyan]\n\n"
        "Analyzing project requirements to suggest appropriate technology stack...",
        border_style="cyan"
    ))
    
    # Generate stack suggestions using AI
    try:
        client = get_ai_client()
        model_config = get_model_config()
        
        system_prompt = """You are a technology stack consultant helping to select the best tools, frameworks, and libraries for a software project.

Your job is to analyze the project requirements and suggest appropriate technologies organized by category.

Provide your response in this exact format:

# Technology Stack Suggestions

## Core Technologies
- **Language**: [Primary programming language with version]
- **Framework**: [Main framework/library with version]
- **Database**: [Database system with version if applicable. Can be None]
- **Runtime/Platform**: [Runtime environment or platform]

## Development Tools
- **Build System**: [Build tool with version]
- **Package Manager**: [Package management tool]
- **Testing Framework**: [Testing library/framework]
- **Code Quality**: [Linting, formatting tools]

## Infrastructure & Deployment
- **Containerization**: [Docker, etc. Only if suitable for the task.]
- **Orchestration**: [Kubernetes, etc. Only if ideal for the task.]
- **CI/CD**: [Continuous integration tools]
- **Hosting/Cloud**: [Deployment platform. Only if suitable for the task.]

## Additional Libraries
- **HTTP Client**: [For API calls. Only if suitable for the task.]
- **Logging**: [Logging framework. Only if suitable for the task.]
- **Configuration**: [Config management. Only if suitable for the task.]
- **Authentication**: [Auth libraries if needed. Only if suitable for the task.]

## Reasoning
[Explain why these technologies were chosen based on the project requirements]

## Alternatives Considered
[Brief mention of other options that were considered but not selected]

Focus on mature, well-supported technologies that align with the project's requirements, scale, and complexity. Don't overcomplicate."""
        
        context = "\n\n".join(context_parts)
        user_prompt = f"Please analyze this project and suggest an appropriate technology stack:\n\n{context}"
        
        response = client.completion(
            model=model_config["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=model_config["max_tokens"],
            temperature=model_config["temperature"]
        )
        
        if response.choices:
            suggestions = response.choices[0].message.content
            
            # Write suggestions to file
            with open(stack_suggest_path, 'w') as f:
                f.write(suggestions)
            
            console.print(f"\n[bold green]✅ Stack suggestions written to {stack_suggest_path}[/bold green]")
            console.print("\n" + "="*60)
            console.print(Markdown(suggestions))
            console.print("="*60)
            
            if interactive:
                console.print(f"\n[bold yellow]Next steps:[/bold yellow]")
                console.print("• Review and modify stack.suggest file as needed")
                console.print("• Use 'taskinator stack discuss' for interactive refinement")
                console.print("• Use 'taskinator stack compile' to create stack.lock")
        
    except Exception as e:
        console.print(f"[ERROR] Failed to generate stack suggestions: {str(e)}", style="bold red")


def _handle_stack_recommend(
    project_dir: str, 
    stack_suggest_path: str, 
    tasks_path: str, 
    prd_file: str = None,
    interactive: bool = True,
    use_research: bool = False
) -> None:
    """Generate enhanced stack recommendations with optional research."""
    
    # Check if AI is available
    if not is_ai_available():
        console.print(
            "[ERROR] AI functionality is not available. Please check your model configuration and credentials.",
            style="bold red",
        )
        return
    
    # Gather context (similar to suggest)
    context_parts = []
    
    # Use saved PRD path if no PRD file provided
    if not prd_file:
        saved_prd_path = get_config_value("PRD_PATH")
        if saved_prd_path and os.path.exists(saved_prd_path):
            prd_file = saved_prd_path
            console.print(f"[INFO] Using saved PRD path: {prd_file}")
    
    # Read PRD if provided or found
    if prd_file and os.path.exists(prd_file):
        with open(prd_file, 'r') as f:
            prd_content = f.read()
            context_parts.append(f"PRD Content:\n{prd_content}")
    
    # Read existing tasks if available
    if os.path.exists(tasks_path):
        try:
            task_collection = read_tasks(tasks_path)
            tasks_summary = []
            for task in task_collection.tasks:
                tasks_summary.append(f"- {task.title}: {task.description}")
            if tasks_summary:
                context_parts.append(f"Existing Tasks:\n" + "\n".join(tasks_summary))
        except Exception as e:
            console.print(f"[WARNING] Could not read tasks: {str(e)}", style="yellow")
    
    # Read existing stack suggestions if available
    existing_suggestions = ""
    if os.path.exists(stack_suggest_path):
        with open(stack_suggest_path, 'r') as f:
            existing_suggestions = f.read()
        context_parts.append(f"Existing Stack Suggestions:\n{existing_suggestions}")
    
    if not context_parts:
        console.print("[ERROR] No context available. Please provide a PRD file or ensure tasks exist.", style="bold red")
        return
    
    research_context = ""
    if use_research:
        research_context = _perform_research(context_parts)
    
    console.print(Panel.fit(
        f"🔍 [bold cyan]Enhanced Technology Stack Recommendations[/bold cyan]\n\n"
        f"Analyzing project requirements{'with research data' if use_research else ''} to recommend optimal technologies...",
        border_style="cyan"
    ))
    
    # Generate enhanced recommendations using AI
    try:
        client = get_ai_client()
        model_config = get_model_config()
        
        system_prompt = """You are a senior technology consultant and architect providing comprehensive technology stack recommendations.

Your job is to analyze project requirements and provide detailed, researched recommendations with:
1. Current industry best practices
2. Technology maturity assessments
3. Ecosystem considerations
4. Performance and scalability implications
5. Learning curve and team considerations
6. Long-term maintainability

Provide your response in this exact format:

# Enhanced Technology Stack Recommendations

## Executive Summary
[2-3 sentences summarizing the recommended approach and key rationale]

## Recommended Core Technologies
- **Primary Language**: [Language with version and detailed justification]
- **Framework**: [Framework with version, why chosen over alternatives]
- **Database**: [Database system with reasoning for choice]
- **Runtime/Platform**: [Deployment target with justification]

## Development Ecosystem
- **Build System**: [Tool with integration benefits]
- **Package Manager**: [Choice with ecosystem considerations]
- **Testing Strategy**: [Framework with testing philosophy]
- **Code Quality Tools**: [Linting, formatting, static analysis]

## Infrastructure & Operations
- **Containerization**: [Docker strategy with reasoning]
- **Orchestration**: [If needed, with scale justification]
- **CI/CD Pipeline**: [Approach with tool recommendations]
- **Monitoring & Observability**: [Strategy and tools]

## Technology Risk Assessment
### Strengths
- [Key advantages of this stack]

### Potential Challenges  
- [Risks and mitigation strategies]

### Alternative Considerations
- [Other viable options that were considered but not chosen, with reasons]

## Implementation Roadmap
1. **Phase 1**: [Foundation setup]
2. **Phase 2**: [Core development]
3. **Phase 3**: [Production readiness]

## Team & Learning Considerations
- [Assessment of team readiness and learning requirements]
- [Recommended resources and training]

Focus on providing actionable, well-reasoned recommendations based on industry expertise and project-specific needs."""
        
        context = "\n\n".join(context_parts)
        if research_context:
            context += f"\n\nResearch Data:\n{research_context}"
        
        user_prompt = f"Please provide enhanced technology stack recommendations for this project:\n\n{context}"
        
        response = client.completion(
            model=model_config["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=model_config["max_tokens"],
            temperature=model_config["temperature"]
        )
        
        if response.choices:
            recommendations = response.choices[0].message.content
            
            # Write recommendations to file with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            output_content = f"# Generated on {timestamp}{'with research' if use_research else ''}\n\n{recommendations}"
            
            with open(stack_suggest_path, 'w') as f:
                f.write(output_content)
            
            console.print(f"\n[bold green]✅ Enhanced stack recommendations written to {stack_suggest_path}[/bold green]")
            console.print("\n" + "="*60)
            console.print(Markdown(recommendations))
            console.print("="*60)
            
            if interactive:
                console.print(f"\n[bold yellow]Next steps:[/bold yellow]")
                console.print("• Review and modify stack.suggest file as needed")
                console.print("• Use 'taskinator stack discuss' for interactive refinement")
                console.print("• Use 'taskinator stack compile' to create stack.lock")
        
    except Exception as e:
        console.print(f"[ERROR] Failed to generate stack recommendations: {str(e)}", style="bold red")


def _perform_research(context_parts: list) -> str:
    """Perform research using Perplexity if available."""
    try:
        # Check if Perplexity environment variables are available
        perplexity_key = os.environ.get("PERPLEXITY_API_KEY") or os.environ.get("PPLX_API_KEY")
        if not perplexity_key:
            console.print("[WARNING] No Perplexity API key found. Skipping research.", style="yellow")
            return ""
        
        console.print("[INFO] Performing research with Perplexity...", style="cyan")
        
        # Extract key technologies and concepts for research
        context_text = " ".join(context_parts)
        research_queries = _extract_research_queries(context_text)
        
        research_results = []
        for query in research_queries[:3]:  # Limit to top 3 queries to avoid rate limits
            result = _query_perplexity(query, perplexity_key)
            if result:
                research_results.append(f"Research Query: {query}\nFindings: {result}\n")
        
        return "\n".join(research_results) if research_results else ""
        
    except Exception as e:
        console.print(f"[WARNING] Research failed: {str(e)}", style="yellow")
        return ""


def _extract_research_queries(context_text: str) -> list:
    """Extract research queries from context."""
    # Simple keyword extraction for research queries
    # In a more sophisticated implementation, you'd use NLP to extract key concepts
    queries = []
    
    # Look for technology mentions
    tech_keywords = ["web app", "mobile app", "api", "database", "real-time", "machine learning", 
                    "authentication", "payment", "analytics", "microservices", "monolith"]
    
    for keyword in tech_keywords:
        if keyword.lower() in context_text.lower():
            queries.append(f"best technology stack for {keyword} 2024")
    
    # Add general query
    queries.append("technology stack trends 2024 best practices")
    
    return queries[:5]  # Limit queries


def _query_perplexity(query: str, api_key: str) -> str:
    """Query Perplexity API for research."""
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a technology research assistant. Provide concise, current information about technology trends and best practices."
                },
                {
                    "role": "user", 
                    "content": query
                }
            ],
            "max_tokens": 500,
            "temperature": 0.2
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            console.print(f"[WARNING] Perplexity query failed: {response.status_code}", style="yellow")
            return ""
            
    except ImportError:
        console.print("[WARNING] requests library not available for Perplexity research", style="yellow")
        return ""
    except Exception as e:
        console.print(f"[WARNING] Perplexity research error: {str(e)}", style="yellow")
        return ""


def _handle_stack_discuss(project_dir: str, stack_suggest_path: str, interactive: bool = True) -> None:
    """Interactive discussion about technology stack."""
    
    if not os.path.exists(stack_suggest_path):
        console.print("[ERROR] No stack.suggest file found. Run 'taskinator stack suggest' first.", style="bold red")
        return
    
    # Check if AI is available
    if not is_ai_available():
        console.print(
            "[ERROR] AI functionality is not available. Please check your model configuration and credentials.",
            style="bold red",
        )
        return
    
    with open(stack_suggest_path, 'r') as f:
        current_suggestions = f.read()
    
    console.print(Panel.fit(
        "💬 [bold cyan]Technology Stack Discussion[/bold cyan]\n\n"
        "Interactive discussion about your technology stack choices.\n"
        "Ask questions, request changes, or explore alternatives.\n\n"
        "[dim]Type 'show' to see current stack, 'quit' to exit[/dim]",
        border_style="cyan"
    ))
    
    try:
        client = get_ai_client()
        model_config = get_model_config()
        conversation_history = []
        
        while True:
            console.print("\n[bold blue]You:[/bold blue] ", end="")
            user_input = input().strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
            elif user_input.lower() in ["show", "current"]:
                console.print("\n[bold]Current Stack Suggestions:[/bold]")
                console.print(Markdown(current_suggestions))
                continue
            elif any(phrase in user_input.lower() for phrase in ["lock", "compile", "finalize", "lock it", "compile it", "finalize it"]):
                console.print("\n[bold cyan]🔒 Locking Technology Stack[/bold cyan]")
                _handle_stack_compile(stack_suggest_path, os.path.join(project_dir, "stack.lock"), interactive)
                console.print("\n[bold green]Stack is now locked! You can continue the discussion or type 'quit' to exit.[/bold green]")
                continue
            
            # Add user input to conversation history
            conversation_history.append({"role": "user", "content": user_input})
            
            # Prepare context for AI
            system_prompt = f"""You are a technology stack consultant discussing technology choices for a software project.

Current stack suggestions:
{current_suggestions}

Your role is to:
1. Answer questions about the current stack choices
2. Suggest modifications when requested
3. Explain trade-offs between different technologies
4. Provide updated stack suggestions when changes are made

If the user requests changes to the stack, provide a complete updated stack suggestion in the same format as the original.

Be conversational and helpful while maintaining technical accuracy."""
            
            try:
                response = client.completion(
                    model=model_config["model"],
                    messages=[{"role": "system", "content": system_prompt}] + conversation_history,
                    max_tokens=model_config["max_tokens"],
                    temperature=model_config["temperature"]
                )
                
                if response.choices:
                    ai_response = response.choices[0].message.content
                    console.print(f"\n[bold green]Assistant:[/bold green]")
                    console.print(Markdown(ai_response))
                    
                    # Add AI response to conversation history
                    conversation_history.append({"role": "assistant", "content": ai_response})
                    
                    # Check if this looks like an updated stack suggestion (more flexible detection)
                    stack_indicators = [
                        "Technology Stack" in ai_response,
                        "Core Technologies" in ai_response,
                        "Infrastructure" in ai_response,
                        "Development Tools" in ai_response,
                        "Additional Libraries" in ai_response,
                        # Check for structured technology listings
                        ("Language:" in ai_response and "Framework:" in ai_response),
                        ("Database:" in ai_response and "Docker" in ai_response),
                    ]
                    
                    if any(stack_indicators) and len(ai_response) > 500:  # Must be substantial content
                        update_file = Prompt.ask(
                            "\n[bold yellow]This looks like an updated stack suggestion. Update stack.suggest file?[/bold yellow] (y/n)",
                            default="y"  # Default to yes since user explicitly made changes
                        )
                        if update_file.lower() in ["y", "yes"]:
                            with open(stack_suggest_path, 'w') as f:
                                f.write(ai_response)
                            current_suggestions = ai_response
                            console.print(f"[bold green]✅ Updated {stack_suggest_path}[/bold green]")
                
            except Exception as e:
                console.print(f"[ERROR] AI request failed: {str(e)}", style="bold red")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[ERROR] {str(e)}", style="bold red")


def _handle_stack_compile(stack_suggest_path: str, stack_lock_path: str, interactive: bool = True) -> None:
    """Compile stack.suggest into a definitive stack.lock file."""
    
    if not os.path.exists(stack_suggest_path):
        console.print("[ERROR] No stack.suggest file found. Run 'taskinator stack suggest' first.", style="bold red")
        return
    
    with open(stack_suggest_path, 'r') as f:
        suggestions = f.read()
    
    console.print(Panel.fit(
        "🔒 [bold cyan]Compile Technology Stack Lock File[/bold cyan]\n\n"
        "Converting stack suggestions into a definitive stack.lock file.\n"
        "This will establish the official technology constraints for the project.",
        border_style="cyan"
    ))
    
    # Extract key information from suggestions
    try:
        # Parse the suggestions to create a structured lock file
        lock_data = {
            "version": "1.0",
            "locked_at": "",
            "core_technologies": {},
            "development_tools": {},
            "infrastructure": {},
            "additional_libraries": {},
            "constraints": {
                "language_version": "",
                "framework_version": "",
                "database_version": "",
                "build_requirements": []
            },
            "forbidden": [],
            "notes": ""
        }
        
        # More robust parsing for technology stack entries
        lines = suggestions.split('\n')
        current_section = None
        
        # Expanded section mapping with more variations
        section_map = {
            'core': 'core_technologies',
            'technolog': 'core_technologies',
            'recommended core': 'core_technologies',
            'executive summary': 'core_technologies',  # Often contains key tech choices
            'primary': 'core_technologies',
            'main': 'core_technologies',
            'development': 'development_tools',
            'dev tool': 'development_tools',
            'development ecosystem': 'development_tools',
            'test': 'development_tools',
            'quality': 'development_tools',
            'infrastructure': 'infrastructure',
            'operations': 'infrastructure',
            'deploy': 'infrastructure',
            'ci/cd': 'infrastructure',
            'hosting': 'infrastructure',
            'additional': 'additional_libraries',
            'libraries': 'additional_libraries',
            'ecosystem': 'additional_libraries',
            'utility': 'additional_libraries'
        }
        
        # Add debug flag to control verbose output
        debug_parsing = False
        console.print("[dim]Parsing stack suggestions...[/dim]")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            if debug_parsing:
                console.print(f"[dim]Line {i+1}: {line}[/dim]")
            
            # Section headers - support various markdown header levels (# to ######)
            if any(line.startswith(f"{h} ") for h in ["#", "##", "###", "####", "#####", "######"]):
                # Extract the header text without the # characters
                header = line.lstrip('#').strip().lower()
                if debug_parsing:
                    console.print(f"[dim]Found section: {header}[/dim]")
                current_section = header
                continue
            
            # Try to extract key-value pairs using multiple approaches
            # This is where we make the parser much more robust
            
            # Approach 1: Look for explicit patterns like "- **Key**: Value" or "**Key**: Value"
            key_value = None
            
            # Pattern: - **Key**: Value
            if (line.startswith("-") and "**" in line and ":" in line and 
                line.count("**") >= 2 and line.index("**") < line.rindex("**")):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].replace("-", "").replace("*", "").strip()
                    value = parts[1].strip()
                    key_value = (key, value)
            
            # Pattern: **Key**: Value
            elif ("**" in line and ":" in line and 
                  line.count("**") >= 2 and line.index("**") < line.rindex("**")):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].replace("*", "").strip()
                    value = parts[1].strip()
                    key_value = (key, value)
            
            # Pattern: - Key: Value (without bold)
            elif line.startswith("-") and ":" in line and not "**" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].replace("-", "").strip()
                    value = parts[1].strip()
                    key_value = (key, value)
            
            # Pattern: Key: Value (plain text)
            elif ":" in line and not line.startswith("#") and not line.startswith("!"):
                parts = line.split(":", 1)
                if len(parts) == 2 and len(parts[0].strip()) < 30:  # Avoid splitting long sentences with colons
                    key = parts[0].strip()
                    value = parts[1].strip()
                    key_value = (key, value)
            
            # If we found a key-value pair, process it
            if key_value:
                key, value = key_value
                
                # Clean up the key and value
                key = key.lower().replace("_", " ")
                
                # Handle values with markdown placeholders like [Python 3.9+]
                if "[" in value and "]" in value:
                    # Only remove if it looks like a placeholder (not a markdown link)
                    if not "(" in value and not ")" in value:  # Not a markdown link [text](url)
                        value = value.replace("[", "").replace("]", "")
                
                # Find the appropriate section to store this value
                target_section = None
                
                # First check if key gives us clues about where it belongs
                key_section_map = {
                    'language': 'core_technologies',
                    'framework': 'core_technologies', 
                    'runtime': 'core_technologies',
                    'database': 'core_technologies',
                    'platform': 'core_technologies',
                    'build': 'development_tools',
                    'testing': 'development_tools',
                    'test framework': 'development_tools',
                    'lint': 'development_tools',
                    'quality': 'development_tools',
                    'package': 'development_tools',
                    'docker': 'infrastructure',
                    'container': 'infrastructure',
                    'orchestration': 'infrastructure',
                    'ci': 'infrastructure',
                    'cd': 'infrastructure',
                    'deployment': 'infrastructure',
                    'hosting': 'infrastructure',
                    'cloud': 'infrastructure',
                    'api': 'additional_libraries',
                    'http': 'additional_libraries',
                    'client': 'additional_libraries',
                    'logging': 'additional_libraries',
                    'auth': 'additional_libraries',
                    'config': 'additional_libraries'
                }
                
                # Try to determine section from the key
                for keyword, section in key_section_map.items():
                    if keyword in key.lower():
                        target_section = section
                        break
                
                # If key doesn't help, try using the current section context
                if not target_section and current_section:
                    for keyword, section in section_map.items():
                        if keyword in current_section.lower():
                            target_section = section
                            break
                
                # If we still don't have a target section, default to core_technologies for important keys
                if not target_section:
                    # These are common core technologies that might appear without clear section headers
                    core_tech_indicators = ['python', 'javascript', 'typescript', 'java', 'c#', 'go', 'rust', 
                                          'react', 'vue', 'angular', 'django', 'flask', 'spring', 'node', 
                                          'postgres', 'mysql', 'mongodb', 'sqlite', 'uv']
                    
                    if any(tech in value.lower() for tech in core_tech_indicators):
                        target_section = 'core_technologies'
                    else:
                        # If we really can't determine the section, skip this entry
                        continue
                
                # Store the key-value pair in the appropriate section
                if target_section:
                    if debug_parsing:
                        console.print(f"[dim]Found entry: {key} = {value} in section {target_section}[/dim]")
                    lock_data[target_section][key.lower()] = value
        
        # Handle version information
        # Extract version information from values and populate constraints
        for tech, value in lock_data["core_technologies"].items():
            if "language" in tech.lower() and value:
                # Try to extract version information (e.g., "Python 3.9+" -> "3.9+")
                import re
                version_match = re.search(r'(\d+\.\d+[\.\d+]*[\+]?)', value)
                if version_match:
                    lock_data["constraints"]["language_version"] = version_match.group(1)
            
            if "framework" in tech.lower() and value:
                version_match = re.search(r'(\d+\.\d+[\.\d+]*[\+]?)', value)
                if version_match:
                    lock_data["constraints"]["framework_version"] = version_match.group(1)
            
            if "database" in tech.lower() and value:
                version_match = re.search(r'(\d+\.\d+[\.\d+]*[\+]?)', value)
                if version_match:
                    lock_data["constraints"]["database_version"] = version_match.group(1)
        
        # Add timestamp
        from datetime import datetime
        lock_data["locked_at"] = datetime.now().isoformat()
        
        # Check if we extracted a reasonable amount of data
        sections_with_data = sum(1 for section in [lock_data["core_technologies"], 
                                                 lock_data["development_tools"],
                                                 lock_data["infrastructure"], 
                                                 lock_data["additional_libraries"]] 
                               if section)
        
        if sections_with_data == 0:
            console.print("[yellow]Warning: Could not extract any technology details from stack.suggest.[/yellow]")
            console.print("[yellow]The stack.lock file will be created with empty values.[/yellow]")
            lock_data["notes"] = "Failed to parse stack.suggest file. Please update manually."
        elif sections_with_data < 2:
            console.print("[yellow]Warning: Limited technology details extracted from stack.suggest.[/yellow]")
            console.print("[yellow]Consider reviewing and manually updating the stack.lock file.[/yellow]")
            lock_data["notes"] = "Limited parsing success. Please review and update as needed."
        
        # Write lock file
        with open(stack_lock_path, 'w') as f:
            json.dump(lock_data, f, indent=2)
        
        console.print(f"[bold green]✅ Created {stack_lock_path}[/bold green]")
        
        # Show summary
        console.print("\n[bold]Technology Stack Locked:[/bold]")
        
        if lock_data["core_technologies"]:
            table = Table(title="Core Technologies", show_header=True)
            table.add_column("Technology", style="cyan")
            table.add_column("Version/Details", style="white")
            
            for key, value in lock_data["core_technologies"].items():
                table.add_row(key.title(), value)
            console.print(table)
        else:
            console.print("[yellow]No core technologies were extracted from the suggestions.[/yellow]")
        
        console.print(f"\n[bold yellow]Important:[/bold yellow] All AI tools (.windsurfrules, CLAUDE.local.md, etc.) will now enforce these technology constraints.")
        console.print("Update your project's AI configuration files to reflect the locked stack.")
        
        if interactive:
            update_configs = Prompt.ask(
                "\n[bold yellow]Update AI tool configuration files to enforce stack.lock?[/bold yellow] (y/n)",
                default="y"
            )
            if update_configs.lower() in ["y", "yes"]:
                _update_ai_configs_with_stack(os.path.dirname(stack_lock_path), lock_data)
        
    except Exception as e:
        console.print(f"[ERROR] Failed to compile stack lock: {str(e)}", style="bold red")
        if debug_parsing:
            import traceback
            console.print(traceback.format_exc())

def _show_stack_status(stack_suggest_path: str, stack_lock_path: str) -> None:
    """Show current stack status."""
    
    console.print("\n[bold]Technology Stack Status:[/bold]")
    
    # Check stack.suggest
    if os.path.exists(stack_suggest_path):
        console.print(f"✅ {stack_suggest_path} exists")
        with open(stack_suggest_path, 'r') as f:
            content = f.read()
            lines = len(content.split('\n'))
            console.print(f"   • {lines} lines of suggestions")
    else:
        console.print(f"❌ {stack_suggest_path} not found")
    
    # Check stack.lock
    if os.path.exists(stack_lock_path):
        console.print(f"🔒 {stack_lock_path} exists")
        try:
            with open(stack_lock_path, 'r') as f:
                lock_data = json.load(f)
                console.print(f"   • Version: {lock_data.get('version', 'unknown')}")
                console.print(f"   • Locked at: {lock_data.get('locked_at', 'unknown')}")
                
                # Show core technologies
                core_tech = lock_data.get('core_technologies', {})
                if core_tech:
                    console.print("   • Core Technologies:")
                    for key, value in core_tech.items():
                        console.print(f"     - {key.title()}: {value}")
        except Exception as e:
            console.print(f"   • [WARNING] Could not parse lock file: {str(e)}", style="yellow")
    else:
        console.print(f"❌ {stack_lock_path} not found")
    
    # Show available commands
    console.print("\n[bold]Available Commands:[/bold]")
    console.print("• taskinator stack suggest [--prd file] - Generate initial suggestions")
    console.print("• taskinator stack discuss - Interactive stack discussion")
    console.print("• taskinator stack compile - Create stack.lock from suggestions")
    console.print("• taskinator stack show - Show this status")


def _update_ai_configs_with_stack(project_dir: str, lock_data: dict) -> None:
    """Update AI configuration files to enforce stack.lock constraints and fill in placeholders."""
    
    # Create stack enforcement text
    stack_text = _generate_stack_enforcement_text(lock_data)
    
    # Update .windsurfrules
    windsurfrules_path = os.path.join(project_dir, ".windsurfrules")
    if os.path.exists(windsurfrules_path):
        _inject_stack_rules(windsurfrules_path, stack_text, "windsurfrules")
        _fill_template_placeholders(windsurfrules_path, lock_data, "windsurfrules")
    
    # Update CLAUDE.local.md
    claude_path = os.path.join(project_dir, "CLAUDE.local.md")
    if os.path.exists(claude_path):
        _inject_stack_rules(claude_path, stack_text, "claude")
        _fill_template_placeholders(claude_path, lock_data, "claude")
    
    # Update Cursor rules
    cursor_dev_path = os.path.join(project_dir, ".cursor", "rules", "dev_workflow.mdc")
    if os.path.exists(cursor_dev_path):
        _inject_stack_rules(cursor_dev_path, stack_text, "cursor")
        _fill_template_placeholders(cursor_dev_path, lock_data, "cursor")
    
    console.print(f"[bold green]✅ Updated AI configuration files with stack.lock constraints and filled in project details[/bold green]")


def _generate_stack_enforcement_text(lock_data: dict) -> str:
    """Generate text for enforcing stack constraints in AI configs."""
    
    text = """## MANDATORY TECHNOLOGY STACK CONSTRAINTS

**CRITICAL**: This project has a locked technology stack (stack.lock). You MUST comply with these constraints:

"""
    
    # Add core technologies
    if lock_data.get("core_technologies"):
        text += "### Required Core Technologies\n"
        for key, value in lock_data["core_technologies"].items():
            text += f"- **{key.title()}**: {value} (REQUIRED)\n"
        text += "\n"
    
    # Add development tools
    if lock_data.get("development_tools"):
        text += "### Required Development Tools\n"
        for key, value in lock_data["development_tools"].items():
            text += f"- **{key.title()}**: {value} (REQUIRED)\n"
        text += "\n"
    
    text += """### Enforcement Rules
1. **NO ALTERNATIVE TECHNOLOGIES** - Do not suggest or use technologies not listed above
2. **EXACT VERSIONS** - Use only the specified versions when provided
3. **NO SUBSTITUTIONS** - Do not substitute similar technologies without explicit permission
4. **COMPLIANCE CHECK** - Always verify your suggestions against this stack.lock file

**If the user requests technologies not in stack.lock, direct them to use 'taskinator stack discuss' to modify the approved stack first.**

"""
    
    return text


def _inject_stack_rules(file_path: str, stack_text: str, file_type: str) -> None:
    """Inject stack enforcement rules into AI config files."""
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Remove existing stack constraints if present
        start_marker = "## MANDATORY TECHNOLOGY STACK CONSTRAINTS"
        end_marker = "**If the user requests technologies not in stack.lock"
        
        start_idx = content.find(start_marker)
        if start_idx != -1:
            # Find the end of the stack constraints section
            remaining_content = content[start_idx:]
            end_idx = remaining_content.find(end_marker)
            if end_idx != -1:
                # Find the end of the line containing end_marker
                line_end = remaining_content.find('\n', end_idx)
                if line_end != -1:
                    # Remove the old stack constraints
                    content = content[:start_idx] + content[start_idx + line_end + 1:]
        
        # Insert new stack constraints at the top (after any initial headers/metadata)
        if file_type == "windsurfrules":
            # Insert after the rule metadata
            insert_pos = content.find("---\n\n") + 5 if "---\n\n" in content else 0
        elif file_type == "claude":
            # Insert after the project overview
            insert_pos = content.find("## Development Workflow")
            if insert_pos == -1:
                insert_pos = content.find("## Core Development")
            if insert_pos == -1:
                insert_pos = len(content.split('\n')[0]) + 1  # After first line
        else:  # cursor
            # Insert after the metadata
            insert_pos = content.find("---\n\n") + 5 if "---\n\n" in content else 0
        
        if insert_pos < len(content):
            content = content[:insert_pos] + stack_text + "\n" + content[insert_pos:]
        else:
            content = content + "\n" + stack_text
        
        with open(file_path, 'w') as f:
            f.write(content)
            
    except Exception as e:
        console.print(f"[WARNING] Could not update {file_path}: {str(e)}", style="yellow")


def _fill_template_placeholders(file_path: str, lock_data: dict, file_type: str) -> None:
    """Fill in template placeholders with actual technology stack information."""
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Generate technology stack details
        tech_details = _generate_tech_details(lock_data)
        
        # Replace placeholder sections based on file type
        if file_type == "windsurfrules":
            # Update technology stack section
            tech_section = f"""## Technology Stack
Core technologies for this project:

### Languages & Frameworks
{tech_details['languages_frameworks']}

### Development Tools
{tech_details['dev_tools']}

### Quality Standards
{tech_details['quality_standards']}"""
            
            # Replace the instruction text with actual details
            content = content.replace(
                "To define your project's technology stack, use the stack management commands:\n\n1. Generate initial suggestions: `taskinator stack suggest --prd your_prd.txt`\n2. Refine through discussion: `taskinator stack discuss`\n3. Lock final decisions: `taskinator stack compile`\n\nOnce you run `taskinator stack compile`, this section will be automatically updated with your project's specific technology constraints.",
                tech_section
            )
            
        elif file_type == "claude":
            # Update technology stack section in CLAUDE.local.md
            tech_section = f"""### Technology Stack
{tech_details['full_stack_details']}

### Code Quality Standards
{tech_details['quality_standards']}

### Development Environment
{tech_details['dev_environment']}"""
            
            # Replace the instruction text
            content = content.replace(
                "To define your project's technology stack:\n\n1. Generate suggestions: `taskinator stack suggest --prd your_prd.txt`\n2. Refine through discussion: `taskinator stack discuss`\n3. Lock final stack: `taskinator stack compile`\n\nAfter running `taskinator stack compile`, this section will be automatically populated with your project's specific technology constraints, coding standards, and development environment requirements.",
                tech_section
            )
            
        elif file_type == "cursor":
            # Update project-specific notes
            notes_section = f"""## Project-Specific Notes
### Technology Stack
{tech_details['languages_frameworks']}

### Development Standards
{tech_details['quality_standards']}

### Build & Testing
{tech_details['build_test_commands']}"""
            
            content = content.replace(
                "After running `taskinator stack compile`, this section will be automatically updated with:\n- Technology-specific workflow rules\n- Coding standards for your chosen stack\n- Build and deployment conventions\n- Quality assurance requirements",
                notes_section
            )
        
        # Write updated content back to file
        with open(file_path, 'w') as f:
            f.write(content)
            
    except Exception as e:
        console.print(f"[WARNING] Could not fill placeholders in {file_path}: {str(e)}", style="yellow")


def _generate_tech_details(lock_data: dict) -> dict:
    """Generate formatted technology details from lock data."""
    
    details = {}
    
    # Languages & Frameworks
    lang_framework = []
    core_tech = lock_data.get('core_technologies', {})
    if core_tech:
        for key, value in core_tech.items():
            lang_framework.append(f"- **{key.title()}**: {value}")
    
    details['languages_frameworks'] = "\n".join(lang_framework) if lang_framework else "- To be defined"
    
    # Development Tools
    dev_tools = []
    dev_tech = lock_data.get('development_tools', {})
    if dev_tech:
        for key, value in dev_tech.items():
            dev_tools.append(f"- **{key.title()}**: {value}")
    
    details['dev_tools'] = "\n".join(dev_tools) if dev_tools else "- To be defined"
    
    # Quality Standards
    quality_items = []
    if core_tech.get('language'):
        lang = core_tech['language'].lower()
        if 'python' in lang:
            quality_items = [
                "- **Formatting**: black, isort",
                "- **Linting**: flake8 or ruff", 
                "- **Type Checking**: mypy",
                "- **Testing**: pytest"
            ]
        elif 'javascript' in lang or 'typescript' in lang:
            quality_items = [
                "- **Formatting**: prettier",
                "- **Linting**: eslint",
                "- **Type Checking**: TypeScript",
                "- **Testing**: jest or vitest"
            ]
        elif 'go' in lang:
            quality_items = [
                "- **Formatting**: gofmt",
                "- **Linting**: golangci-lint", 
                "- **Testing**: go test",
                "- **Documentation**: godoc"
            ]
        elif 'rust' in lang:
            quality_items = [
                "- **Formatting**: rustfmt",
                "- **Linting**: clippy",
                "- **Testing**: cargo test", 
                "- **Documentation**: rustdoc"
            ]
    
    if not quality_items:
        quality_items = ["- Follow language-specific best practices"]
    
    details['quality_standards'] = "\n".join(quality_items)
    
    # Full stack details for Claude
    full_details = []
    if core_tech:
        full_details.append("**Core Technologies:**")
        for key, value in core_tech.items():
            full_details.append(f"- **{key.title()}**: {value}")
    
    if dev_tech:
        full_details.append("\n**Development Tools:**")
        for key, value in dev_tech.items():
            full_details.append(f"- **{key.title()}**: {value}")
    
    details['full_stack_details'] = "\n".join(full_details) if full_details else "Technology stack to be defined."
    
    # Development Environment
    env_details = []
    if core_tech.get('language'):
        lang = core_tech['language']
        env_details.append(f"- **Primary Language**: {lang}")
    
    if core_tech.get('framework'):
        framework = core_tech['framework'] 
        env_details.append(f"- **Framework**: {framework}")
    
    if dev_tech.get('build system') or dev_tech.get('build_system'):
        build_tool = dev_tech.get('build system') or dev_tech.get('build_system')
        env_details.append(f"- **Build Tool**: {build_tool}")
    
    details['dev_environment'] = "\n".join(env_details) if env_details else "- Development environment to be configured"
    
    # Build & Test Commands (basic examples based on language)
    build_commands = []
    if core_tech.get('language'):
        lang = core_tech['language'].lower()
        if 'python' in lang:
            build_commands = [
                "- **Install**: `pip install -r requirements.txt`",
                "- **Test**: `pytest`",
                "- **Lint**: `flake8 . && black --check .`",
                "- **Type Check**: `mypy .`"
            ]
        elif 'javascript' in lang or 'node' in lang:
            build_commands = [
                "- **Install**: `npm install`", 
                "- **Test**: `npm test`",
                "- **Lint**: `npm run lint`",
                "- **Build**: `npm run build`"
            ]
        elif 'go' in lang:
            build_commands = [
                "- **Build**: `go build`",
                "- **Test**: `go test ./...`",
                "- **Lint**: `golangci-lint run`",
                "- **Format**: `go fmt ./...`"
            ]
        elif 'rust' in lang:
            build_commands = [
                "- **Build**: `cargo build`",
                "- **Test**: `cargo test`", 
                "- **Lint**: `cargo clippy`",
                "- **Format**: `cargo fmt`"
            ]
    
    details['build_test_commands'] = "\n".join(build_commands) if build_commands else "- Build commands to be configured"
    
    return details


def _show_stack_help() -> None:
    """Show help for stack command."""
    
    help_text = """
[bold]Technology Stack Management[/bold]

Available commands:
• taskinator stack suggest [--prd file] - Generate basic technology stack suggestions
• taskinator stack recommend [--prd file] [--research] - Generate enhanced recommendations with research
• taskinator stack discuss - Interactive discussion about stack choices  
• taskinator stack compile - Create definitive stack.lock file
• taskinator stack show - Show current stack status

Workflow:
1. Generate basic suggestions: taskinator stack suggest --prd my_prd.txt
   OR enhanced recommendations: taskinator stack recommend --prd my_prd.txt --research
2. Refine through discussion: taskinator stack discuss
3. Lock the final stack: taskinator stack compile
4. AI tools will enforce the locked stack constraints

Files:
• stack.suggest - Draft technology suggestions and reasoning
• stack.lock - Final locked technology constraints (JSON)
"""
    
    console.print(Panel(help_text, title="Stack Management Help", border_style="blue"))