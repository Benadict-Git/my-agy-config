---
name: markitdown
description: Convert files of any format (PDF, DOCX, PPTX, XLSX, XLS, images, audio, HTML, CSV, JSON, XML, ZIP) into clean Markdown for reading, inspecting, and extracting text. Activate whenever the user asks to read, inspect, view, parse, examine, summarize, or extract content from any file, document, spreadsheet, slide deck, or media attachment.
---

# MarkItDown File Reader

Use `markitdown` to read, inspect, and convert files of any format into clean Markdown.

## When to Activate

Trigger this skill whenever the user asks to:
- Read, view, parse, examine, analyze, or summarize any file or document.
- Extract text, tables, or data from non-plain-text files (.pdf, .docx, .pptx, .xlsx, .xls, .html, .zip, audio, images).
- Convert any file to Markdown.
- Inspect an unknown or binary file's contents without raw byte clutter.

## Supported Formats

- **Documents**: PDF (`.pdf`), Word (`.docx`), RTF
- **Presentations**: PowerPoint (`.pptx`)
- **Spreadsheets**: Excel (`.xlsx`, `.xls`), CSV, TSV
- **Web & Structured Data**: HTML (`.html`, `.htm`), XML, JSON
- **Archives**: ZIP (`.zip` containing supported files)
- **Media**: Images (EXIF metadata & OCR), Audio (speech transcription)
- **Text**: Plain text, source code, Markdown

## Usage Instructions

### 1. Read / Convert a File
Run `markitdown` directly to read the content:
```bash
markitdown "<path/to/file>"
```

### 2. Convert and Save to Markdown
To save the parsed markdown into a file or scratch file:
```bash
markitdown "<path/to/file>" -o "<path/to/output.md>"
```

### 3. Read Stdin with Format Hint
```bash
cat "<path/to/file>" | markitdown -x <ext>
```

### 4. Python API
When programmatic parsing is preferred:
```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("<path/to/file>")
print(result.text_content)
```

## Guidelines for CLI Agent
- When asked to read or inspect any document or data file, run `markitdown "<filepath>"` to inspect its content in Markdown.
- If the output is large, inspect sections or pipe through pagers/filters.
