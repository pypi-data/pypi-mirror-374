# CHANGELOG

<!-- version list -->

## v0.2.0-alpha.24 (2025-07-25)

### Bug Fixes

- Pin numba to also bring up llvmlite ([#144](https://github.com/aptible/daydream/pull/144),
  [`7bcf3dd`](https://github.com/aptible/daydream/commit/7bcf3dd9202df95d3550b28c047ff4e7139cbac9))


## v0.2.0-alpha.23 (2025-07-25)

### Documentation

- Stub out the Mintlify docs ([#134](https://github.com/aptible/daydream/pull/134),
  [`19aa638`](https://github.com/aptible/daydream/commit/19aa638914e614249dba7553c17b0afc1ae83eb8))

### Features

- Agent create uses default template + include ref to daydream tools list in agent templates
  [SC-34009] ([#142](https://github.com/aptible/daydream/pull/142),
  [`74a0326`](https://github.com/aptible/daydream/commit/74a0326d6e08d91337a04ffd204a19f81d6c18bb))


## v0.2.0-alpha.22 (2025-07-25)

### Features

- Daydream agent quickstart & daydream configure updates
  ([#136](https://github.com/aptible/daydream/pull/136),
  [`bad84c8`](https://github.com/aptible/daydream/commit/bad84c872a7a323e0301bdaa17333175c039f699))


## v0.2.0-alpha.21 (2025-07-24)

### Bug Fixes

- Configure the `default_from` email for the PagerDuty client
  ([#140](https://github.com/aptible/daydream/pull/140),
  [`128e601`](https://github.com/aptible/daydream/commit/128e60121d75890ad0f9bc6d3b21bf7596267ff8))


## v0.2.0-alpha.20 (2025-07-24)

### Features

- Build graph in the background and check the status of the build
  ([#133](https://github.com/aptible/daydream/pull/133),
  [`50ffdaf`](https://github.com/aptible/daydream/commit/50ffdaf8e5b0b1d09c3be3ff6ad187d59b4f34d6))


## v0.2.0-alpha.19 (2025-07-23)

### Bug Fixes

- Networking plugin: implement ping tool with scapy so it does not require root privs
  ([#138](https://github.com/aptible/daydream/pull/138),
  [`b9fc0ab`](https://github.com/aptible/daydream/commit/b9fc0ab5c908d6162b63a8f602501627bc4a7862))

### Features

- Enable trace debugging with MLflow tracking server
  ([#137](https://github.com/aptible/daydream/pull/137),
  [`3edaeb8`](https://github.com/aptible/daydream/commit/3edaeb89635c49a506dc4d54953b7884a99e4057))


## v0.2.0-alpha.18 (2025-07-23)

### Bug Fixes

- Fix an issue causing the server to hang when run from a package
  ([#139](https://github.com/aptible/daydream/pull/139),
  [`0bb9a6f`](https://github.com/aptible/daydream/commit/0bb9a6fedbb90f12b459fa5a711f32b3c0509683))


## v0.2.0-alpha.17 (2025-07-22)

### Features

- Introduce Daydream Agents ([#128](https://github.com/aptible/daydream/pull/128),
  [`7277eb5`](https://github.com/aptible/daydream/commit/7277eb5ac2fcc1ca85ae3dce16f82d6d0e92f233))

- PagerDuty plugin ([#129](https://github.com/aptible/daydream/pull/129),
  [`b15cb2c`](https://github.com/aptible/daydream/commit/b15cb2c7b32f604b22d3947d1656db51ed942b5e))


## v0.2.0-alpha.16 (2025-07-12)

### Features

- Support PAPERTRAIL_API_TOKEN env var ([#125](https://github.com/aptible/daydream/pull/125),
  [`90b1608`](https://github.com/aptible/daydream/commit/90b1608a99fbf09d5653696bc274ee72d406ae48))


## v0.2.0-alpha.15 (2025-07-11)

### Features

- Papertrail search tool 🔎 [SC-33639] ([#117](https://github.com/aptible/daydream/pull/117),
  [`7c5bc61`](https://github.com/aptible/daydream/commit/7c5bc615cbf2195acf35e82af1e7d5d3925e016c))


## v0.2.0-alpha.14 (2025-07-11)

### Bug Fixes

- Improve edge inference performance 🚀 ([#122](https://github.com/aptible/daydream/pull/122),
  [`7335ea5`](https://github.com/aptible/daydream/commit/7335ea5a61c3091c86875e4769740f5e9aa237d8))


## v0.2.0-alpha.13 (2025-07-10)

### Features

- Expose shell tools individually ([#119](https://github.com/aptible/daydream/pull/119),
  [`a54bc5c`](https://github.com/aptible/daydream/commit/a54bc5cb7da07a9a9a84cb68d87ea201f2a8cd05))


## v0.2.0-alpha.12 (2025-07-08)

### Features

- Shell command plugin ([#118](https://github.com/aptible/daydream/pull/118),
  [`187dfd4`](https://github.com/aptible/daydream/commit/187dfd475d06c2a07d53628dd6d60ec1d5f9b639))


## v0.2.0-alpha.11 (2025-07-08)

### Bug Fixes

- Fix Aptible auth by passing headers correctly
  ([#115](https://github.com/aptible/daydream/pull/115),
  [`52047f8`](https://github.com/aptible/daydream/commit/52047f8bee55179f161d08ba2e1e6e0832ffa34b))


## v0.2.0-alpha.10 (2025-07-08)

### Bug Fixes

- Handle errors when retrieving target health for ALBs
  ([#116](https://github.com/aptible/daydream/pull/116),
  [`60c97c7`](https://github.com/aptible/daydream/commit/60c97c718cd3896b14b78b9745f8539ec78567cd))


## v0.2.0-alpha.9 (2025-07-07)

### Bug Fixes

- Upgrade FastMCP and fix the server initialization calls
  ([#114](https://github.com/aptible/daydream/pull/114),
  [`d05d6ab`](https://github.com/aptible/daydream/commit/d05d6abc461cbbda3a55ecdb0e8d26264c2b15a9))


## v0.2.0-alpha.8 (2025-07-07)

### Features

- Various updates to enable hosted/shared use cases
  ([#112](https://github.com/aptible/daydream/pull/112),
  [`784b95f`](https://github.com/aptible/daydream/commit/784b95f24389e189d1d884bbe72b8edc5c7f3ce0))


## v0.2.0-alpha.7 (2025-06-27)

### Features

- Basic Kubernetes integration ([#101](https://github.com/aptible/daydream/pull/101),
  [`c4cb1a1`](https://github.com/aptible/daydream/commit/c4cb1a1ea29597322a001c8e7b2e96f1e59f3864))


## v0.2.0-alpha.6 (2025-06-26)

### Features

- Improve Aptible logs reliability ([#44](https://github.com/aptible/daydream/pull/44),
  [`4b61269`](https://github.com/aptible/daydream/commit/4b61269670d697871ef0743699aedab2e1e5a906))


## v0.2.0-alpha.5 (2025-06-24)

### Bug Fixes

- Plugin context was not being assigned to cached plugins
  ([#100](https://github.com/aptible/daydream/pull/100),
  [`23d69ba`](https://github.com/aptible/daydream/commit/23d69ba0213e38deb175f459a83be05fd3199a5c))


## v0.2.0-alpha.4 (2025-06-24)

### Bug Fixes

- Several minor issues with `daydream configure`
  ([#99](https://github.com/aptible/daydream/pull/99),
  [`5d895b0`](https://github.com/aptible/daydream/commit/5d895b0c2e602212d066f5dfff0bbc2d64ff2c10))


## v0.2.0-alpha.3 (2025-06-17)

### Bug Fixes

- Stage the uv.lock changes for released versions
  ([#95](https://github.com/aptible/daydream/pull/95),
  [`5e80e60`](https://github.com/aptible/daydream/commit/5e80e60c0c4b701af57bbcbd7a93abdb9cf883a3))


## v0.2.0-alpha.2 (2025-06-16)

### Features

- **aws**: Add support for importing S3 buckets into the knowledge graph [SC-33583] [SC-33589]
  ([#80](https://github.com/aptible/daydream/pull/80),
  [`1aa9fed`](https://github.com/aptible/daydream/commit/1aa9fed03cc0f21a08f8ac757885fe5721dd0aff))


## v0.2.0-alpha.1 (2025-06-16)

### Bug Fixes

- Infinite loop, plus bump version ([#77](https://github.com/aptible/daydream/pull/77),
  [`318e43a`](https://github.com/aptible/daydream/commit/318e43aee5ba8c396a042e8ef327e9822eb281da))

- Uv lock oops ([#76](https://github.com/aptible/daydream/pull/76),
  [`1593fae`](https://github.com/aptible/daydream/commit/1593fae034ef96f0db8cd6c44aaa0a2a9924c009))

### Documentation

- Update readme [SC-33559] ([#58](https://github.com/aptible/daydream/pull/58),
  [`80b6962`](https://github.com/aptible/daydream/commit/80b696213892fad7538ba4870ac7dc92ed2497c0))

### Features

- `daydream configure` command [SC-33566] ([#72](https://github.com/aptible/daydream/pull/72),
  [`195b0b3`](https://github.com/aptible/daydream/commit/195b0b3913bffc8faf1baf1d5e97941ffe355cdd))

- `daydream version` ([#78](https://github.com/aptible/daydream/pull/78),
  [`62f77a2`](https://github.com/aptible/daydream/commit/62f77a2369d5259e647bec4a4ef7b5e248732ca9))

- **integrations**: Implement a basic Datadog plugin
  ([#46](https://github.com/aptible/daydream/pull/46),
  [`309ebc9`](https://github.com/aptible/daydream/commit/309ebc90a9ebf5c28865aeaa40c0d771bd76d840))

- **meta**: Automate releases and changelog generation with `python-semantic-release`
  ([#71](https://github.com/aptible/daydream/pull/71),
  [`da63c2c`](https://github.com/aptible/daydream/commit/da63c2c31b6663277c58688e353a1357536376af))


## v0.1.0 (2025-06-02)

- Initial Release
