# CSV to DRES JSON Converter - Refactoring Summary

## Overview
The `csv2eval_template.py` script has been refactored from a monolithic 460-line file into a modular architecture with 4 files, improving readability and maintainability.

## File Structure

### 1. **csv2eval_template.py** (Main Entry Point)
- **Purpose**: Command-line interface and orchestration
- **Lines**: ~75 lines (was 460+ lines)
- **Responsibilities**:
  - Parse command-line arguments
  - Read CSV file
  - Loop through rows and call `parse_row()`
  - Write JSON output
  - Main entry point

### 2. **csv_parser.py** (CSV Parsing Logic)
- **Purpose**: CSV format detection and row parsing
- **Key Functions**:
  - `normalize_row_keys()`: Standardize column names
  - `parse_explicit_task_type()`: Handle explicit task_type column
  - `parse_query_type_format()`: Handle Query Type column with seconds
  - `parse_inferred_format()`: Infer task type from columns
  - `parse_row()`: Main dispatcher function
- **Supported Formats**:
  1. Explicit task_type column (tkis, qa-kis, trake, vkis)
  2. Query Type column with Second Start/End
  3. Inferred from Answer(QA)/FrameList/Frame Start-End columns

### 3. **task_builders.py** (Task Construction)
- **Purpose**: Build DRES task objects
- **Key Functions**:
  - `build_tkis_task()`: Textual Known Item Search tasks
  - `build_qa_or_trake_task()`: Question-Answer and Tracking tasks
  - `build_vkis_task()`: Visual Known Item Search tasks
- **Features**:
  - Hint management with time buckets
  - Target construction (MEDIA_ITEM_TEMPORAL_RANGE, TEXT)
  - Question extraction for QA tasks

### 4. **dres_utils.py** (Shared Utilities)
- **Purpose**: Common utility functions
- **Key Functions**:
  - `make_uuid()`: Generate unique task IDs
  - `split_hints()`: Parse semicolon-separated hints
  - `frames_to_ms()`: Convert frame numbers to milliseconds
  - `seconds_to_ms()`: Convert seconds to milliseconds
- **Constants**:
  - `DEFAULT_COLLECTION_ID`: Default collection UUID
  - `TASK_TYPE_MAP`: Task type normalization mapping

## Testing Results

Both original CSV formats continue to work correctly:

### sample_without_trake.csv
```
Total tasks: 34
Task types: {'qa-kis': 7, 'tkis': 15, 'vkis': 12}
```

### sample_csv.csv
```
Total tasks: 34
Task types: {'qa-kis': 7, 'tkis': 15, 'vkis': 12}
```

## Benefits of Refactoring

1. **Improved Readability**: Each file has a clear, single purpose
2. **Easier Testing**: Functions can be tested independently
3. **Better Maintainability**: Changes to one aspect don't affect others
4. **Reusability**: Utility functions and task builders can be used in other scripts
5. **Documentation**: Each module has clear docstrings explaining its purpose
6. **Reduced Complexity**: Main file is now just 75 lines vs 460+

## Module Dependencies

```
csv2eval_template.py
    └── imports parse_row from csv_parser.py
            └── imports functions from task_builders.py
                    └── imports utilities from dres_utils.py
```

## Usage (Unchanged)

```bash
python3 utils/csv2eval_template.py -i utils/sample_csv.csv -o output.json
```

## Migration Notes

- **Backward Compatible**: All existing CSV formats continue to work
- **Same Output**: Generated JSON is identical to pre-refactor version
- **No Breaking Changes**: Command-line interface remains the same
- **All Tests Pass**: Verified with both sample CSV files
