# Changelog

## v0.7.0 (2025-02-27)

### Features

- Update rubric handling to support loading from a folder and refactor related types ([`e0b115d`](https://github.com/markm-io/ai-essay-grader/commit/e0b115d8f6fd42624c184d6f66964dd24c6dd74c))

## v0.6.0 (2025-02-27)

### Features

- Implement pydantic model for grading response validation and enhance rubric loading ([`5e43ebc`](https://github.com/markm-io/ai-essay-grader/commit/5e43ebc6e994c2835cf6f7b15ef8d396152163bc))
- Implement asynchronous csv writing using aiocsv in csv_processor.py ([`7a7ce0d`](https://github.com/markm-io/ai-essay-grader/commit/7a7ce0df7ca53eec3d5df964cce3409c3dffd6ab))

### Bug fixes

- Add response format handling in chat completion parsing ([`607933a`](https://github.com/markm-io/ai-essay-grader/commit/607933a227fb503ce51260c3b927dec3bcbdda86))
- Update model mapping for 'short' scoring format in grader.py ([`dbce7ab`](https://github.com/markm-io/ai-essay-grader/commit/dbce7aba6f24e729f84a70d1a2ed96f2cf8330f3))
- Add aiocsv dependency with version >=1.3.2 in project configuration ([`0aa4c47`](https://github.com/markm-io/ai-essay-grader/commit/0aa4c47cf8dccc8b1f0baac794f1e7ad2505863d))
- Change default scoring format option to none in fine-tuning cli ([`bc8dcc7`](https://github.com/markm-io/ai-essay-grader/commit/bc8dcc7da8e930f9c7acda6c2a3d298b07031652))
- Update api key validation logic to use 'and' condition ([`7750d13`](https://github.com/markm-io/ai-essay-grader/commit/7750d13fded347ef919228aa7225e4ffb301e74b))

## v0.5.0 (2025-02-27)

### Features

- Implement asynchronous csv processing and evaluation with openai api ([`521d9ad`](https://github.com/markm-io/ai-essay-grader/commit/521d9adb84bd7252c822e59c8e01a360032b8a4a))

## v0.4.1 (2025-02-26)

### Bug fixes

- Standardize field names to lowercase in csv processor ([`29624b4`](https://github.com/markm-io/ai-essay-grader/commit/29624b476de734345ac76883fa98a6bbd4c77cc8))
- Add new model mapping for 'short' scoring format in grader ([`9a28aff`](https://github.com/markm-io/ai-essay-grader/commit/9a28aff2283e5345c09b15d647b537e0140a2a05))

## v0.4.0 (2025-02-26)

### Bug fixes

- Make scoring format option mandatory in cli ([`5639c1c`](https://github.com/markm-io/ai-essay-grader/commit/5639c1c741629a1f667051c4ccdb5aafd0d9809f))

### Features

- Update scoring format handling in cli and validation logic ([`dfe151a`](https://github.com/markm-io/ai-essay-grader/commit/dfe151aa44af07ed6c5223eb2a85a81d80b6477b))

## v0.3.0 (2025-02-26)

### Features

- Improve csv processing with progress bar and refactor file handling ([`2318ade`](https://github.com/markm-io/ai-essay-grader/commit/2318adefd8fce0348d47c9495e47884ab8624c32))

## v0.2.0 (2025-02-26)

### Features

- Enhance cli options with detailed help messages for grading parameters ([`81d42ed`](https://github.com/markm-io/ai-essay-grader/commit/81d42ed9463e9544d922bdd394bcf6e240f78890))

## v0.1.0 (2025-02-26)

### Features

- Add optional openai api key parameter to upload and fine-tune commands ([`b36e60f`](https://github.com/markm-io/ai-essay-grader/commit/b36e60fe81f116a5246ce1b94faabf8fff4ce689))
- Initial commit ([`d1e73af`](https://github.com/markm-io/ai-essay-grader/commit/d1e73afb484a1f06d0d586496bc20e8e9c51032c))

### Documentation

- Add @markm-io as a contributor ([`98a90d7`](https://github.com/markm-io/ai-essay-grader/commit/98a90d7dbf63129de2e44e01bdef9a170e59965d))
