"""
Startup script for PRISM Backend
Ensures proper Python path and starts the server
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variable for the project root
os.environ['PYTHONPATH'] = str(project_root)

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print(">> Starting PRISM Backend Server")
    print("=" * 60)
    print(f"Project Root: {project_root}")
    print(f"Python Path: {sys.path[0]}")
    print("=" * 60)
    print()
    print("Swagger UI: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print("Health Check: http://localhost:8000/health")
    print()
    print("=" * 60)
    print()
    
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
