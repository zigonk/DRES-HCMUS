"""
Task builder functions for creating DRES task objects.

Each builder function takes a row dictionary (normalized CSV row)
and returns a task dictionary conforming to the DRES JSON schema.
"""

import os
from dres_utils import make_uuid, split_hints

DEFAULT_COLLECTION_ID = "796ac77f-44de-44b8-8191-656395621088"


def build_tkis_task(row):
    """
    Build a Textual Known Item Search (TKIS) task.

    CSV columns (after normalization):
        - query_name → name (or auto-generated)
        - video_filename → extracted to media_name (without extension) and location
        - second_start → converted to start_ms (milliseconds)
        - second_end → converted to end_ms (milliseconds)
        - description or trans → hint text (accumulated for each 60s time block)
        - note → comment (optional)

    Internal fields used:
        - collectionId: uses DEFAULT_COLLECTION_ID
        - duration: defaults to 300 seconds

    Returns:
        Task dictionary with MEDIA_ITEM_TEMPORAL_RANGE target
    """
    task_id = make_uuid()
    name = row.get('query_name') or row.get('name') or f"tkis-{task_id[:8]}"
    collectionId = row.get('collectionId') or DEFAULT_COLLECTION_ID

    # Extract media info from video_filename
    video_filename = row.get('video_filename') or ''
    if video_filename:
        media_name = os.path.splitext(video_filename)[0]
        location = video_filename
    else:
        media_name = row.get('media_name') or ''
        location = f'{media_name}.mp4'

    # Get time range - expect seconds from CSV, convert to milliseconds
    start_ms = row.get('start_ms') or ''
    end_ms = row.get('end_ms') or ''

    # hints: guideline expects three fixed time blocks for TKIS
    # Hint in both english and vietnamese
    vie_raw_hints = row.get('description') or ''
    eng_raw_hints = row.get('trans') or ''
    # Hint parts from both languages
    vie_hint_parts = split_hints(vie_raw_hints)
    eng_hint_parts = split_hints(eng_raw_hints)
    # Combine hint parts by index respectively
    hint_parts = []
    max_parts = max(len(vie_hint_parts), len(eng_hint_parts))
    for i in range(max_parts):
        vie_part = vie_hint_parts[i] if i < len(vie_hint_parts) else ''
        eng_part = eng_hint_parts[i] if i < len(eng_hint_parts) else ''
        combined_part = '\n'.join(filter(None, [eng_part, vie_part]))
        if combined_part:
            hint_parts.append(combined_part)
    hints = []
    # Map up to 3 hint pieces to the given ranges 0-60,60-120,120+ (seconds)
    accumulated_hints = []
    for i, hint_part in enumerate(hint_parts):
        accumulated_hints.append(hint_part)
        # If last hint, end = duration
        if i == len(hint_parts) - 1:
            end_time = int(row.get('duration') or 300)
        else:
            end_time = (i + 1) * 60
        hints.append({
            "type": "TEXT",
            "start": i * 60,
            "end": end_time,
            "description": " ".join(accumulated_hints),
            "dataType": "text/plain"
        })

    task = {
        "id": task_id,
        "name": name,
        "taskGroup": "tkis",
        "taskType": "Textual Known Item Search",
        "duration": int(row.get('duration') or 300),
        "collectionId": collectionId,
        "targets": [],
        "hints": hints,
        "comment": row.get('note') or row.get('comment', '') or ''
    }

    # Add a MEDIA_ITEM_TEMPORAL_RANGE target when media_name and start/end provided
    if media_name and start_ms and end_ms:
        item = {
            "name": media_name,
            "type": "VIDEO",
            "collectionId": collectionId,
            "location": location,
        }
        # remove None values
        item = {k: v for k, v in item.items() if v is not None}
        target = {
            "type": "MEDIA_ITEM_TEMPORAL_RANGE",
            "range": {
                "start": {"value": str(start_ms), "unit": "MILLISECONDS"},
                "end": {"value": str(end_ms), "unit": "MILLISECONDS"}
            },
            "item": item
        }
        task['targets'].append(target)

    return task


def build_qa_or_trake_task(row, kind='qa-kis'):
    """
    Build a QA or Trake task with TEXT target.

    CSV columns for QA (query_type='qa'):
        - query_name → name (or auto-generated)
        - ans → answer_qa (answer text)
        - video_filename → extracted to media_name
        - start_ms → used in target (milliseconds)
        - end_ms → used in target (milliseconds)
        - description or trans → hint text (question extracted if contains '?')
        - note → comment (optional)

        Target format: "QA-{answer}-{video}-{start_ms}-{end_ms}"

    CSV columns for Trake (query_type='trake'):
        - query_name → name (or auto-generated)
        - video_filename → extracted to media_name
        - frame_list → comma/semicolon-separated frame numbers (from separate column)
        - description or trans → hint text (not split)
        - note → comment (optional)

        Target format: "TR-{video}-{frame1,frame2,...}"

    Internal fields:
        - collectionId: uses DEFAULT_COLLECTION_ID
        - duration: defaults to 300 seconds

    Args:
        row: Normalized CSV row dictionary
        kind: Task kind ('qa-kis' or 'trake')

    Returns:
        Task dictionary with TEXT target
    """
    task_id = make_uuid()
    name = row.get('query_name') or row.get('name') or f"{kind}-{task_id[:8]}"
    collectionId = row.get('collectionId') or DEFAULT_COLLECTION_ID
    duration = int(row.get('duration') or 300)

    # Extract media name from video_filename
    video_filename = row.get('video_filename') or ''
    media_name = os.path.splitext(video_filename)[
        0] if video_filename else row.get('media_name', '')

    # Build target_text for QA or Trake
    if (kind == 'qa-kis'):
        answer = row.get('ans') or row.get('answer_qa') or ''
        start_ms = row.get('start_ms') or ''
        end_ms = row.get('end_ms') or ''
        target_text = f'QA-{answer}-{media_name}-{start_ms}-{end_ms}'
    elif (kind == 'trake'):
        frames = row.get('frame_list') or ''
        # Change delimiter to comma if semicolon used
        frames = frames.replace(';', ',')
        target_text = f'TR-{media_name}-{frames}'

    # Hint in both english and vietnamese
    vie_raw_hints = row.get('description') or ''
    eng_raw_hints = row.get('trans') or ''
    # Hint parts from both languages
    vie_hint_parts = split_hints(vie_raw_hints)
    eng_hint_parts = split_hints(eng_raw_hints)
    # Combine hint parts by index respectively
    hint_parts = []
    max_parts = max(len(vie_hint_parts), len(eng_hint_parts))
    for i in range(max_parts):
        vie_part = vie_hint_parts[i] if i < len(vie_hint_parts) else ''
        eng_part = eng_hint_parts[i] if i < len(eng_hint_parts) else ''
        combined_part = '\n'.join(filter(None, [eng_part, vie_part]))
        if combined_part:
            hint_parts.append(combined_part)
    hints = []

    if kind == 'qa-kis':
        # qa-kis: split hints on semicolons into separate TEXT hints
        for i, hint_part in enumerate(hint_parts):
            if i == len(hint_parts) - 1:
                end_time = int(row.get('duration') or 300)
            else:
                end_time = (i + 1) * 60
            hints.append({
                "type": "TEXT",
                "start": i * 60,
                "end": end_time,
                "description": hint_part,
                "dataType": "text/plain"
            })
    else:
        # trake: do not split; put entire hints string as one TEXT hint
        raw_hints = '\n'.join([vie_raw_hints, eng_raw_hints]).strip()
        if raw_hints:
            hints.append({
                "type": "TEXT",
                "start": 0,
                "description": raw_hints,
                "dataType": "text/plain"
            })

    task = {
        "id": task_id,
        "name": name,
        "taskGroup": kind,
        "taskType": kind,
        "duration": duration,
        "collectionId": collectionId,
        "targets": [],
        "hints": hints,
        "comment": row.get('note') or row.get('comment', '') or ''
    }

    if target_text:
        task['targets'].append({
            "type": "TEXT",
            "target": target_text
        })

    return task


def build_vkis_task(row):
    """
    Build a Visual Known Item Search (VKIS) task.

    Similar to TKIS but with taskType/taskGroup set to Visual Known Item Search.
    Uses the same CSV columns as build_tkis_task().

    CSV columns (query_type='vkis'):
        - query_name → name (or auto-generated)
        - video_filename → extracted to media_name (without extension) and location
        - second_start → converted to start_ms (milliseconds)
        - second_end → converted to end_ms (milliseconds)
        - description or trans → hint text (accumulated for each 60s time block)
        - note → comment (optional)

    Internal fields used:
        - collectionId: uses DEFAULT_COLLECTION_ID
        - duration: defaults to 300 seconds
        - taskType: set to "Visual Known Item Search"
        - taskGroup: set to "vkis"

    Args:
        row: Normalized CSV row dictionary

    Returns:
        Task dictionary with MEDIA_ITEM_TEMPORAL_RANGE target
    """
    # For vkis we mirror the TKIS structure but mark taskType and taskGroup as Visual Known Item Search
    row['duration'] = 240  # Set default duration to 240 seconds for VKIS
    t = build_tkis_task(row)
    t['taskType'] = 'Visual Known Item Search'
    t['taskGroup'] = 'vkis'
    return t
