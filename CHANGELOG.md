# Changelog

All notable changes to this project will be documented in this file.


## [1.1.0] - 2020-05-20

### Added
- Streamlined sign-up process
- A patient registration and consent process
- Support for 'Ineligible' patients (recorded, but not monitored)
- Registration confirmation page
- Discharge Required now links staff to discharge form
- Various audit tests
- Tool to authenticate redcap session

### Changed
- Re-ordered many fields in Registration instrument
- Patient Age now based on [registration_date] not [admission_date]
- Pre-existing Condition fields changed from checkboxes to radiobuttos
- Daily observation prompts logic rebuilt
- Separated discharge into separate instrument / survey
- Discharge Required trigger logic changed
- Monitoring status now based on monitoring group and discharge form
- Field [mon_discharge_reason] now defaults to 'HEALTHY'
- Standardised naming of COVID (not Covid) across the project
- Rebuilt alert_update tool to remove need for curl-copy-pastes

### Deprecated - things we intend to take away
- WEEKLY monitoring group patients

### Fixed
- Patient can now skip an observation without getting stuck


## [0.9.0] - 2020-05-05

### Added
- First public release of the system


[1.1.0]: https://github.com/rmhcovid/txtmon/compare/v0.9.0...v1.1.0
[0.9.0]: https://github.com/rmhcovid/txtmon/releases/tag/v0.9.0
