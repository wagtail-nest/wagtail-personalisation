# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.17.0] - [UNRELEASED]

- Add Wagtail 7.0, 7.3, and 7.4 support, drop support for Wagtail < 7.0
- Add Django 5.2 and 6.0 support, drop support for Django < 5.2
- Add Python 3.14 support
- Fix Django 5.2 regression in GeoIP module detection (no longer relies on `ImportError` at import time)
- Fix Django 5.2 regression in `get_rules()` when filtering by an unsaved `Segment` instance

## [0.16.0] - 2026-01-27

- Upgrade to Wagtail 7.3, drop support for Wagtail < 4.1
- Add Django 4.2 support, drop support for Django 4.0 and 4.1
- Add Python 3.13 support, drop support for Python 3.9 and below
- Replace wagtailfontawesome with wagtail-font-awesome-svg

## [0.15.3] - 2022-02-04

- Add wagtail >= 2.15 support with get_context_data override instead of get_context

## [0.15.2] - 2021-09-24

- Replace staticfiles tag with static

## [0.15.1] - 2021-07-13

- Remove old versions from test matrix
- Fix button support in wagtail admin for newer wagtail versions

## [0.15.0] - 2021-07-09

- Fix is_authenticated 'bool' object is not callable error
- Add wagtail <=2.11 support
- Use Github Actions to test package instead of Travis CI

## [0.14.0] - 2019-09-27

- Fix 'bool' object is not callable error
- Fix deleting descendants with variants when deleting a page
- Add wagtail 2.6 support

## [0.13.0] - not officially released

- Merged Praekelt fork
- Add custom javascript to segment forms
- bugfix:exclude variant returns queryset when params is queryset
- Added RulePanel, a subclass of InlinePanel, for Rules
- Upgrade to Wagtail > 2.0, drop support for Wagtail < 2

## [0.12.1] - 2018-09-27

- Fix Django version classifier in setup.py

## [0.12.0] - 2018-09-26

- Merged forks of Torchbox and Praekelt
- Wagtail 2 compatibility
- Makefile adjustments for portability
- Adds simple segment forcing for superusers
- Fix excluding pages without variant
- Fix bug on visiting a segment page in the admin
- Use Wagtail's logic in the page count in the dash
- Prevent corrected summary item from counting the root page
- Delete variants of a page that is being deleted
- Add end user and developer documentation
- Add an option to show a personalised block to everyone
- Add origin country rule (#190)
- Return 404 if variant page is accessed directly (#188)
- Do not generate sitemap entries for variants (#187)
- Remove restrictive wagtail dependency version constraint (#192)

## [0.11.3] - unofficially released

- Bugfix: Handle errors when testing an invalid visit count rule

## [0.11.2] - unofficially released

- Bugfix: Stop populating static segments when the count is reached

## [0.11.1] - unofficially released

- Populate entirely static segments from registered Users not active Sessions

## [0.11.0] - unofficially released

- Bug Fix: Query rule should not be static
- Enable retrieval of user data for static rules through csv download

## [0.10.9] - unofficially released

- Bug Fix: Display the number of users in a static segment on dashboard

## [0.10.8] - unofficially released

- Don't add users to exclude list for dynamic segments
- Store segments a user is excluded from in the session

## [0.10.7] - unofficially released

- Bug Fix: Ensure static segment members are show the survey immediately
- Records users excluded by randomisation on the segment
- Don't re-check excluded users

## [0.10.6] - unofficially released

- Accepts and stores randomisation percentage for segment
- Adds users to segment based on random number relative to percentage

## [0.10.5] - unofficially released

- Count how many users match a segments rules before saving the segment
- Stores count on the segment and displays in the dashboard
- Enables testing users against rules if there isn't an active request

## [0.10.0] - unofficially released

- Adds static and dynamic segments

## [0.9.1] - unofficially released

- Fixes import for reverse resolver for older Django versions (<1.10)
- Bases migrations off of older wagtail dependencies
- Adds more dashboard panels and fixes exclude variants function


## [0.9.0] - 2017-06-02

Initial release of wagtail-personalisation. This Wagtail module provides basic
personalisation based on pre-defined rules in the backend.

This module was developed by Boris Besemer (@blurrah) and Jasper Berghoef
(@jberghoef) for Lab Digital (http://labdigital.nl)
