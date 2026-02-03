# Sync dependencies from pyproject.toml
sync:
    uv sync

# Run type checking with ty
typecheck:
    uv run ty check src/llm_benchmark

# Run ruff linter with automatic fixes
lint:
    uv run ruff check --fix src/llm_benchmark examples tests

# Format code
format:
    uv run ruff format src/llm_benchmark examples tests

# Run all tests with pytest (coverage enabled by default)
test:
    uv run pytest tests/ -v

# Generate and open HTML coverage report
cov-html:
    uv run pytest tests/ --cov-report=html
    xdg-open htmlcov/index.html

# Open benchmark HTML report
report:
    xdg-open results/report.html

# Clean up generated files and caches
clean:
    rm -rf .pytest_cache .ruff_cache .coverage htmlcov results/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
