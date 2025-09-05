#!/usr/bin/env python3
"""
AI Security MCP - Main Entry Point
Entry point for uvx execution: uvx ai-security-mcp
"""

import sys
import os

def main():
    """Main entry point for the AI Security MCP server"""
    
    # Add the parent directory to Python path to import from src/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    
    # Try to locate the main CISO_Agent directory
    possible_paths = [
        parent_dir,  # If installed in CISO_Agent/ai-security-mcp/
        os.path.join(parent_dir, 'CISO_Agent'),  # If in a different structure
        '/Users/david/Documents/GitHub/CISO_Agent',  # Development fallback
        os.path.expanduser('~/Documents/GitHub/CISO_Agent'),  # Home directory fallback
    ]
    
    main_repo_path = None
    for path in possible_paths:
        if os.path.exists(os.path.join(path, 'src', 'core', 'orchestrator.py')):
            main_repo_path = path
            break
    
    if not main_repo_path:
        print("Error: Could not locate CISO_Agent source code", file=sys.stderr)
        print("Please ensure ai-security-mcp is installed correctly", file=sys.stderr)
        sys.exit(1)
    
    if main_repo_path not in sys.path:
        sys.path.insert(0, main_repo_path)
    
    try:
        # Import and run the MCP server
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from server import MCPServer
        import asyncio
        
        server = MCPServer()
        asyncio.run(server.run_stdio())
        
    except KeyboardInterrupt:
        print("AI Security MCP Server stopped", file=sys.stderr)
    except Exception as e:
        print(f"Server failed to start: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()