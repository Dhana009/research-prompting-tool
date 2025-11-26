# QDRANT DOCUMENT STORAGE TEMPLATE

**Document ID:** doc_61eb2a5efabee003  
**Version:** 1.0  
**Status:** active  
**Priority:** critical

---

SUMMARY: Defines the standard format for storing documents in Qdrant to ensure easy semantic search and retrieval. Provides structure, metadata guidelines, and best practices for document organization.

DOCUMENT STRUCTURE TEMPLATE:

Format:
DOCUMENT TITLE: [Clear, Descriptive Title in UPPERCASE]

SUMMARY: [1-2 sentence summary of the document's purpose and key content]

[MAIN CONTENT ORGANIZED BY SECTIONS]

SECTION 1: [Section Title]
[Content with clear structure]

SECTION 2: [Section Title]
[Content with clear structure]

KEY POINTS:
- Point 1
- Point 2
- Point 3

EXAMPLES:
[Concrete examples if applicable]

---

METADATA STRUCTURE (for Qdrant payload):
{
  "doc_id": "doc_[unique_id]",
  "title": "Document Title",
  "category": "reference|research_summary|test_pattern|code_example|architecture_decision|other",
  "document_type": "tool_selection_strategy|research_findings|best_practices|workflow|template",
  "purpose": "cost_optimization|research_guidance|decision_support|implementation_guide",
  "key_topics": ["topic1", "topic2", "topic3"],
  "version": "1.0|2.0|etc",
  "status": "active|deprecated",
  "priority": "critical|high|medium|low",
  "created_at": "ISO8601_timestamp",
  "updated_at": "ISO8601_timestamp"
}

CONTENT ORGANIZATION BEST PRACTICES:

1. Start with summary - First 1-2 sentences capture the essence
2. Use clear section headers - UPPERCASE with colons (e.g., SECTION NAME:)
3. Keep sections focused - One main idea per section
4. Include keywords naturally - Don't keyword stuff, embed naturally
5. Add quick reference - Tables, checklists, decision trees for fast lookup
6. Provide examples - Concrete examples improve understanding

METADATA BEST PRACTICES:

1. Use consistent categories - reference, research_summary, test_pattern, etc.
2. Include key topics - Array of 3-7 main topics for filtering
3. Version control - Track versions (1.0, 2.0, etc.)
4. Status tracking - Mark deprecated documents
5. Priority levels - critical, high, medium, low
6. Timestamps - ISO8601 format for created_at/updated_at

SEARCH OPTIMIZATION:

1. Natural language - Write in clear, natural language
2. Explicit terms - Use the exact terms people will search for
3. Synonyms - Include alternative terms in key_topics
4. Context preservation - Keep related information together
5. Summary at start - Helps embeddings capture main idea

CHUNKING GUIDELINES (if document is large):

When to Chunk:
- Documents > 1000 tokens should be chunked
- Each chunk: 200-400 tokens (sweet spot: 300 tokens)
- Overlap: 10-30% between chunks (~50 tokens)

Chunk Structure:
- Include section header in chunk
- Keep semantically coherent
- Add summary at start if needed
- Overlap with previous chunk if needed
- Maintain context

QUALITY CHECKLIST:

Before storing in Qdrant, verify:
- Document has clear title in UPPERCASE
- Summary (1-2 sentences) at the start
- Sections use UPPERCASE headers with colons
- Content is semantically coherent
- Keywords are naturally embedded
- Metadata is complete and accurate
- Key topics array has 3-7 relevant topics
- Version and status are set correctly
- Document is searchable (test with sample queries)
- No duplicate content (check existing documents)

SEARCH QUERY EXAMPLES:

Documents formatted this way can be found with:
- "tool selection strategy" → Finds strategy documents
- "cost optimization" → Finds cost-related content
- "GPT-5 Mini credits" → Finds specific tool information
- "decision framework" → Finds decision-making guides
- "workflow" → Finds process documents

TEMPLATE CATEGORIES:

Reference Documents:
- Tool selection strategies
- Best practices
- Decision frameworks
- Quick reference guides

Research Documents:
- Research findings
- Analysis results
- Comparison studies
- Technical investigations

Code/Implementation:
- Code examples
- Implementation patterns
- Test strategies
- Architecture decisions

Workflow Documents:
- Process guides
- Step-by-step instructions
- Checklists
- Templates

VERSION CONTROL:

- Version format: major.minor (e.g., 1.0, 2.1)
- Major version: Significant changes, restructuring
- Minor version: Updates, corrections, additions
- Status: active (current) or deprecated (replaced)
- Replacement: If deprecated, include replaced_by: doc_id

FINAL NOTES:

1. Consistency is key - Follow this template for all documents
2. Test searchability - Before storing, test with sample queries
3. Update metadata - Keep metadata current and accurate
4. Remove duplicates - Check for existing content before storing
5. Mark deprecated - Don't delete, mark as deprecated with replacement doc_id

