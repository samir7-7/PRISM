"""
Verify all required dependencies are installed for PRISM.
"""
import sys

def check_dependency(module_name, package_name=None):
    """Check if a module can be imported."""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} - MISSING")
        return False

def main():
    print("\n" + "="*60)
    print("PRISM Dependency Verification")
    print("="*60 + "\n")
    
    dependencies = [
        # Web Framework
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        
        # Validation & Settings
        ("pydantic", "pydantic"),
        ("pydantic_settings", "pydantic-settings"),
        
        # Database
        ("sqlalchemy", "sqlalchemy"),
        ("alembic", "alembic"),
        
        # HTTP Client
        ("httpx", "httpx"),
        
        # Static Analysis (CRITICAL for H1 fix)
        ("tree_sitter", "tree-sitter"),
        ("tree_sitter_python", "tree-sitter-python"),
        ("tree_sitter_javascript", "tree-sitter-javascript"),
        ("tree_sitter_typescript", "tree-sitter-typescript"),
        
        # Graph Engine
        ("networkx", "networkx"),
        
        # Utilities
        ("dotenv", "python-dotenv"),
        ("multipart", "python-multipart"),
        ("typer", "typer"),
        ("rich", "rich"),
    ]
    
    print("Checking required dependencies:\n")
    
    all_installed = True
    for module, package in dependencies:
        if not check_dependency(module, package):
            all_installed = False
    
    print("\n" + "="*60)
    if all_installed:
        print("✓ ALL DEPENDENCIES INSTALLED")
        print("="*60)
        print("\nYou can now run:")
        print("  - Backend: python backend/main.py")
        print("  - CLI: prism --help")
        print("  - Tests: pytest tests/")
        return 0
    else:
        print("✗ SOME DEPENDENCIES MISSING")
        print("="*60)
        print("\nRun: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
