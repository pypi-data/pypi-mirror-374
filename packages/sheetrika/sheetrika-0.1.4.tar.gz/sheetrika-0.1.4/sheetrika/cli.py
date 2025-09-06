import argparse
import base64
import json
import os
import sys

from sheetrika.loader import SheetrikaLoader


def encode_file_to_base64(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        sys.exit(f'Failed to read or parse JSON file: {e}')

    try:
        json_string = json.dumps(data)
        encoded_bytes = base64.b64encode(json_string.encode('utf-8'))
        return encoded_bytes.decode('utf-8')
    except Exception as e:
        sys.exit(f'Encoding failed: {e}')


def decode_base64_to_json_string(encoded_str: str) -> str:
    try:
        decoded_bytes = base64.b64decode(encoded_str)
        json_obj = json.loads(decoded_bytes.decode('utf-8'))
        return json.dumps(json_obj, indent=4)
    except Exception as e:
        sys.exit(f'Decoding failed: {e}')


def run_tasks_from_config(config_path, task):
    loader = SheetrikaLoader(
        ym_token=os.getenv('YANDEX_API_TOKEN'),
        goo_token=os.getenv('GOOGLE_API_TOKEN'),
        config_path='config.yaml',
    )
    stat = loader.run(task)
    print(json.dumps(stat, indent=4, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description='Encode or decode JSON using base64.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode a JSON file to a base64 string.')
    encode_parser.add_argument('filepath', help='Path to the JSON file.')

    # Decode command
    decode_parser = subparsers.add_parser('decode', help='Decode a base64 string to formatted JSON.')
    decode_parser.add_argument('string', nargs='?', help='Base64 encoded string. If not provided, reads from stdin.')

    # Run command
    decode_parser = subparsers.add_parser('run', help='Run tasks from config.')
    decode_parser.add_argument('filepath', nargs='?', help='Path to the YAML file.')
    decode_parser.add_argument('task', nargs='?', help='Task from config [optional].')

    args = parser.parse_args()

    if args.command == 'encode':
        output = encode_file_to_base64(args.filepath)
        print(output)

    elif args.command == 'decode':
        input_string = args.string
        if input_string is None:
            input_string = sys.stdin.read().strip()
        output = decode_base64_to_json_string(input_string)
        print(output)

    elif args.command == 'run':
        run_tasks_from_config(args.filepath, args.task)


if __name__ == '__main__':
    main()
