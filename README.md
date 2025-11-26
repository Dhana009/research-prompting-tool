# Research Prompting Tool

A comprehensive multi-model AI research toolkit for topic research, coding research, debugging analysis, architectural design, and general-purpose reasoning. Built with MongoDB storage and MCP (Model Context Protocol) server integration.

## 🚀 Features

- **5 AI Research Tools**: 
  - Topic Research - High-level understanding, definitions, and fundamentals
  - Coding Research - Patterns, best practices, implementation guides
  - Debugging - Root cause analysis with tier-based escalation
  - Architecture - System design, flows, and frameworks
  - General Purpose - Auto-upgrading queries for various tasks

- **10 Verified AI Models**: Optimized routing based on task complexity
- **MongoDB Storage**: Persistent storage with multi-instance support
- **MCP Server Integration**: Use directly from Cursor IDE
- **Test-Driven Development**: Comprehensive test coverage
- **Flexible Configuration**: Support for multiple MongoDB instances

## 📋 Requirements

- Python 3.8+
- MongoDB (local or cloud instance)
- RouteLLM API key

## 🛠️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Dhana009/research-prompting-tool.git
cd research-prompting-tool
```

### 2. Install Dependencies

```bash
cd research_toolkit
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file:

```bash
cp research_toolkit/.env.example research_toolkit/.env
```

Update `research_toolkit/.env` with your credentials:

```env
ROUTELLM_API_KEY=your-api-key
ROUTELLM_API_URL=https://routellm.abacus.ai/v1
MONGODB_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE=research_toolkit
MONGODB_COLLECTION=research_documents
```

### 4. Run Tests

```bash
cd research_toolkit
pytest
```

## 📁 Project Structure

```
research-prompting-tool/
├── research_toolkit/          # Main toolkit package
│   ├── src/
│   │   ├── models/            # Question IDs, document schemas
│   │   ├── storage/           # MongoDB operations
│   │   ├── router/            # Model selection logic
│   │   ├── tools/             # AI tools (5 tools)
│   │   ├── utils/             # Token management, output handling
│   │   ├── cli/               # Command-line interface
│   │   └── mcp_server.py      # MCP server implementation
│   ├── tests/                 # Test suite
│   │   ├── unit/              # Unit tests
│   │   ├── integration/       # Integration tests
│   │   └── fixtures/          # Test fixtures
│   ├── requirements.txt       # Python dependencies
│   └── README.md              # Toolkit-specific documentation
├── documenrts/                # Research documentation
├── requirements/              # Project requirements
└── README.md                  # This file
```

## 🔧 MCP Server Setup

The toolkit includes an MCP server for integration with Cursor IDE. See [research_toolkit/MCP_SETUP.md](research_toolkit/MCP_SETUP.md) for detailed setup instructions.

### Quick MCP Setup

1. Add to your `mcp.json` (Cursor config):

```json
{
  "mcpServers": {
    "research-toolkit": {
      "command": "python",
      "args": ["path/to/research_toolkit/src/mcp_server.py"],
      "env": {
        "ROUTELLM_API_KEY": "your-api-key",
        "ROUTELLM_API_URL": "https://routellm.abacus.ai/v1",
        "MONGODB_CONNECTION_STRING": "mongodb+srv://...",
        "MONGODB_DATABASE": "research_toolkit",
        "MONGODB_COLLECTION": "research_documents"
      }
    }
  }
}
```

2. Restart Cursor
3. Use the tools from the MCP panel

## 📚 Documentation

- [Toolkit README](research_toolkit/README.md) - Detailed toolkit documentation
- [MCP Setup Guide](research_toolkit/MCP_SETUP.md) - MCP server configuration
- [MongoDB Configuration](research_toolkit/MCP_MONGODB_CONFIG.md) - Multi-instance MongoDB setup
- [Requirements](requirements/final_draft_requirements.md) - Complete requirements specification

## 🧪 Usage Examples

### Topic Research

```python
from research_toolkit.src.tools.topic_research import TopicResearchTool

tool = TopicResearchTool()
result = tool.research(
    question="What is test-driven development?",
    complexity="simple"
)
```

### Coding Research

```python
from research_toolkit.src.tools.coding_research import CodingResearchTool

tool = CodingResearchTool()
result = tool.research(
    question="How do you write unit tests in Python using pytest?",
    complexity="simple"
)
```

### Debugging Analysis

```python
from research_toolkit.src.tools.debugging import DebuggingTool

tool = DebuggingTool()
result = tool.debug(
    code="def calculate_total(items): ...",
    explanation="Function returns incorrect totals",
    tier=1
)
```

## 🔄 MongoDB Multi-Instance Support

The toolkit supports multiple MongoDB instances with runtime switching. See [MCP_MONGODB_CONFIG.md](research_toolkit/MCP_MONGODB_CONFIG.md) for configuration details.

## 🧩 Development

This project follows Test-Driven Development (TDD):

1. **RED**: Write failing tests
2. **GREEN**: Implement to pass tests
3. **REFACTOR**: Improve code quality
4. Repeat

## 📝 License

This project is open source and available for use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Repository**: [https://github.com/Dhana009/research-prompting-tool](https://github.com/Dhana009/research-prompting-tool)

