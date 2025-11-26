# Research Prompting Tool - Complete Reference

**Version:** 1.0  
**Last Updated:** 2025-01-XX  
**Repository:** https://github.com/Dhana009/research-prompting-tool

---

## 1. Infrastructure Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────┐
│         Cursor IDE / MCP Client          │
└─────────────────┬─────────────────────────┘
                  │ JSON-RPC 2.0 (stdio)
┌─────────────────▼─────────────────────────┐
│         MCP Server (Python)               │
│  ┌─────────────────────────────────────┐ │
│  │  5 Research Tools                    │ │
│  │  • Topic Research                   │ │
│  │  • Coding Research                   │ │
│  │  • Debugging                        │ │
│  │  • Architecture                     │ │
│  │  • General Purpose                  │ │
│  └──────────────┬──────────────────────┘ │
│                 │                         │
│  ┌──────────────▼──────────────────────┐ │
│  │  Model Router                       │ │
│  │  (10 Verified Models)              │ │
│  └──────────────┬──────────────────────┘ │
│                 │                         │
│  ┌──────────────▼──────────────────────┐ │
│  │  RouteLLM API Client                │ │
│  └──────────────┬──────────────────────┘ │
└─────────────────┼─────────────────────────┘
                  │
┌─────────────────▼─────────────────────────┐
│      MongoDB (Multi-Instance Support)      │
│  • Default / Primary / Secondary          │
│  • Runtime Switching                      │
└───────────────────────────────────────────┘
```

### 1.2 Technology Stack

- **Language:** Python 3.8+
- **Protocol:** MCP (Model Context Protocol) v2024-11-05
- **Database:** MongoDB (Atlas or self-hosted)
- **API:** RouteLLM (Abacus AI)
- **Communication:** stdio (standard input/output)

### 1.3 Dependencies

```
pymongo>=4.6.0
pytest>=7.4.0
pytest-cov>=4.1.0
python-dotenv>=1.0.0
pydantic>=2.5.0
openai>=1.0.0
pytz>=2023.3
```

---

## 2. MongoDB Schema

### 2.1 Document Structure

```json
{
  "_id": "ObjectId",
  "question": "Raw user question string",
  "markdown_content": "Exact markdown response from AI (unmodified)",
  "category": "topic_research | coding_research | debugging | architecture | general",
  "sub_category": "Optional sub-category string",
  "question_id": "TR-20251126-105433IST-WED-QX18",
  "timestamp_ist": "2025-11-26 10:54:33 IST (Wednesday)",
  "model_used": "gemini-2.5-flash",
  "complexity_score": 3,
  "contains_code": true,
  "estimated_segments": 5,
  "language_tags": ["python", "javascript"],
  "segments": [],
  "vectors": [],
  "graph_nodes": [],
  "graph_edges": []
}
```

### 2.2 Field Specifications

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | Yes | Raw user input |
| `markdown_content` | string | Yes | Unmodified AI response |
| `category` | enum | Yes | Tool category |
| `sub_category` | string | No | Optional classification |
| `question_id` | string | Yes | Unique identifier (see format below) |
| `timestamp_ist` | string | Yes | IST format: `YYYY-MM-DD HH:MM:SS IST (DAY)` |
| `model_used` | string | Yes | Model identifier |
| `complexity_score` | int | Yes | 1-10 scale |
| `contains_code` | bool | Yes | Code detection flag |
| `estimated_segments` | int | Yes | Segment count estimate |
| `language_tags` | array | Yes | Detected languages |
| `segments` | array | Yes | Future vectorization |
| `vectors` | array | Yes | Future embeddings |
| `graph_nodes` | array | Yes | Future knowledge graph |
| `graph_edges` | array | Yes | Future graph edges |

### 2.3 Question ID Format

```
<TOOL_PREFIX>-<YYYYMMDD>-<HHMMSS>IST-<DAY>-<RANDOM>
```

**Examples:**
- `TR-20251126-105433IST-WED-QX18` (Topic Research)
- `CR-20251126-183212IST-WED-AX39` (Coding Research)
- `DB-20251126-091500IST-WED-MN72` (Debugging)
- `AR-20251126-143022IST-WED-KL45` (Architecture)
- `GP-20251126-160845IST-WED-PQ89` (General Purpose)

**Tool Prefixes:**
- `TR` = Topic Research
- `CR` = Coding Research
- `DB` = Debugging
- `AR` = Architecture
- `GP` = General Purpose

### 2.4 Database Configuration

**Default Collection:** `research_documents`  
**Default Database:** `research_toolkit`

**Multi-Instance Support:**
- Each instance can have different database/collection names
- Runtime switching without server restart
- Instance names are case-insensitive

---

## 3. Requirements & Specifications

### 3.1 Five Research Tools

| Tool | Purpose | Output |
|------|---------|--------|
| **Topic Research** | High-level understanding, definitions, fundamentals | Clean markdown |
| **Coding Research** | Patterns, best practices, implementation guides | Clean markdown |
| **Debugging** | Root cause analysis (no code generation) | Clean markdown |
| **Architecture** | System design, flows, frameworks | Clean markdown |
| **General Purpose** | Queries outside other categories | Clean markdown |

### 3.2 Verified Models (10 Total)

**Low-Cost / Lightweight:**
- `gpt-5-nano`
- `gpt-4.1-nano`
- `gpt-4o-mini`
- `gemini-2.5-flash`

**Standard Reasoning:**
- `gpt-5`
- `claude-sonnet-4-20250514`
- `meta-llama/Meta-Llama-3.1-8B-Instruct`

**Heavy Reasoning:**
- `deepseek/deepseek-v3.1`
- `deepseek-ai/DeepSeek-V3.1-Terminus`
- `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8`

### 3.3 Model Routing Strategy

| Tool | Complexity/Tier | Primary Model | Backup Model |
|------|----------------|---------------|--------------|
| Topic Research | simple | `gemini-2.5-flash` | `gpt-4o-mini` |
| Topic Research | large | `gpt-5` | - |
| Coding Research | simple | `meta-llama/Meta-Llama-3.1-8B-Instruct` | - |
| Coding Research | moderate | `deepseek/deepseek-v3.1` | - |
| Coding Research | deep | `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | - |
| Debugging | Tier 1 | `deepseek-ai/DeepSeek-V3.1-Terminus` | - |
| Debugging | Tier 2 | `deepseek/deepseek-v3.1` | - |
| Debugging | Tier 3 | `gpt-5` or `claude-sonnet-4-20250514` | - |
| Architecture | default | `claude-sonnet-4-20250514` | `gpt-5` |
| General Purpose | simple | `gpt-5-nano` | - |
| General Purpose | medium | `gemini-2.5-flash` | - |

### 3.4 Token Strategy

| Query Size | Expected Tokens | Max Limit |
|------------|----------------|-----------|
| Small | 200-1,000 | 1,500 |
| Medium | 2,000-4,000 | 5,000 |
| Large | 5,000-8,000 | 10,000 |
| Very Large | >10,000 | Continuation required |

**Rules:**
- No truncation allowed
- Auto-refetch if incomplete
- Concatenate before storing

### 3.5 Debugging Escalation

**User-Driven Escalation:**
- System waits for user trigger (no auto-prompts)
- Trigger phrases: `["not working", "didn't work", "failed", "escalate", "tier 2", "tier2"]`
- Case-insensitive string matching
- Full context preservation across tiers

**Tier Flow:**
1. Tier 1 → Initial analysis
2. Tier 2 → User triggers escalation
3. Tier 3 → User triggers escalation
4. Each tier output stored separately

---

## 4. Configuration

### 4.1 Environment Variables

**Required:**
```env
ROUTELLM_API_KEY=your-api-key
ROUTELLM_API_URL=https://routellm.abacus.ai/v1
MONGODB_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DATABASE=research_toolkit
MONGODB_COLLECTION=research_documents
```

**Multi-Instance (Optional):**
```env
MONGODB_INSTANCE_PRIMARY_URI=mongodb+srv://...
MONGODB_INSTANCE_PRIMARY_DB=research_toolkit
MONGODB_INSTANCE_PRIMARY_COLLECTION=research_documents

MONGODB_INSTANCE_SECONDARY_URI=mongodb+srv://...
MONGODB_INSTANCE_SECONDARY_DB=research_toolkit_backup
MONGODB_INSTANCE_SECONDARY_COLLECTION=research_documents
```

### 4.2 MCP Server Configuration

**mcp.json:**
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

### 4.3 MCP Tools (8 Total)

**Research Tools (5):**
1. `topic_research` - Topic research queries
2. `coding_research` - Coding pattern research
3. `debugging` - Root cause analysis
4. `architecture` - System design queries
5. `general_purpose` - General queries

**MongoDB Management (3):**
6. `list_mongodb_instances` - List all instances
7. `get_active_mongodb_instance` - Get active instance
8. `switch_mongodb_instance` - Switch instance

---

## 5. Project Structure

```
research-prompting-tool/
├── research_toolkit/
│   ├── src/
│   │   ├── models/          # Document & Question schemas
│   │   ├── storage/          # MongoDB client
│   │   ├── router/          # Model routing logic
│   │   ├── tools/            # 5 research tools
│   │   ├── utils/            # API client, token manager
│   │   ├── cli/              # CLI interface
│   │   └── mcp_server.py     # MCP server entry point
│   ├── tests/                # Test suite
│   ├── requirements.txt      # Dependencies
│   └── README.md             # Toolkit docs
├── documenrts/               # Research documentation
├── requirements/             # Requirements specs
└── README.md                 # Project README
```

---

## 6. Key Principles

1. **MongoDB as Source of Truth** - Raw markdown stored unmodified
2. **No Response Modification** - AI responses stored exactly as received
3. **Future Vectorization** - Segments/vectors stored but not processed yet
4. **User-Driven Escalation** - Debugging waits for user triggers
5. **Simple & Maintainable** - No over-engineering
6. **Test-Driven Development** - TDD approach throughout

---

## 7. Quick Reference

**Question ID Format:** `<PREFIX>-<YYYYMMDD>-<HHMMSS>IST-<DAY>-<RANDOM>`  
**Timestamp Format:** `YYYY-MM-DD HH:MM:SS IST (DAY_OF_WEEK)`  
**Default Database:** `research_toolkit`  
**Default Collection:** `research_documents`  
**Protocol:** MCP v2024-11-05  
**Communication:** stdio (JSON-RPC 2.0)

---

**Document Version:** 1.0  
**Maintained By:** Research Prompting Tool Team  
**Last Updated:** 2025-01-XX

