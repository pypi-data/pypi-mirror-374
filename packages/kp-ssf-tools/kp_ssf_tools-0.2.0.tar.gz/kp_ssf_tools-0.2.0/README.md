# SSF Tools - Forensic Analysis Toolkit

A forensic analysis toolkit for cybersecurity professionals performing PCI Secure Software Framework assessments and general forensic analysis.

Full documentation on [ReadtheDocs]

## Features

- **Volatility Integration**: Automated memory analysis workflows using Volatility 3
- **Rich CLI Interface**: Beautiful, user-friendly command-line interface with colored output
- **Intelligent Process Matching**: Handles process name truncation and partial extension matching
- **File Collision Management**: Smart handling of existing files with user-controlled resolution
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

1. **Python 3.13+** - Required for the SSF Tools CLI
2. **Volatility 3** - Required for memory analysis (installed automatically)
3. **Detect Secrets** -- Required for credential detection (installed automatically)

### Install SSF Tools
These instructions assume you'll use [PyPI's PIPX](https://pipx.pypa.io/latest/installation/) to manage the behind-the-scenese Python virtual environment.

**On Windows**
```powershell
# Install PIPX (recommended)
py -m pip install --user pipx
pipx ensurepath

# Restart your terminal

# Install SSF Tools
pipx install kp-ssf-tools
```

**On MacOS**
```bash
# Install PIPX
brew install pipx
pipx ensurepath

# Restart your terminal

# Install SSF Tools
pipx install kp-ssf-tools
```

**On Linux**
```bash
# Install PIPX (use your distro's package manager)
sudo apt update; sudo apt install pipx
pipx ensurepath

# Restart your terminal

# Install SSF Tools
pipx install kp-ssf-tools
```

## Usage

### Volatility Memory Analysis

The `volatility` sub-command automates extracting useful information from RAM images:

```bash
# Help page
ssf_tools volatility --help

# Basic usage
ssf_tools volatility memory-dump.raw windows interesting-processes.txt
```

### Entropy Analysis

The `analyze entropy` command will compute Shannon entropy using a sliding window over each file.  Results will be stored in `analyze-credentials-<timestamp>.xlsx`.

```bash
# Help page
ssf_tools analyze entropy --help

# Basic usage
ssf_tools analyze entropy src/
```

### Credential Detection

The `analyze credentials` command uses the `detect-secrets` package to identify API keys, credentials, Base64-encoded secrets and other potential secrets.  Results will be stored in `analyze-credentials-<timestamp>.xlsx`.

```bash
# Help page
ssf_tools analyze credentials --help

# Basic usage
ssf_tools analyze credentials src/
```

## Development

```bash
# Install development dependencies
uv sync --dev --extra docs

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Format code
uv run ruff format .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.