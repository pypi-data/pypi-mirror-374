# WebOasis Repository Structure

This document describes the structure of the WebOasis repository, a comprehensive web agent framework for researchers.

## Overview

WebOasis is designed to help researchers focus on high-level agent design instead of browser manipulation details. The framework provides all necessary interaction functions with browsers, allowing researchers to concentrate on agent architecture, reasoning, and behavior.

## Directory Structure

```
weboasis/
├── act_book/                 # Core automation framework
│   ├── core/                # Base classes and interfaces
│   │   ├── base.py         # Operation base classes
│   │   ├── registry.py     # Operation registry and discovery
│   │   ├── automator_interface.py  # Browser automation interface
│   │   ├── adapters.py     # Adapter implementations
│   │   └── extractor.py    # Data extraction utilities
│   ├── book/               # High-level operations
│   │   ├── interaction.py  # Click, fill, scroll operations
│   │   ├── navigation.py   # Navigate, get URL operations
│   │   └── extraction.py   # Get text, screenshot operations
│   ├── engines/            # Browser engine implementations
│   │   ├── playwright/     # Playwright engine
│   │   │   ├── actions.py  # Low-level Playwright actions
│   │   │   └── adapter.py  # Playwright adapter
│   │   └── selenium/       # Selenium engine
│   │       ├── actions.py  # Low-level Selenium actions
│   │       └── adapter.py  # Selenium adapter
│   ├── browser/            # Browser-specific operations
│   ├── composite/          # Composite operations
│   ├── dom/                # DOM manipulation utilities
│   └── __init__.py         # Main package interface
├── ui_automator/           # UI automation utilities
│   ├── parsers/           # Customizable parser system for LLM responses
│   ├── base_manager.py    # Base browser manager interface
│   ├── playwright_manager.py  # Playwright automation manager
│   ├── selenium_manager.py    # Selenium automation manager
│   └── __init__.py        # UI automator interface
├── agents/                 # Agent implementations
│   ├── base.py            # Base agent classes
│   ├── dual_agent.py      # Dual agent architecture
│   ├── constants.py       # Agent constants and configuration
│   └── __init__.py        # Agent interface
├── config/                 # Configuration files
│   └── prompts.yaml       # Prompt templates and configurations
├── javascript/             # Browser JavaScript utilities
│   ├── add_outline_elements.js      # Element outlining
│   ├── frame_mark_elements.js       # Frame element marking
│   ├── frame_unmark_elements.js     # Frame element unmarking
│   ├── identify_interactive_elements.js  # Interactive element identification
│   ├── remove_outline_elements.js   # Element outline removal
│   └── show_decision_making_process.js   # Decision process visualization
├── scripts/                # Example scripts and tools
│   ├── action_parser_example.py    # Action parser usage example
│   ├── clean_example.py            # Clean automation example
│   ├── example_usage.py            # General usage examples
│   ├── init_repo.py                # Repository initialization
│   ├── setup_dev.py                # Development environment setup
│   └── simulated_webagent.py       # Simulated web agent example
├── tests/                  # Unit tests
│   ├── test_registry.py   # Operation registry tests
│   ├── test_simple_parser.py  # Parser tests
│   └── run_tests.py       # Test runner
├── docs/                   # Documentation
│   ├── conf.py            # Sphinx configuration
│   ├── index.rst          # Main documentation page
│   ├── api.rst            # API documentation
│   └── Makefile           # Documentation build system
├── .github/                # GitHub workflows and templates
│   └── workflows/         # CI/CD workflows
├── .gitignore             # Git ignore patterns
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── LICENSE                 # Apache License, Version 2.0
├── Makefile               # Build and development commands
├── README.md              # Main project documentation
├── REPOSITORY_STRUCTURE.md # This file
├── pyproject.toml         # Modern Python packaging configuration
├── requirements.txt       # Python dependencies
├── setup.py               # Legacy setup configuration
└── utils.py               # Utility functions
```

## Key Components

### act_book
The core automation framework that provides:
- **Operations**: High-level automation operations (click, fill, navigate, etc.)
- **Engines**: Browser engine adapters for Playwright and Selenium
- **Core**: Base classes, interfaces, and utilities

### ui_automator
Browser management and automation interfaces:
- **Managers**: Browser-specific managers (Playwright, Selenium)
- **Parsers**: LLM response parsing and action extraction
- **Base Classes**: Common interfaces and utilities

### agents
Agent framework implementation:
- **Base Classes**: Foundation for building web agents
- **Dual Architecture**: Support for both automated and interactive agents
- **Constants**: Configuration and prompt templates

### javascript
Browser-side utilities for:
- **Element Marking**: Visual identification of page elements
- **Interaction**: Enhanced user interaction capabilities
- **Visualization**: Decision-making process display

## Development Workflow

1. **Installation**: `pip install -e .` for development
2. **Testing**: `make test` to run all tests
3. **Linting**: `make lint` to check code quality
4. **Formatting**: `make format` to auto-format code
5. **Documentation**: `make docs` to build documentation

## Contributing

When contributing to WebOasis:
1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation as needed
4. Use the provided Makefile commands for quality checks

## License

WebOasis is licensed under the Apache License, Version 2.0, allowing for both academic and commercial use while preserving the author's commercial rights.
