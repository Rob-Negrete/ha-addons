# Contributing to HA Add-ons

Thank you for your interest in contributing! This document provides guidelines for contributing to our Home Assistant add-ons.

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- Git with conventional commits knowledge

### Development Setup

1. **Clone the repository**:

   ```bash
   git clone <your-repo-url>
   cd ha-addons
   ```

2. **Set up face-rekon development**:

   ```bash
   cd face-rekon
   # Quick setup verification
   python run_tests.py check
   python run_tests.py unit
   ```

3. **Run full test suite** (⭐ Recommended):
   ```bash
   # Memory-optimized integration tests (57 seconds)
   ./run_integration_tests.sh
   ```

## 📝 Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) for automated changelog generation and semantic versioning.

### Commit Types

- **feat**: ✨ New features
- **fix**: 🐛 Bug fixes
- **docs**: 📚 Documentation changes
- **test**: ✅ Adding or modifying tests
- **refactor**: ♻️ Code refactoring
- **perf**: ⚡ Performance improvements
- **build**: 🔧 Build system changes
- **ci**: 🔄 CI/CD changes
- **chore**: 🧹 Maintenance tasks

### Examples

```bash
feat(face-rekon): add new face detection algorithm
fix(face-rekon): resolve memory leak in image processing
docs(face-rekon): update API documentation
test(face-rekon): add unit tests for face matching
```

### Scopes

- `face-rekon`: Changes to the face recognition add-on
- `git-sync-agent`: Changes to the git sync add-on
- `ci`: CI/CD related changes
- `deps`: Dependency updates

## 🧪 Testing

### Quick Reference

| Command | Description | Time | Use Case |
|---------|-------------|------|----------|
| `python run_tests.py unit` | Unit tests | ~0.1s | Development feedback |
| `python run_tests.py check` | Dependency check | ~2s | Setup verification |
| `./run_integration_tests.sh` | **⭐ Recommended** | ~57s | Complete testing |
| `python run_tests.py coverage` | Coverage report | ~60s | Code coverage analysis |

### Running Tests

```bash
# Development workflow (fast feedback)
python run_tests.py unit

# Full test suite (CI/CD ready)
./run_integration_tests.sh

# Individual test categories
python run_tests.py api      # API integration tests
python run_tests.py database # Database tests
python run_tests.py e2e      # End-to-end tests

# Coverage analysis
python run_tests.py coverage
```

### Test Architecture ✅

**Current Status: 24/24 tests passing (100% success rate)**

- **Unit Tests**: 10 tests (~0.04s) - Core business logic
- **API Integration**: 11 tests (~18s) - HTTP endpoints with real Flask
- **Database Integration**: 8 tests (~18s) - TinyDB operations with real ML models
- **End-to-End**: 5 tests (~18s) - Complete user workflows

### Test Structure

```
face-rekon/tests/
├── unit/
│   └── test_simple.py          # Unit tests (10 tests)
├── integration/
│   ├── conftest.py             # Test fixtures and setup
│   ├── test_api_integration.py      # API tests (11 tests)
│   ├── test_database_integration.py # DB tests (8 tests)
│   └── test_end_to_end.py          # E2E tests (5 tests)
├── pytest*.ini                # Test configurations
└── TESTING.md                  # Comprehensive testing guide
```

### Writing Tests

1. **Unit tests**: Fast, isolated logic tests without external dependencies
2. **Integration tests**: Real ML models, databases, and API endpoints
3. **End-to-end tests**: Complete workflows from API to database
4. **All tests use real components** - no mocks for integration testing

**📖 For detailed testing instructions, see [face-rekon/TESTING.md](./face-rekon/TESTING.md)**

## 📋 Pull Request Process

1. **Create a feature branch**:

   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes**:

   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:

   ```bash
   # Quick feedback during development
   python run_tests.py unit
   
   # Full test suite before PR
   ./run_integration_tests.sh
   ```

4. **Commit using conventional commits**:

   ```bash
   git add .
   git commit -m "feat(face-rekon): add new feature description"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feat/your-feature-name
   ```

## 🚀 Release Process

Releases are automated using [release-please](https://github.com/googleapis/release-please):

1. **Merge PRs** with conventional commit messages
2. **Release-please** automatically:
   - Creates release PRs with changelog
   - Bumps versions semantically
   - Creates GitHub releases
   - Builds and publishes Docker images

### Version Bumping

- **patch** (1.0.17 → 1.0.18): `fix:`, `docs:`, `test:`, `chore:`
- **minor** (1.0.17 → 1.1.0): `feat:`
- **major** (1.0.17 → 2.0.0): `feat!:`, `fix!:` (breaking changes)

## 🛠️ Development Guidelines

### Code Quality

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write descriptive commit messages
- Add docstrings to public functions
- Keep functions focused and testable

### Docker Best Practices

- Use multi-stage builds for optimization
- Minimize layer count
- Use specific version tags
- Add health checks where appropriate

### Security

- Never commit secrets or API keys
- Use environment variables for configuration
- Scan dependencies for vulnerabilities
- Follow Home Assistant security guidelines

## 📞 Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check existing docs and README files

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.
