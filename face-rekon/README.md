# Face-Rekon Home Assistant Add-on

AI-powered face recognition add-on for Home Assistant using InsightFace, FAISS, and Flask REST API.

## 🚀 Quick Start

### Run Tests (Recommended)

```bash
# Full integration test suite (57 seconds)
./run_integration_tests.sh

# Quick unit tests for development
python run_tests.py unit
```

### Run the Application

```bash
# Development mode
docker-compose up

# Production build
docker build -t face-rekon .
```

## 📖 Documentation

- **[TESTING.md](./TESTING.md)** - Complete testing guide and commands
- **[CLAUDE.md](../../CLAUDE.md)** - Project architecture and development guidance

## 🧪 Testing Infrastructure

This project includes a **professional-grade testing framework**:

- ✅ **24 tests** with 100% success rate
- ⏱️ **57-second** execution time for full suite
- 🔒 **Memory-optimized** containerized testing
- 🎯 **CI/CD ready** with proper isolation

### Test Categories

- **Unit Tests**: 10 tests (~0.04s) - Fast development feedback
- **Integration Tests**: 14 tests (~57s) - Real ML model testing
- **Coverage**: Complete API, database, and workflow testing

## 🏗️ Architecture

- **Backend**: Python 3.10, Flask, OpenCV, InsightFace
- **Database**: TinyDB with FAISS vector search
- **API**: RESTful endpoints with Swagger documentation
- **Container**: Multi-architecture Docker support

## 🎯 Key Features

- Real-time face detection and recognition
- Unknown face storage and classification workflow
- REST API with comprehensive documentation
- Professional testing infrastructure
- CI/CD ready with automated releases

## 🔧 API Endpoints

- `GET /face-rekon/ping` - Health check
- `POST /face-rekon/recognize` - Face recognition from base64 image
- `GET /face-rekon` - List unclassified faces
- `GET /face-rekon/<face_id>` - Get specific face data
- `PATCH /face-rekon/<face_id>` - Update face information

## 📊 Project Status

- ✅ **Core Features**: Complete and tested
- ✅ **Testing**: Professional-grade framework
- ✅ **Documentation**: Comprehensive guides
- ✅ **CI/CD**: GitHub Actions with release automation
- ✅ **Production Ready**: Memory-optimized and reliable

---

**For detailed testing instructions, see [TESTING.md](./TESTING.md)**
