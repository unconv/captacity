# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2024-06-07

### Changed

- TextClips are now cached to make rendering much faster

### Fixed

- The program got stuck when trying to draw a word that was too long for the video. Now a notice is printed in the console and the word will be drawn but cropped.

## [0.3.0] - 2024-06-04

### Added

- Support for using the OpenAI Whisper API instead of local `openai-whisper`

### Changed

- OpenAI Whisper API is used by default instead of local `openai-whisper`

## [0.2.0] - 2024-06-04

### Added

- Ability to pass in custom initial prompt
- Ability to pass in custom Whisper segments

## [0.1.2] - 2024-05-31

### Added

- Font licenses

## [0.1.1] - 2024-05-31

### Added

- Command line entrypoint

### Changed

- Font path in README

## [0.1.0] - 2024-05-31
