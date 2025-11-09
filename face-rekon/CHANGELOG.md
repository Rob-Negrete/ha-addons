# Changelog

All notable changes to the Face Rekon Home Assistant add-on will be documented in this file.

## [0.3.4-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.3.3-alpha.1...face-rekon-v0.3.4-alpha.1) (2025-11-09)


### ⚡ Performance Improvements

* **docker:** optimize build time and remove unused gfpgan dependency ([#171](https://github.com/Rob-Negrete/ha-addons/issues/171)) ([361819a](https://github.com/Rob-Negrete/ha-addons/commit/361819a1e02ca749f642139e5a6e133739eed574))

## [0.3.3-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.3.2-alpha.1...face-rekon-v0.3.3-alpha.1) (2025-11-08)


### 🐛 Bug Fixes

* **docker:** add jq dependency for configuration parsing ([#169](https://github.com/Rob-Negrete/ha-addons/issues/169)) ([fac5f0d](https://github.com/Rob-Negrete/ha-addons/commit/fac5f0defc4c09cfb823b1a5510880efe340ebb0))

## [0.3.2-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.3.1-alpha.1...face-rekon-v0.3.2-alpha.1) (2025-11-06)


### 🐛 Bug Fixes

* **config:** remove armv7 architecture support ([#167](https://github.com/Rob-Negrete/ha-addons/issues/167)) ([204a372](https://github.com/Rob-Negrete/ha-addons/commit/204a3727f0976939af03dd58b2b898e21151db33))

## [0.3.1-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.3.0-alpha.1...face-rekon-v0.3.1-alpha.1) (2025-11-04)


### 🐛 Bug Fixes

* **docker:** update libglib2.0-0 to libglib2.0-0t64 for Debian Trixie ([#165](https://github.com/Rob-Negrete/ha-addons/issues/165)) ([6b076ac](https://github.com/Rob-Negrete/ha-addons/commit/6b076accd84abbfce02a3cd018f133323fcbbfef))

## [0.3.0-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.2.8-alpha.1...face-rekon-v0.3.0-alpha.1) (2025-11-04)


### ✨ Features

* achieve 74% coverage for /recognize endpoint with comprehensive test strategy ([#95](https://github.com/Rob-Negrete/ha-addons/issues/95)) ([6341e69](https://github.com/Rob-Negrete/ha-addons/commit/6341e69f728b6559abe0755d55ceeeff71ced0c6))
* add smart coverage target selection with validation ([#136](https://github.com/Rob-Negrete/ha-addons/issues/136)) ([bdc5d2d](https://github.com/Rob-Negrete/ha-addons/commit/bdc5d2de96f237db6ae57d44a49be10b02d22e74))
* implement hybrid adaptive thumbnail generation for tiny faces ([#150](https://github.com/Rob-Negrete/ha-addons/issues/150)) ([ae8a747](https://github.com/Rob-Negrete/ha-addons/commit/ae8a747899aacb66e5cd37f89c17813c9dc8845e))
* implement Real-ESRGAN 4x super-resolution for tiny face thumbnails ([#151](https://github.com/Rob-Negrete/ha-addons/issues/151)) ([ae8bfbc](https://github.com/Rob-Negrete/ha-addons/commit/ae8bfbc7ac1e542a97881a593e41dc5904ff5261))
* Improve /assets/&lt;path:filename&gt; endpoint coverage to 78% ([#104](https://github.com/Rob-Negrete/ha-addons/issues/104)) ([9abef0f](https://github.com/Rob-Negrete/ha-addons/commit/9abef0f48485397e0261ec9a529cd66498b50b03))
* Improve debug_test_webp endpoint coverage from 37.5% to 52.1% ([#97](https://github.com/Rob-Negrete/ha-addons/issues/97)) ([948fabd](https://github.com/Rob-Negrete/ha-addons/commit/948fabd14b55fd125aa148697e90184cbcd6eb42))
* Improve loadSnapshot endpoint coverage from 76% to 77% ([#102](https://github.com/Rob-Negrete/ha-addons/issues/102)) ([da0958d](https://github.com/Rob-Negrete/ha-addons/commit/da0958defdeb83708bc8a08efec5ec671f2914e1))
* remove debug endpoint and improve image processing coverage ([#128](https://github.com/Rob-Negrete/ha-addons/issues/128)) ([ab8b2ea](https://github.com/Rob-Negrete/ha-addons/commit/ab8b2ea6be48ec5ef24ac1b4b8203f86f557775c))


### 🐛 Bug Fixes

* add configurable thresholds to reduce false positive face detections ([#164](https://github.com/Rob-Negrete/ha-addons/issues/164)) ([376a8c8](https://github.com/Rob-Negrete/ha-addons/commit/376a8c8fa3c576a3cdd41bc19d71fbdb1ba95769))
* handle LFS file conflicts in coverage-health workflow ([#119](https://github.com/Rob-Negrete/ha-addons/issues/119)) ([fbc73f6](https://github.com/Rob-Negrete/ha-addons/commit/fbc73f688c6328ca4bf32fdffdf5f500c24c0f28))
* move select_coverage_target.py to tests directory ([#141](https://github.com/Rob-Negrete/ha-addons/issues/141)) ([c19fe39](https://github.com/Rob-Negrete/ha-addons/commit/c19fe39762cd50dfccbca1aad87a3351f66c8aa7))
* upgrade qdrant-client to 1.9.0 to fix CVE-2024-3829 ([6fde630](https://github.com/Rob-Negrete/ha-addons/commit/6fde63016127d1c67d784e9dcc21c6c9f7fbba29))


### 📚 Documentation

* enhance /bump-coverage command with Docker integration testing guidelines ([#99](https://github.com/Rob-Negrete/ha-addons/issues/99)) ([97d99de](https://github.com/Rob-Negrete/ha-addons/commit/97d99de3a1c78a70a6937df5d803c12c8fec3e38))


### ♻️ Code Refactoring

* move test images from Git LFS to regular Git tracking ([#121](https://github.com/Rob-Negrete/ha-addons/issues/121)) ([309e53a](https://github.com/Rob-Negrete/ha-addons/commit/309e53a8e5efecf42d28018dead85ed8c4032567))
* remove dead code and fix data prefix parsing to reach 90% coverage ([#161](https://github.com/Rob-Negrete/ha-addons/issues/161)) ([c9e3915](https://github.com/Rob-Negrete/ha-addons/commit/c9e391525440303a7cdd9eea43f1fb8884b28282))
* remove dead code to achieve 92% coverage ([#163](https://github.com/Rob-Negrete/ha-addons/issues/163)) ([15ae4b4](https://github.com/Rob-Negrete/ha-addons/commit/15ae4b44bfafe1ce3a7732285500277dcab36441))
* remove unused Qdrant remote server code to achieve 90%+ coverage ([#162](https://github.com/Rob-Negrete/ha-addons/issues/162)) ([acc688b](https://github.com/Rob-Negrete/ha-addons/commit/acc688b328acd6fa5c22442b541b00a2b9562f00))


### ✅ Tests

* achieve 100% coverage for clasificador.update_face function ([#145](https://github.com/Rob-Negrete/ha-addons/issues/145)) ([49eafad](https://github.com/Rob-Negrete/ha-addons/commit/49eafad9bd353b5c08e9396d31e10fb2b003c369))
* achieve 100% coverage for delete_face function ([#131](https://github.com/Rob-Negrete/ha-addons/issues/131)) ([4ff3d2b](https://github.com/Rob-Negrete/ha-addons/commit/4ff3d2b613b9eb6c8c673bad248b055e8e965825))
* achieve 100% coverage for QdrantAdapter._connect_with_retry ([#139](https://github.com/Rob-Negrete/ha-addons/issues/139)) ([9e4ef45](https://github.com/Rob-Negrete/ha-addons/commit/9e4ef458ecfcd6fdeb632f914dc0527e6e1c467b))
* achieve 100% coverage for save_face_crop_to_file function ([#140](https://github.com/Rob-Negrete/ha-addons/issues/140)) ([bdaaa9f](https://github.com/Rob-Negrete/ha-addons/commit/bdaaa9feeb59e0264a04f8ae08aea922d02eda56))
* achieve 100% coverage for serve_face_image endpoint ([#129](https://github.com/Rob-Negrete/ha-addons/issues/129)) ([ddac922](https://github.com/Rob-Negrete/ha-addons/commit/ddac922283a0dd6073e1cffec2369fa24e66ecb2))
* achieve 100% coverage for update_face method ([#134](https://github.com/Rob-Negrete/ha-addons/issues/134)) ([68f5984](https://github.com/Rob-Negrete/ha-addons/commit/68f59845356a07dc2c15a882195d297048552279))
* achieve coverage for check_recent_detection function ([#133](https://github.com/Rob-Negrete/ha-addons/issues/133)) ([133a674](https://github.com/Rob-Negrete/ha-addons/commit/133a6743d1a105fa8655268af272d13d95f72f1b))
* add comprehensive integration tests for search_similar_faces ([#146](https://github.com/Rob-Negrete/ha-addons/issues/146)) ([214633d](https://github.com/Rob-Negrete/ha-addons/commit/214633dbb1056807744e7dd5db6429322a4818a3))
* add optimized test images for Real-ESRGAN validation ([#152](https://github.com/Rob-Negrete/ha-addons/issues/152)) ([edb7244](https://github.com/Rob-Negrete/ha-addons/commit/edb72449f5f5b069670fdd84e631e4e94afdfc71))
* add Recognize.post exception handler coverage (lines 223-234) ([#158](https://github.com/Rob-Negrete/ha-addons/issues/158)) ([0fc54b8](https://github.com/Rob-Negrete/ha-addons/commit/0fc54b8aaab5e042dfd9e9794474c9cae1b3eed4))
* enhance extract_faces_with_crops coverage to 85.28% with real degraded images ([#149](https://github.com/Rob-Negrete/ha-addons/issues/149)) ([edcebea](https://github.com/Rob-Negrete/ha-addons/commit/edcebea06c5934a57c135513c35a74be15fef165))
* enhance extract_faces_with_crops coverage with real degraded images ([#148](https://github.com/Rob-Negrete/ha-addons/issues/148)) ([639e98e](https://github.com/Rob-Negrete/ha-addons/commit/639e98ec2c4d33150bbb0cde3edcf8bca09e0666))
* enhance identify_all_faces coverage to 84.29% ([#147](https://github.com/Rob-Negrete/ha-addons/issues/147)) ([79b849d](https://github.com/Rob-Negrete/ha-addons/commit/79b849daae4945f151cdb345d238cf9004b1605d))
* improve apply_super_resolution coverage to 100% with error path testing ([#156](https://github.com/Rob-Negrete/ha-addons/issues/156)) ([9766efa](https://github.com/Rob-Negrete/ha-addons/commit/9766efae61b2388333d0e12f7ae1e6b98c5761bb))
* improve apply_super_resolution coverage to 58.1% with Real-ESRGAN integration tests ([#153](https://github.com/Rob-Negrete/ha-addons/issues/153)) ([8207f41](https://github.com/Rob-Negrete/ha-addons/commit/8207f4174e79cf4a40b763d057ece8ea9d42b42f))
* improve extract_faces_with_crops coverage using real face images ([#116](https://github.com/Rob-Negrete/ha-addons/issues/116)) ([aa210d9](https://github.com/Rob-Negrete/ha-addons/commit/aa210d9e9635deef4a4c2812e1a58048289f5ab3))
* improve identify_all_faces borderline/unknown coverage to 90%+ ([#157](https://github.com/Rob-Negrete/ha-addons/issues/157)) ([9cef2b3](https://github.com/Rob-Negrete/ha-addons/commit/9cef2b30490699bd7cb087b50c84350e1db6084f))
* improve identify_all_faces coverage with real face images ([#118](https://github.com/Rob-Negrete/ha-addons/issues/118)) ([5986bfc](https://github.com/Rob-Negrete/ha-addons/commit/5986bfc035cb8b9fe1180c58f9f1bc100d75e14e))
* improve QdrantAdapter connection retry coverage to 100% ([#154](https://github.com/Rob-Negrete/ha-addons/issues/154)) ([f4a3612](https://github.com/Rob-Negrete/ha-addons/commit/f4a36129b5ba1a0b125933544d6fdd4013a39344))
* improve Recognize.post coverage to 84.29% ([#143](https://github.com/Rob-Negrete/ha-addons/issues/143)) ([6142ed0](https://github.com/Rob-Negrete/ha-addons/commit/6142ed0e94b03696b8f6924bb4a95cc16d62322e))


### 🧹 Chores

* cleanup legacy coverage files and improve gitignore ([#144](https://github.com/Rob-Negrete/ha-addons/issues/144)) ([255c0a3](https://github.com/Rob-Negrete/ha-addons/commit/255c0a31f607927fbf46d09469e47dfee743c860))
* improve clasificador.py coverage from 36% to 40% ([#115](https://github.com/Rob-Negrete/ha-addons/issues/115)) ([a38313c](https://github.com/Rob-Negrete/ha-addons/commit/a38313c876d57e2f7a85314c4d9efe7ee44f1817))
* improve clasificador.py coverage from 36% to 41% ([#114](https://github.com/Rob-Negrete/ha-addons/issues/114)) ([2d99f70](https://github.com/Rob-Negrete/ha-addons/commit/2d99f70f4a106b0951ec5aaa5a8b8d0dd11360d9))
* Improve qdrant_adapter.py coverage from 34% to 78% ([#124](https://github.com/Rob-Negrete/ha-addons/issues/124)) ([6b9b345](https://github.com/Rob-Negrete/ha-addons/commit/6b9b3450fa3c4b0d901d2e404e4f15c08a27fa81))
* Improve save_multiple_faces_optimized() coverage from 0% to 100% ([#123](https://github.com/Rob-Negrete/ha-addons/issues/123)) ([1a7ab9e](https://github.com/Rob-Negrete/ha-addons/commit/1a7ab9e58f86d65b84494d906441d02d4ec36974))
* raise coverage baseline from 72% to 80% ([#155](https://github.com/Rob-Negrete/ha-addons/issues/155)) ([7230e44](https://github.com/Rob-Negrete/ha-addons/commit/7230e442b96be00dfb521c21cbcedd910faced0e))

## [0.2.8-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.2.7-alpha.1...face-rekon-v0.2.8-alpha.1) (2025-09-28)


### ✅ Tests

* improve coverage for app.py /recognize endpoint to 80% ([#92](https://github.com/Rob-Negrete/ha-addons/issues/92)) ([88eb512](https://github.com/Rob-Negrete/ha-addons/commit/88eb5126a2e8500f04a8695aefc880a775b2833e))

## [0.2.7-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.2.6-alpha.1...face-rekon-v0.2.7-alpha.1) (2025-09-27)


### 🧹 Chores

* add comprehensive /bump-coverage slash command ([#90](https://github.com/Rob-Negrete/ha-addons/issues/90)) ([a78eec6](https://github.com/Rob-Negrete/ha-addons/commit/a78eec6b3a157767f594933bf71f5d76de02f5a4))

## [0.2.6-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.2.5-alpha.1...face-rekon-v0.2.6-alpha.1) (2025-09-27)


### ✅ Tests

* improve face-rekon coverage to 47.9% with consolidated integration tests ([#87](https://github.com/Rob-Negrete/ha-addons/issues/87)) ([2e771d5](https://github.com/Rob-Negrete/ha-addons/commit/2e771d51d22d549a3631fe0b5fd399cd0fb562b4))

## [0.2.5-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.2.4-alpha.1...face-rekon-v0.2.5-alpha.1) (2025-09-27)


### 🧹 Chores

* update path to face-rekon ([#84](https://github.com/Rob-Negrete/ha-addons/issues/84)) ([39c9df7](https://github.com/Rob-Negrete/ha-addons/commit/39c9df7a05868e4a54501581232c3722bd9a88ce))

## [0.2.4-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.2.3-alpha.1...face-rekon-v0.2.4-alpha.1) (2025-09-25)


### 🧹 Chores

* implement Docker-first integration testing infrastructure ([#69](https://github.com/Rob-Negrete/ha-addons/issues/69)) ([b10c08e](https://github.com/Rob-Negrete/ha-addons/commit/b10c08e97e08ea3986e940a69ae49d83cad68c54))

## [0.2.3-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.2.2-alpha.1...face-rekon-v0.2.3-alpha.1) (2025-09-25)


### 🧹 Chores

* use high-quality snapshot-clean.png for camera icon links ([#65](https://github.com/Rob-Negrete/ha-addons/issues/65)) ([86f9241](https://github.com/Rob-Negrete/ha-addons/commit/86f92416a8dd0aa5b1d0422f0df55e447fb7eef2))

## [0.2.2-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.2.1-alpha.1...face-rekon-v0.2.2-alpha.1) (2025-09-24)


### 🧹 Chores

* align coverage health workflow with actual test environment ([#62](https://github.com/Rob-Negrete/ha-addons/issues/62)) ([8e02771](https://github.com/Rob-Negrete/ha-addons/commit/8e0277102ad67bc07fe5fb9241dc38841af06247))

## [0.2.1-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.2.0-alpha.1...face-rekon-v0.2.1-alpha.1) (2025-09-24)


### 📚 Documentation

* update documentation with current Qdrant architecture ([#60](https://github.com/Rob-Negrete/ha-addons/issues/60)) ([051b3ea](https://github.com/Rob-Negrete/ha-addons/commit/051b3ea0735a92fbfe0072fc6c28cc3688fe60a9))

## [0.2.0-alpha.1](https://github.com/Rob-Negrete/ha-addons/compare/face-rekon-v0.1.2-alpha.1...face-rekon-v0.2.0-alpha.1) (2025-09-24)


### ✨ Features

* sort unclassified faces by newest first ([#55](https://github.com/Rob-Negrete/ha-addons/issues/55)) ([2f12e95](https://github.com/Rob-Negrete/ha-addons/commit/2f12e95990b5a1e8c6fd8fa2ee0ab1e6152535aa))


### 🧹 Chores

* improve log message clarity for face sorting ([#57](https://github.com/Rob-Negrete/ha-addons/issues/57)) ([753db84](https://github.com/Rob-Negrete/ha-addons/commit/753db846588c8466599fa1ebe5cd387145e45876))
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
