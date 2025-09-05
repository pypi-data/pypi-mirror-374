"""
AI Security MCP - Agentic Security Scanner for Model Context Protocol

World's first comprehensive agentic AI security scanner with 27 specialized agents
covering 100% OWASP ASI (Agentic Security Interface) and LLM vulnerabilities.

Features:
- 27 specialized security agents (17 ASI + 10 LLM)
- 100% OWASP ASI + LLM coverage
- Local processing (no cloud dependencies for basic scanning)
- Sub-second scan times
- Comprehensive vulnerability detection with remediation guidance
- Native Claude Code integration via MCP protocol

Usage:
    After installation with `claude mcp add ai-security-scanner uvx ai-security-mcp`,
    simply ask Claude Code to scan your repository:
    
    "Scan this repository for agentic AI vulnerabilities"
    
    The scanner will automatically execute all 27 agents and provide detailed
    security findings with risk scores and remediation guidance.
"""

__version__ = "1.0.0"
__author__ = "AI Security Team"
__email__ = "security@ai-threat-scanner.com"
__license__ = "MIT"

# Package exports
from .server import MCPServer
from .main import main

__all__ = ["MCPServer", "main", "__version__"]