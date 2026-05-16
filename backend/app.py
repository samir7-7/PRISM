"""
PRISM Backend - Application Re-export
Thin module that re-exports the FastAPI app from backend.main for compatibility.
"""
from backend.main import app

__all__ = ["app"]

# Made with Bob
