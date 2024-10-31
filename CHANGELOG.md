# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [ 2024.4.5 ] (2024-10-31)

### Update
 - Updated duckdb-version


## [ 2024.4.4 ] (2024-09-19)

### Fix
 - VooropleidingKort in assets has now correct values for all items.
 - ProfielVooropleiding now has data.

## [ 2024.4.3 ] (2024-06-12)

### Fix
 - Column order is preserved when replacing pgn with pseudo-id.


## [ 2024.4.2 ] (2024-06-06)

### Fix
 - Added openpyxl as a dependency so Excel convert works out of the box.

### Add
 - Added warning for maximum number of rows when exporting to Excel.


## [ 2024.4.1 ] (2024-05-29)

### Fix
 - A convert of only eencijfer-file is now possible (removed dependency of eindexamencijfers).

## [ 2024.4.0 ] (2024-04-18)

### Added
 - Added duckdb export-format
 - Added CLI options for source_dir and result_dir


## [ 2024.3.1 ] (2024-04-16)

### Fix
 - Added gracefull exit when no eencijfer-file is found
 - Fixed broken import

## [ 2024.3.0 ] (2024-04-15)

### Add
 - Added working-dir for intermediate saves

### Update
 - Updated some column-definitions that, according to documentation should be objects, instead of int.


## [ 2024.2.4 ] (2024-04-12)

### Update

 - Added possibility to export to csv or excel.


## [ 2024.2.3 ] (2024-03-29)

### Update

 - Downgrade numpy-version so it might work on pyodide.


## [ 2024.2.2 ] (2024-03-27)

### Fixed

 - Code errors.


## [ 2024.1.1 ] (2024-03-12)

### Fixed

 - Moved code around so it is easier to find code.


## [ 2024.1.0 ] (2024-03-12)

### Added

 - config-file is optional, simply calling `eencijfer convert` in the `source_dir` will just work.


## [ 2024.0.2 ] (2024-02-23)

### Updated

 - changed definition of VAKHAVW because of update from DUO.


## [ 2024.0.0 ] (2024-02-19)

### Added

 - added new eencijfer 2024


## [ 2023.2.3 ] (2024-02-18)

### Fixes

 - added dependency pyarrow

## [ 2023.2.2 ] (2024-02-18)

### Fixes

 - changed the the config variablepoetry run bump-my-version bump


## [ 0.2.12 ] (2023-12-29)

### Fixes

 - changed the way dependencies are added

## 0.2.11 (2023-12-29)

### Fixes

 - less dependencies for package

## 0.2.9 (2023-12-28)

### Fixes
 - changed action to publish to test.pypi

## 0.2.8 (2023-12-28)

### Fixes
 - working pipeline

## 0.1.0 (2023-12-27)

 - First release on PyPI.
