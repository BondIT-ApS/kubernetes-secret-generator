# 🧱 Kubernetes Secret Generator

![Build Status](https://img.shields.io/github/actions/workflow/status/BondIT-ApS/kubernetes-secret-generator/docker-publish.yml?branch=main&style=for-the-badge&logo=github)
![License](https://img.shields.io/github/license/BondIT-ApS/kubernetes-secret-generator?style=for-the-badge)
![Code Coverage](https://img.shields.io/codecov/c/github/BondIT-ApS/kubernetes-secret-generator?style=for-the-badge&logo=codecov)
![Repo Size](https://img.shields.io/github/repo-size/BondIT-ApS/kubernetes-secret-generator?style=for-the-badge)

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-kubernetes--secret--generator-blue?logo=docker&style=for-the-badge)](https://hub.docker.com/r/maboni82/kubernetes-secret-generator)
[![Docker Pulls](https://img.shields.io/docker/pulls/maboni82/kubernetes-secret-generator?style=for-the-badge&logo=docker)](https://hub.docker.com/r/maboni82/kubernetes-secret-generator)

> **Like building with LEGO blocks** - snap your environment variables into Kubernetes Secrets with perfect precision! 🎯

A lightweight, enterprise-grade Flask web application that seamlessly transforms `.env` files into production-ready Kubernetes Secret JSON manifests. Built with security and simplicity in mind.

---

## ✨ Key Features

**🎨 Flexible Format Support**
- Handles both `=` and `:` key-value formats
- Supports quoted values (single and double quotes)
- Preserves inline comments with intelligent parsing
- Accepts empty values

**🔐 Security First**
- Automatic Base64 encoding for all secret values
- Kubernetes naming convention validation
- Path traversal protection with filename sanitization
- Regular Bandit and CodeQL security scans

**🚀 Modern Architecture**
- Lightweight Flask backend (single-file simplicity)
- Dockerized for consistent deployments
- Multi-platform Docker images (AMD64, ARM64)
- Stateless design for horizontal scaling

**✅ Enterprise Quality**
- 99% test coverage with comprehensive test suite
- Pylint score: 10/10
- Automated CI/CD pipelines
- SBOM and provenance attestations

---

## 🚀 Quick Start

### Prerequisites
- [Docker](https://www.docker.com/get-started) & [Docker Compose](https://docs.docker.com/compose/install/) (recommended)
- Or Python 3.11+ for local development

### Installation

**Option 1: Docker Compose (Recommended)**
```bash
# Clone the repository
git clone https://github.com/BondIT-ApS/kubernetes-secret-generator.git
cd kubernetes-secret-generator

# Start the application
docker-compose up -d

# Access the web interface
open http://localhost:5050
```

**Option 2: Docker Hub**
```bash
# Pull and run the latest image
docker pull maboni82/kubernetes-secret-generator:latest
docker run -d -p 5050:5000 maboni82/kubernetes-secret-generator:latest

# Access the application
open http://localhost:5050
```

**Option 3: Local Development**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access the application
open http://localhost:5000
```

---

## 📖 Usage

### Web Interface

1. **Navigate to the web interface** at `http://localhost:5050`
2. **Paste your `.env` content** into the text area
3. **Specify the secret name and namespace**
4. **Click "Generate Secret in JSON"** to preview the output
5. **Download the JSON file** and apply it to your cluster

### Supported `.env` Formats

```bash
# Standard format
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=secret-api-key-here

# Quoted values (recommended for special characters)
DB_PASSWORD="p@ssw0rd!with$pecial"
REDIS_URL='redis://localhost:6379'

# Colon format
SMTP_HOST: smtp.gmail.com
SMTP_PORT: "587"

# Empty values
OPTIONAL_CONFIG=
FEATURE_FLAG:

# Inline comments (automatically stripped)
DEBUG=false  # Disable in production
LOG_LEVEL="INFO"  # Can be DEBUG, INFO, WARN, ERROR
```

### Applying to Kubernetes

```bash
# Download the generated JSON
# Apply to your cluster
kubectl apply -f generated-secret.json

# Verify the secret
kubectl get secret your-secret-name -n your-namespace

# View the secret (base64 decoded)
kubectl get secret your-secret-name -n your-namespace -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

---

## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    🧱 Frontend Layer                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │  templates/index.html - Web UI Form                │    │
│  │  • Input: .env content, secret name, namespace     │    │
│  │  • Output: JSON preview + download button          │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ⚙️ Flask Backend (app.py)                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Routes:                                           │    │
│  │  • GET/POST /        - Main UI + JSON generation   │    │
│  │  • POST /download    - File download endpoint      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Core Functions:                                   │    │
│  │  • parse_env()           - Master parser           │    │
│  │  • _parse_env_line()     - Regex-based parsing     │    │
│  │  • _remove_inline_comments() - Comment handling    │    │
│  │  • _is_valid_k8s_key()   - Validation logic        │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  📦 Output: Kubernetes Secret               │
│  {                                                          │
│    "kind": "Secret",                                        │
│    "apiVersion": "v1",                                      │
│    "metadata": { "name": "...", "namespace": "..." },      │
│    "type": "Opaque",                                        │
│    "data": { "KEY": "base64_encoded_value" }               │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Backend**: Python 3.11+ with Flask 3.1
- **Frontend**: HTML5 with vanilla JavaScript
- **Containerization**: Docker with multi-stage builds
- **Testing**: pytest with 99% coverage
- **Security**: Bandit, CodeQL, secure filename sanitization
- **CI/CD**: GitHub Actions with quality gates

---

## 🛠️ Development

### Local Development Setup

```bash
# Clone and setup
git clone https://github.com/BondIT-ApS/kubernetes-secret-generator.git
cd kubernetes-secret-generator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
FLASK_ENV=development FLASK_DEBUG=true python app.py
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Code Quality Checks

```bash
# Format code
black app.py tests/ --line-length=88

# Lint code
pylint app.py --rcfile=.pylintrc

# Security scan
bandit -r app.py -x tests/

# Run all quality checks
black app.py tests/ --check && \
pylint app.py && \
pytest tests/ --cov=. --cov-fail-under=70 && \
bandit -r app.py
```

### VSCode Integration

The repository includes pre-configured VSCode tasks for common development operations:

1. Copy template files:
   ```bash
   cd .vscode
   cp settings.json.template settings.json
   cp launch.json.template launch.json
   ```

2. Run tasks via Command Palette (`Cmd+Shift+P` → "Tasks: Run Task"):
   - 🧱 Setup Virtual Environment
   - 🚀 Run Flask App (Development)
   - 🧪 Run Tests with Coverage
   - 🚀 Pre-Push Quality Gate

See [`.vscode/README.md`](.vscode/README.md) for full details.

---

## 📊 Project Status

### Quality Metrics

| Metric | Status | Target |
|--------|--------|--------|
| 🧪 Test Coverage | 99% | ≥70% |
| ✨ Pylint Score | 10/10 | 10/10 |
| 🛡️ Security Scans | ✅ Passing | All passing |
| 📦 Tests Passing | 35/35 (100%) | 100% |
| 🐳 Docker Build | ✅ Success | Success |

### CI/CD Pipeline

**Pull Request Quality Gate:**
- ✅ Pylint linting (must score 10/10)
- ✅ Pytest with 70% coverage requirement
- ✅ Bandit security scanning
- ✅ CodeQL security analysis
- ✅ Docker integration test

**Production Deployment:**
- ✅ All quality checks must pass
- ✅ Multi-platform Docker build (AMD64, ARM64)
- ✅ Semantic versioning (YY.M.PATCH)
- ✅ SBOM and provenance attestations
- ✅ Automated Docker Hub publishing

---

## 🤝 Contributing

We welcome contributions! Before submitting a PR:

1. **Run the quality gate locally:**
   ```bash
   # Via VSCode task: "🚀 Pre-Push Quality Gate"
   # Or manually:
   black app.py tests/ --check && \
   pylint app.py && \
   pytest tests/ --cov=. --cov-fail-under=70 && \
   bandit -r app.py && \
   docker-compose up -d --build
   ```

2. **Ensure all tests pass** with ≥70% coverage

3. **Follow code style guidelines:**
   - PEP 8 compliance (enforced by Black)
   - Line length: 88 characters (Black default)
   - Pylint score must be 10/10

4. **Security requirements:**
   - No Bandit HIGH or MEDIUM severity issues
   - Pass CodeQL security checks
   - Use `secure_filename()` for user-provided file names

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and test
pytest tests/ --cov=.

# 3. Format and lint
black app.py tests/
pylint app.py

# 4. Commit changes (no AI attribution)
git commit -m "feat: add your feature description"

# 5. Push and create PR
git push origin feature/your-feature-name
```

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 📞 Contact & Support

**Developed by BondIT ApS** 🇩🇰

- 🌐 Website: [bondit.services](https://bondit.services)
- 💼 Company: BondIT ApS
- 📧 Support: Open an issue on GitHub
- 🐛 Bug Reports: [GitHub Issues](https://github.com/BondIT-ApS/kubernetes-secret-generator/issues)

---

## 🗺️ Roadmap

- [x] Multi-format .env support (=, :, quotes)
- [x] Kubernetes key validation
- [x] Docker multi-platform builds
- [x] 99% test coverage
- [x] Automated CI/CD pipelines
- [ ] YAML output format support
- [ ] Batch conversion API endpoint
- [ ] Secret rotation recommendations
- [ ] Integration with secret management tools (Vault, AWS Secrets Manager)

---

## 🙏 Acknowledgments

Built with the LEGO principle: **modular, reliable, and easy to use**. Every environment variable should snap into place perfectly! 🧱

---

<div align="center">

**[⭐ Star this repository](https://github.com/BondIT-ApS/kubernetes-secret-generator)** if you find it useful!

Made with ❤️ by the BondIT team

</div>
