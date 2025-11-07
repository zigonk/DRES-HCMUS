"""
eval_template2csv.py

Convert DRES JSON evaluation template back to CSV format.

Usage:
    python eval_template2csv.py --input sample_eval_template.json --output output.csv
"""

import json
import csv
import argparse
import sys


def extract_task_data(task):
    """
    Extract data from a task and convert to CSV row format.

    Args:
        task: Task dictionary from JSON

    Returns:
        Dictionary with CSV column names as keys
    """
    row = {
        'ID': '',  # Not in original JSON
        'QID': '',  # Not in original JSON
        'Query Type': '',
        'Query Name': task.get('name', ''),
        'Description': '',
        'Trans': '',
        'Video Filename': '',
        'Second Start': '',
        'Second End': '',
        'Ans': '',
        'Note': task.get('comment', ''),
        'Frame List': '',
    }

    # Determine query type from taskGroup
    task_group = task.get('taskGroup', '')
    if task_group == 'qa-kis':
        row['Query Type'] = 'qa'
    elif task_group == 'tkis':
        row['Query Type'] = 'tkis'
    elif task_group == 'vkis':
        row['Query Type'] = 'vkis'
    elif task_group == 'trake':
        row['Query Type'] = 'trake'

    # Extract hints
    hints = task.get('hints', [])
    hint_texts = []
    for hint in hints:
        if hint.get('type') == 'TEXT':
            desc = hint.get('description', '')
            if desc:
                hint_texts.append(desc)

    # Join hints with semicolons (or newlines for readability)
    if hint_texts:
        row['Description'] = '\n'.join(hint_texts)
        # For Trans, we could use the same or leave empty
        # row['Trans'] = '\n'.join(hint_texts)

    # Extract target information
    targets = task.get('targets', [])
    if targets:
        target = targets[0]
        target_type = target.get('type', '')

        if target_type == 'TEXT':
            # QA or Trake target
            target_text = target.get('target', '')

            # Parse QA target: "QA-answer-video-start-end"
            if target_text.startswith('QA-'):
                parts = target_text.split('-')
                if len(parts) >= 5:
                    row['Ans'] = parts[1]
                    row['Video Filename'] = parts[2]
                    # QA targets store milliseconds, convert to seconds
                    try:
                        row['Second Start'] = str(int(parts[3]) // 1000)
                        row['Second End'] = str(int(parts[4]) // 1000)
                    except (ValueError, TypeError):
                        row['Second Start'] = parts[3]
                        row['Second End'] = parts[4]
                elif len(parts) >= 3:
                    row['Ans'] = parts[1]
                    row['Video Filename'] = parts[2]

            # Parse Trake target: "TR-video-frame1,frame2,..."
            elif target_text.startswith('TR-'):
                parts = target_text.split('-', 2)
                if len(parts) >= 3:
                    row['Video Filename'] = parts[1]
                    # Frame list would go in a separate column if we had one
                    # Change delimiter to semicolon for CSV
                    row['Frame List'] = parts[2].replace(',', ';')

        elif target_type == 'MEDIA_ITEM_TEMPORAL_RANGE':
            # TKIS or VKIS target
            item = target.get('item', {})
            range_info = target.get('range', {})

            row['Video Filename'] = item.get(
                'location', '') or item.get('name', '')

            # Extract time range (convert from milliseconds to seconds)
            start_info = range_info.get('start', {})
            end_info = range_info.get('end', {})

            start_val = start_info.get('value', '')
            end_val = end_info.get('value', '')

            if start_val:
                # Convert milliseconds to seconds
                try:
                    row['Second Start'] = str(int(start_val) // 1000)
                except (ValueError, TypeError):
                    row['Second Start'] = start_val

            if end_val:
                try:
                    row['Second End'] = str(int(end_val) // 1000)
                except (ValueError, TypeError):
                    row['Second End'] = end_val

    return row


def convert_json_to_csv(input_json, output_csv):
    """
    Convert DRES JSON evaluation template to CSV format.

    Args:
        input_json: Path to input JSON file
        output_csv: Path to output CSV file
    """
    # Load JSON
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tasks = data.get('tasks', [])

    if not tasks:
        print("No tasks found in JSON file", file=sys.stderr)
        return

    # CSV headers matching the input format
    headers = [
        'ID',
        'QID',
        'Query Type',
        'Query Name',
        'Description',
        'Trans',
        'Video Filename',
        'Second Start',
        'Second End',
        'Ans',
        'Note',
        'Frame List',
    ]

    # Convert tasks to rows
    rows = []
    for i, task in enumerate(tasks, start=1):
        row = extract_task_data(task)
        row['ID'] = str(i)
        row['QID'] = str(i)
        rows.append(row)

    # Write CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Successfully converted {len(rows)} tasks from {input_json} to {output_csv}")
    print(f"Task breakdown:")
    from collections import Counter
    types = Counter(row['Query Type'] for row in rows)
    for task_type, count in sorted(types.items()):
        print(f"  {task_type}: {count}")


def main():
    """Main entry point for the JSON to CSV converter."""
    parser = argparse.ArgumentParser(
        description='Convert DRES JSON evaluation template to CSV format')
    parser.add_argument('-i', '--input', required=True,
                        help='Input JSON file path')
    parser.add_argument('-o', '--output', required=True,
                        help='Output CSV file path')
    args = parser.parse_args()

    convert_json_to_csv(args.input, args.output)


if __name__ == '__main__':
    main()
