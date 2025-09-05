# LF-CRLF Converter

A simple Python library to convert line endings between LF (Unix) and CRLF (Windows) formats.

## Features

- Convert individual files between LF and CRLF line endings
- Recursively convert all files in a directory with common extensions
- Support for various text-based file formats (.txt, .py, .html, .css, .js, .json, .xml, .md)

## Usage

### Installation
```bash
pip install lfcrlf
```

### Basic Usage
```python
from lfcrlf import convert_file, convert_dir

#Convert a single file from LF to CRLF
convert_file('path/to/file.txt', 'lf')

#Convert a single file from CRLF to LF
convert_file('path/to/file.txt', 'crlf')

#Convert all files in a directory from LF to CRLF
convert_dir('path/to/directory', 'lf')

## Convert all files in a directory from CRLF to LF
convert_dir('path/to/directory', 'crlf')
```

---
### Supported File Types
The library automatically processes files with these extensions:

- .txt
- .py
- .html
- .css
- .js
- .json
- .xml
- .md

### Requirements
Python 3.6 or higher

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

- Fork the project
- Create your feature branch *git checkout -b feature/AmazingFeature*
- Commit your changes *git commit -m 'Add some AmazingFeature'*
- Push to the branch *git push origin feature/AmazingFeature*

Support
If you have any questions or issues, please open an issue on GitHub.