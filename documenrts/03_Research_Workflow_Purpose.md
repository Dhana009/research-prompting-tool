# RESEARCH WORKFLOW: PURPOSE AND KEY DECISIONS

**Document ID:** doc_c8e5ead3801fb13b  
**Version:** 1.0  
**Status:** active  
**Priority:** critical

---

SUMMARY: Defines the core purpose of the research workflow and key decisions for storing critical information in Qdrant for easy retrieval when needed.

MAIN PURPOSE:

The research workflow exists to:
1. Extract key, actionable information from research
2. Reformat information following Qdrant template structure
3. Store in Qdrant with proper metadata for searchability
4. Enable easy retrieval when AI needs the information

CRITICAL DECISIONS:

Decision 1: What to Store
- Store all key information and critical decisions discussed
- Focus on actionable, essential information (not exam-level details)
- Store information that AI needs to remember and retrieve

Decision 2: When to Store
- Store immediately after research (extract → reformat → store)
- Store critical decisions as they are made
- Store workflow changes and strategy updates
- Store whenever important context is established

Decision 3: How to Store
- Always follow Qdrant document template format
- Use UPPERCASE section headers
- Include summary at start (1-2 sentences)
- Complete metadata structure (document_type, purpose, key_topics, version, status, priority)
- Ensure searchability with proper key_topics

Decision 4: Format Requirements
- Title in UPPERCASE
- Summary section first
- Sections with UPPERCASE headers
- Complete metadata for filtering and search
- Keep content focused and actionable

WORKFLOW:

Step 1: Research
- Use appropriate AI model based on complexity
- Extract key, actionable information
- Focus on what AI needs to know

Step 2: Extract
- Identify critical information
- Focus on essential, actionable content
- Remove unnecessary details

Step 3: Reformat
- Apply Qdrant template structure immediately
- Use UPPERCASE headers
- Add summary at start
- Structure for searchability

Step 4: Store
- Store in Qdrant with complete metadata
- Include proper key_topics for search
- Set appropriate category, document_type, purpose

Step 5: Retrieve
- Search Qdrant when information is needed
- Use semantic search with key topics
- Retrieve formatted, actionable information

KEY PRINCIPLE:

If we discuss something critical or make a key decision, it must be stored in Qdrant in proper format. This ensures:
- Information is not lost between sessions
- AI can retrieve context when needed
- Decisions are documented and searchable
- Workflow remains consistent

