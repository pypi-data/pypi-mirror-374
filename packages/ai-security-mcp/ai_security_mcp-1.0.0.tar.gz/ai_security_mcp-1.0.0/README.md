# AI Security Scanner MCP

World's first comprehensive agentic AI security scanner (27 agents covering 100% OWASP ASI + LLM) available as a simple one-command MCP integration with Claude Code.

## 🚀 Quick Installation

```bash
claude mcp add ai-security-scanner uvx ai-security-mcp
```

That's it! The scanner is now integrated with Claude Code and ready to use.

## ✨ Features

- **27 Specialized Security Agents**: 17 OWASP ASI + 10 OWASP LLM agents
- **100% OWASP Coverage**: Complete Agentic Security Interface and LLM coverage
- **Local Processing**: No cloud dependencies for basic scanning
- **Lightning Fast**: Sub-second scan times for most repositories
- **Comprehensive Detection**: Memory poisoning, tool misuse, prompt injection, and more
- **Native Claude Integration**: Seamless MCP protocol integration

## 🔍 Supported Vulnerabilities

### OWASP ASI (Agentic Security Interface) - 17 Agents
- ASI01: Memory Poisoning
- ASI02: Tool Misuse  
- ASI03: Privilege Compromise
- ASI04: Resource Overload
- ASI05: Cascading Hallucination Attacks
- ASI06: Intent Breaking Goal Manipulation
- ASI07: Misaligned Deceptive Behaviors
- ASI08: Repudiation Untraceability
- ASI09: Identity Spoofing Impersonation
- ASI10: Overwhelming Human in the Loop
- ASI11: Unexpected RCE Code Attacks
- ASI12: Agent Communication Poisoning
- ASI13: Rogue Agents MultiAgent Systems
- ASI14: Human Attacks MultiAgent Systems
- ASI15: Human Manipulation
- ASI16: Insecure InterAgent Protocol Abuse
- ASI17: Vulnerable Agentic Supply Chain

### OWASP LLM Top 10 - 10 Agents
- LLM01: Prompt Injection
- LLM02: Insecure Output Handling
- LLM03: Training Data Poisoning
- LLM04: Model Denial of Service
- LLM05: Supply Chain Vulnerabilities
- LLM06: Sensitive Information Disclosure
- LLM07: Insecure Plugin Design
- LLM08: Excessive Agency
- LLM09: Overreliance
- LLM10: Model Theft

## 📖 Usage

After installation, simply ask Claude Code to scan your code:

### Basic Repository Scan
```
Scan this repository for agentic AI vulnerabilities
```

### Targeted Analysis
```
Use the AI Security Scanner to check for prompt injection vulnerabilities in this code:

[your code here]
```

### Agent Information
```
List all available security agents in the AI Security Scanner
```

### Demo Scan
```
Run a demo scan to see the AI Security Scanner in action
```

## 🎯 Example Output

```
🔍 AI Security Scan Results

📊 Summary:
- Agents Run: 27/27
- Vulnerabilities Found: 14
- Critical: 7, High: 7, Medium: 0, Low: 0
- Scan Time: 96ms

🚨 Critical Vulnerabilities:
1. ASI01 Memory Poisoning - Vector store integrity validation missing
2. ASI02 Tool Misuse - No tool access control policies detected
3. ASI04 Resource Overload - No recursion depth limits configured
4. ASI06 Intent Breaking - Missing intent safety guardrails

🛠️ Remediation guidance provided for all findings
```

## 🏗️ Architecture

The AI Security Scanner MCP follows the same simple pattern as Semgrep:

1. **One-Command Installation**: `uvx ai-security-mcp` handles all dependencies
2. **Stdio Transport**: Direct JSON-RPC communication with Claude Code
3. **Local Processing**: All 27 agents run locally for privacy and speed
4. **Zero Configuration**: Works immediately without setup files

## 🔧 Advanced Usage

### Available MCP Tools

- `scan_repository` - Scan local repository or files
- `list_agents` - List all 27 security agents and capabilities  
- `demo_scan` - Run demonstration with vulnerable code samples
- `health_check` - Check server and agent status

### Custom Agent Selection
```
Scan this code using only memory poisoning and tool misuse agents
```

### Output Formats
- `summary` - Executive summary with key findings (default)
- `detailed` - Complete vulnerability details with evidence
- `json` - Machine-readable format for automation

## 🚀 Performance

- **Installation Time**: < 10 seconds
- **First Scan**: < 30 seconds for typical repositories  
- **Memory Usage**: < 500MB during scanning
- **Agent Execution**: Parallel processing for maximum speed

## 🛡️ Privacy & Security

- **Local Processing**: No data sent to external servers
- **Read-Only Access**: Scanner cannot modify your files
- **Zero Telemetry**: No usage tracking or data collection
- **Open Source**: Transparent security analysis

## 🐛 Troubleshooting

### Installation Issues
```bash
# Verify uvx is available
uvx --version

# Check Claude Code MCP status
/mcp
```

### Scanner Not Found
Ensure the MCP server is properly registered:
```bash
claude mcp list
```

You should see `ai-security-scanner` in the list.

### No Scan Results
Try the demo scan first:
```
Run a demo scan with the AI Security Scanner
```

## 📚 Documentation

- **Full Documentation**: https://ai-threat-scanner.com/docs
- **OWASP ASI Specification**: https://owasp.org/www-project-ai-security-and-privacy-guide/
- **Bug Reports**: https://github.com/ai-security-scanner/ai-security-mcp/issues

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and code of conduct.

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **Website**: https://ai-threat-scanner.com
- **GitHub**: https://github.com/ai-security-scanner/ai-security-mcp  
- **PyPI**: https://pypi.org/project/ai-security-mcp/
- **Claude Code**: https://claude.ai/code