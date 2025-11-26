# Testing Strategy

## Important: No Real API Calls During Development

**CRITICAL RULE**: Do NOT call real AI models during development/testing. This wastes tokens and costs money.

### Development Phase (Current)

1. **Use Mock Responses**: All tests use `tests/fixtures/test_data.py` for sample responses
2. **Mock API Clients**: Use `tests/fixtures/mock_models.py` to simulate API calls
3. **Mock MongoDB**: Use mock MongoDB client for database operations
4. **Test Logic Only**: Focus on testing business logic, routing, storage, validation

### End-to-End Testing Phase (After System is Ready)

1. **Real API Calls**: Only after all unit/integration tests pass
2. **Real MongoDB**: Use test database for end-to-end testing
3. **Tweak & Adjust**: Fine-tune based on real model responses
4. **Cost Control**: Monitor token usage during E2E testing

## Test Structure

### Unit Tests
- Test individual functions/classes in isolation
- Use mocks for all external dependencies
- Fast execution, no API calls

### Integration Tests
- Test component interactions
- Use mock API and mock MongoDB
- Verify data flow and transformations

### End-to-End Tests
- Real API calls (only when system is ready)
- Real MongoDB (test database)
- Full workflow validation

## Mock Usage Examples

```python
# In tests, always use mocks:
from tests.fixtures.mock_models import MockRouteLLMClient
from tests.fixtures.test_data import SAMPLE_TOPIC_RESEARCH_RESPONSE

# Mock the API client
mock_client = MockRouteLLMClient(api_key="test", api_url="test")
response = mock_client.chat_completion(
    model="gemini-2.5-flash",
    messages=[{"role": "user", "content": "What is TDD?"}]
)
```

## When to Use Real Models

**ONLY** when:
1. All unit tests pass
2. All integration tests pass
3. System is functionally complete
4. Ready for final validation
5. User explicitly approves E2E testing

