# ABOUTME: CLI interface for converting documents to markdown format.
# ABOUTME: Handles argument parsing, file discovery, and conversion orchestration.

import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from markitdown import MarkItDown
import pymupdf4llm


def convert_with_markitdown(input_path: Path) -> str:
    """Convert DOCX or XLSX files using markitdown."""
    md = MarkItDown()
    result = md.convert(str(input_path))
    return result.text_content


def convert_with_pymupdf(input_path: Path) -> str:
    """Convert PDF files using pymupdf4llm."""
    return pymupdf4llm.to_markdown(str(input_path))


def convert_file(input_path: Path, output_path: Path) -> bool:
    """
    Convert a single file to markdown.

    Returns True if successful, False otherwise.
    """
    suffix = input_path.suffix.lower()

    # Check if file type is supported
    if suffix not in {'.docx', '.xlsx', '.pdf'}:
        return True  # Silently skip unsupported files

    try:
        # Select converter based on file type
        if suffix in {'.docx', '.xlsx'}:
            content = convert_with_markitdown(input_path)
        elif suffix == '.pdf':
            content = convert_with_pymupdf(input_path)
        else:
            return True  # Should not reach here

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write markdown file
        output_path.write_text(content, encoding='utf-8')

        print(f"Converted: {input_path} -> {output_path}")
        return True

    except Exception as e:
        print(f"Error converting {input_path}: {e}", file=sys.stderr)
        return False


def process_directory(input_dir: Path, output_dir: Path, workers: int = None) -> tuple[int, int]:
    """
    Process all files in directory recursively using parallel processing.

    Returns tuple of (successful_count, error_count).
    """
    # Collect all files to process
    tasks = []
    for input_path in input_dir.rglob('*'):
        if not input_path.is_file():
            continue

        # Only queue supported file types
        if input_path.suffix.lower() not in {'.docx', '.xlsx', '.pdf'}:
            continue

        # Calculate relative path to preserve directory structure
        relative_path = input_path.relative_to(input_dir)
        output_path = output_dir / relative_path.with_suffix('.md')
        tasks.append((input_path, output_path))

    if not tasks:
        return 0, 0

    successful = 0
    errors = 0

    # Use ProcessPoolExecutor for CPU-bound tasks
    # Default to CPU count if workers not specified
    if workers is None:
        workers = os.cpu_count() or 1

    with ProcessPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(convert_file, input_path, output_path): input_path
            for input_path, output_path in tasks
        }

        # Process results as they complete
        for future in as_completed(future_to_file):
            input_path = future_to_file[future]
            try:
                result = future.result()
                if result:
                    successful += 1
                else:
                    errors += 1
            except Exception as e:
                print(f"Error processing {input_path}: {e}", file=sys.stderr)
                errors += 1

    return successful, errors


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Convert documents (DOCX, XLSX, PDF) to Markdown format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        'directory',
        type=Path,
        help='Directory containing files to convert'
    )

    parser.add_argument(
        '--output-to',
        type=Path,
        help='Output directory (default: <directory>/markdown)'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of parallel workers (default: CPU count)'
    )

    args = parser.parse_args()

    # Validate input directory
    if not args.directory.exists():
        print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
        sys.exit(1)

    if not args.directory.is_dir():
        print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
        sys.exit(1)

    # Determine output directory
    output_dir = args.output_to if args.output_to else args.directory / 'markdown'

    print(f"Converting files from: {args.directory}")
    print(f"Output directory: {output_dir}")
    print(f"Workers: {args.workers if args.workers else os.cpu_count()}")
    print()

    # Process all files
    successful, errors = process_directory(args.directory, output_dir, args.workers)

    print()
    print(f"Conversion complete: {successful} successful, {errors} errors")

    sys.exit(0 if errors == 0 else 1)


if __name__ == '__main__':
    main()
