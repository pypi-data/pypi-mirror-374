# Bitbucket Code Reviewer

A CLI tool for reviewing code in Bitbucket repositories. Automate code reviews, check for common issues, and integrate with your development workflow.

## Features

- 🚀 **CLI-based**: Easy to use command-line interface
- 🔍 **Code Review**: Automated code analysis and review suggestions
- 📊 **Rich Output**: Beautiful terminal output with Rich
- 🔧 **Configurable**: Flexible configuration options
- 📦 **PyPI Ready**: Easy installation and distribution

## Installation

### From PyPI (Recommended)

```bash
pip install bitbucket-code-reviewer
```

### From Source

```bash
git clone https://bitbucket.org/yourworkspace/bitbucket-code-reviewer.git
cd bitbucket-code-reviewer
poetry install
poetry build
pip install dist/*.whl
```

## Quick Start

1. **Set up your Bitbucket access token:**

```bash
bb-review config --token YOUR_BITBUCKET_TOKEN
```

2. **Review a repository:**

```bash
# Review a specific pull request
bb-review review workspace/repo --pr 123

# Review a specific branch
bb-review review workspace/repo --branch feature-branch

# Review with token (if not configured)
bb-review review workspace/repo --token YOUR_TOKEN
```

## Usage

### Commands

#### `bb-review review <repository>`

Review code in a Bitbucket repository.

```bash
bb-review review workspace/repo [OPTIONS]
```

**Options:**
- `--pr, -p INTEGER`: Pull request ID to review
- `--branch, -b TEXT`: Branch name to review
- `--token, -t TEXT`: Bitbucket access token

#### `bb-review config`

Manage configuration settings.

```bash
bb-review config [OPTIONS]
```

**Options:**
- `--show`: Show current configuration
- `--token TEXT`: Set Bitbucket access token
- `--workspace TEXT`: Set default workspace

#### `bb-review version`

Show the current version.

```bash
bb-review version
```

## Configuration

The tool supports configuration through:

1. **Command line options** (highest priority)
2. **Environment variables**
3. **Configuration file** (planned)

### Environment Variables

```bash
export BITBUCKET_TOKEN=your_token_here
export BITBUCKET_WORKSPACE=your_default_workspace
```

## Development

### Prerequisites

- Python 3.9+
- Poetry

### Setup

```bash
# Clone the repository
git clone https://bitbucket.org/yourworkspace/bitbucket-code-reviewer.git
cd bitbucket-code-reviewer

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run tests
pytest

# Lint code
ruff check .
ruff format .
```

### Project Structure

```
bitbucket-code-reviewer/
├── bitbucket_code_reviewer/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── bitbucket-pipelines.yml
├── pyproject.toml
├── README.md
└── .gitignore
```

## Contributing

1. Clone the repository: `git clone https://bitbucket.org/yourworkspace/bitbucket-code-reviewer.git`
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `poetry run pytest`
5. Lint code: `poetry run ruff check . && poetry run ruff format .`
6. Commit your changes: `git commit -am 'Add your feature'`
7. Push to the branch: `git push origin feature/your-feature`
8. Create a pull request in Bitbucket

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bitbucket_code_reviewer

# Run specific test
pytest tests/test_main.py::test_version_command
```

## Linting and Formatting

This project uses Ruff for fast Python linting and formatting:

```bash
# Check for issues
ruff check .

# Fix issues automatically
ruff check --fix .

# Format code
ruff format .
```

## CI/CD

This project uses Bitbucket Pipelines for:

- **Testing**: Runs on multiple Python versions (3.9-3.12)
- **Linting**: Ensures code quality with Ruff
- **Publishing**: Automatically publishes to PyPI on main branch pushes and version tags

### Publishing to PyPI

To publish a new version:

1. Update version in `pyproject.toml`
2. Create a git tag: `git tag v0.1.0`
3. Push the tag: `git push origin v0.1.0`

The Bitbucket Pipelines will automatically build and publish to PyPI.

### Setting up PyPI Publishing

1. Go to your Bitbucket repository → Repository settings → Pipelines → Environment variables
2. Add a new variable named `PYPI_TOKEN`
3. Set the value to your PyPI API token (get it from https://pypi.org/manage/account/)
4. Make sure "Secured" is checked to protect the token

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Code quality analysis
- [ ] Security vulnerability scanning
- [ ] Custom rule configuration
- [ ] Integration with CI/CD pipelines
- [ ] Web dashboard
- [ ] Support for other Git hosting services
- [ ] Plugin system for custom reviewers
