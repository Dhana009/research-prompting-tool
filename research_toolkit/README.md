# Research & Debugging Toolkit

A multi-model AI system for topic research, coding research, debugging analysis, architectural design, and general-purpose reasoning.

## Features

- **5 AI Tools**: Topic Research, Coding Research, Debugging, Architecture & Design, General Purpose
- **10 Verified Models**: Optimized routing based on task complexity
- **MongoDB Storage**: Raw markdown storage as source of truth
- **User-Driven Escalation**: Debugging tool with tier-based escalation
- **TDD Approach**: Test-driven development with comprehensive test coverage

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Update `.env` with your MongoDB connection string and RouteLLM API key.

4. Run tests:
```bash
pytest
```

## Project Structure

```
research_toolkit/
├── src/
│   ├── models/          # Question IDs, document schemas
│   ├── storage/         # MongoDB operations
│   ├── router/          # Model selection logic
│   ├── tools/           # AI tools (5 tools)
│   ├── utils/           # Token management, output handling
│   └── cli/             # Command-line interface
├── tests/
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── fixtures/        # Test fixtures
└── requirements.txt
```

## Development

This project follows Test-Driven Development (TDD):
1. Write tests first (RED)
2. Implement to pass tests (GREEN)
3. Refactor
4. Repeat

## Requirements

See `../requirements/final_draft_requirements.md` for complete requirements specification.

