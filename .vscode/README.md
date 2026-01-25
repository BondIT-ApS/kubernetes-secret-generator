# 🧱 VSCode Configuration - Kubernetes Secret Generator

This folder contains team-shared VSCode configuration for the Kubernetes Secret Generator project.

## 🚀 Quick Setup

### For New Team Members:

1. **Copy templates to create your local settings:**
   ```bash
   cd .vscode
   cp settings.json.template settings.json
   cp launch.json.template launch.json
   ```

2. **Install recommended extensions:**
   - VSCode will automatically prompt you to install recommended extensions
   - Or manually: `Cmd+Shift+P` → "Extensions: Show Recommended Extensions"

3. **Verify Python interpreter:**
   - `Cmd+Shift+P` → "Python: Select Interpreter"
   - Choose: `venv/bin/python` (from the project root)

## 📁 File Structure

### Shared Files (committed to git):
- **`extensions.json`** - Recommended extensions for the project
- **`tasks.json`** - Build, test, and development tasks
- **`*.json.template`** - Templates for local configuration
- **`README.md`** - This setup guide

### Local Files (ignored by git):
- **`settings.json`** - Your personal VSCode settings (created from template)
- **`launch.json`** - Your debug configurations (created from template)

## 🔧 Key Features

### Flask Application Development:
- ✅ Python virtual environment auto-detection
- ✅ Black formatting (88 char line length)
- ✅ Pylint linting with project-specific rules
- ✅ pytest test discovery and debugging
- ✅ Flask development server debugging

### Full Stack:
- ✅ Docker integration
- ✅ GitHub Actions workflow validation
- ✅ Git workflow enhancements
- ✅ Security scanning integration

## 🧪 Testing & Debugging

### Available Debug Configurations:
- **🧪 Debug Current Test File** - Debug the currently open test file
- **🧪 Debug All Tests** - Run all tests with debugger
- **🚀 Debug Flask App** - Debug the Flask application
- **🐳 Debug Docker Container** - Attach to running Docker container

### Available Tasks (Cmd+Shift+P → "Tasks: Run Task"):
- **🧱 Backend: Setup Virtual Environment** - Create and configure Python venv
- **🚀 Backend: Run Flask App (Development)** - Start Flask in debug mode
- **🧪 Backend: Run Tests** - Execute pytest test suite
- **📊 Backend: Run Tests with Coverage** - Run tests with coverage reporting
- **🎨 Backend: Format Code (Black)** - Format Python code
- **🔍 Backend: Lint (Pylint)** - Run code quality checks
- **🛡️ Backend: Security Scan (Bandit)** - Security vulnerability analysis
- **🔐 Backend: Dependency Security Check (Safety)** - Check dependencies for vulnerabilities
- **🐳 Docker: Build and Run** - Build and start containers
- **🏥 Docker: Health Check** - Test application endpoints
- **🚀 Pre-Push Quality Gate** - Run all quality checks before pushing

## 🔄 Updating Configuration

### For Template Changes:
1. Update the `.template` files
2. Commit and push changes
3. Team members can merge changes into their local files as needed

### For Personal Settings:
- Modify your local `settings.json` and `launch.json`
- These changes stay local and won't be committed

## 🆘 Troubleshooting

### Tests Not Showing Up:
1. Reload window: `Cmd+Shift+P` → "Developer: Reload Window"
2. Refresh tests: `Cmd+Shift+P` → "Python: Test: Refresh Tests"
3. Check Python interpreter is set to `venv/bin/python`

### Python Import Issues:
1. Ensure virtual environment is activated in VSCode
2. Check that Python interpreter points to project venv
3. Restart Python language server: `Cmd+Shift+P` → "Python: Restart Language Server"

### Flask Debug Issues:
1. Verify environment variables are set correctly
2. Check that port 5000 is available (or 5050 with Docker)
3. Ensure dependencies are installed in venv

## 🌐 Development Workflow

### Local Development:
1. Run: **🧱 Backend: Setup Virtual Environment**
2. Start: **🚀 Backend: Run Flask App (Development)**
3. Test: Open http://localhost:5000 in browser

### Before Committing:
1. Run: **🚀 Pre-Push Quality Gate**
2. Fix any issues found by linting/security scans
3. Ensure all tests pass

---
*Following the LEGO principle - every Kubernetes secret should fit together perfectly! 🧱*
