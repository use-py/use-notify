# Changelog

## 0.4.0 - 2026-07-11

### Added

- Support dynamic channel credentials by allowing fields such as `token`, `topic`,
  and `user` to be zero-argument callables resolved when a request is built.
- Add CI coverage enforcement with a 95% minimum total coverage threshold.
- Add explicit channel registry lookup for `Notify.from_settings`.

### Fixed

- Avoid rendering `None` in title-less Chanify and WeChat messages.
- Align Email async missing-recipient logging with the documented `to_emails`
  field.
- Avoid over-redacting ordinary single-segment URLs while still redacting
  secret-like provider paths.
- Reject bool values for numeric retry and Email port configuration.

### Tests

- Expand channel, retry, Email, provider response, redaction, and dynamic
  credential coverage. The suite now runs 126 tests with 97% total coverage.
