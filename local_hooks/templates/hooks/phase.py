#!/usr/bin/env python3
"""
Script to clear a file and write a specified string to it.
Usage: python3 phase.py --string "your_text"
Default: writes 'code' if no string is specified
"""
import argparse
import os


def write_phase_file(content="code"):
    file_path = os.path.join(os.path.dirname(__file__), "../current_phase")
    try:
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Successfully wrote '{content}' to {file_path}")
    except FileNotFoundError:
        print(f"Error: Directory or file not found: {file_path}")
    except PermissionError:
        print(f"Error: Permission denied when writing to {file_path}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Write content to the current_phase file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 phase.py                    # Write 'code' (default)
  python3 phase.py --string "hello"   # Write 'hello'
  python3 phase.py -s "test"          # Write 'test'
        """,
    )
    parser.add_argument(
        "--string",
        "-s",
        type=str,
        default="code",
        help="String to write to the file (default: code)",
    )
    args = parser.parse_args()
    write_phase_file(args.string)


if __name__ == "__main__":
    main()
