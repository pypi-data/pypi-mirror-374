# Development Guidelines

This document contains critical information about working with this codebase.
Follow these guidelines precisely.

## Structure

```
code-speak/
├── src/ispeak/            # Main package source
│   ├── __init__.py            # Package initialization and exports
│   ├── cli.py                 # Command-line interface and interactive setup
│   ├── config.py              # Configuration management and validation
│   ├── core.py                # Core voice input and text processing logic  
│   └── recorder.py            # Audio recording abstraction layer
├── main.py                    # Development entry point
├── ispeak                 # Legacy shell helper script
├── ispeak.json            # Local fallback configuration
├── pyproject.toml             # Project metadata and dependencies
└── README.md                  # Documentation
```

## Rules

1. Code Quality
   - Type hints required for all code
   - Follow existing patterns exactly
   - Use Google style for docstring
