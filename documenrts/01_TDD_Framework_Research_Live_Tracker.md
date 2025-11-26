# TDD FRAMEWORK RESEARCH: LIVE TRACKER

**Document ID:** doc_b2aeed3768c1619a  
**Version:** 1.0  
**Status:** active  
**Priority:** critical  
**Last Updated:** 2025-11-25

---

SUMMARY: Live tracking document for TDD framework research project. Updated continuously to maintain session context and progress visibility.

CURRENT STATUS:

Research Progress:
- Category A (TDD Fundamentals): ✅ Complete & Formatted - Q1, Q2, Q3 stored in Qdrant with proper template format
- Category B (SDLC Integration): ⏳ Pending - Q4, Q5, Q6
- Category C (Technology-Specific): ⏳ Pending - Q7, Q8, Q9
- Category D (AI Pain Points): ⏳ Pending - Q10, Q11, Q12
- Category E (End-to-End Workflow): ⏳ Pending - Q13, Q14, Q15

Completed: 3/15 questions (20%)
Pending: 12/15 questions (80%)

ACTIVE STRATEGIES:

Tool Selection:
- Research Primary: GPT-5 Mini (~6.54 credits/call) for well-known topics
- Escalation: GPT-4.1 → Claude Sonnet only if needed
- Cost optimization: Try GPT-5 Mini 2-3 times before escalating
- Code Generation Primary: Qwen 2.5 Coder 32B (Code Write Primary) - ~0.79 credits/call
- Code Generation Backup: Grok Code Fast (Code Write Backup) - ~1.59 credits/call

Document Format:
- Follow Qdrant template: Title (UPPERCASE) → Summary → Sections → Metadata
- ALWAYS use MCP (Qdrant) for storage - NO local storage
- All documents stored in Qdrant via MCP only
- Local files are temporary/for reference only (not primary storage)
- Category A reformatted to match template structure

Output Rules:
- No documents unless explicitly requested
- Keep output short, focused, minimal
- Provide summaries directly in conversation

Tracker Updates:
- Proactively update tracker after each completed step
- Update status immediately when work is done
- Keep tracker current and accurate

KEY DOCUMENTS IN QDRANT:

- Tool Selection Strategy (doc_48691f09bfb694f3) - v2.1
- Qdrant Document Template (doc_61eb2a5efabee003) - v1.0
- Research Workflow Purpose (doc_c8e5ead3801fb13b) - v1.0
- TDD Research Questions (doc_340080e7954fcc44) - v1.0
- Model Comparison Category A (doc_cf69a5405412fc2a) - v1.0
- Implementation Changes (doc_208e5797ec26fa50) - v1.0
- Category A Findings (e43274f473e16c195445bfd7b5af833bac466dc8cb81284c211c0ffa2ae1389d) - v1.0 (reformatted)
- Research Session Summary (doc_032a59087cec7f7d) - v1.0
- Output Rules (doc_31fc6b7606b2871e) - v1.0
- This Tracker (doc_b2aeed3768c1619a) - Live

NEXT ACTIONS:

1. Continue Category B research (Q4-Q6)
2. Use GPT-5 Mini for research
3. Format findings using Qdrant template immediately
4. Store in Qdrant with proper metadata
5. Generate code examples after research

LAST UPDATED: 2025-11-25 - All framework_design documents now in Qdrant, ready for Category B

