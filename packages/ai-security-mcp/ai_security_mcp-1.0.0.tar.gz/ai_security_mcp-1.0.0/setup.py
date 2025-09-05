#!/usr/bin/env python3
"""
AI Security MCP - Setup Configuration
PyPI package for one-command MCP installation like Semgrep
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else """
# AI Security Scanner MCP

Thin client MCP server for world's first comprehensive agentic AI security scanner (27 cloud-hosted agents covering 100% OWASP ASI + LLM).

## Quick Installation

```bash
claude mcp add ai-security-scanner -e AI_SECURITY_API_KEY=your_key_here -- uvx ai-security-mcp
```

## Thin Client Architecture

- **Lightweight local client**: No proprietary agent code included
- **Secure cloud processing**: All 27 agents run on protected cloud infrastructure  
- **API key authentication**: Uses AI_SECURITY_API_KEY environment variable
- **Fallback support**: Demo mode when cloud unavailable
- **Privacy focused**: Only MCP communication happens locally

## Features

- 27 specialized security agents (17 ASI + 10 LLM) running on cloud
- 100% OWASP ASI + LLM coverage via cloud processing
- Thin client design protects proprietary IP
- Sub-second response times from cloud infrastructure
- Comprehensive vulnerability detection via cloud agents
- Integration with Claude Code via MCP protocol

## Usage

After installation with your API key, simply ask Claude Code:

```
Scan this repository for agentic AI vulnerabilities
```

The thin client connects to our cloud infrastructure where all 27 security agents analyze your code and return comprehensive findings.
"""

setup(
    name="ai-security-mcp",
    version="1.0.0",
    author="AI Security Team",
    author_email="security@ai-threat-scanner.com",
    description="Thin client MCP server for AI Security Scanner - connects to cloud-hosted 27 agents (100% OWASP coverage)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-security-scanner/ai-security-mcp",
    project_urls={
        "Bug Reports": "https://github.com/ai-security-scanner/ai-security-mcp/issues",
        "Source": "https://github.com/ai-security-scanner/ai-security-mcp",
        "Documentation": "https://ai-threat-scanner.com/docs",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "asyncio",
        "pathlib",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "full": [
            "rich>=13.0.0",  # For beautiful console output
            "colorama>=0.4.6",  # For cross-platform colored output
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-security-mcp=ai_security_mcp.main:main",
            "ai-security-scanner=ai_security_mcp.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_security_mcp": [
            "agents/*.py",
            "utils/*.py",
            "*.py",
        ],
    },
    keywords=[
        "security", "ai", "agentic", "llm", "owasp", "vulnerability", "scanner", 
        "mcp", "claude", "claude-code", "agent", "multi-agent", "asi", "prompt-injection",
        "cybersecurity", "devsecops", "static-analysis", "security-testing"
    ],
    platforms=["any"],
    zip_safe=False,
    # Metadata for PyPI
    license="MIT",
    maintainer="AI Security Team",
    maintainer_email="security@ai-threat-scanner.com",
)