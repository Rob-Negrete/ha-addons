# Changelog

All notable changes to the Face Rekon Home Assistant add-on will be documented in this file.

## [2.0.0](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.0.19...face-rekon-v2.0.0) (2025-09-09)


### ⚠ BREAKING CHANGES

* **face-rekon:** Testing infrastructure requires Docker for integration tests

### ✨ Features

* **face-rekon:** add comprehensive testing infrastructure and release automation ([3e4cbf0](https://github.com/Rob-Negrete/ha-addons/commit/3e4cbf06f009b4825c8b4ee53683406f621f8598))


### 🐛 Bug Fixes

* **ci:** update docker-compose to docker compose commands ([2f9e54b](https://github.com/Rob-Negrete/ha-addons/commit/2f9e54bf7ba74cd4060a6e3bc1221f3c2735282d))
* correct version to patch 1.0.19 instead of major 2.0.0 ([f1528e3](https://github.com/Rob-Negrete/ha-addons/commit/f1528e30bc7e07eb5e6d6f7ab528c4a1ec54bb14))
* **face-rekon:** improve README description clarity ([942b1a8](https://github.com/Rob-Negrete/ha-addons/commit/942b1a8d5e42280a63c0ec8f305d77e05ebb6961))


### 📚 Documentation

* **face-rekon:** enhance README with API endpoints section ([533f80b](https://github.com/Rob-Negrete/ha-addons/commit/533f80b235220d69858db069677927bc13b53c7d))
* **face-rekon:** improve CHANGELOG formatting and descriptions ([922ad71](https://github.com/Rob-Negrete/ha-addons/commit/922ad71322842f1dc5eddc0ba2711cff3bb83bcb))


### 🧹 Chores

* **face-rekon:** add comprehensive testing infrastructure ([2671638](https://github.com/Rob-Negrete/ha-addons/commit/26716386a7240d04d4cb9ac505f327aed2f840fb))
* **face-rekon:** release 1.0.19 ([bfaf837](https://github.com/Rob-Negrete/ha-addons/commit/bfaf83733e3c22f9d2cbde7f5ce1c5598f6d0ab3))

## [1.0.19](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.0.17...face-rekon-v1.0.19) (2025-09-09)

### 🧪 Testing Infrastructure

- **face-rekon:** add comprehensive testing infrastructure and release automation ([3e4cbf0](https://github.com/Rob-Negrete/ha-addons/commit/3e4cbf06f009b4825c8b4ee53683406f621f8598))
  - Add pytest-based unit tests (10 tests) and integration tests (14 tests)
  - Implement Docker-based testing for CI/CD with memory optimization
  - Create professional test runner with smart dependency detection
  - Add session-scoped ML model fixtures for reliable testing
  - Include comprehensive documentation and troubleshooting guides

### 🐛 Bug Fixes

- **ci:** update docker-compose to docker compose commands ([2f9e54b](https://github.com/Rob-Negrete/ha-addons/commit/2f9e54bf7ba74cd4060a6e3bc1221f3c2735282d))
- **face-rekon:** improve README description clarity ([942b1a8](https://github.com/Rob-Negrete/ha-addons/commit/942b1a8d5e42280a63c0ec8f305d77e05ebb6961))

### 📚 Documentation

- **face-rekon:** enhance README with API endpoints section ([533f80b](https://github.com/Rob-Negrete/ha-addons/commit/533f80b235220d69858db069677927bc13b53c7d))

### 🧹 Chores

- **face-rekon:** add comprehensive testing infrastructure ([2671638](https://github.com/Rob-Negrete/ha-addons/commit/26716386a7240d04d4cb9ac505f327aed2f840fb))

## [1.0.17] - 2024-09-09

### ✅ Tests

- feat: Add comprehensive testing infrastructure with pytest
- feat: Add containerized testing with Docker support
- feat: Add unit, integration, and end-to-end test suites
- feat: Add professional test runner with dependency detection
- feat: Add GitHub Actions workflow for automated testing

### 🔧 Build System

- feat: Add multi-architecture Docker support (amd64, arm64, armv7)
- feat: Add dedicated test container with ML dependencies
- feat: Add Docker Compose configuration for testing

### 📚 Documentation

- feat: Add comprehensive testing documentation
- feat: Add test structure and usage guides
- feat: Add professional README for testing setup

### 🔄 Continuous Integration

- feat: Add release-please for automated versioning
- feat: Add semantic versioning with conventional commits
- feat: Add automated changelog generation

## Previous Versions

See commit history for changes prior to v1.0.17.
