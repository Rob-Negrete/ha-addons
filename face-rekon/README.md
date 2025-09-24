# Face-Rekon Home Assistant Add-on

AI-powered face recognition add-on for Home Assistant with web UI interface using InsightFace, Qdrant vector database, and Flask REST API.

## 🚀 Quick Start

### Run Tests (Recommended)

```bash
# Full integration test suite (Python + UI)
./run_integration_tests.sh

# Quick unit tests for development
python run_tests.py unit

# Run UI tests only
npm test --prefix ui
```

### Run the Application

```bash
# Development mode
docker compose up

# Production build
docker build -t face-rekon .

# Access web UI at http://localhost:5001/ (when running locally)
```

## 📖 Documentation

- **[TESTING.md](./TESTING.md)** - Complete testing guide and commands
- **[CLAUDE.md](../../CLAUDE.md)** - Project architecture and development guidance

## 🧪 Testing Infrastructure

This project includes a **professional-grade testing framework**:

- ✅ **163 tests** with 100% success rate
- ⏱️ **Fast execution** time for full suite
- 🔒 **Memory-optimized** containerized testing
- 🎯 **CI/CD ready** with proper isolation

### Test Categories

- **Python Unit Tests**: 10 tests (~0.04s) - Fast development feedback
- **Python Integration Tests**: 14 tests (~57s) - Real ML model testing
- **UI Unit Tests**: 139 tests - Component and service testing
- **Coverage**: Complete API, database, UI, and workflow testing

## 🏗️ Architecture

- **Backend**: Python 3.10, Flask, OpenCV, InsightFace
- **Frontend**: Vanilla JavaScript with SOLID principles, responsive design
- **Database**: Qdrant vector database for optimized similarity search
- **API**: RESTful endpoints with Swagger documentation
- **UI Integration**: Home Assistant ingress support
- **Container**: Multi-architecture Docker support

## 🎯 Key Features

- **Web UI**: Face listing, labeling, and management interface
- **Real-time face detection**: Recognition from base64 images
- **Unknown face workflow**: Storage and classification of unidentified faces (sorted by newest first)
- **Vector similarity search**: Qdrant database for efficient face matching
- **REST API**: Comprehensive documentation with Swagger
- **Home Assistant integration**: Seamless ingress support
- **Professional testing**: 163 comprehensive test cases
- **CI/CD ready**: Automated releases and deployment

## 🔧 API Endpoints

- `GET /api/face-rekon/ping` - Health check
- `POST /api/face-rekon/recognize` - Face recognition from base64 image
- `GET /api/face-rekon` - List unclassified faces
- `GET /api/face-rekon/<face_id>` - Get specific face data
- `PATCH /api/face-rekon/<face_id>` - Update face information

## 🖥️ Web UI Features

- **Face Gallery**: Visual grid of unclassified faces with thumbnails
- **Face Details**: Modal interface for viewing and editing face information
- **Classification**: Name and notes assignment for unknown faces
- **Real-time Updates**: Automatic refresh and loading indicators
- **Responsive Design**: Works on desktop and mobile devices

## 📊 Project Status

- ✅ **Core API Features**: Complete and tested
- ✅ **Web UI**: Complete with responsive design
- ✅ **Testing Framework**: 163 comprehensive tests
- ✅ **Documentation**: Complete guides and architecture docs
- ✅ **Home Assistant Integration**: Ingress support enabled
- ✅ **CI/CD**: GitHub Actions with release automation
- ✅ **Production Ready**: Memory-optimized and reliable

---

**For detailed testing instructions, see [TESTING.md](./TESTING.md)**
