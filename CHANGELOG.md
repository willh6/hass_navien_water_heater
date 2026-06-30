# Changelog

All notable changes to this integration are documented here. This project
adheres loosely to [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-06-29

Stability release. This is a maintenance fork of the (unmaintained) original
integration by **nikshriv** and the later fork by **bakerkj**. The cloud
protocol logic is unchanged; the connection lifecycle was rewritten to stop a
crash.

### Fixed

- **File-descriptor leak that could crash Home Assistant Core.** On every
  cloud disconnect, the old reconnect path spawned a fresh `start()` task while
  leaving the previous AWS IoT MQTT client (and its open sockets) dangling. Over
  a sustained outage this leaked file descriptors until Core hit
  `[Errno 24] No file descriptors available` and the event loop shut down with
  exit code 1. The client is now explicitly disconnected and released before
  every reconnect, and during failed start-up attempts.
- **Overlapping reconnect loops.** Reconnects are now guarded so only one loop
  can ever be active, instead of multiplying on each failure.
- **Blocking I/O in the event loop.** `configureCredentials()` reads the CA
  certificate from disk synchronously; it now runs in an executor, clearing
  Home Assistant's blocking-call warning.
- **Silent temperature-conversion bug** in `water_heater.py`: cross-unit
  set-temperature used `==` instead of `=`, so the converted value was
  discarded. Fixed.

### Changed

- **Exponential reconnect backoff** (15s → capped at 600s), replacing the fixed
  15-second retry that hammered both Navien's cloud and the FD table during
  outages. Backoff resets to the floor after a successful connection.
- Cleaner config-entry unload/reload that always releases the connection.
- Modernized `manifest.json` (added `issue_tracker`, dropped deprecated empty
  `ssdp`/`zeroconf`/`homekit` stubs) and `hacs.json`.
- Added a module version banner and `VERSION` constant.

### Notes

- The underlying `AWSIoTPythonSDK` dependency remains. It is itself
  effectively unmaintained; migrating to a modern AWS IoT / MQTT library is
  tracked as a possible future v3 but was intentionally **not** attempted here,
  to keep this release a low-risk, drop-in stability fix.

## [1.0.1] - prior

- Inherited baseline from bakerkj/nikshriv. See original repositories for
  history prior to this fork.
