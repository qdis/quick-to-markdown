# ABOUTME: Tests for document conversion functionality.
# ABOUTME: Validates DOCX and PDF conversion to markdown format.

import tempfile
from pathlib import Path
import pytest

from tomarkdown.cli import (
    convert_file,
    convert_with_markitdown,
    convert_with_pymupdf,
    process_directory,
)


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures directory."""
    return Path(__file__).parent / 'fixtures'


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_convert_docx_with_markitdown(fixtures_dir):
    """Test DOCX conversion using markitdown."""
    docx_file = fixtures_dir / 'test_document.docx'
    assert docx_file.exists(), f"Test fixture not found: {docx_file}"

    result = convert_with_markitdown(docx_file)

    assert isinstance(result, str)
    assert len(result) > 0
    assert 'Test Document' in result


def test_convert_pdf_with_pymupdf(fixtures_dir):
    """Test PDF conversion using pymupdf4llm."""
    pdf_file = fixtures_dir / 'test_document.pdf'
    assert pdf_file.exists(), f"Test fixture not found: {pdf_file}"

    result = convert_with_pymupdf(pdf_file)

    assert isinstance(result, str)
    assert len(result) > 0


def test_convert_file_docx(fixtures_dir, temp_output_dir):
    """Test converting a DOCX file to markdown."""
    input_file = fixtures_dir / 'test_document.docx'
    output_file = temp_output_dir / 'test_document.md'

    success = convert_file(input_file, output_file)

    assert success is True
    assert output_file.exists()
    content = output_file.read_text()
    assert 'Test Document' in content


def test_convert_file_pdf(fixtures_dir, temp_output_dir):
    """Test converting a PDF file to markdown."""
    input_file = fixtures_dir / 'test_document.pdf'
    output_file = temp_output_dir / 'test_document.md'

    success = convert_file(input_file, output_file)

    assert success is True
    assert output_file.exists()
    content = output_file.read_text()
    assert len(content) > 0


def test_convert_file_unsupported_type(temp_output_dir):
    """Test that unsupported file types are skipped silently."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
        tmp.write(b'test content')
        tmp.flush()
        input_file = Path(tmp.name)

    output_file = temp_output_dir / 'output.md'

    try:
        success = convert_file(input_file, output_file)
        assert success is True  # Should return True for skipped files
        assert not output_file.exists()  # But no output file created
    finally:
        input_file.unlink()


def test_process_directory(fixtures_dir, temp_output_dir):
    """Test processing an entire directory."""
    successful, errors = process_directory(fixtures_dir, temp_output_dir, workers=1)

    assert successful == 2  # DOCX and PDF
    assert errors == 0

    # Check output files exist
    assert (temp_output_dir / 'test_document.md').exists()


def test_convert_file_creates_output_dirs(fixtures_dir, temp_output_dir):
    """Test that output directories are created as needed."""
    input_file = fixtures_dir / 'test_document.docx'
    output_file = temp_output_dir / 'nested' / 'dir' / 'output.md'

    success = convert_file(input_file, output_file)

    assert success is True
    assert output_file.exists()
    assert output_file.parent.exists()
