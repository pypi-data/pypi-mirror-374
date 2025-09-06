# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-05

### Added
- Initial release of Canva Connect API Python client
- Complete OpenAPI-generated client for Canva Connect API (2024-06-18)
- Support for all major API endpoints:
  - App API
  - Asset API  
  - Autofill API
  - Brand Template API
  - Comment API
  - Connect API
  - Design API
  - Design Import API
  - Export API
  - Folder API
  - OAuth API
  - Resize API
  - User API
- Full type annotations with Pydantic v2
- Python 3.9+ support
- OAuth 2.0 + PKCE authentication support
- Comprehensive error handling
- Complete API documentation
- Testing framework setup (pytest, mypy, flake8)

### Features
- **Design Management**: Create, read, update designs
- **Asset Management**: Upload, manage user assets  
- **Autofill**: Automated template data population
- **Export**: Multiple format export support (PNG, JPG, PDF, MP4, etc.)
- **Brand Templates**: Enterprise brand template access
- **Collaboration**: Comments, mentions, and team features
- **Folder Management**: Organize designs and assets
- **OAuth Integration**: Secure user authentication

### Technical
- Generated from OpenAPI specification using OpenAPI Generator v7.15.0
- Built with setuptools and modern Python packaging standards
- Lazy loading for optimal performance
- Comprehensive type checking support
- Production-ready error handling and retries

### Dependencies
- urllib3 (>=2.1.0,<3.0.0)
- python-dateutil (>=2.8.2)
- pydantic (>=2)
- typing-extensions (>=4.7.1)
- lazy-imports (>=1,<2)

## [Unreleased]

### Planned
- Enhanced documentation and examples
- Additional utility functions
- Performance optimizations
- More comprehensive testing coverage