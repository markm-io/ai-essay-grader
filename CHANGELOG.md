# Changelog

## v0.13.1 (2025-03-04)

### Bug fixes

- Update ci configuration to fetch tags and use main branch for checkout ([`cee0088`](https://github.com/markm-io/ai-essay-grader/commit/cee008888b6d89fe3c0b3c8af120ec4aa0cbd19a))
- Update model mapping for short ai model in grader.py ([`b02bb12`](https://github.com/markm-io/ai-essay-grader/commit/b02bb127f28cf5ccf62530a57a756e4bc2e09425))

## v0.13.0 (2025-03-03)

### Features

- Implement rate limiting and token counting in evaluator for openai api calls ([`df11f37`](https://github.com/markm-io/ai-essay-grader/commit/df11f37fc945a0a875c9b8d5d1c87483f9918338))

## v0.12.0 (2025-03-03)

### Features

- Add tiktoken package and update dependencies in pyproject.toml and uv.lock ([`9ca15ca`](https://github.com/markm-io/ai-essay-grader/commit/9ca15ca945c8dd7c7cc18a649f542d6e800cfef1))

## v0.11.0 (2025-03-03)

### Features

- Updating branch to merge all changes ([`b63e21c`](https://github.com/markm-io/ai-essay-grader/commit/b63e21cec8ee286873a56c524c4b240f7243b42a))

## v0.10.0 (2025-03-03)

### Features

- Refactor story handling to support loading multiple stories from a folder ([`c258ab4`](https://github.com/markm-io/ai-essay-grader/commit/c258ab444b93e7a3fc3e32ce418dacf108eef24f))

## v0.9.0 (2025-03-03)

### Features

- Enhance grading feedback by incorporating grade level and language context in generator.py ([`1c810a7`](https://github.com/markm-io/ai-essay-grader/commit/1c810a79d9e9012115b795406c702259dbf084df))

### Bug fixes

- Correct required fields naming for extended scoring format in validator.py ([`3c3d317`](https://github.com/markm-io/ai-essay-grader/commit/3c3d31798a6809005a617251bec016bdcd400189))
- Update model mapping for extended scoring format in grader.py ([`44dfc66`](https://github.com/markm-io/ai-essay-grader/commit/44dfc66f66012b15142c22ebf124feac97014109))

## v0.8.0 (2025-02-28)

### Features

- Enhance story handling by loading multiple stories from a folder and refactor grading response validation ([`d9212bb`](https://github.com/markm-io/ai-essay-grader/commit/d9212bb05f51f3febea87c60aeaaf6cd028749b5))

## v0.7.1 (2025-02-28)

### Bug fixes

- Update model mapping for item-specific scoring format in grader.py ([`1634502`](https://github.com/markm-io/ai-essay-grader/commit/16345023075b125af730762477203151e6639172))

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
