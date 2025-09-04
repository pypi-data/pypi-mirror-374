# Learning PyPI Demo Package Specification

## Project Overview
**Package Name:** `learning-pypi-demo-nisimi`  
**Purpose:** Educational Python package to demonstrate PyPI publishing process  
**Key Feature:** Prints "HELLO NEW PACKAGE" during pip installation  

## Requirements

### Functional Requirements
1. **Installation Message**: Display "HELLO NEW PACKAGE" in terminal during `pip install` process
2. **Basic Functionality**: Include a simple `hello()` function that returns a greeting
3. **Hash-based Installation**: Support installation via `pip install -r requirements.txt --require-hashes`
4. **PyPI Publishing**: Package must be publishable to PyPI

### Non-Functional Requirements
- **Simplicity**: Minimal codebase for learning purposes
- **Speed**: Fast installation and minimal dependencies
- **Compatibility**: Python 3.7+ support

## Architecture & Package Structure

```
learning-pypi-demo-nisimi/
├── learning_pypi_demo_nisimi/
│   ├── __init__.py
│   └── core.py
├── setup.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── LICENSE
└── MANIFEST.in
```

### Core Components

#### 1. Package Module (`learning_pypi_demo_nisimi/`)
- **`__init__.py`**: Package initialization, exports main function
- **`core.py`**: Contains the `hello()` function implementation

#### 2. Setup Configuration
- **`setup.py`**: Custom installation class to print message during install
- **`pyproject.toml`**: Modern Python packaging configuration
- **`MANIFEST.in`**: Include additional files in distribution

#### 3. Distribution Files
- **`requirements.txt`**: Package with hash for secure installation
- **`README.md`**: Package documentation
- **`LICENSE`**: MIT License for open source distribution

## Implementation Details

### Installation Message Implementation
Use custom `install` command in `setup.py`:
```python
from setuptools import setup, find_packages
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        print("HELLO NEW PACKAGE")
        super().run()

setup(
    cmdclass={'install': CustomInstall},
    # ... other setup parameters
)
```

### Core Functionality
Simple greeting function in `core.py`:
```python
def hello(name="World"):
    """Return a friendly greeting."""
    return f"Hello, {name}! This is learning-pypi-demo-nisimi package."
```

### Package Configuration
- **Version**: 0.1.0 (semantic versioning)
- **Python Requirements**: >=3.7
- **Dependencies**: None (keep it minimal)
- **License**: MIT
- **Author**: nisimi

## PyPI Publishing Process

### Prerequisites
1. Create PyPI account at https://pypi.org/
2. Install required tools: `pip install build twine`
3. Generate API token from PyPI account settings

### Publishing Steps
1. **Build Package**: `python -m build`
2. **Upload to TestPyPI** (optional): `twine upload --repository testpypi dist/*`
3. **Upload to PyPI**: `twine upload dist/*`

### requirements.txt Generation
After publishing, generate hash-enabled requirements.txt:
```bash
pip install learning-pypi-demo-nisimi
pip freeze | grep learning-pypi-demo-nisimi > temp_req.txt
pip-compile --generate-hashes temp_req.txt -o requirements.txt
```

## Testing Plan

### Unit Tests
- Test `hello()` function returns expected string
- Test `hello(name="Alice")` returns personalized greeting
- Test package import works correctly

### Integration Tests
- Test package installation via pip
- Test installation message appears during install
- Test `pip install -r requirements.txt --require-hashes` works

### Manual Testing Checklist
- [ ] Package builds without errors
- [ ] Installation message prints during pip install
- [ ] Package functions work after import
- [ ] Requirements.txt with hashes installs successfully
- [ ] Package appears correctly on PyPI

## File Contents Specification

### setup.py Template
- Custom install command for message printing
- Package metadata (name, version, author, description)
- Python version requirement specification
- Package discovery configuration

### pyproject.toml Template
- Build system specification (setuptools + wheel)
- Project metadata aligned with setup.py
- Modern packaging standards compliance

### Package Code Template
- Simple module structure with clear imports
- Docstrings for all public functions
- Clean, readable code for educational purposes

## Security Considerations
- Use API tokens (not username/password) for PyPI uploads
- Verify package hashes in requirements.txt
- Keep dependencies minimal to reduce attack surface
- Include license file for legal clarity

## Success Criteria
1. Package successfully publishes to PyPI
2. Installation message appears during `pip install`
3. Package functions work as expected after installation
4. Hash-based installation via requirements.txt works
5. Complete learning experience achieved for PyPI publishing process

## Timeline
**Estimated Implementation Time**: 1-2 hours
- Package structure: 30 minutes
- Code implementation: 30 minutes  
- Testing and debugging: 30 minutes
- PyPI publishing: 30 minutes
