
# 🚀 KHX-Publish-PyPI

[![PyPI version](https://badge.fury.io/py/khx_publish_pypi.svg)](https://pypi.org/project/khx_publish_pypi/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/Khader-X/khx-publish-pypi/ci.yml)](https://github.com/Khader-X/khx-publish-pypi/actions)
[![Code Coverage](https://img.shields.io/codecov/c/github/Khader-X/khx-publish-pypi)](https://codecov.io/gh/Khader-X/khx-publish-pypi)

> ✨ **A beautiful, intelligent CLI tool to streamline Python package publishing to PyPI and TestPyPI**

KHX-Publish-PyPI is an interactive command-line interface that simplifies the entire process of preparing, building, and publishing Python packages. With **enhanced version detection** supporting all modern build backends, rich visual feedback, intelligent error handling, and secure token management, it makes package publishing as smooth as a breeze.

🎯 **NEW**: **Enhanced Version Detection System** - Works with **ANY** modern Python package configuration including setuptools, scikit-build-core, setuptools-scm, flit, hatchling, and more!

## 🆕 What's New in Latest Version

### 🚀 Enhanced Version Detection System
- **✅ Universal compatibility** with all modern Python build backends
- **✅ Intelligent 5-stage fallback** detection process
- **✅ Rich diagnostics** showing detection method, source, and confidence
- **✅ Programmatic API** for advanced integration
- **✅ Comprehensive support** for dynamic versioning configurations

### 📊 Before vs After
**Before**: Limited to basic setuptools configurations  
**After**: Works with setuptools, scikit-build-core, setuptools-scm, flit, hatchling, and more!

**Before**: `🔢 Version .......................... ✅ (0.1.11)`  
**After**: `🔢 Version .......................... ✅ (v0.1.12 (setuptools_dynamic_attr) dynamic backend:setuptools)`

### 🎯 Enhanced Output Example
```
🔢 Version .......................... ✅ (v0.1.12 (setuptools_dynamic_attr) dynamic backend:setuptools)
```
This shows you:
- **Version**: 0.1.12
- **Detection Method**: setuptools_dynamic_attr  
- **Type**: dynamic versioning
- **Build Backend**: setuptools

## 🌟 Features

- 🎨 **Beautiful Interface**: Rich, colorful output with progress bars and interactive prompts
- 🔍 **Smart Pre-checks**: Validates your package structure, version, and configuration before publishing
- � **Enhanced Version Detection**: Comprehensive support for all modern Python packaging approaches
  - ✅ **Static versions** in pyproject.toml
  - ✅ **Dynamic versions** with setuptools, scikit-build-core, setuptools-scm, flit, hatchling
  - ✅ **Intelligent fallback system** with 5-stage detection process
  - ✅ **Rich diagnostics** showing detection method, source, and confidence scoring
- �🔐 **Secure Token Management**: Stores API tokens securely using your system's keyring
- 📦 **One-Command Publishing**: Complete workflow from checks to upload in a single command
- 🧪 **TestPyPI Support**: Publish to TestPyPI first for safe testing
- 📈 **Version Management**: Automatic version bumping with semantic versioning
- 🛠️ **Error Intelligence**: Provides specific suggestions when uploads fail
- 🚀 **CI/CD Ready**: Perfect for automated publishing pipelines

## 📸 Screenshots

<!-- 
### Interactive Publishing Workflow
![KHX-Publish-PyPI Demo](screenshots/...)

*Complete guided publishing workflow showing checks, token setup, version bumping, and publishing*

### CLI Interface Examples
![CLI Commands](screenshots/cli-commands.png)
*Available CLI commands and options*

![Pre-publish Checks](screenshots/pre-checks.png)
*Automated validation of package structure and requirements* -->

## 🛠️ Installation

### From PyPI (Recommended)
```bash
pip install khx-publish-pypi
```

![Installation Gif](https://raw.githubusercontent.com/Khader-X/khx-publish-pypi/refs/heads/master/screenshots/khx-publish-pypi_video_installation_version.gif)


Check the latest version:
```bash
khx-publish-pypi --version
```

### From GitHub (Release or main)
- Install from a tagged GitHub Release asset (requires download first):
  - Go to Releases, download the `.whl` or `.tar.gz` from assets, then:
    ```bash
    pip install path/to/khx_publish_pypi-<version>-py3-none-any.whl
    # or
    pip install path/to/khx_publish_pypi-<version>.tar.gz
    ```
- Or install directly from the repo using pip’s VCS support:
    ```bash
    # specific tag
    pip install git+https://github.com/Khader-X/khx-publish-pypi.git@vX.Y.Z#egg=khx_publish_pypi
    # latest on default branch
    pip install git+https://github.com/Khader-X/khx-publish-pypi.git@main#egg=khx_publish_pypi
    ```

### From Source (Development)
```bash
git clone https://github.com/Khader-X/khx-publish-pypi.git
cd khx-publish-pypi
pip install -e .
```

### Requirements
- Python 3.9+
- `twine` for uploads
- `build` for package building
- `keyring` for secure token storage

## 🚀 Quick Start

1. **Install the package**
   ```bash
   pip install khx-publish-pypi
   ```

2. **Set up your API tokens**
   ```bash
   khx-publish-pypi setup-tokens
   ```

3. **Publish your package**
   ```bash
   khx-publish-pypi run
   ```

That's it! The guided workflow will handle everything else.

## 📖 Usage

### Interactive Publishing (Recommended)
```bash
khx-publish-pypi run
```

This command provides a complete guided experience:
- ✅ Runs pre-publish checks with enhanced version detection
- 🔑 Manages API token configuration
- 📈 Offers version bumping options
- 🏗️ Builds your package distributions
- 📤 Publishes to TestPyPI and/or PyPI

### Individual Commands
```bash
# Run pre-publish checks with enhanced version detection
khx-publish-pypi check

# Bump version
khx-publish-pypi bump patch

# Publish to TestPyPI only
khx-publish-pypi publish-test

# Publish to PyPI only
khx-publish-pypi publish-prod
```

### Programmatic API (New!)

KHX-Publish-PyPI now exposes a powerful programmatic API for version detection:

```python
from khx_publish_pypi import detect_package_version, get_package_version
from pathlib import Path

# Simple version detection (legacy interface)
version = get_package_version(Path("."))
print(f"Version: {version}")

# Enhanced detection with full diagnostics
result = detect_package_version(Path("."))
if result.version_info:
    info = result.version_info
    print(f"Version: {info.version}")
    print(f"Method: {info.method}")
    print(f"Backend: {info.build_backend}")
    print(f"Confidence: {info.confidence}%")
    print(f"Source: {info.source}")
else:
    print(f"Failed: {', '.join(result.attempts)}")
```

## 📚 CLI Commands

| Command | Description |
|---------|-------------|
| `khx-publish-pypi --version` | Show CLI version |
| `khx-publish-pypi check` | Run interactive pre-publish checks |
| `khx-publish-pypi bump [patch\|minor\|major]` | Bump package version |
| `khx-publish-pypi setup-tokens` | Configure API tokens interactively |
| `khx-publish-pypi update-tokens` | Update existing tokens |
| `khx-publish-pypi run` | Complete guided publishing workflow |
| `khx-publish-pypi publish-test` | Publish to TestPyPI |
| `khx-publish-pypi publish-prod` | Publish to PyPI |

### Command Options

#### Token Setup
```bash
# Interactive setup
khx-publish-pypi setup-tokens

# Non-interactive setup
khx-publish-pypi setup-tokens --test-token YOUR_TEST_TOKEN --prod-token YOUR_PROD_TOKEN
```

#### Version Bumping
```bash
khx-publish-pypi bump patch  # 1.0.0 → 1.0.1
khx-publish-pypi bump minor  # 1.0.1 → 1.1.0
khx-publish-pypi bump major  # 1.1.0 → 2.0.0
```

## ⚙️ Configuration

### API Tokens

KHX-Publish-PyPI securely stores your PyPI API tokens using your system's keyring:

- **TestPyPI**: Stored as `khx-publish-testpypi`
- **PyPI**: Stored as `khx-publish-pypi`

#### Getting API Tokens

1. **TestPyPI Token**: [Generate at test.pypi.org](https://test.pypi.org/manage/account/token/)
2. **PyPI Token**: [Generate at pypi.org](https://pypi.org/manage/account/token/)

#### Environment Variables (Alternative)

You can also provide tokens via environment variables:
```bash
export TESTPYPI_TOKEN=your_test_token
export PYPI_TOKEN=your_prod_token
```

### Package Requirements

Your Python package must have:
- ✅ `pyproject.toml` with project metadata
- ✅ `README.md` file
- ✅ `LICENSE` file
- ✅ Package directory in `src/` or root
- ✅ Version defined anywhere! Our enhanced detection supports:
  - Static version in `pyproject.toml`
  - Dynamic versions with setuptools, scikit-build-core, setuptools-scm, flit, hatchling
  - `__version__.py` files in various locations
  - Package `__init__.py` with `__version__` attribute

## 🔍 Enhanced Version Detection

KHX-Publish-PyPI now features a **comprehensive version detection system** that handles all modern Python packaging approaches:

### Supported Configurations

| **Build Backend** | **Configuration Example** | **Detection Result** |
|------------------|---------------------------|---------------------|
| **Static** | `version = "1.0.0"` in pyproject.toml | `✅ v1.0.0 (static)` |
| **Setuptools** | `{attr = "package.__version__"}` | `✅ v1.0.0 (setuptools_dynamic_attr) dynamic backend:setuptools` |
| **Scikit-build-core** | `provider = "scikit_build_core.metadata.regex"` | `✅ v1.0.0 (scikit_build_regex) dynamic backend:scikit-build-core` |
| **Setuptools-SCM** | `[tool.setuptools_scm]` | `✅ v1.0.0 (setuptools_scm) dynamic backend:setuptools-scm` |
| **Flit** | `[tool.flit.module]` | `✅ v1.0.0 (flit_module) dynamic backend:flit` |
| **Hatchling** | `source = "regex"` | `✅ v1.0.0 (hatchling_regex) dynamic backend:hatchling` |

### Intelligent Detection Process

1. **Static version** from pyproject.toml (100% confidence)
2. **Dynamic version** from build backend configs (90-95% confidence)
3. **Direct package import** attempts (85% confidence)
4. **File parsing** of `__version__.py` files (80% confidence)
5. **Setuptools-scm fallback** for git-based projects (70% confidence)

### Rich Diagnostics

When version detection succeeds, you'll see detailed information:
```
🔢 Version .......................... ✅ (v0.1.11 (setuptools_dynamic_attr) dynamic backend:setuptools)
```

When it fails, you get helpful diagnostics:
```
🔢 Version .......................... ❌ Failed to detect version. Tried: static_pyproject_version, dynamic_pyproject_version, import_package_version. Errors: Import failed: No module named 'missing_package'
```

[📖 **Read the Complete Enhanced Version Detection Guide**](ENHANCED_VERSION_DETECTION.md)

## 🔧 Troubleshooting

### Common Issues

#### ❌ Version Detection Failed
**Cause**: Package version not found or improperly configured
**Solutions**: 
1. Ensure `__version__` is properly exported in `__init__.py`:
   ```python
   from .__version__ import __version__
   __all__ = ["__version__"]
   ```
2. Check dynamic version configuration in `pyproject.toml`
3. Verify version file locations match expected patterns
4. Use enhanced diagnostics: `khx-publish-pypi check` shows detailed detection attempts

#### ❌ Upload Fails with 400 Error
**Cause**: Package version already exists on PyPI
**Solution**: Bump the version
```bash
khx-publish-pypi bump patch
```

#### ❌ Authentication Failed (403)
**Cause**: Invalid or expired API token
**Solution**: Reconfigure tokens
```bash
khx-publish-pypi setup-tokens
```

#### ❌ Build Fails
**Cause**: Missing build dependencies or invalid `pyproject.toml`
**Solution**: Install build tools and validate configuration
```bash
pip install build twine
python -m build --help
```

#### ❌ Token Storage Issues
**Cause**: Keyring not available or corrupted
**Solution**: Use environment variables or reinstall keyring
```bash
pip uninstall keyring
pip install keyring
```

### Debug Mode
Enable verbose output for troubleshooting:
```bash
khx-publish-pypi run --verbose
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   python -m pytest
   ```
5. **Submit a pull request**

### Development Setup
```bash
git clone https://github.com/Khader-X/khx-publish-pypi.git
cd khx-publish-pypi
pip install -e ".[dev]"
```

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Add tests for new features

## 📊 CI/CD Integration

KHX-Publish-PyPI works great with CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Publish to PyPI
  run: |
    khx-publish-pypi setup-tokens --test-token ${{ secrets.TEST_PYPI_TOKEN }} --prod-token ${{ secrets.PYPI_TOKEN }}
    khx-publish-pypi publish-prod
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI magic
- Beautiful output powered by [Rich](https://rich.readthedocs.io/)
- Secure token storage via [Keyring](https://github.com/jaraco/keyring)
- Package building with [Build](https://github.com/pypa/build)
- Uploads handled by [Twine](https://github.com/pypa/twine)
- Enhanced version detection supports modern packaging standards

## 📚 Documentation

- 📖 **[Enhanced Version Detection Guide](ENHANCED_VERSION_DETECTION.md)**: Complete guide to the new version detection system
- 🧪 **[Test Examples](test_enhanced_version_detection.py)**: Comprehensive test suite demonstrating all capabilities
- 💻 **[API Usage Examples](example_api_usage.py)**: Programmatic usage examples

## 📞 Support

- 📧 **Email**: abueltayef.khader@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/Khader-X/khx-publish-pypi/issues)
- 📖 **Documentation**: [GitHub Wiki](https://github.com/Khader-X/khx-publish-pypi/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Khader-X/khx-publish-pypi/discussions)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/Khader20">ABUELTAYEF Khader</a>
</p>

<p align="center">
  <a href="https://github.com/Khader-X/khx-publish-pypi">⭐ Star this repo</a> •
  <a href="https://pypi.org/project/khx_publish_pypi/">📦 View on PyPI</a> •
  <a href="https://khaderabueltayef.blogspot.com/">📝 Blog</a>
</p>
