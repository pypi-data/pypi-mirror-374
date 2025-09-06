
# 🚀 KHX-Publish-PyPI

[![PyPI version](https://badge.fury.io/py/khx_publish_pypi.svg)](https://pypi.org/project/khx_publish_pypi/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/Khader-X/khx-publish-pypi/ci.yml)](https://github.com/Khader-X/khx-publish-pypi/actions)
[![Code Coverage](https://img.shields.io/codecov/c/github/Khader-X/khx-publish-pypi)](https://codecov.io/gh/Khader-X/khx-publish-pypi)

> ✨ **A beautiful, user-friendly CLI tool to streamline Python package publishing to PyPI and TestPyPI**

KHX-Publish-PyPI is an interactive command-line interface that simplifies the entire process of preparing, building, and publishing Python packages. With rich visual feedback, intelligent error handling, and secure token management, it makes package publishing as smooth as a breeze.

## 🌟 Features

- 🎨 **Beautiful Interface**: Rich, colorful output with progress bars and interactive prompts
- 🔍 **Smart Pre-checks**: Validates your package structure, version, and configuration before publishing
- 🔐 **Secure Token Management**: Stores API tokens securely using your system's keyring
- 📦 **One-Command Publishing**: Complete workflow from checks to upload in a single command
- 🧪 **TestPyPI Support**: Publish to TestPyPI first for safe testing
- 📈 **Version Management**: Automatic version bumping with semantic versioning
- 🛠️ **Error Intelligence**: Provides specific suggestions when uploads fail
- 🚀 **CI/CD Ready**: Perfect for automated publishing pipelines

## 📸 Screenshots

### Installation
<!-- ![Installation Screenshot](screenshots/khx-publish-pypi_install.png) -->
<!-- ![Installation Gif](screenshots/khx-publish-pypi_video_installation_version.gif) -->
![Installation Gif](https://raw.githubusercontent.com/Khader-X/khx-publish-pypi/refs/heads/master/screenshots/khx-publish-pypi_video_installation_version.gif)


### Interactive Publishing Workflow
![KHX-Publish-PyPI Demo](screenshots/...)

*Complete guided publishing workflow showing checks, token setup, version bumping, and publishing*

### CLI Interface Examples
![CLI Commands](screenshots/cli-commands.png)
*Available CLI commands and options*

![Pre-publish Checks](screenshots/pre-checks.png)
*Automated validation of package structure and requirements*

## 🛠️ Installation

### From PyPI (Recommended)
```bash
pip install khx-publish-pypi
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
- ✅ Runs pre-publish checks
- 🔑 Manages API token configuration
- 📈 Offers version bumping options
- 🏗️ Builds your package distributions
- 📤 Publishes to TestPyPI and/or PyPI

### Individual Commands
```bash
# Run pre-publish checks
khx-publish-pypi check

# Bump version
khx-publish-pypi bump patch

# Publish to TestPyPI only
khx-publish-pypi publish-test

# Publish to PyPI only
khx-publish-pypi publish-prod
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
- ✅ Version defined in `__version__.py` or `pyproject.toml`

## 🔧 Troubleshooting

### Common Issues

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
