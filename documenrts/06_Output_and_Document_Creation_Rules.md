# OUTPUT AND DOCUMENT CREATION RULES

**Document ID:** doc_31fc6b7606b2871e  
**Version:** 1.0  
**Status:** active  
**Priority:** critical

---

SUMMARY: Defines rules for output brevity and document creation. Only create documents when explicitly requested. Keep all output short, focused, and minimal.

DOCUMENT CREATION RULES:

Rule 1: No Documents Unless Requested
- Do NOT create documents automatically
- Provide summaries and information directly in conversation
- Only create documents when user explicitly says "write a document" or "create a document"
- Avoid wasting credits, tokens, and time on unnecessary documents

Rule 2: Keep Output Short and Focused
- Provide minimum required information
- Avoid 100+ line summaries
- Focus on what is important
- Be concise and narrow in scope
- High-level summaries only

Rule 3: Document Format When Needed
- Follow Qdrant document template format by default
- Use structure: Title (UPPERCASE) → Summary → Sections → Metadata
- Include complete metadata for Qdrant storage
- Store in Qdrant as primary storage

OUTPUT GUIDELINES:

Conversation Output:
- Short, focused responses
- High-level summaries
- Only essential information
- No unnecessary elaboration

Document Output (when requested):
- Follow Qdrant template format
- Title in UPPERCASE
- Summary at start (1-2 sentences)
- Sections with UPPERCASE headers
- Complete metadata structure

KEY PRINCIPLES:
1. Minimal output - only what's needed
2. No documents unless asked
3. Short, focused, narrow scope
4. Format follows template when documents are created
5. Store in Qdrant when documents are created

