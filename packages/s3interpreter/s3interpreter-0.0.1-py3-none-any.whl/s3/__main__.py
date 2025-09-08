import argparse
import sys
from .interpreter import S3Interpreter, display_help

def main():
    parser = argparse.ArgumentParser(description="S3 Language Interpreter CLI")
    parser.add_argument('file', nargs='?', help="S3 program file (.s3) to run")
    parser.add_argument('--help-s3', action='store_true', help="Show S3 language help and exit")
    args = parser.parse_args()

    interpreter = S3Interpreter()

    if args.help_s3:
        display_help()
        sys.exit(0)

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                code_lines = f.read().splitlines()
            interpreter.multiline(*code_lines)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("Enter your S3 program, finish with an empty line:")
        code_lines = []
        while True:
            try:
                line = input()
                if line.strip() == "":
                    break
                code_lines.append(line)
            except EOFError:
                break
        if code_lines:
            interpreter.multiline(*code_lines)
        else:
            print("No program entered. Exiting.")

if __name__ == "__main__":
    main()
