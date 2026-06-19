#!/usr/bin/env python3
"""
Convert PDF and DOCX files to Markdown
Usage: python convert_docs.py <source-dir> <output-dir>
"""

import os
import sys
from pathlib import Path

try:
    import pypdf
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def pdf_to_markdown(pdf_path, output_path):
    """Convert PDF to Markdown"""
    if not PDF_AVAILABLE:
        raise ImportError("pypdf not installed. Run: pip install pypdf")

    reader = pypdf.PdfReader(pdf_path)
    markdown_lines = []

    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        if text.strip():
            markdown_lines.append(f"\n\n---\n\n## Page {page_num}\n\n{text}")

    markdown = "\n".join(markdown_lines).strip()

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    return True


def docx_to_markdown(docx_path, output_path):
    """Convert DOCX to Markdown"""
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx not installed. Run: pip install python-docx")

    doc = Document(docx_path)
    markdown_lines = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Simple heading detection
        if para.style.name.startswith('Heading'):
            level = int(para.style.name[-1])
            markdown_lines.append(f"{'#' * level} {text}")
        else:
            markdown_lines.append(text)

    markdown = "\n\n".join(markdown_lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    return True


def convert_directory(source_dir, output_dir):
    """Convert all PDF/DOCX files in source directory"""
    source_path = Path(source_dir)
    output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    converted = []
    skipped = []

    for file in source_path.rglob('*'):
        if file.is_file():
            ext = file.suffix.lower()
            if ext == '.pdf':
                output_file = output_path / f"{file.stem}.md"
                try:
                    pdf_to_markdown(file, output_file)
                    converted.append((str(file), str(output_file)))
                except Exception as e:
                    print(f"✗ Failed to convert {file}: {e}")

            elif ext in ['.docx', '.doc']:
                output_file = output_path / f"{file.stem}.md"
                try:
                    docx_to_markdown(file, output_file)
                    converted.append((str(file), str(output_file)))
                except Exception as e:
                    print(f"✗ Failed to convert {file}: {e}")
            else:
                skipped.append(str(file))

    return converted, skipped


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_docs.py <source-dir> [output-dir]")
        print("\nRequirements:")
        if not PDF_AVAILABLE:
            print("  - pip install pypdf")
        if not DOCX_AVAILABLE:
            print("  - pip install python-docx")
        sys.exit(1)

    source_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(source_dir), 'sources'
    )

    print(f"Converting files from: {source_dir}")
    print(f"Output directory: {output_dir}\n")

    converted, skipped = convert_directory(source_dir, output_dir)

    print(f"\n✓ Converted: {len(converted)} files")
    for src, dst in converted:
        print(f"  {Path(src).name} → {Path(dst).name}")

    if skipped:
        print(f"\n○ Skipped: {len(skipped)} files (not PDF/DOCX)")

    if not PDF_AVAILABLE or not DOCX_AVAILABLE:
        print("\n⚠ Warning: Some converters not installed")


if __name__ == '__main__':
    main()