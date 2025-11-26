Here is your **Final Requirements Document – Version 5**
Updated with:

* ✔ The 10 verified working models
* ✔ Removal of Qwen 2.5 Coder 32B
* ✔ Clean structure
* ✔ Simple, maintainable architecture
* ✔ User-driven escalation for Debugging Tool

This is now the **authoritative requirements specification** for your entire Research + Coding + Debugging + Architecture Toolkit project.

---

# **FINAL REQUIREMENTS DOCUMENT — VERSION 5**

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

```
{
    question: "<raw user question>",

    markdown_content: "<exact markdown response>",

    category: "topic_research | coding_research | debugging | architecture | general",
    sub_category: "<optional>",

    question_id: "TR-20251126-105433IST-WED-QX18",

    timestamp_ist: "2025-11-26 10:54:33 IST (Wednesday)",

    model_used: "<model_name>",
    complexity_score: <1-10>,

    contains_code: true/false,
    estimated_segments: <int>,
    language_tags: ["python","javascript"],

    // for future vectorization
    segments: [],
    vectors: [],
    graph_nodes: [],
    graph_edges: []
}
```

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

# **7. Question Identification Rules**

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

# **8. Simplicity & Maintainability Rules**

* Do NOT over-engineer
* Do NOT rewrite API responses
* Do NOT mix text/code
* Do NOT modify markdown
* MongoDB is always the **ground truth**
* Qdrant and Knowledge Graph are **derived indexes**
* Pre-processing must be clean and predictable
* Adding new tools/models must not break the pipeline

---

# **9. Overall Workflow**

### **Step 1** — User asks a question

### **Step 2** — Router selects the correct model

### **Step 3** — Tool processes the query

### **Step 4** — Save raw markdown into MongoDB

### **Step 5** — Later run pre-processing to extract segments

### **Step 6** — Embed segments

### **Step 7** — Store vectors and metadata

### **Step 8** — Use vector store / graph for future intelligent referencing

---

# **END OF FINAL DRAFT — VERSION 5**

This is now your full, final, stable blueprint.

If you want next:

* **Model Router Implementation**
* **Folder Structure**
* **Mongo Schema File**
* **Python Client Setup**

Just tell me.
