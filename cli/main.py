"""
PRISM CLI - Pull Request Impact and Security Monitor

Main entry point for the CLI application with global error handling.
"""

import sys
from functools import wraps
from typing import Callable, Any

import typer
from rich.console import Console

from errors import PRISMError, is_prism_error
from formatter import format_error

# Initialize Typer app
app = typer.Typer(
    name="prism",
    help="PRISM CLI - Analyze pull requests for security and impact",
    add_completion=False
)

# Console for output
console = Console()


# ============================================================================
# Error Handler Decorator
# ============================================================================

def handle_errors(func: Callable) -> Callable:
    """
    Decorator to handle errors in CLI commands.
    
    Catches all exceptions, formats them nicely, and exits with
    appropriate status codes.
    
    Usage:
        @app.command()
        @handle_errors
        def my_command():
            # Command logic here
            pass
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except PRISMError as e:
            # Handle PRISM-specific errors
            format_error(e)
            sys.exit(1)
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            console.print("\n\n[!] Operation cancelled by user", style="yellow")
            sys.exit(130)
        except Exception as e:
            # Handle unexpected errors
            format_error(e)
            console.print("\n[!] This is an unexpected error. Please report it.", style="yellow")
            sys.exit(1)
    
    return wrapper


# ============================================================================
# Commands
# ============================================================================

@app.command()
@handle_errors
def analyze(
    pr_id: str = typer.Argument(..., help="PR identifier (e.g., 123, #123, pr-123)"),
    repo: str = typer.Option(None, "--repo", "-r", help="Repository URL or owner/repo"),
    backend: str = typer.Option(None, "--backend", "-b", help="Backend API URL"),
    token: str = typer.Option(None, "--token", "-t", help="GitHub token"),
    open_browser: bool = typer.Option(False, "--open", "-o", help="Open dashboard in browser"),
    json_output: bool = typer.Option(False, "--json", hidden=True, help="Output as JSON"),
):
    """
    Analyze a pull request for security and impact.
    
    Examples:
        prism analyze 123
        prism analyze #456 --repo owner/repo
        prism analyze pr-789 --open
    """
    # TODO: Implement analyze command
    console.print(f"[cyan]Analyzing PR: {pr_id}[/cyan]")
    console.print("[yellow][!] Command not yet implemented[/yellow]")


@app.command()
@handle_errors
def demo():
    """
    Run a demo analysis with sample data.
    
    This command demonstrates the CLI without requiring a real PR or backend.
    """
    # TODO: Implement demo command
    console.print("[cyan]Running demo...[/cyan]")
    console.print("[yellow][!] Command not yet implemented[/yellow]")


@app.command()
def version():
    """
    Show the CLI version.
    """
    console.print("[bold cyan]PRISM CLI[/bold cyan] version [bold]0.1.0[/bold]")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()