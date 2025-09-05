# Changelog

All notable changes to HashID Analyzer will be documented in this file.

## [2.0.0] - 2024-01-XX

### Added
- **Persistent Mode**: New `--persistent` flag allows continuous analysis without restarting
- **Session Management**: Track analysis count, history, and session statistics
- **Interactive Commands**: `help`, `history`, `stats`, `clear` commands in persistent mode
- **PyPI Distribution**: Package now available on PyPI as `hashid-analyzer`
- **Console Scripts**: Multiple entry points (`hashid`, `hash-analyzer`, `hash-id`)
- **Enhanced CLI Interface**: Improved argument parsing and user experience
- **Package Structure**: Properly structured Python package with core and CLI modules
- **Public API**: Simple `analyze()` and `quick_analyze()` functions for programmatic use

### Enhanced
- **Blackploit HashID Integration**: Enhanced pattern detection with confidence ranking
- **JWT Analysis**: Improved JSON Web Token parsing and security analysis
- **Cryptocurrency Support**: Extended address format detection
- **Error Handling**: Better error messages and graceful failure handling
- **Documentation**: Comprehensive README with PyPI installation instructions

### Technical Improvements
- **Modular Design**: Split analyzer into separate core and CLI components
- **Type Hints**: Added comprehensive type annotations
- **Testing Framework**: Prepared structure for pytest-based testing
- **Modern Packaging**: Using pyproject.toml and setuptools for distribution

### Breaking Changes
- Command changed from `python hash_analyzer.py` to `hashid`
- Import changed from `from hash_analyzer import HashTokenAnalyzer` to `from hashid import HashTokenAnalyzer`
- Some internal API methods have been refactored

## [1.0.0] - Initial Release

### Features
- Basic hash format identification
- Token analysis capabilities  
- Encoding/decoding support
- Single-file script distribution