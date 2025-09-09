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
   # Run tests to verify setup
   python run_tests.py unit
   ```

3. **Run containerized tests**:
   ```bash
   docker-compose -f docker-compose.test.yml run --rm unit-tests
   docker-compose -f docker-compose.test.yml run --rm integration-tests
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

### Running Tests

```bash
# Unit tests (fast)
python run_tests.py unit

# Integration tests (requires ML dependencies or Docker)
python run_tests.py integration

# All tests
python run_tests.py all

# Containerized testing (recommended)
docker-compose -f docker-compose.test.yml run --rm integration-tests
```

### Test Structure

```
tests/
├── unit/           # Fast tests, no external dependencies
├── integration/    # Component interaction tests  
└── conftest.py     # Shared test fixtures
```

### Writing Tests

1. **Unit tests**: Test individual functions/classes in isolation
2. **Integration tests**: Test component interactions with mocking
3. **End-to-end tests**: Test complete workflows

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
   python run_tests.py all
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