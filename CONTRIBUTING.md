# 🧱 Contributing to Kubernetes Secret Generator

> **Like building with LEGO blocks** - every contribution should snap into place perfectly! 🎯

Thank you for considering contributing to the Kubernetes Secret Generator! This guide will help you understand how to build with us, ensuring your contributions fit seamlessly into our architecture.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Quality Standards](#quality-standards)
- [Submitting Changes](#submitting-changes)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Getting Started

### Prerequisites

Before you start building with us, ensure you have:
- Python 3.11 or higher
- Docker & Docker Compose (for testing)
- Git
- Your favorite code editor (we ❤️ VSCode with our pre-configured tasks)

### Setting Up Your Development Environment

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/kubernetes-secret-generator.git
cd kubernetes-secret-generator

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py

# 5. Run tests to verify setup
pytest tests/ -v
```

## Development Workflow

### 🧱 Building Your First Brick

1. **Find or Create an Issue**
   - Check [existing issues](https://github.com/BondIT-ApS/kubernetes-secret-generator/issues)
   - If creating new, use our issue templates
   - Comment on the issue to let others know you're working on it

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Make Your Changes**
   - Write clean, focused code
   - Follow our [Quality Standards](#quality-standards)
   - Add tests for new functionality

4. **Test Your Changes**
   ```bash
   # Run all tests
   pytest tests/ -v

   # Run with coverage
   pytest tests/ --cov=. --cov-report=term-missing

   # Run quality checks
   black app.py tests/ --check
   pylint app.py
   bandit -r app.py -x tests/
   ```

5. **Commit Your Changes**
   ```bash
   # Use conventional commit format
   git commit -m "feat: add support for YAML output format"
   git commit -m "fix: resolve rate limiting issue with multiple IPs"
   git commit -m "docs: update README with new examples"
   ```

## Quality Standards

Like LEGO's legendary quality control, we maintain strict standards:

### ✅ Required Checks (All Must Pass)

| Check | Requirement | Command |
|-------|-------------|---------|
| **Pylint** | Score: 10/10 | `pylint app.py --rcfile=.pylintrc` |
| **Tests** | Coverage ≥ 70% | `pytest tests/ --cov=. --cov-fail-under=70` |
| **Black** | PEP 8 compliant | `black app.py tests/ --check --line-length=88` |
| **Bandit** | No HIGH/MEDIUM | `bandit -r app.py -x tests/` |
| **actionlint** | Workflows valid | `actionlint .github/workflows/*.yml` |

### 🚀 Pre-Push Quality Gate

Run this command before pushing (or use VSCode task "🚀 Pre-Push Quality Gate"):

```bash
black app.py tests/ --check && \
pylint app.py && \
pytest tests/ --cov=. --cov-fail-under=70 && \
bandit -r app.py && \
actionlint .github/workflows/*.yml
```

### 📏 Code Style Guidelines

**Pylint Configuration** (`.pylintrc`):
- Max line length: 120 characters
- Max args: 6
- Max locals: 20
- Max branches: 12
- Disabled: missing-docstring, too-few-public-methods, invalid-name

**Black Formatting**:
- Line length: 88 characters (Black default)
- Run: `black app.py tests/ --line-length=88`

### 🔒 Security Guidelines

- **Never** commit secrets, API keys, or credentials
- Use `secure_filename()` for user-provided file names
- Validate all user inputs
- Follow OWASP Top 10 best practices
- Pass Bandit security scans

## Submitting Changes

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**
```bash
feat: add YAML output format support
fix: resolve base64 encoding issue with special characters
docs: update installation instructions for Windows
test: add test cases for empty value handling
ci: update GitHub Actions to use Node 20
```

### Branch Naming

- `feature/descriptive-name` - New features
- `fix/bug-description` - Bug fixes
- `docs/what-you-changed` - Documentation
- `refactor/what-you-refactored` - Code refactoring
- `test/what-you-tested` - Test additions/updates

## Issue Guidelines

### 🐛 Reporting Bugs

Use the **Bug Report** template and include:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, Docker version)
- Relevant logs or error messages

### 💡 Suggesting Features

Use the **Feature Request** template and include:
- Clear description of the feature
- Use case and benefits
- Proposed implementation (if you have ideas)
- Alternatives considered

### ❓ Asking Questions

Use the **Question** template for:
- Usage questions
- Clarification on documentation
- Architecture questions
- General discussions

## Pull Request Process

### 📋 Checklist

Before submitting your PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Coverage is ≥ 70% (`pytest tests/ --cov=. --cov-fail-under=70`)
- [ ] Pylint score is 10/10 (`pylint app.py`)
- [ ] Code is formatted with Black (`black app.py tests/ --check`)
- [ ] Security scan passes (`bandit -r app.py`)
- [ ] Documentation is updated (if needed)
- [ ] Commit messages follow conventional format
- [ ] PR description is clear and complete

### 📝 PR Description

Use our **Pull Request template** and include:
- Summary of changes
- Related issue number (closes #123)
- Type of change (bug fix, feature, etc.)
- Test plan
- Screenshots/examples (if applicable)

### 🔄 Review Process

1. **Automated Checks**: PR Quality Gate runs automatically
   - All checks must pass (Pylint, tests, Bandit, CodeQL)
   - Docker build must succeed

2. **Code Review**: Maintainers will review your code
   - Address feedback constructively
   - Make requested changes
   - Ask questions if unclear

3. **Merge**: Once approved and checks pass
   - Squash and merge (default)
   - Delete your branch after merge

### ⏱️ Response Times

We strive to:
- Acknowledge PRs within 48 hours
- Complete initial review within 1 week
- Provide clear feedback on required changes

## Community

### 🤝 Getting Help

- **Documentation**: Check [README.md](README.md) and [CLAUDE.md](CLAUDE.md)
- **Issues**: Search [existing issues](https://github.com/BondIT-ApS/kubernetes-secret-generator/issues)
- **Questions**: Open a new issue with the Question template

### 💬 Communication

- Be respectful and constructive
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)
- Focus on the code, not the person
- Assume good intentions

### 🎯 Contribution Ideas

Not sure where to start? Look for issues labeled:
- `good first issue` - Perfect for newcomers
- `help wanted` - We'd love assistance
- `documentation` - Improve our docs
- `enhancement` - New features to build

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes (for significant contributions)
- Our gratitude and appreciation! 🙏

---

## Questions?

If you have questions about contributing, please:
1. Check this guide and the README
2. Search existing issues
3. Open a new issue with the Question template

---

**Made with ❤️ by the BondIT team** 🇩🇰

*Every great LEGO creation starts with a single brick - thank you for being part of ours!* 🧱
