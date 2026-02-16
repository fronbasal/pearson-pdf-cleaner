# pearson-pdf-cleaner

PDF processing utility that removes Pearson textbook watermarks and metadata overlays to improve document readability.

**Removes:**
- Watermark overlays embedded in PDF marked content blocks
- Metadata annotations and license text
- Non-essential document metadata

**Preserves:**
- All book content and text
- Chapter titles and author information in headers/footers
- Document structure and formatting

## Use Cases

- Cleaning PDFs for archival or research purposes
- Improving readability by removing page overlays
- Processing batch textbook collections
- Document processing pipelines

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
pearson-pdf-cleaner [-h] [-v] [--dry-run] <input-file> <output-file>
```

Example:

```bash
pearson-pdf-cleaner input.pdf output.pdf
```

Dry run (preview changes without modifying the PDF):

```bash
pearson-pdf-cleaner --dry-run input.pdf output.pdf
```

## How it works

The utility processes each page by:

1. **Removing marked content overlays**: Strips PDF marked content blocks (`/Artifact BMC...EMC`) that contain non-essential text
2. **Cleaning symbolic font data**: Removes decorative/symbolic font elements 
3. **Normalizing metadata**: Removes or cleans document-level metadata while preserving document dates and structure

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
