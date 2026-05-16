"""
Formatting utilities for PRISM CLI.

This module provides functions to format output for the CLI, including
error messages, analysis results, and other user-facing content using
the Rich library for beautiful terminal output.
"""

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from errors import PRISMError, is_prism_error


# ============================================================================
# Console Setup
# ============================================================================

# Global console instance for consistent formatting
# Force UTF-8 encoding to handle emojis on Windows
console = Console(force_terminal=True, legacy_windows=False)


# ============================================================================
# Error Formatting
# ============================================================================

def format_error(error: Exception, show_traceback: bool = False) -> None:
    """
    Format and display an error message using Rich.
    
    Handles both PRISMError instances (with rich formatting) and
    standard exceptions (with basic formatting).
    
    Args:
        error: The exception to format
        show_traceback: Whether to show the full traceback (for debugging)
    """
    if is_prism_error(error):
        _format_prism_error(error)  # type: ignore[arg-type]
    else:
        _format_generic_error(error)
    
    if show_traceback:
        console.print_exception()


def _format_prism_error(error: PRISMError) -> None:
    """
    Format a PRISMError with rich styling.
    
    Creates a beautiful error panel with:
    - Error code and message
    - Optional suggestion
    - Color-coded by error type
    
    Args:
        error: The PRISMError to format
    """
    # Determine color based on error code prefix
    color = _get_error_color(error.code)
    
    # Build the error content
    content = Text()
    content.append("[X] Error ", style="bold red")
    content.append(f"[{error.code}]", style=f"bold {color}")
    content.append(f": {error.message}\n", style="red")
    
    # Add suggestion if available
    if error.suggestion:
        content.append("\n[!] ", style="bold yellow")
        content.append("Suggestion: ", style="bold yellow")
        content.append(error.suggestion, style="yellow")
    
    # Create panel with appropriate styling
    panel = Panel(
        content,
        border_style=color,
        padding=(1, 2),
        expand=False
    )
    
    console.print()
    console.print(panel)
    console.print()


def _format_generic_error(error: Exception) -> None:
    """
    Format a generic exception with basic styling.
    
    Args:
        error: The exception to format
    """
    content = Text()
    content.append("[X] Error: ", style="bold red")
    content.append(str(error), style="red")
    
    panel = Panel(
        content,
        border_style="red",
        padding=(1, 2),
        expand=False
    )
    
    console.print()
    console.print(panel)
    console.print()


def _get_error_color(error_code: str) -> str:
    """
    Get the color for an error based on its code.
    
    Args:
        error_code: The error code (e.g., "E1001")
        
    Returns:
        Color name for Rich styling
    """
    if error_code.startswith("E1"):
        return "yellow"  # Validation errors
    elif error_code.startswith("E2"):
        return "red"  # Network errors
    elif error_code.startswith("E3"):
        return "magenta"  # API errors
    elif error_code.startswith("E4"):
        return "blue"  # Configuration errors
    else:
        return "red"  # Default


# ============================================================================
# Success Formatting
# ============================================================================

def format_success(message: str) -> None:
    """
    Format and display a success message.
    
    Args:
        message: The success message to display
    """
    content = Text()
    content.append("[OK] ", style="bold green")
    content.append(message, style="green")
    
    console.print()
    console.print(content)
    console.print()


# ============================================================================
# Info Formatting
# ============================================================================

def format_info(message: str, title: Optional[str] = None) -> None:
    """
    Format and display an informational message.
    
    Args:
        message: The info message to display
        title: Optional title for the message
    """
    if title:
        content = Text()
        content.append(f"[i] {title}\n", style="bold cyan")
        content.append(message, style="cyan")
    else:
        content = Text()
        content.append("[i] ", style="bold cyan")
        content.append(message, style="cyan")
    
    console.print()
    console.print(content)
    console.print()


# ============================================================================
# Warning Formatting
# ============================================================================

def format_warning(message: str) -> None:
    """
    Format and display a warning message.
    
    Args:
        message: The warning message to display
    """
    content = Text()
    content.append("[!] ", style="bold yellow")
    content.append(message, style="yellow")
    
    console.print()
    console.print(content)
    console.print()


# ============================================================================
# Analysis Result Formatting
# ============================================================================

def format_analysis_result(result: dict) -> None:
    """
    Format and display an analysis result.
    
    Args:
        result: Dictionary containing analysis results with keys:
            - report_id: UUID string
            - dashboard_url: URL to the dashboard
            - risk_score: Integer risk score
            - risk_label: Risk level (LOW, MEDIUM, HIGH)
            - impacted_node_count: Number of impacted nodes
            - status: Analysis status (COMPLETE, PARTIAL)
    """
    # Create a table for the results
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="bold cyan")
    table.add_column("Value", style="white")
    
    # Add rows
    table.add_row("Report ID", result.get("report_id", "N/A"))
    table.add_row("Dashboard URL", result.get("dashboard_url", "N/A"))
    
    # Format risk score with color
    risk_label = result.get("risk_label", "UNKNOWN")
    risk_score = result.get("risk_score", 0)
    risk_color = _get_risk_color(risk_label)
    risk_text = Text(f"{risk_score} ({risk_label})", style=f"bold {risk_color}")
    table.add_row("Risk Score", risk_text)
    
    table.add_row("Impacted Nodes", str(result.get("impacted_node_count", 0)))
    table.add_row("Status", result.get("status", "UNKNOWN"))
    
    # Create panel
    panel = Panel(
        table,
        title="[bold green][OK] Analysis Complete[/bold green]",
        border_style="green",
        padding=(1, 2)
    )
    
    console.print()
    console.print(panel)
    console.print()


def _get_risk_color(risk_label: str) -> str:
    """
    Get the color for a risk label.
    
    Args:
        risk_label: The risk label (LOW, MEDIUM, HIGH)
        
    Returns:
        Color name for Rich styling
    """
    risk_colors = {
        "LOW": "green",
        "MEDIUM": "yellow",
        "HIGH": "red"
    }
    return risk_colors.get(risk_label.upper(), "white")


# ============================================================================
# Progress Formatting
# ============================================================================

def format_progress(message: str) -> None:
    """
    Format and display a progress message.
    
    Args:
        message: The progress message to display
    """
    content = Text()
    content.append("[...] ", style="bold blue")
    content.append(message, style="blue")
    
    console.print(content)


# ============================================================================
# JSON Formatting
# ============================================================================

def format_json(data: dict) -> None:
    """
    Format and display JSON data.
    
    Args:
        data: Dictionary to display as JSON
    """
    import json
    console.print_json(json.dumps(data, indent=2))


# Made with Bob