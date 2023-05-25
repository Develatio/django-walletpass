# Changelog


## [3.0] - 2023-05-25

## Breaking Changes

- deprecate cert based authentication for APNS

## Minor Changes

- replace `pyAPNS2` with `aioapns` to enable Django>=4.0 compatibility and resolve unmaintained `hyper` dependency
- increase minimum Python version to 3.6

### Fixed

- sumer time switch bugfix 

## [2.0] - 2023-01-09

### Added

- lint && test github workflow

### Changed

- upgrade pyopenssl usage due to https://github.com/pyca/cryptography/issues/6456

### Fixed

- use 'with' for resource-allocating operations

## [1.2] - 2020-03-25

### Added

- Support JWT auth in push notifications
