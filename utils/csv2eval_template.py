"""
csv2eval_template.py

CSV -> DRES JSON converter for tasks.

Supports multiple CSV formats:
1. Explicit task_type column (tkis, qa-kis, trake, vkis)
2. Query Type column with Second Start/End (qa, tkis, vkis)
3. Inferred from columns (Answer(QA), FrameList, Frame Start/End)

Usage:
    python csv2eval_template.py --input sample.csv --output output.json

Output:
    JSON file with {"tasks": [...]} conforming to DRES schema.

See csv_parser.py for detailed column descriptions.
"""

import csv
import json
import argparse
import os
import sys

from csv_parser import parse_row


def convert_csv(input_csv, output_json):
    """
    Convert CSV file to DRES JSON format.

    Args:
        input_csv: Path to input CSV file
        output_json: Path to output JSON file

    Returns:
        Path to output JSON file
    """
    tasks = []
    with open(input_csv, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for raw_row in reader:
            task = parse_row(raw_row)
            if task:
                tasks.append(task)

    out_obj = {"tasks": tasks}
    with open(output_json, 'w', encoding='utf-8') as out_f:
        json.dump(out_obj, out_f, ensure_ascii=False, indent=2)
    return output_json


def main():
    """Main entry point for the CSV to JSON converter."""
    parser = argparse.ArgumentParser(
        description='Convert CSV file to DRES evaluation template JSON')
    parser.add_argument('-i', '--input', required=True,
                        help='Input CSV file path')
    parser.add_argument('-o', '--output', required=True,
                        help='Output JSON file path')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input CSV not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    output = convert_csv(args.input, args.output)
    print(f"Successfully converted {args.input} to {output}")
    print(f"Wrote {output} with tasks")


if __name__ == '__main__':
    main()
