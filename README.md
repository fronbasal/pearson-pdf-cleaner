# pearson-pdf-cleaner

A lean, straightforward watermark removal tool for improving legibility of Pearson eLibrary content.

**What it does:**

- Removes `/Artifact` marked content blocks that contain watermarks and overlays
- Sanitizes document metadata (removes creation/modification dates, producer info)
- Preserves all book content, structure, and formatting

**Limitations:**

- This is a simple, "dirty" approach - some PDFs may require manual cleanup
- Does not attempt to detect watermark type - processes all `/Artifact` blocks uniformly
- Best results on standard Pearson eLibrary PDFs

## Use cases

- Improving readability of Pearson textbooks by removing watermark overlays
- Cleaning PDFs for personal archival
- Batch processing eLibrary content

## Install

Using uv:

```bash
uv pip install pearson-pdf-cleaner
```

Using pip:

```bash
pip install pearson-pdf-cleaner
```

## Usage

```bash
pearson-pdf-cleaner [-f] [-v] [--dry-run] <input-file> <output-file>
```

Options:

- `-f, --force`: Overwrite output file if it exists
- `-v, --verbose`: Debug output
- `--dry-run`: Check if PDF is processable without making changes

Example:

```bash
pearson-pdf-cleaner input.pdf output.pdf
pearson-pdf-cleaner -f input.pdf output.pdf  # Overwrite if exists
```

## How it works

The tool processes each PDF page by:

1. **Removing marked content blocks**: Strips `/Artifact` sections that typically contain watermarks and overlays
2. **Sanitizing metadata**: Removes creation/modification dates and producer information to avoid traceability

That's it. It's intentionally simple.

## Development

```bash
uv sync --dev
uv run pearson-pdf-cleaner --help
uv run pre-commit install --hook-type pre-commit --hook-type pre-push
black --check .
mypy src
```

## Release

- Tag releases using semver, prefixed with `v` (example: `v1.2.3`).
- GitHub Actions builds and creates a GitHub Release.
