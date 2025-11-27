Here is your **Final Requirements Document – Version 6**
Updated with:

* ✔ The 10 verified working models
* ✔ Removal of Qwen 2.5 Coder 32B
* ✔ Clean structure
* ✔ Simple, maintainable architecture
* ✔ User-driven escalation for Debugging Tool
* ✔ System-1 document management (document_id, conversation_id, parent_id)
* ✔ Follow-up functionality with automatic linking
* ✔ Multiple MongoDB instance support
* ✔ MCP server integration
* ✔ Document orchestrator system

This is now the **authoritative requirements specification** for your entire Research + Coding + Debugging + Architecture Toolkit project.

---

# **FINAL REQUIREMENTS DOCUMENT — VERSION 6**

**Project:** Research & Debugging Toolkit
**Goal:** Build a multi-model AI system that performs topic research, coding research, debugging analysis, architectural design, and general-purpose reasoning — with clean storage, simple pre-processing, and future-proof vector integration.

---

# **1. Toolset Overview**

The system provides 5 AI tools:

1. **Topic Research Tool**

   * High-level topic understanding
   * Definitions, fundamentals, terminology

2. **Coding Research Tool**

   * Best coding patterns
   * Implementation guides
   * Edge cases, pitfalls

3. **Debugging Tool**

   * Takes failing code + explanation
   * Analyzes root cause
   * **User-driven escalation** (waits for user trigger, no automatic prompts)
   * Does NOT generate code — only deep reasoning

4. **Architecture & Design Tool**

   * Helps design flows, frameworks, and system layouts
   * Identifies critical hotspots

5. **General Purpose Tool**

   * For queries that don’t fall under any category

Each tool always returns **clean markdown**, stored exactly as received.

---

# **2. Final Model List (Verified Working Set)**

These model IDs are **100% tested and working** with your Abacus RouteLLM account.

## **Low-Cost / Lightweight Models**

Used for small tasks, simple research, cheap queries.

```
gpt-5-nano
gpt-4.1-nano
gpt-4o-mini
gemini-2.5-flash
```

## **Standard Reasoning Models**

Used for topic research, structured thinking, moderate coding analysis.

```
gpt-5
claude-sonnet-4-20250514
meta-llama/Meta-Llama-3.1-8B-Instruct
```

## **Heavy Reasoning / Debugging / Architecture**

Used when deep logic, multi-step reasoning, or root cause analysis is needed.

```
deepseek/deepseek-v3.1
deepseek-ai/DeepSeek-V3.1-Terminus
meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8
```

## **Removed Model**

❌ `qwen-2.5-coder-32b` (requires dedicated hosting; excluded)

---

# **3. Model Routing Strategy**

## **Topic Research Tool**

* Primary: `gemini-2.5-flash`
* Backup: `gpt-4o-mini`
* For large conceptual topics: `gpt-5`

## **Coding Research Tool**

* Simple coding insight → `meta-llama/Meta-Llama-3.1-8B-Instruct`
* Moderate to heavy coding logic → `deepseek/deepseek-v3.1`
* Deep contextual examples → `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8`

## **Debugging Tool (User-Driven Escalation)**

1. Tier-1: `deepseek-ai/DeepSeek-V3.1-Terminus` (initial call)
2. Tier-2: `deepseek/deepseek-v3.1` (if user triggers escalation)
3. Tier-3: `gpt-5` or `claude-sonnet-4-20250514` (if user triggers escalation)

**Escalation Rules:**
* System waits for user to initiate escalation (no automatic prompts)
* Trigger phrases: `["not working", "didn't work", "failed", "escalate", "tier 2", "tier2"]` (case-insensitive)
* Simple string matching for trigger detection
* Must preserve full context: original question + all previous tier outputs + user feedback
* Each tier output stored separately in MongoDB

## **Architecture & Design Tool**

* Primary: `claude-sonnet-4-20250514`
* Backup: `gpt-5`

## **General Purpose Tool**

* Default: `gpt-5-nano`
* If complexity rises: auto-upgrade to `gpt-4o-mini` or `gemini-2.5-flash`

---

# **4. Token Strategy (Dynamic Allocation)**

Tokens must be decided based on expected output length:

### **Small Queries**

* Expected: 200–1000 tokens
* Limit: 1500 tokens

### **Medium Queries**

* Expected: 2000–4000
* Limit: 5000

### **Large Queries**

* Expected: 5000–8000
* Limit: 10,000

### **Very Large Queries**

If output exceeds 10K, require continuation:

* “continue from previous message”

### **No Truncation Allowed**

If the system detects incomplete output:

* automatically refetch the missing part
* concatenate before storing

---

# **5. MongoDB Storage Layer (Source of Truth)**

Every AI response is stored **exactly as markdown**, no modifications.

## **Document Structure**

### **System-1 Metadata Fields (New Format)**

```
{
    // System-1 metadata (primary identifiers)
    document_id: "TR-20251127-112619-ABD31",
    conversation_id: "CV-20251127-112619-ABD31",
    parent_id: "<parent_document_id> | null",
    content_type: "text | code",
    
    // Core content
    question: "<raw user question>",
    markdown_content: "<exact markdown response>",
    
    // Legacy fields (backward compatibility)
    question_id: "TR-20251126-105433IST-WED-QX18",
    timestamp_ist: "2025-11-26 10:54:33 IST (Wednesday)",
    
    // Tool metadata
    category: "topic_research | coding_research | debugging | architecture | general",
    sub_category: "<optional>",
    model_used: "<model_name>",
    complexity_score: <1-10>,
    
    // Content analysis
    contains_code: true/false,
    estimated_segments: <int>,
    language_tags: ["python","javascript"],
    
    // Future vectorization (System-2)
    segments: [],
    vectors: [],
    graph_nodes: [],
    graph_edges: []
}
```

### **Document ID Formats**

**New Format (System-1)**:
- `document_id`: `{TOOL_PREFIX}-{YYYYMMDD}-{HHMMSS}-{SHORT_ID}`
  - Example: `TR-20251127-112619-ABD31`
  - Generated by: `MetadataBuilder` (5-character UUID hex)

**Legacy Format (Backward Compatibility)**:
- `question_id`: `{TOOL_PREFIX}-{YYYYMMDD}-{HHMMSS}IST-{DAY}-{RANDOM_SUFFIX}`
  - Example: `TR-20251126-105433IST-WED-QX18`
  - Generated by: `generate_question_id()` function

### **Conversation Threading**

- `conversation_id`: Links all documents in the same conversation thread
  - Format: `CV-{YYYYMMDD}-{HHMMSS}-{SHORT_ID}`
  - Root query: Creates new conversation_id
  - Follow-up: Inherits parent's conversation_id

### **Parent-Child Relationships**

- `parent_id`: Points to parent document (null for root queries)
- Enables traversing conversation history
- Documents form a tree structure

## **Timestamp Format**

Always in Indian Standard Time:

```
YYYY-MM-DD HH:MM:SS IST (DAY_OF_WEEK)
```

Example:

```
2025-11-26 10:54:33 IST (Wednesday)
```

---

# **6. Pre-Processing & Vectorization (Future Phase)**

### **Step 1 — Load raw markdown from Mongo**

Do not alter markdown.

### **Step 2 — Split into segments**

* TEXT → outside ``` blocks
* CODE → inside ``` blocks
* Mixed content becomes multiple segments

### **Step 3 — Embed**

Use two vector dimensions only:

### **Text Embedding**

* Dimension: **384**
* Distance: cosine

### **Code Embedding**

* Dimension: **768**
* Distance: cosine

### **Step 4 — Store segments**

Each segment gets:

```
segment_id
question_id
segment_type (text/code)
serial_number (1,2,3...)
content (snippet)
embedding_dimension (384 or 768)
```

### **Step 5 — Link**

All segments link via:

```
question_id + serial_number
```

No complex graph logic for now.

---

# **7. Follow-Up System**

## **7.1 Follow-Up Functionality**

The system supports automatic linking of follow-up questions to previous research:

**Automatic Follow-Up Linking:**
- When `follow_up=True` flag is set, system automatically uses last saved document as parent
- In-memory `FollowUpMemory` tracks last `document_id` and `conversation_id`
- If explicit `parent_id` is provided, it takes precedence over automatic linking

**Follow-Up Memory:**
- After each successful save, system updates in-memory tracking
- Queries MongoDB for most recent document (sorted by `_id` descending)
- Extracts `document_id` (or `question_id` for backward compatibility)
- Extracts `conversation_id`
- Updates global follow-up memory instance

**Parent Document Loading:**
- When `parent_id` is provided, system loads parent document from MongoDB
- Checks both `document_id` (new format) and `question_id` (legacy format)
- Parent's `conversation_id` is inherited by child document
- Child's `parent_id` points to parent's `document_id`

## **7.2 Follow-Up Workflow**

1. **Initial Query**: User asks research question
   - Document saved with new `document_id` and `conversation_id`
   - Follow-up memory updated

2. **Follow-Up Query**: User asks follow-up question
   - System checks `follow_up=True` flag
   - Uses `_followup_memory.last_document_id` if no explicit `parent_id`
   - Loads parent document from MongoDB
   - Creates child document with:
     - `parent_id`: Points to parent's `document_id`
     - `conversation_id`: Inherits from parent (maintains thread)
     - `document_id`: New unique ID

3. **Conversation Threading**: All documents in same conversation share `conversation_id`

---

# **8. Multiple MongoDB Instance Support**

The system supports multiple MongoDB instances for different environments:

**Instance Configuration:**
- Instances loaded from environment variables
- Format: `MONGODB_INSTANCE_{NAME}_URI`, `MONGODB_INSTANCE_{NAME}_DB`, `MONGODB_INSTANCE_{NAME}_COLLECTION`
- Default instance: `MONGODB_CONNECTION_STRING`, `MONGODB_DATABASE`, `MONGODB_COLLECTION`

**Instance Management:**
- Runtime switching between instances via `switch_mongodb_instance()`
- Active instance tracked globally
- All operations use active instance
- Supports primary, secondary, and custom named instances

**Use Cases:**
- Primary: Production database
- Secondary: Backup or alternative database
- Development: Local or test database

---

# **9. Question Identification Rules**

Each question must be uniquely identifiable.

Format:

```
<TOOL_PREFIX>-<YYYYMMDD>-<HHMMSS>IST-<DAY>-<RANDOM_SUFFIX>
```

Example:

```
CR-20251126-183212IST-WED-AX39
```

---

# **10. Simplicity & Maintainability Rules**

* Do NOT over-engineer
* Do NOT rewrite API responses
* Do NOT mix text/code
* Do NOT modify markdown
* MongoDB is always the **ground truth**
* Qdrant and Knowledge Graph are **derived indexes**
* Pre-processing must be clean and predictable
* Adding new tools/models must not break the pipeline

---

# **11. Overall Workflow**

### **Step 1** — User asks a question (via MCP server)

### **Step 2** — MCP server routes to appropriate tool class

### **Step 3** — Router selects the correct model based on complexity

### **Step 4** — Tool processes the query via API client

### **Step 5** — Document orchestrator builds document with metadata:
   - Generate document_id and conversation_id
   - Load parent document if follow-up
   - Detect content_type (text/code)
   - Merge all fields

### **Step 6** — Save raw markdown into MongoDB (via MongoWriter)
   - Validate database/collection
   - Check for duplicate document_id
   - Insert document

### **Step 7** — Update follow-up memory (in-memory tracking)

### **Step 8** — Return response to user

### **Step 9** — Later run pre-processing to extract segments (System-2)

### **Step 10** — Embed segments

### **Step 11** — Store vectors and metadata

### **Step 12** — Use vector store / graph for future intelligent referencing

---

# **12. MCP Server Integration**

The system exposes all tools via MCP (Model Context Protocol) server:

**MCP Protocol:**
- JSON-RPC 2.0 over stdio
- Protocol version: 2024-11-05
- Server name: research-toolkit

**Exposed Tools:**
- `topic_research`: Research topics and concepts
- `coding_research`: Research coding patterns and best practices
- `debugging`: Analyze failing code with root cause analysis
- `architecture`: Design system architecture and flows
- `general_purpose`: General purpose queries
- `list_mongodb_instances`: List available MongoDB instances
- `get_active_mongodb_instance`: Get current active instance
- `switch_mongodb_instance`: Switch to different MongoDB instance

**Tool Parameters:**
- All research tools support `follow_up` flag for automatic linking
- All research tools support `parent_id` for explicit parent linking
- All research tools support `save_to_db` flag (default: true)

---

# **13. Document Orchestration System**

The system uses a layered document orchestration approach:

**DocumentOrchestrator:**
- Coordinates the full save pipeline
- Loads parent documents when needed
- Calls DocumentAssembler to build document
- Calls MongoWriter to save to database

**DocumentAssembler:**
- Builds final document structure
- Extracts parent information
- Calls MetadataBuilder for System-1 metadata
- Merges all fields (new + legacy)

**MetadataBuilder:**
- Generates System-1 metadata fields
- Creates conversation_id (inherits or new)
- Creates document_id (unique)
- Detects content_type (text/code)
- Sets parent_id

**MongoWriter:**
- Handles MongoDB operations
- Validates database/collection existence
- Prevents duplicate document_id
- Inserts documents

---

# **14. Error Handling Requirements**

The system must handle errors gracefully:

**Parent Document Not Found:**
- If `parent_id` is provided but document doesn't exist, raise `ValueError`
- Error message must clearly indicate parent document not found
- Save operation must fail gracefully (no partial saves)

**Duplicate Document IDs:**
- System must detect if `document_id` already exists before insertion
- Raise `ValueError` with duplicate ID message if detected
- Prevent accidental overwrites of existing documents

**Memory Update Failures:**
- Follow-up memory updates are non-critical
- If memory update fails, exception must be silently caught
- System must continue normally even if memory update fails
- Next query may not have follow-up memory (acceptable behavior)

**MongoDB Connection Failures:**
- System must validate database and collection exist before operations
- Connection failures must raise appropriate exceptions
- Error messages must be clear and actionable

**Backward Compatibility:**
- System must support both `document_id` (new) and `question_id` (legacy) formats
- When loading parents, check both formats
- Legacy documents must remain accessible

---

# **END OF FINAL DRAFT — VERSION 6**

This is now your full, final, stable blueprint with System-1 implementation complete.

**Implemented Features:**
* ✅ All 5 research tools
* ✅ Model routing with 10 verified models
* ✅ MongoDB storage with System-1 metadata
* ✅ Follow-up functionality with automatic linking
* ✅ Multiple MongoDB instance support
* ✅ MCP server integration
* ✅ Document orchestration system
* ✅ Backward compatibility with legacy question_id format

**Future Work (System-2):**
* ⏳ Pre-processing and segment extraction
* ⏳ Vector embedding (384 for text, 768 for code)
* ⏳ Qdrant vector store integration
* ⏳ Knowledge graph construction
