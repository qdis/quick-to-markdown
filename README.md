# tomarkdown

Convert documents (DOCX, XLSX, PDF) to Markdown format with parallel processing.

## Installation

```bash
uv tool install git+https://github.com/qdis/quick-to-markdown.git
```

## Usage

```bash
# Convert files in current directory
tomarkdown .

# Convert files in specific directory
tomarkdown /path/to/documents

# Specify output directory
tomarkdown /path/to/documents --output-to /path/to/output

# Control parallel workers (defaults to CPU count)
tomarkdown /path/to/documents --workers 4
```

## Features

- Recursively processes directories
- Preserves directory structure in output
- Parallel processing for faster conversion
- Uses [markitdown](https://github.com/microsoft/markitdown) for DOCX/XLSX
- Uses [pymupdf4llm](https://github.com/pymupdf/RAG) for PDF

## Development

```bash
# Clone repository
git clone git@github.com:qdis/quick-to-markdown.git
cd quick-to-markdown

# Install dependencies
make install

# Run tests
make test
```
