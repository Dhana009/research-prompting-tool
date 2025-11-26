# QUICK REFERENCE: Tool Selection Decision Guide

**Document ID:** doc_86a1896d08fbd34d  
**Version:** 2025-11-25T06:53:14.782778Z  
**Status:** active  
**Priority:** high

---

WHEN TO USE WHICH TOOL - DECISION TREE:

STEP 1: Assess Question Complexity

Is it a SIMPLE question?
- Definition? ("What is X?")
- Basic explanation? ("How does X work?")
- Simple fact? ("What are types of Y?")
→ USE: Budget GPT-4o-mini
→ BACKUP: Budget GPT-5-nano → Research Primary

Is it a MEDIUM complexity question?
- Best practices? ("What are best practices for X?")
- Patterns? ("What are common mistakes in Y?")
- Structured info? ("How should Z be organized?")
- Multi-part? ("What are principles, patterns, examples of X?")
→ USE: Research Primary (GPT-5-mini)
→ BACKUP: Research Backup (Gemini 2.5 Flash) → Claude Sonnet

Is it a HIGH complexity question?
- Deep analysis? ("Analyze root causes and solutions for X")
- Complex reasoning? ("What are architectural implications of Y?")
- Multi-domain? ("Research X across domains and synthesize")
- Critical? ("Optimal strategy for production-critical Z?")
→ USE: Claude Sonnet
→ BACKUP: GPT-5 → Research Primary

TOOL COST COMPARISON (per 1M tokens):

BUDGET TIER:
- Budget GPT-4o-mini: $0.15/$0.60
- Budget GPT-5-nano: $0.05/$0.40
- Budget Meta Llama: $0.02/$0.05

STANDARD TIER:
- Research Primary (GPT-5-mini): $0.25/$2
- Research Backup (Gemini 2.5 Flash): $0.30/$2.50

PREMIUM TIER:
- GPT-5: $1.25/$10 (has timeout issues)
- Claude Sonnet: $3/$15

CODE GENERATION:
- Code Write Primary: $0.79/$0.79

CRITICAL RULES:

1. NEVER use premium models for simple questions
2. ALWAYS start with budget tier for definitions/basic facts
3. MOST research questions = medium complexity = Research Primary
4. ONLY use premium for deep analysis/complex reasoning
5. AVOID Smart Abacus if you know complexity (may over-select expensive models)
6. ALWAYS use Code Write Primary after research for practical examples

WORKFLOW CHECKLIST:

For Each Research Question:
☐ Assess complexity (Simple/Medium/High)
☐ Select appropriate tool based on complexity
☐ Wait 5-10 seconds between calls
☐ Evaluate response quality
☐ If insufficient → use backup tool
☐ Generate code examples with Code Write Primary
☐ Store results in Qdrant

COMMON MISTAKES TO AVOID:

❌ Using Claude Sonnet for "What is TDD?" (use Budget GPT-4o-mini)
❌ Using GPT-5 for simple definitions (use Budget tier)
❌ Using Smart Abacus when complexity is known (use specific tool)
❌ Skipping Code Write Primary after research (always generate examples)
❌ Not having backup chain ready (always plan escalation)

