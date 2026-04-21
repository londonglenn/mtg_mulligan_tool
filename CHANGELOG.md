# Changelog

## [1.1.0] - 2026-04-20
### Added
- Optional in-app model comparison mode
- Toggle to turn model feedback on or off during a session
- Feedback screen showing:
  - player decision
  - model decision
  - keep probability
  - explanation of top model reasons
- Next button flow when model comparison is enabled
- Automatic model download from the server on app startup
- Local model caching for offline use
- Model status display in the GUI
- Additional CSV output fields for model decision data

### Changed
- Keep/Mulligan no longer always auto-advance when model comparison is enabled
- Results CSV schema expanded to include model feedback fields
- Tool now supports server-synced model updates in addition to result uploads

### Fixed
- Better offline behavior by falling back to cached model files when the server is unavailable

## [1.0.1] - 2026-04-13
### Added
- Username prompt at startup
- Automatic upload to hosted server
- Results filenames with username and timestamp
- Random play/draw assignment shown in GUI
- Play/draw saved to CSV

### Changed
- GUI now stays open between hands instead of opening a new window each time