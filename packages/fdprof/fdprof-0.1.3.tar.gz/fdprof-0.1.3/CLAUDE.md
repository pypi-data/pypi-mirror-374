# Claude Development Notes

This file contains development notes and commands for working with fdprof using Claude Code.

## Development Environment

### Setup
```bash
# Install development dependencies
uv sync --extra dev

# Install pre-commit hooks
uv run pre-commit install

# Verify installation
uv run fdprof --help
```

### Testing
```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ -v --cov=src/fdprof --cov-report=html --cov-report=term

# Run integration tests only
uv run pytest tests/test_integration.py -v

# Run specific test
uv run pytest tests/test_events.py::TestEventParsing::test_parse_events_single_event -v
```

### Code Quality
```bash
# Run linter
uv run ruff check src/ tests/

# Fix linting issues
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/

# Run pre-commit checks
uv run pre-commit run --all-files
```

**Note**: Linting and formatting are handled locally during development. On GitHub, the pre-commit bot automatically handles linting checks for pull requests, so CI focuses only on functionality testing.

### Building and Installing
```bash
# Build distribution
uv build

# Install locally for testing
uv tool install --from ./dist/fdprof-0.1.0-py3-none-any.whl fdprof

# Test uvx installation
uvx --from ./dist/fdprof-0.1.0-py3-none-any.whl fdprof echo "test"

# Uninstall
uv tool uninstall fdprof
```

### Testing uvx/uv tool compatibility
```bash
# From local build
uvx --from ./dist/fdprof-0.1.0-py3-none-any.whl fdprof --help

# From GitHub (after push)
uvx --from git+https://github.com/ianhi/fdprof fdprof echo "test"
uv tool install git+https://github.com/ianhi/fdprof
```

## Package Structure

```
fdprof/
├── src/fdprof/           # Main package
│   ├── __init__.py       # Entry points
│   ├── core.py           # CLI and main logic
│   ├── monitoring.py     # FD monitoring
│   ├── events.py         # Event parsing
│   ├── analysis.py       # Plateau detection
│   └── plotting.py       # Visualization
├── tests/                # Test suite
│   ├── conftest.py       # Pytest fixtures
│   ├── test_*.py         # Test modules
├── pyproject.toml        # Package configuration
├── README.md             # User documentation
├── MISSION.md            # Design philosophy
├── INSTALL_TEST.md       # Installation testing
└── CLAUDE.md             # This file
```

## Key Design Decisions

### Entry Points
- CLI entry point: `fdprof = "fdprof:cli_main"`
- Main function in `core.py`: `main()`
- CLI wrapper in `__init__.py`: `cli_main()`

### Module Organization
- `core.py`: CLI parsing, main execution loop
- `monitoring.py`: Process monitoring and FD capture
- `events.py`: EVENT: message parsing
- `analysis.py`: Plateau detection algorithms
- `plotting.py`: Matplotlib visualization

### Testing Structure
- Unit tests for each module
- Integration tests for CLI functionality
- Fixtures for test data and cleanup
- 54+ comprehensive tests covering all features

## Common Development Tasks

### Adding New Features
1. Add functionality to appropriate module
2. Write unit tests in `tests/test_<module>.py`
3. Add integration test if needed
4. Update documentation
5. Run `uv run ruff check src/ tests/ && uv run pytest tests/ -v` to verify

### Updating Dependencies
```bash
# Add new dependency
uv add <package>

# Add dev dependency
uv add --group dev <package>

# Update all dependencies
uv sync --upgrade
```

### Release Preparation
1. Update version in `pyproject.toml` and `__init__.py`
2. Update `CHANGELOG.md`
3. Run full test suite: `uv run ruff check src/ tests/ && uv run pytest tests/ -v`
4. Build and test: `uv build && uvx --from ./dist/... fdprof --help`
5. Commit and tag

## Troubleshooting

### Tests Not Running
- Ensure package is installed: `uv sync --reinstall`
- Check Python path includes src: `uv run python -c "import sys; print(sys.path)"`
- Verify imports work: `uv run python -c "import fdprof; print('OK')"`

### uvx Installation Issues
- Check wheel builds correctly: `uv build`
- Test local install: `uvx --from ./dist/... fdprof --help`
- Verify entry point: Check `[project.scripts]` in pyproject.toml

### Import Errors in Development
- Run `uv sync` to reinstall in development mode
- Check that `src/` is in Python path
- Ensure no conflicting installations: `pip list | grep fdprof`

## Mission Alignment

Remember fdprof's mission: **whole-process monitoring from the outside**

✅ Good additions:
- Better FD analysis algorithms
- Additional plot types
- More OS compatibility
- Performance improvements

❌ Avoid these (scope creep):
- Python decorators
- In-process instrumentation
- Complex configuration systems
- Web interfaces or APIs

See `MISSION.md` for complete design philosophy.
