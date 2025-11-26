# CATEGORY A: TDD FUNDAMENTALS FOR AI ASSISTANTS

**Document ID:** doc_0a9a7ba08b6e547e  
**Version:** 1.0  
**Status:** active  
**Priority:** high  
**Research Category:** Category A  
**Questions:** Q1, Q2, Q3

---

SUMMARY: Research findings for Category A questions (Q1, Q2, Q3) covering critical TDD principles, common AI mistakes, and test case structure for maximizing AI code quality and minimizing debugging time.

QUESTION 1: CRITICAL TDD PRINCIPLES FOR AI ASSISTANTS

What are the most critical test-driven development principles that AI coding assistants must follow to produce high-quality, bug-free code?

KEY PRINCIPLES:

1. Start with small, explicit behavioral tests (single-behavior-per-test)
2. Use Given-When-Then (Arrange-Act-Assert) structure with explicit comments
3. Make edge cases and invariants explicit (boundary tests & property tests)
4. Use strong, precise assertions (not just truthy checks)
5. Write tests as executable specifications/contracts for APIs and services
6. Prefer table-driven/parameterized tests for combinatoric cases
7. Control external dependencies deterministically (mock, stub, VCR)
8. Make expected failure modes explicit (negative tests)
9. Use snapshot or golden-file tests for complex outputs
10. Create regression tests for every bug found
11. Prefer narrow unit tests + selective integration tests (test pyramid)
12. Ensure test isolation and reset global state
13. Use clear input/output examples for ambiguous requirements
14. Make tests minimal and fast; prefer unit-level determinism
15. Use mutation testing and flakiness detection to harden tests
16. Assert on semantics, not implementation details
17. Seed randomness and time in tests to ensure determinism
18. Provide explicit failure messages and help texts in tests
19. Use BDD/Gherkin for cross-team clarity when requirement comes from product language
20. CI-first loop: tests → minimal implementation → run locally → CI

QUESTION 2: TOP 5 COMMON MISTAKES AI ASSISTANTS MAKE IN TDD

What are the top 5 most common mistakes AI assistants make when attempting test-driven development?

MISTAKE 1: SKIPPING THE "WRITE A FAILING TEST FIRST" STEP
- Root cause: Assistant attempts to show working solution quickly or misunderstands TDD
- Negative impact: Bugs discovered only after implementation, making debugging larger chunks harder
- Solution: Always produce single explicit failing test case first. Show test run output with failure before implementation.

MISTAKE 2: WRITING TESTS THAT ARE TOO BROAD / INTEGRATION-LEVEL INSTEAD OF SMALL, FOCUSED UNIT TESTS
- Root cause: Desire to demonstrate end-to-end example or lack of decomposition
- Negative impact: Failing tests point to large surface area; hard to isolate cause
- Solution: Break behavior into small units, one focused test per small behavior/edge case. Use mocks/stubs to isolate unit.

MISTAKE 3: CREATING BRITTLE OR NONDETERMINISTIC TESTS (FLAKY TESTS)
- Root cause: Tests rely on external services, global state, system time, random numbers without control
- Negative impact: Tests pass sometimes and fail other times; team spends time debugging flakes
- Solution: Isolate external dependencies with mocks/fakes. Control nondeterminism: seed random generators, inject clock/mock time, ensure tests reset global state.

MISTAKE 4: WEAK OR MISSING ASSERTIONS (FALSE-POSITIVES)
- Root cause: Tests only check function returned without throwing, or check general shape instead of specific behavior
- Negative impact: Tests pass while incorrect behavior remains; bugs surface later in production
- Solution: Make assertions explicit and precise. Include negative tests and error cases. Use property-based tests or parameterized tests.

MISTAKE 5: IMPLEMENTING LARGE, OPTIMIZED SOLUTIONS INSTEAD OF MINIMAL CODE TO PASS TESTS
- Root cause: Assistant writes full-featured or optimized implementation immediately rather than smallest change
- Negative impact: Large code harder to reason about, introduces more bugs, needs rewriting after subsequent tests
- Solution: Enforce "smallest possible implementation" rule. Provide step-by-step micro-iterations. Use strict scaffolding with NotImplementedError until test dictates behavior.

QUESTION 3: TEST CASE STRUCTURE AND ORGANIZATION FOR AI CODE QUALITY

How should test cases be structured and organized to maximize AI code quality and minimize debugging time?

TEST NAMING CONVENTIONS:
- Files: Prefix by scope (unit_, integration_, contract_, e2e_, perf_, security_)
- Test functions: Use behavioral names (should_<expected>_when_<condition>) or Given_When_Then format
- Add tags/metadata for severity, type, flakiness

TEST ORGANIZATION STRATEGY:
- Directory layout: tests/unit/, tests/integration/, tests/contract/, tests/e2e/, tests/perf/, tests/security/
- Put lightweight, fast tests in unit/ (pure logic)
- Put slower, real-dependency tests in integration/ (DB, external)
- Contract tests validate API surface
- Golden files/snapshots for large outputs stored under tests/data/golden/

TEST DATA PATTERNS (cover all classes of inputs):
- Nominal (typical) inputs
- Boundary/edge values (min, max, off-by-one)
- Invalid inputs (null, empty, wrong type, malformed)
- Adversarial & security inputs (SQLi, XSS, path traversal, large payloads)
- Internationalization inputs (Unicode, RTL, combining marks)
- Locale/time inputs (timezones, DST transitions, leap-day)
- Numeric edgecases (0, -0, NaN, ±Inf, large BigInt)
- Concurrency & ordering (repeated requests, duplicates, race scenarios)
- Deterministic randomness (seeded RNGs)
- Performance stress inputs (very large arrays, deeply nested structures)

TEST DESIGN PATTERNS:
- Table-driven tests (parametrized) - keeps explicit list of edge cases
- Property-based tests (Hypothesis, QuickCheck) - express invariants
- Golden-file tests - for complex outputs, compare to committed golden files
- Snapshot tests with deterministic serializer
- Contract tests - auto-generate from OpenAPI
- Fuzzing for security-critical code

MAKE TESTS EXPLICIT AND UNAMBIGUOUS:
- Prefer exact assertions over vague ones
- Include postconditions and side-effect assertions
- Include explicit cleanup expectations
- Deterministic ordering and seeding
- Avoid brittle whitespace-only comparisons

EDGE-CASE FORCING EXAMPLES:
- Null/None/missing field vs empty string vs empty array
- Zero, negative numbers, maximum integers
- Off-by-one: size N and size N+1
- Special numeric values: NaN, ±Inf, -0
- Unicode normalization differences (NFC vs NFD)
- Timezones: DST start/end, leap day, Unix epoch boundaries
- Filesystem: symlinks, broken symlinks, permission denied
- Network: partial/chunked responses, timeouts
- Concurrency: repeated create/delete, idempotent retry keys
- Platform-specific behavior: path separators, reserved names, line endings

