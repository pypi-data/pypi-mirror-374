# Changelog

All notable changes to utm-referrer-attribution-parser will be documented in this file.

## [0.1.4] - 2025-08-18

### Added

- Support for Google Ads Campaign ID extraction via `gad_campaignid` parameter
- New `campaign_id` field in webmetic_referrer output for direct campaign ID access
- Enhanced Google Ads tracking parameter support including `gad_campaignid`
- Comprehensive test suite for modern advertising platform tracking parameters
- Examples demonstrating Google Ads campaign tracking functionality

### Enhanced

- Improved Google Ads parameter tracking infrastructure
- Extended click ID priority logic to handle modern Google Ads parameters
- Enhanced documentation with campaign ID extraction examples

### Technical Improvements

- Added `gad_campaignid` to tracked Google Ads parameters
- Updated webmetic output format to include dedicated `campaign_id` field
- Maintained full backward compatibility with existing UTM parameter extraction
- Added 17 new test cases covering Google Ads campaign tracking scenarios

## [0.1.3] - 2025-08-10

### Changed

- Updated contact information
- Changed support email
- Added webmetic.de website links to project metadata

## [0.1.2] - 2025-08-05

### Added

- Advanced domain parsing using `tldextract` for robust international TLD support
- Comprehensive test suite for tldextract integration with 12+ new test cases
- Support for complex TLD scenarios (`.edu.au`, `.gov.br`, `.ac.uk`, etc.)
- Internal navigation detection between subdomains and root domains

### Changed

- **BREAKING**: Added `tldextract>=3.1.0` as a new dependency
- Improved internal referrer detection using root domain comparison instead of exact hostname matching
- Enhanced referrer lookup efficiency - direct jump to root domain instead of recursive subdomain stripping
- Updated referrer parser to handle complex international domains correctly

### Fixed

- Fixed same-domain referrer detection bug where `bauma.de` → `exhibitors.bauma.de` was incorrectly classified as external referral
- Fixed subdomain navigation detection for complex TLDs (`.co.uk`, `.com.au`, etc.)
- Improved domain parsing accuracy for deeply nested subdomains

### Technical Improvements

- Replaced hardcoded TLD list with industry-standard `tldextract` library
- Optimized referrer database lookup performance for complex domains
- Added fallback logic for edge cases where tldextract might fail
- Enhanced test coverage for international domain scenarios

## [0.1.1] - 2025-08-01

### Changed

- Performance optimization for high-traffic scenarios
- Fix UTM source casing inconsistency and standardize search medium
- Implement unified click ID structure for cleaner API

## [0.1.0] - 2025-07-25

### Added

- Initial release with UTM parameter extraction
- Referrer database integration using Snowplow data
- Support for 25+ tracking parameters
- Unified click ID tracking structure
- Auto-updating referrer database
- Comprehensive test suite with 150+ real-world cases
