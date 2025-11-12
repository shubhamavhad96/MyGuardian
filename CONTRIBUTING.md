# Contributing to MyGuardian

Thank you for your interest in contributing! This document provides guidelines and instructions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/MyGuardian.git`
3. Create a branch: `git checkout -b feature/your-feature`

## Development Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```bash
# Golden tests (5 cases)
python tests/run_goldens.py

# Full eval harness (50 cases)
python eval/run_eval.py

# With markdown report
python eval/run_eval.py --report md
```

## Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Keep functions focused and small
- Add docstrings for public functions

## Good First Issues

Look for issues labeled `good-first-issue`:

- Add more test cases to `eval/cases/`
- Improve error messages
- Add more integration examples
- Documentation improvements
- Performance optimizations

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add tests for new features
4. Submit PR with clear description
5. Address review feedback

## Questions?

Open an issue or reach out to the maintainers.

