# Copilot Instructions for txttoqti

## Project Overview
- **txttoqti** converts text-based question banks into QTI packages for Canvas LMS and other QTI-compliant systems.
- Modular architecture: core conversion logic (`src/txttoqti/`) and educational workflows (`src/txttoqti/educational/`).
- No external dependencies beyond Python 3.10+ standard library.

## Key Components
- **converter.py**: Main orchestrator for conversion pipeline.
- **parser.py**: Extracts and validates questions from text.
- **qti_generator.py**: Generates QTI XML and ZIP packages.
- **validator.py**: Validates question formats.
- **smart_converter.py**: Change detection and incremental updates.
- **models.py**: Data models for questions and assessments.
- **educational/**: High-level academic workflow (auto-detection, batch processing, format bridging).
- **cli.py** and **educational/cli.py**: Command-line interfaces (basic and educational).

## Developer Workflows
- **Testing**: Use `make test`, `python -m pytest`, or `python scripts/dev.py test` (see `CLAUDE.md` for variants).
- **Linting/Formatting**: `make lint`, `make format`, or run `black`, `flake8`, `mypy` directly.
- **Build/Install**: `make build`, `make install-dev`, or `pip install -e .[dev]`.
- **Clean**: `make clean` or `python scripts/dev.py clean`.
- **Publish**: Use `scripts/publish.sh` for PyPI (test/prod).

## Project Conventions
- All code (AI or human) must be reviewed and tested before merging.
- AI-generated code should be clearly attributed (see `AI_MANIFESTO.md`).
- Exception handling uses a custom hierarchy (`exceptions.py`).
- Logging is centralized (`logging_config.py`).
- Question formats and validation rules are enforced in `validator.py` and `educational/formats.py`.
- Tests are in `tests/` and `tests/educational/`.

## Integration Points
- **CLI**: `txttoqti` (basic), `txttoqti-edu` (educational, auto-detecting).
- **API**: Import from `src/txttoqti/` for programmatic use.
- **Docs**: See `docs/` for API, CLI, and format details.

## AI Agent Guidance
- Follow the layered architecture: core logic is separate from educational workflows.
- Prefer using and extending existing models/utilities over duplicating logic.
- Attribute all AI-generated content as per `AI_MANIFESTO.md`.
- Do not introduce external dependencies.
- Maintain compatibility with Python 3.10+.
- Reference `CLAUDE.md` and `AI_MANIFESTO.md` for project philosophy and workflow details.
