# Home Assistant Add-ons Repository

<!-- Test: Verifying Coverage Health Check workflow triggering -->

![Coverage](https://img.shields.io/badge/coverage-49%25-yellow)
![CI](https://github.com/Rob-Negrete/ha-addons/workflows/CI/badge.svg)
![Coverage Health](https://github.com/Rob-Negrete/ha-addons/workflows/Coverage%20Health%20Check/badge.svg)

This repository contains custom Home Assistant add-ons for enhanced home automation capabilities.

## 🏠 Available Add-ons

### Face-Rekon

**AI-powered face recognition add-on**

- **Version**: 0.1.2-alpha.1
- **Architecture**: amd64, armv7, aarch64
- **Description**: Advanced face recognition system using InsightFace, Qdrant vector database, and Flask REST API
- **Port**: 5001

**Key Features:**

- Real-time face detection and recognition
- Unknown face storage and classification workflow
- REST API with Swagger documentation
- Professional testing infrastructure with 49% coverage and automated health checks
- Qdrant vector database for optimized face similarity search
- Comprehensive web UI for face management

**Quick Start:**

```bash
cd face-rekon
docker compose up
```

**Documentation**: [face-rekon/README.md](./face-rekon/README.md)

## 🛠️ Installation

### Prerequisites

- Home Assistant OS 16+
- Docker support
- Sufficient resources for AI/ML processing

### Adding Repository to Home Assistant

1. Navigate to **Supervisor** > **Add-on Store**
2. Click the **3-dot menu** (⋮) in the top right
3. Select **Repositories**
4. Add this repository URL:
   ```
   https://github.com/Rob-Negrete/ha-addons
   ```
5. Click **Add**

### Installing Add-ons

1. Refresh the Add-on Store
2. Find the desired add-on in the **Local add-ons** section
3. Click **Install**
4. Configure options as needed
5. Start the add-on

## 🔧 Configuration

Each add-on includes its own configuration options. Common patterns:

### Storage Paths

Most add-ons use `/config/[addon-name]/` for persistent data:

- Database files
- Configuration files
- Logs
- Cached data

### Port Mapping

Add-ons expose services on specific ports:

- **face-rekon**: 5001 (REST API)

## 📋 Development

### Repository Structure

```
ha-addons/
├── README.md              # This file
├── face-rekon/           # Face recognition add-on
│   ├── config.json       # HA add-on configuration
│   ├── Dockerfile        # Container definition
│   ├── README.md         # Add-on specific docs
│   └── scripts/          # Application code
├── .github/              # GitHub Actions workflows
└── CONTRIBUTING.md       # Development guidelines
```

### Contributing

1. Read [CONTRIBUTING.md](./CONTRIBUTING.md)
2. Follow the existing patterns and conventions
3. Ensure all tests pass before submitting PRs
4. Update documentation as needed

### Building Locally

```bash
# Navigate to specific add-on
cd face-rekon

# Build container
docker build -t local/face-rekon .

# Test locally
docker compose up
```

### Testing

Each add-on includes its own test suite. Example for face-rekon:

```bash
cd face-rekon

# Run full test suite
./run_integration_tests.sh

# Run unit tests only
python run_tests.py unit
```

## 🚀 Release Management

This repository uses automated release management with enhanced CI/CD:

- **Release Please**: Automatic version bumping and changelog generation
- **GitHub Actions**: Automated building, testing, and coverage analysis
- **Semantic Versioning**: Standard version numbering
- **Coverage Health Checks**: Automated test coverage monitoring with fallback mechanisms
- **Cross-Workflow Artifacts**: Reliable artifact sharing between CI and coverage workflows
- **Quality Gates**: Comprehensive testing with unit and integration test suites

## 📖 Documentation

- **Individual Add-ons**: Each add-on contains detailed README.md
- **Project Architecture**: See [CLAUDE.md](../CLAUDE.md) for overall project structure
- **Contributing**: [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines
- **Coverage Health**: [COVERAGE-GUIDE.md](./COVERAGE-GUIDE.md) for test coverage system and troubleshooting

## 🔗 Links

- [Home Assistant Add-on Development](https://developers.home-assistant.io/docs/add-ons/)
- [Docker Documentation](https://docs.docker.com/)
- [Home Assistant Community](https://community.home-assistant.io/)

## 📄 License

Individual add-ons may have their own licensing. Please check each add-on's directory for specific license information.

---

**Repository Status**: Active Development
**Minimum Home Assistant Version**: 2023.1
**Last Updated**: September 2025
