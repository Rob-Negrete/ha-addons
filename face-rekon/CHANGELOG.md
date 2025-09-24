# Changelog

All notable changes to the Face Rekon Home Assistant add-on will be documented in this file.

## [0.2.0-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.1.2-alpha.1...face-rekon-v0.2.0-alpha.1) (2025-09-24)


### ✨ Features

* sort unclassified faces by newest first ([#55](https://github.com/Rob-Negrete/ha-addons/issues/55)) ([2f12e95](https://github.com/Rob-Negrete/ha-addons/commit/2f12e95990b5a1e8c6fd8fa2ee0ab1e6152535aa))


### 🧹 Chores

* improve test coverage and remove obsolete code ([#51](https://github.com/Rob-Negrete/ha-addons/issues/51)) ([c5292b9](https://github.com/Rob-Negrete/ha-addons/commit/c5292b9e8618ae96a8676c8abecb8080f4842628))

## [0.1.2-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.1.1-alpha.1...face-rekon-v0.1.2-alpha.1) (2025-09-24)


### ✨ Features

* enhance UI with timestamp tooltips and source snapshot modal ([#48](https://github.com/Rob-Negrete/ha-addons/issues/48)) ([e8ad196](https://github.com/Rob-Negrete/ha-addons/commit/e8ad196bc1f668e37a5772df6d8befeb9ad684c4))

## [0.1.1-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.1.0-alpha.1...face-rekon-v0.1.1-alpha.1) (2025-09-23)


### ✨ Features

* enhance Home Assistant add-on description with optimized storage mention ([a7382f5](https://github.com/Rob-Negrete/ha-addons/commit/a7382f54e87e498eae6915a12da2d47693a4a0cc))

## [3.0.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v3.0.0...face-rekon-v3.0.1) (2025-09-23)


### 🐛 Bug Fixes

* add missing thumbnail and image_path storage to Qdrant adapter ([#44](https://github.com/Rob-Negrete/ha-addons/issues/44)) ([9ff05eb](https://github.com/Rob-Negrete/ha-addons/commit/9ff05eb73a13a5e6d12cbcf68df330f74663bed4))

## [3.0.0](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v2.2.2...face-rekon-v3.0.0) (2025-09-23)


### ⚠ BREAKING CHANGES

* Remove FAISS and TinyDB dependencies - Migrate    to Qdrant-only architecture ([#41](https://github.com/Rob-Negrete/ha-addons/issues/41))

### ✨ Features

* Remove FAISS and TinyDB dependencies - Migrate    to Qdrant-only architecture ([#41](https://github.com/Rob-Negrete/ha-addons/issues/41)) ([116d887](https://github.com/Rob-Negrete/ha-addons/commit/116d887f5cd8eb1feee07cf45a2b0dc098e23009))

## [2.2.2](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v2.2.1...face-rekon-v2.2.2) (2025-09-22)


### 🧹 Chores

* configure docker-compose for embedded Qdrant mode ([#39](https://github.com/Rob-Negrete/ha-addons/issues/39)) ([abbc04a](https://github.com/Rob-Negrete/ha-addons/commit/abbc04aef937eb159d2c96cd0d6272932c7f64be))

## [2.2.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v2.2.0...face-rekon-v2.2.1) (2025-09-22)


### 🐛 Bug Fixes

* resolve Flask reload conflicts with embedded Qdrant ([#37](https://github.com/Rob-Negrete/ha-addons/issues/37)) ([4854259](https://github.com/Rob-Negrete/ha-addons/commit/48542592630d01665afbcf7aa4e27a94fe542fad))

## [2.2.0](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v2.1.0...face-rekon-v2.2.0) (2025-09-22)


### ✨ Features

* add embedded Qdrant mode for Home Assistant OS compatibility ([#35](https://github.com/Rob-Negrete/ha-addons/issues/35)) ([98716a6](https://github.com/Rob-Negrete/ha-addons/commit/98716a6db137200d81fcf679c7b099a675c22762))

## [2.1.0](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v2.0.1...face-rekon-v2.1.0) (2025-09-19)


### ✨ Features

* bump version to 2.0.2 to force Home Assistant image rebuild ([#32](https://github.com/Rob-Negrete/ha-addons/issues/32)) ([814aaf1](https://github.com/Rob-Negrete/ha-addons/commit/814aaf15996b6422c31513b8a22ab2b536c9791d))

## [2.0.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v2.0.0...face-rekon-v2.0.1) (2025-09-19)


### 🐛 Bug Fixes

* post-merge stability improvements for Qdrant integration ([#30](https://github.com/Rob-Negrete/ha-addons/issues/30)) ([3ebde42](https://github.com/Rob-Negrete/ha-addons/commit/3ebde42da218a152803e548ea7ab20166ad74f22))

## [2.0.0](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.3.0...face-rekon-v2.0.0) (2025-09-19)

### ⚠ BREAKING CHANGES

- Complete migration to Qdrant vector database architecture

### ✨ Features

- migrate face recognition from TinyDB+FAISS to Qdrant vector database ([9be4af7](https://github.com/Rob-Negrete/ha-addons/commit/9be4af768a6f964c0c272a365fd4aeeafa5734f1))

## [1.3.0](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.2.6...face-rekon-v1.3.0) (2025-09-19)

### ✨ Features

- implement smart grouping suggestions for borderline face matches ([6220bcb](https://github.com/Rob-Negrete/ha-addons/commit/6220bcbecaecced80a709dcc48c6c03ff4a04358))

## [1.2.6](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.2.5...face-rekon-v1.2.6) (2025-09-18)

### 🐛 Bug Fixes

- add noqa comment for Black/flake8 slice notation conflict ([034e840](https://github.com/Rob-Negrete/ha-addons/commit/034e8402478c4e28e566f70128911b32f02df4a5))
- resolve CI flake8 linting errors and improve thumbnail directory handling ([1d788ce](https://github.com/Rob-Negrete/ha-addons/commit/1d788ce1a8f7001b8932e33a63f43d7e0450636e))
- resolve CI permission errors and test environment compatibility ([a321b1b](https://github.com/Rob-Negrete/ha-addons/commit/a321b1b19159d909d7eabbfa43ac0ce554a12d19))
- shorten comment to satisfy flake8 line length requirement ([1ac6507](https://github.com/Rob-Negrete/ha-addons/commit/1ac6507b10ce554c4e3419cc7d09d57ef0bd551a))

## [1.2.5](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.2.4...face-rekon-v1.2.5) (2025-09-18)

### 🧹 Chores

- optimize TinyDB storage with file-based thumbnails and embedding deduplication ([04bf067](https://github.com/Rob-Negrete/ha-addons/commit/04bf06724093bdfe13f7f698e5c0b6b42a8797c7))

## [1.2.4](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.2.3...face-rekon-v1.2.4) (2025-09-18)

### 🐛 Bug Fixes

- implement robust database recovery mechanism for TinyDB corruption ([ce832f2](https://github.com/Rob-Negrete/ha-addons/commit/ce832f2589b115f18ce2022df3bbecb1f81fca72))

## [1.2.3](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.2.2...face-rekon-v1.2.3) (2025-09-18)

### 🐛 Bug Fixes

- resolve WEBP image processing and 404 error filtering in face recognition ([c094fc9](https://github.com/Rob-Negrete/ha-addons/commit/c094fc96cf419df98b15e51cf864277b0e69ba39))

## [1.2.2](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.2.1...face-rekon-v1.2.2) (2025-09-18)

### 🐛 Bug Fixes

- improve WEBP support and 404 error filtering in face recognition ([f517be9](https://github.com/Rob-Negrete/ha-addons/commit/f517be991198b32babf22263c34a024926d02b74))

## [1.2.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.2.0...face-rekon-v1.2.1) (2025-09-18)

### 🐛 Bug Fixes

- add comprehensive logging and WEBP support for face recognition ([d6524b4](https://github.com/Rob-Negrete/ha-addons/commit/d6524b469c04bd90d5a0012f0de4d0d9c4e1f910))
- resolve critical formatting issues and improve code quality ([50ddc43](https://github.com/Rob-Negrete/ha-addons/commit/50ddc437c0d39f1816ddf11d32be491ebeeff164))
- update test mocks for robust image loading ([c42a2d1](https://github.com/Rob-Negrete/ha-addons/commit/c42a2d146846b75e8c5fa1afd41c173f1569aaa6))

## [1.2.0](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.1.0...face-rekon-v1.2.0) (2025-09-18)

### ✨ Features

- **face-rekon:** implement face extraction and quality filtering for issue [#19](https://github.com/Rob-Negrete/ha-addons/issues/19) ([336b763](https://github.com/Rob-Negrete/ha-addons/commit/336b7636b334496a68f2066b1232df74f3710100))
- Implement local image serving for face thumbnails ([#17](https://github.com/Rob-Negrete/ha-addons/issues/17)) ([d0e9df5](https://github.com/Rob-Negrete/ha-addons/commit/d0e9df58949b38f8acb0d975749ee9a8abb9955b))

## [1.1.0](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.0.21...face-rekon-v1.1.0) (2025-09-17)

### ✨ Features

- **face-rekon:** add comprehensive web UI for face management ([10a5b4c](https://github.com/Rob-Negrete/ha-addons/commit/10a5b4ce169d27504ca9e963d2189b0c4ac5a751))

## [1.0.21](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.0.21...face-rekon-v1.0.21) (2025-09-12)

### ⚠ BREAKING CHANGES

- **face-rekon:** Testing infrastructure requires Docker for integration tests

### ✨ Features

- Add comprehensive coverage health checks with green/red/amber status indicators ([dad136f](https://github.com/Rob-Negrete/ha-addons/commit/dad136fa16bc23a5b316c0ef5433413201df6202))
- Add comprehensive coverage health checks with green/red/amber status indicators ([#13](https://github.com/Rob-Negrete/ha-addons/issues/13)) ([e3b3ad4](https://github.com/Rob-Negrete/ha-addons/commit/e3b3ad4158b06374ddabaac34e922372df266a09))
- **face-rekon:** add comprehensive testing infrastructure and release automation ([3e4cbf0](https://github.com/Rob-Negrete/ha-addons/commit/3e4cbf06f009b4825c8b4ee53683406f621f8598))

### 🐛 Bug Fixes

- **ci:** update docker-compose to docker compose commands ([2f9e54b](https://github.com/Rob-Negrete/ha-addons/commit/2f9e54bf7ba74cd4060a6e3bc1221f3c2735282d))
- correct version to patch 1.0.19 instead of major 2.0.0 ([f1528e3](https://github.com/Rob-Negrete/ha-addons/commit/f1528e30bc7e07eb5e6d6f7ab528c4a1ec54bb14))
- **face-rekon:** Fixed imports order ([2580f0b](https://github.com/Rob-Negrete/ha-addons/commit/2580f0b80362cab46b85dc5c84f00ec2fec0b9f1))
- **face-rekon:** improve README description clarity ([942b1a8](https://github.com/Rob-Negrete/ha-addons/commit/942b1a8d5e42280a63c0ec8f305d77e05ebb6961))
- resolve OpenCV compatibility issues and improve test coverage ([30edf81](https://github.com/Rob-Negrete/ha-addons/commit/30edf81981aba47e586c433093a01293028f2512))
- resolve OpenCV compatibility issues and improve test coverage ([72548ad](https://github.com/Rob-Negrete/ha-addons/commit/72548ad2c0d21ce35997bf6f56cfd1d815638fd6))
- resolve test import paths and mocking for GitHub Actions workflow ([c38b3ca](https://github.com/Rob-Negrete/ha-addons/commit/c38b3ca5030cbb834a1923e70da0988d09d7d211))

### 📚 Documentation

- **face-rekon:** enhance README with API endpoints section ([533f80b](https://github.com/Rob-Negrete/ha-addons/commit/533f80b235220d69858db069677927bc13b53c7d))
- **face-rekon:** improve CHANGELOG formatting and descriptions ([922ad71](https://github.com/Rob-Negrete/ha-addons/commit/922ad71322842f1dc5eddc0ba2711cff3bb83bcb))

### 🔄 Continuous Integration

- skip CI workflow for release-please auto-generated branches ([#6](https://github.com/Rob-Negrete/ha-addons/issues/6)) ([6605d53](https://github.com/Rob-Negrete/ha-addons/commit/6605d5356cd8354ee48a9a2222d3a769218b9087))

### 🧹 Chores

- **face-rekon:** add comprehensive testing infrastructure ([2671638](https://github.com/Rob-Negrete/ha-addons/commit/26716386a7240d04d4cb9ac505f327aed2f840fb))
- **face-rekon:** Apply lint rules to integration tests files ([06fd747](https://github.com/Rob-Negrete/ha-addons/commit/06fd7476d771bdfde00ff819851e079234164662))
- **face-rekon:** Formated file according lint rules ([266b335](https://github.com/Rob-Negrete/ha-addons/commit/266b335068deaaaeb8070aba6eb59913f4cedb42))
- **face-rekon:** release 1.0.19 ([bfaf837](https://github.com/Rob-Negrete/ha-addons/commit/bfaf83733e3c22f9d2cbde7f5ce1c5598f6d0ab3))
- release 1.0.20 ([a53ac9b](https://github.com/Rob-Negrete/ha-addons/commit/a53ac9b56e3e2108b34277dbf93314d127d16713))
- release 2.0.0 ([4ccf76e](https://github.com/Rob-Negrete/ha-addons/commit/4ccf76eb81fe2c474b966d303a93d68913f671f5))

## [1.0.21](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.0.21...face-rekon-v1.0.21) (2025-09-11)

### ⚠ BREAKING CHANGES

- **face-rekon:** Testing infrastructure requires Docker for integration tests

### ✨ Features

- **face-rekon:** add comprehensive testing infrastructure and release automation ([3e4cbf0](https://github.com/Rob-Negrete/ha-addons/commit/3e4cbf06f009b4825c8b4ee53683406f621f8598))

### 🐛 Bug Fixes

- **ci:** update docker-compose to docker compose commands ([2f9e54b](https://github.com/Rob-Negrete/ha-addons/commit/2f9e54bf7ba74cd4060a6e3bc1221f3c2735282d))
- correct version to patch 1.0.19 instead of major 2.0.0 ([f1528e3](https://github.com/Rob-Negrete/ha-addons/commit/f1528e30bc7e07eb5e6d6f7ab528c4a1ec54bb14))
- **face-rekon:** Fixed imports order ([2580f0b](https://github.com/Rob-Negrete/ha-addons/commit/2580f0b80362cab46b85dc5c84f00ec2fec0b9f1))
- **face-rekon:** improve README description clarity ([942b1a8](https://github.com/Rob-Negrete/ha-addons/commit/942b1a8d5e42280a63c0ec8f305d77e05ebb6961))
- resolve OpenCV compatibility issues and improve test coverage ([30edf81](https://github.com/Rob-Negrete/ha-addons/commit/30edf81981aba47e586c433093a01293028f2512))
- resolve OpenCV compatibility issues and improve test coverage ([72548ad](https://github.com/Rob-Negrete/ha-addons/commit/72548ad2c0d21ce35997bf6f56cfd1d815638fd6))
- resolve test import paths and mocking for GitHub Actions workflow ([c38b3ca](https://github.com/Rob-Negrete/ha-addons/commit/c38b3ca5030cbb834a1923e70da0988d09d7d211))

### 📚 Documentation

- **face-rekon:** enhance README with API endpoints section ([533f80b](https://github.com/Rob-Negrete/ha-addons/commit/533f80b235220d69858db069677927bc13b53c7d))
- **face-rekon:** improve CHANGELOG formatting and descriptions ([922ad71](https://github.com/Rob-Negrete/ha-addons/commit/922ad71322842f1dc5eddc0ba2711cff3bb83bcb))

### 🔄 Continuous Integration

- skip CI workflow for release-please auto-generated branches ([#6](https://github.com/Rob-Negrete/ha-addons/issues/6)) ([6605d53](https://github.com/Rob-Negrete/ha-addons/commit/6605d5356cd8354ee48a9a2222d3a769218b9087))

### 🧹 Chores

- **face-rekon:** add comprehensive testing infrastructure ([2671638](https://github.com/Rob-Negrete/ha-addons/commit/26716386a7240d04d4cb9ac505f327aed2f840fb))
- **face-rekon:** Apply lint rules to integration tests files ([06fd747](https://github.com/Rob-Negrete/ha-addons/commit/06fd7476d771bdfde00ff819851e079234164662))
- **face-rekon:** Formated file according lint rules ([266b335](https://github.com/Rob-Negrete/ha-addons/commit/266b335068deaaaeb8070aba6eb59913f4cedb42))
- **face-rekon:** release 1.0.19 ([bfaf837](https://github.com/Rob-Negrete/ha-addons/commit/bfaf83733e3c22f9d2cbde7f5ce1c5598f6d0ab3))
- release 1.0.20 ([a53ac9b](https://github.com/Rob-Negrete/ha-addons/commit/a53ac9b56e3e2108b34277dbf93314d127d16713))
- release 2.0.0 ([4ccf76e](https://github.com/Rob-Negrete/ha-addons/commit/4ccf76eb81fe2c474b966d303a93d68913f671f5))

## [1.0.21](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.0.20...face-rekon-v1.0.21) (2025-09-11)

### ⚠ BREAKING CHANGES

- **face-rekon:** Testing infrastructure requires Docker for integration tests

### ✨ Features

- **face-rekon:** add comprehensive testing infrastructure and release automation ([3e4cbf0](https://github.com/Rob-Negrete/ha-addons/commit/3e4cbf06f009b4825c8b4ee53683406f621f8598))

### 🐛 Bug Fixes

- **ci:** update docker-compose to docker compose commands ([2f9e54b](https://github.com/Rob-Negrete/ha-addons/commit/2f9e54bf7ba74cd4060a6e3bc1221f3c2735282d))
- correct version to patch 1.0.19 instead of major 2.0.0 ([f1528e3](https://github.com/Rob-Negrete/ha-addons/commit/f1528e30bc7e07eb5e6d6f7ab528c4a1ec54bb14))
- **face-rekon:** Fixed imports order ([2580f0b](https://github.com/Rob-Negrete/ha-addons/commit/2580f0b80362cab46b85dc5c84f00ec2fec0b9f1))
- **face-rekon:** improve README description clarity ([942b1a8](https://github.com/Rob-Negrete/ha-addons/commit/942b1a8d5e42280a63c0ec8f305d77e05ebb6961))
- resolve OpenCV compatibility issues and improve test coverage ([30edf81](https://github.com/Rob-Negrete/ha-addons/commit/30edf81981aba47e586c433093a01293028f2512))
- resolve OpenCV compatibility issues and improve test coverage ([72548ad](https://github.com/Rob-Negrete/ha-addons/commit/72548ad2c0d21ce35997bf6f56cfd1d815638fd6))
- resolve test import paths and mocking for GitHub Actions workflow ([c38b3ca](https://github.com/Rob-Negrete/ha-addons/commit/c38b3ca5030cbb834a1923e70da0988d09d7d211))

### 📚 Documentation

- **face-rekon:** enhance README with API endpoints section ([533f80b](https://github.com/Rob-Negrete/ha-addons/commit/533f80b235220d69858db069677927bc13b53c7d))
- **face-rekon:** improve CHANGELOG formatting and descriptions ([922ad71](https://github.com/Rob-Negrete/ha-addons/commit/922ad71322842f1dc5eddc0ba2711cff3bb83bcb))

### 🧹 Chores

- **face-rekon:** add comprehensive testing infrastructure ([2671638](https://github.com/Rob-Negrete/ha-addons/commit/26716386a7240d04d4cb9ac505f327aed2f840fb))
- **face-rekon:** Apply lint rules to integration tests files ([06fd747](https://github.com/Rob-Negrete/ha-addons/commit/06fd7476d771bdfde00ff819851e079234164662))
- **face-rekon:** Formated file according lint rules ([266b335](https://github.com/Rob-Negrete/ha-addons/commit/266b335068deaaaeb8070aba6eb59913f4cedb42))
- **face-rekon:** release 1.0.19 ([bfaf837](https://github.com/Rob-Negrete/ha-addons/commit/bfaf83733e3c22f9d2cbde7f5ce1c5598f6d0ab3))
- release 1.0.20 ([a53ac9b](https://github.com/Rob-Negrete/ha-addons/commit/a53ac9b56e3e2108b34277dbf93314d127d16713))
- release 2.0.0 ([4ccf76e](https://github.com/Rob-Negrete/ha-addons/commit/4ccf76eb81fe2c474b966d303a93d68913f671f5))

## [1.0.20](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v1.0.19...face-rekon-v1.0.20) (2025-09-11)

### ⚠ BREAKING CHANGES

- **face-rekon:** Testing infrastructure requires Docker for integration tests

### ✨ Features

- **face-rekon:** add comprehensive testing infrastructure and release automation ([3e4cbf0](https://github.com/Rob-Negrete/ha-addons/commit/3e4cbf06f009b4825c8b4ee53683406f621f8598))

### 🐛 Bug Fixes

- **ci:** update docker-compose to docker compose commands ([2f9e54b](https://github.com/Rob-Negrete/ha-addons/commit/2f9e54bf7ba74cd4060a6e3bc1221f3c2735282d))
- correct version to patch 1.0.19 instead of major 2.0.0 ([f1528e3](https://github.com/Rob-Negrete/ha-addons/commit/f1528e30bc7e07eb5e6d6f7ab528c4a1ec54bb14))
- **face-rekon:** Fixed imports order ([2580f0b](https://github.com/Rob-Negrete/ha-addons/commit/2580f0b80362cab46b85dc5c84f00ec2fec0b9f1))
- **face-rekon:** improve README description clarity ([942b1a8](https://github.com/Rob-Negrete/ha-addons/commit/942b1a8d5e42280a63c0ec8f305d77e05ebb6961))

### 📚 Documentation

- **face-rekon:** enhance README with API endpoints section ([533f80b](https://github.com/Rob-Negrete/ha-addons/commit/533f80b235220d69858db069677927bc13b53c7d))
- **face-rekon:** improve CHANGELOG formatting and descriptions ([922ad71](https://github.com/Rob-Negrete/ha-addons/commit/922ad71322842f1dc5eddc0ba2711cff3bb83bcb))

### 🧹 Chores

- **face-rekon:** add comprehensive testing infrastructure ([2671638](https://github.com/Rob-Negrete/ha-addons/commit/26716386a7240d04d4cb9ac505f327aed2f840fb))
- **face-rekon:** Apply lint rules to integration tests files ([06fd747](https://github.com/Rob-Negrete/ha-addons/commit/06fd7476d771bdfde00ff819851e079234164662))
- **face-rekon:** Formated file according lint rules ([266b335](https://github.com/Rob-Negrete/ha-addons/commit/266b335068deaaaeb8070aba6eb59913f4cedb42))
- **face-rekon:** release 1.0.19 ([bfaf837](https://github.com/Rob-Negrete/ha-addons/commit/bfaf83733e3c22f9d2cbde7f5ce1c5598f6d0ab3))
- release 2.0.0 ([4ccf76e](https://github.com/Rob-Negrete/ha-addons/commit/4ccf76eb81fe2c474b966d303a93d68913f671f5))

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
