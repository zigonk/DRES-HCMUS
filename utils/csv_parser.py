"""
CSV parsing and row normalization for DRES conversion.

Handles multiple CSV formats:
1. Explicit task_type column
2. Query Type column (qa/tkis/vkis) with Second Start/End
3. Inferred from columns (Answer(QA), FrameList, Frame Start/End)
"""

import re
import os
import sys
from dres_utils import frames_to_ms, seconds_to_ms
from task_builders import build_tkis_task, build_qa_or_trake_task, build_vkis_task


# Map simple CSV task_type values to full taskType and taskGroup names
TASK_TYPE_MAP = {
    'tkis': ('Textual Known Item Search', 'tkis'),
    'qa-kis': ('qa-kis', 'qa-kis'),
    'qa_kis': ('qa-kis', 'qa-kis'),
    'qa': ('qa-kis', 'qa-kis'),
    'trake': ('trake', 'trake'),
    'vkis': ('Visual Known Item Search', 'vkis')
}


def normalize_row_keys(row):
    """
    Normalize CSV header keys to snake_case identifiers.

    Examples:
        "Query Name" -> "query_name"
        "Answer(QA)" -> "answer_qa"
        "FrameList(';'-Trake)" -> "framelist_trake"

    Args:
        row: Dictionary with original CSV headers as keys

    Returns:
        Dictionary with normalized keys
    """
    out = {}
    for k, v in row.items():
        if k is None:
            continue
        key = k.strip()
        # normalize to snake-like key: replace non-alphanum with underscore
        key = re.sub(r'[^0-9A-Za-z]+', '_', key)
        key = key.strip('_').lower()
        out[key] = v
    return out


def prepare_row_fields(row):
    """
    Prepare and convert CSV fields to match task builder expectations.

    Converts seconds to milliseconds, extracts media names, etc.
    """
    # Convert seconds to milliseconds for start_ms and end_ms
    if row.get('second_start'):
        converted = seconds_to_ms(row['second_start'])
        if converted is not None:
            row['start_ms'] = str(converted)
    if row.get('second_end'):
        converted = seconds_to_ms(row['second_end'])
        if converted is not None:
            row['end_ms'] = str(converted)

    # Extract media_name from video_filename if present
    video_filename = row.get('video_filename')
    if video_filename:
        row['media_name'] = os.path.splitext(video_filename)[0]

    # Map 'ans' to 'answer_qa' for QA tasks
    if row.get('ans'):
        row['answer_qa'] = row['ans']

    return row


def parse_explicit_task_type(row):
    """
    Parse row with explicit task_type or query_type column.

    Args:
        row: Normalized row dictionary

    Returns:
        Task dictionary or None if task_type not found
    """
    # Check for 'query_type' or 'task_type'
    ttype_raw = (row.get('query_type') or row.get(
        'task_type') or row.get('tasktype') or '')
    if not ttype_raw:
        return None

    kind_key = ttype_raw.strip().lower()
    if kind_key not in TASK_TYPE_MAP:
        kind_key = kind_key.replace(' ', '-').replace('_', '-')

    # Prepare row fields before calling builders
    row = prepare_row_fields(row)

    if kind_key in ('tkis',):
        return build_tkis_task(row)
    elif kind_key in ('qa-kis', 'qa'):
        return build_qa_or_trake_task(row, kind='qa-kis')
    elif kind_key == 'trake':
        return build_qa_or_trake_task(row, kind='trake')
    elif kind_key == 'vkis':
        return build_vkis_task(row)
    else:
        print(
            f"Unknown task_type '{ttype_raw}' - skipping row", file=sys.stderr)
        return None


def parse_row(raw_row):
    """
    Parse a single CSV row and convert to task dictionary.

    Tries multiple parsing strategies in order:
    1. Explicit task_type column
    2. Query Type column (format 2)
    3. Inferred from other columns (format 1)

    Args:
        raw_row: Raw CSV row dictionary with original headers

    Returns:
        Task dictionary or None if row cannot be parsed
    """
    row = normalize_row_keys(raw_row)

    # Try explicit task_type
    task = parse_explicit_task_type(row)
    if task:
        return task

    # Unable to parse
    print(f"Skipping row (could not infer task): {raw_row}", file=sys.stderr)
    return None
