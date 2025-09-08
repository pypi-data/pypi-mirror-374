#!/usr/bin/env python3
"""
Central database locator for all Claude scripts
RULE: Local project DB or fail - no fallbacks allowed

Cross-platform support: Windows, macOS, Linux
Multi-project support: Works in any project with .claude directory
"""
from pathlib import Path
import sys
import os
import subprocess

def find_project_database():
    """
    Find project database with zero fallbacks
    
    Logic:
    1. Start from current working directory
    2. Search upward for .claude directory
    3. Verify project.db exists inside .claude/memory/
    4. Return paths or exit with detailed error
    
    Returns:
        tuple: (project_root_path, database_file_path)
    
    Exits:
        If no .claude directory found or database doesn't exist
    """
    # Start from current directory and resolve any symlinks
    current = Path.cwd().resolve()
    original_cwd = str(current)
    searched_paths = []
    home_dir = Path.home().resolve()
    
    # Search upward for .claude directory (but exclude home directory)
    while current != current.parent and current != home_dir:
        searched_paths.append(str(current))
        claude_dir = current / '.claude'
        
        # Check if .claude exists and is a directory
        if claude_dir.exists() and claude_dir.is_dir():
            db_path = claude_dir / 'memory' / 'project.db'
            
            # Verify database file exists
            if db_path.exists() and db_path.is_file():
                return current, db_path
            
            # .claude exists but no project.db
            _print_database_missing_error(current, claude_dir, db_path)
            
        current = current.parent
    
    # No .claude directory found anywhere
    _print_no_claude_error(original_cwd, searched_paths)

def _print_database_missing_error(project_root, claude_dir, expected_db):
    """Print detailed error when .claude exists but database is missing"""
    print("=" * 80, file=sys.stderr)
    print("ERROR: .claude directory found but database is missing", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(f"Project root found: {project_root}", file=sys.stderr)
    print(f".claude directory: {claude_dir}", file=sys.stderr)
    print(f"Expected database: {expected_db}", file=sys.stderr)
    print(f"Database exists: {expected_db.exists()}", file=sys.stderr)
    print("", file=sys.stderr)
    print("SOLUTION: Initialize database with:", file=sys.stderr)
    print(f"  uv run python ~/.claude/scripts/agent_db.py init", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    sys.exit(1)

def _print_no_claude_error(original_cwd, searched_paths):
    """Print detailed error when no .claude directory found"""
    print("=" * 80, file=sys.stderr)
    print("ERROR: No .claude project directory found", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(f"Started search from: {original_cwd}", file=sys.stderr)
    print(f"Operating system: {os.name} ({sys.platform})", file=sys.stderr)
    print(f"Home directory excluded: {Path.home()}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Searched directories:", file=sys.stderr)
    for i, path in enumerate(searched_paths, 1):
        print(f"  {i:2d}. {path}", file=sys.stderr)
    print("", file=sys.stderr)
    print("RULE: Local project database or fail - no fallbacks allowed", file=sys.stderr)
    print("", file=sys.stderr)
    print("SOLUTIONS:", file=sys.stderr)
    print("  1. Run from within a project directory containing .claude/", file=sys.stderr)
    print("  2. Initialize project with: mkdir -p .claude/memory", file=sys.stderr)
    print("  3. Create database with: uv run python ~/.claude/scripts/agent_db.py init", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    sys.exit(1)

def get_project_db_path():
    """
    Simple wrapper that returns just the database path
    
    Returns:
        Path: Database file path
    
    Exits:
        If database cannot be located
    """
    _, db_path = find_project_database()
    return db_path

def get_project_root():
    """
    Get the project root directory (contains .claude)
    
    Returns:
        Path: Project root directory path
    
    Exits:
        If project root cannot be located
    """
    project_root, _ = find_project_database()
    return project_root

def print_database_info():
    """
    Print detailed information about located database
    Useful for debugging and verification
    """
    try:
        project_root, db_path = find_project_database()
        
        print("Database Location Information:")
        print("=" * 50)
        print(f"Project root: {project_root}")
        print(f"Database path: {db_path}")
        print(f"Working directory: {Path.cwd()}")
        print(f"Database exists: {db_path.exists()}")
        if db_path.exists():
            stat = db_path.stat()
            print(f"Database size: {stat.st_size:,} bytes")
            print(f"Last modified: {stat.st_mtime}")
        print("=" * 50)
        
    except SystemExit:
        # Error already printed by find_project_database()
        pass

if __name__ == "__main__":
    # When run directly, show database info
    print_database_info()