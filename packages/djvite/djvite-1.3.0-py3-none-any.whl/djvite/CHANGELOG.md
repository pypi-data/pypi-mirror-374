# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## 1.3.0
### Fixed
- Allow vite to be use with React (directly serve JSX/TSX in dev)
### Changed
- Allow to serve files from vite public directory in dev
- Migrate to Node 24 in examples
- Migrate to Vite 7 by default in examples
### Added
- React example added

## 1.2.1
### Fixed
- Prevent recursion in vite manifest parsing
### Removed
- Yapf removal as it is not maintained anymore, ruff used instead

## 1.2.0
### Added
- Add X-Forwarded proxy headers to vite proxy

## 1.1.0
### Changed
- Auto discover if url should be served with vite or proxified to django


## 1.0.0
### Changed
- Better django config under one DJVITE setting

- Simplest tag syntax

- Use pnpm instead of yarn

### Added
- Initial release
