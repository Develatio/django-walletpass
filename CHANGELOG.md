# Changelog

## [4.1] - 2024-07-15

### Changed

- improve handling of timestamps (thanks to GonzaloMachado)
- fix a logical bug that would prevent registrations to get deleted (thanks to GonzaloMachado)

## [4.0] - 2024-07-04

### Breaking changes

- minimum Python version is now 3.10
- minimun Django version is now 3.2.9

### Added

- create an event loop if this app is being executed outside of one
- add a human readable name
- add string representation for various models
- add support for Python 3.10 - 3.12

### Changed

- improve admin (search fields, filter fields, log, etc...)
- handle invalid registrations

## [3.0] - 2023-05-25

### Breaking Changes

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
