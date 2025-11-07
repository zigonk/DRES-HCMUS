# DRES Utilities

Utilities for converting between CSV and JSON formats for DRES (Distributed Retrieval Evaluation Server) evaluation templates.

## Overview

This directory contains tools for bidirectional conversion between CSV files and DRES JSON evaluation templates, making it easier to create, edit, and manage evaluation tasks.

```
CSV File ←→ JSON Evaluation Template
```
## Limitations
- Can't auto import MEDIA_ITEM due to lack of ID in database

## Files

### Conversion Tools

- **`csv2eval_template.py`** - Convert CSV files to DRES JSON format
- **`eval_template2csv.py`** - Convert DRES JSON back to CSV format

### Support Modules

- **`csv_parser.py`** - CSV parsing logic with format detection
- **`task_builders.py`** - Task construction functions for DRES schema
- **`dres_utils.py`** - Shared utility functions

### Documentation

- **`sample_eval_template.json`** - Example DRES JSON template
- **`sample_eval_template.csv`** - Example CSV format

---

## CSV to JSON Conversion

### Usage


Edit `dres_utils.py` to change the default collection (currently use of AIC2025). Export evaluation template on the system to see collection ID:
```python
DEFAULT_COLLECTION_ID = "your-collection-uuid-here"
```
```bash
python csv2eval_template.py -i input.csv -o output.json
```

### CSV Format

The tool supports CSV files with the following columns:

| Column | Description | Required | Notes |
|--------|-------------|----------|-------|
| ID | Task ID | Optional | Auto-generated if missing |
| QID | Query ID | Optional | Auto-generated if missing |
| Query Type | Task type | **Required** | `qa`, `tkis`, `vkis`, or `trake` |
| Query Name | Task name | Optional | Auto-generated if missing |
| Description | Task description/hints | Optional | Multiple hints separated by endline |
| Trans | Translation/English hints | Optional |  Multiple hints separated by endline |
| Video Filename | Video file path | **Required** | e.g., `L08_V026.mp4` |
| Second Start | Start time in seconds | **Required** | Converted to milliseconds |
| Second End | End time in seconds | **Required** | Converted to milliseconds |
| Ans | Answer (QA tasks only) | Required for QA | Answer text for QA tasks |
| Note | Comments | Optional | Additional notes |
| Frame List | Frame numbers (Trake only) | Required for Trake | Semicolon-separated frames |

### Supported Task Types

#### 1. **QA (Question-Answer)**
- Query Type: `qa`
- Requires: `Ans`, `Video Filename`, `Second Start`, `Second End`
- Target format: `QA-{answer}-{video}-{start_ms}-{end_ms}`
- Hints: Questions (containing `?`) are automatically extracted and formatted

#### 2. **TKIS (Textual Known Item Search)**
- Query Type: `tkis`
- Requires: `Video Filename`, `Second Start`, `Second End`
- Target: Media temporal range with video segment
- Hints: Accumulated progressively over 60-second intervals

#### 3. **VKIS (Visual Known Item Search)**
- Query Type: `vkis`
- Requires: `Video Filename`, `Second Start`, `Second End`
- Similar to TKIS but with visual focus
- Hints: Same accumulation pattern as TKIS

#### 4. **Trake (Tracking)**
- Query Type: `trake`
- Requires: `Video Filename`, `Frame List`
- Target format: `TR-{video}-{frame1,frame2,...}`
- Hints: Not split, used as single block

### Example CSV

```csv
ID,QID,Query Type,Query Name,Description,Trans,Video Filename,Second Start,Second End,Ans,Note,Frame List
1,1,qa,query-qa-01,Hỏi trong video có bao nhiêu người?,,L08_V026,631,658,5,,
2,2,tkis,query-tkis-01,Một robot chạy trên đồng cỏ; Có bò đứng cạnh robot,,L16_V010,367,406,,,
3,3,vkis,query-vkis-01,,,L06_V028,76,83,,,
4,4,trake,query-trake-01,Cảnh lắp ráp xe,,L26_V176,,,,,4725;4875;5020
```

## JSON to CSV Conversion

### Usage

```bash
python eval_template2csv.py -i input.json -o output.csv
```

## Modular Architecture

The codebase is organized into focused modules for maintainability:

### `dres_utils.py`
Common utility functions used across all modules:
- `make_uuid()` - Generate unique task IDs
- `split_hints()` - Parse semicolon-separated hints
- `frames_to_ms(frame, fps)` - Convert frame numbers to milliseconds
- `seconds_to_ms(seconds)` - Convert seconds to milliseconds
- Constants: `DEFAULT_COLLECTION_ID`, `TASK_TYPE_MAP`

### `task_builders.py`
Task construction functions that create DRES-compliant task objects:
- `build_tkis_task(row)` - Build TKIS tasks with temporal range targets
- `build_qa_or_trake_task(row, kind)` - Build QA/Trake tasks with text targets
- `build_vkis_task(row)` - Build VKIS tasks (extends TKIS)

Each builder handles:
- UUID generation
- Hint formatting with time blocks
- Target construction (media ranges or text)
- Field validation and defaults

### `csv_parser.py`
CSV parsing and normalization:
- `normalize_row_keys(row)` - Convert headers to snake_case
- `prepare_row_fields(row)` - Convert seconds to ms, extract media names
- `parse_explicit_task_type(row)` - Handle query_type column
- `parse_row(raw_row)` - Main dispatcher for row parsing

Supports multiple CSV formats:
1. Explicit `query_type` column
2. Inferred from `Answer`/`Frame List` columns
3. Legacy formats with different column names

---

## Examples

### Convert CSV to JSON

```bash
# Basic conversion
python csv2eval_template.py -i tasks.csv -o evaluation.json

# With custom file paths
python csv2eval_template.py \
  --input /path/to/tasks.csv \
  --output /path/to/output.json
```

### Convert JSON back to CSV

```bash
# Extract tasks from JSON to CSV
python eval_template2csv.py -i evaluation.json -o tasks.csv

# Edit the CSV, then convert back
python csv2eval_template.py -i tasks_edited.csv -o evaluation_v2.json
```

### Workflow Example

1. **Create tasks in spreadsheet** (Excel, Google Sheets)
2. **Export to CSV** with required columns
3. **Convert to JSON**: `python csv2eval_template.py -i tasks.csv -o eval.json`
4. **Import to DRES** system for evaluation
5. **Later, extract back to CSV** for editing: `python eval_template2csv.py -i eval.json -o tasks.csv`
6. **Make changes** in spreadsheet
7. **Re-convert**: `python csv2eval_template.py -i tasks.csv -o eval_v2.json`






