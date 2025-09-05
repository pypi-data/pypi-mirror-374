# MyEPUBApp

A powerful text-to-EPUB conversion tool that transforms plain text files into standard EPUB e-book format.

## Features

- 📖 **Text to EPUB Conversion**: Convert plain text files to EPUB-compliant e-books
- 🌏 **Chinese Optimization**: Specially optimized for Chinese content with Chinese book title mark conversion
- 📑 **Automatic Chapter Splitting**: Automatically identify and split chapters using special marker symbols
- 🔄 **Flexible Modes**: Support creating new EPUB or appending chapters to existing EPUB
- 🏗️ **Modular Architecture**: Clean code structure for easy maintenance and extension
- 📝 **Detailed Logging**: Complete operation logging

## Installation

### Requirements
- Python 3.8+
- pip package manager

### Option 1: Install from PyPI (Recommended)

```bash
pip install myepubapp
```

### Option 2: Install from Source

1. Clone the project:
```bash
git clone https://github.com/eyes1971/myepubapp.git
cd myepubapp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install in development mode:
```bash
pip install -e .
```

## Usage

### Basic Usage

#### 1. Initialize New EPUB File
```bash
python -m myepubapp -i input.txt --output-epub output.epub
```
**自動書名生成**: 書名會從輸入文件名自動生成，例如 `my_book.txt` 會生成書名 "My Book"

#### 2. Append Chapters to Existing EPUB
```bash
python -m myepubapp -a input.txt --input-epub existing.epub --output-epub new.epub
```

### Command Line Arguments

- `-i, --init`: Initialize mode, create new EPUB file
- `-a, --append`: Append mode, add chapters to existing EPUB
- `input_file`: Input text file path
- `--input-epub, -ie`: Existing EPUB file (required in append mode)
- `--output-epub, -o`: Output EPUB file path
- `--convert-tags, -ct`: Convert `<>` tags to Chinese book title marks `《》`

### Input File Format

Text files should use the following format for chapter splitting:

```
※☆ Introduction Content
This is the introduction page content.
It can span multiple paragraphs and will be displayed as a separate introduction page.

※ⅰ Chapter 1 Title
Chapter content first paragraph...

※ⅱ Chapter 1 Section 1 Subsection Title
Subsection content...

※ⅲ Chapter 1 Section 1 Subsection 1
Deeper level content...
```

#### Format Description:
- `※☆`: Introduction page (creates a separate intro page)
- `※ⅰ`: Level 1 chapter (h1)
- `※ⅱ`: Level 2 chapter (h2)
- `※ⅲ`: Level 3 chapter (h3)

## Examples

### Create Simple EPUB
```bash
python -m myepubapp -i sample.txt --output-epub mybook.epub
```

### Create EPUB with Tag Conversion
```bash
python -m myepubapp -i sample.txt --output-epub mybook.epub --convert-tags
```

### Append Chapters to Existing EPUB
```bash
python -m myepubapp -a chapter2.txt --input-epub mybook.epub --output-epub mybook_updated.epub
```

## Dependencies

- `ebooklib>=0.18.0`: EPUB file processing
- `beautifulsoup4>=4.12.0`: HTML/XML parsing

## Project Structure

```
myepubapp/
├── core/                 # Core modules
│   ├── book.py          # EPUB book class
│   ├── chapter.py       # Chapter class
│   └── metadata.py      # Metadata class
├── generators/          # Generator modules
│   ├── content.py       # Content generator
│   └── toc.py          # Table of contents generator
├── utils/               # Utility modules
│   ├── file_handler.py  # File handling
│   ├── logger.py        # Logging
│   └── text_processor.py # Text processing
├── exceptions/          # Custom exceptions
│   └── epub_exceptions.py
├── cli.py              # Command line interface
└── __init__.py         # Package initialization
```

## Logging

All operations are logged to `logs/myepubapp.log` file.

## License

This project is licensed under the MIT License.

## Contributing

Issues and Pull Requests are welcome!

## Version

Current version: 1.0.0
