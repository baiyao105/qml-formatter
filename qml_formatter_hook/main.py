"""QML formatter pre-commit hook"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence


def find_qmlformat() -> Optional[str]:
    """Find qmlformat executable"""
    possible_names = ["pyside6-qmlformat", "pyside6-qmlformat.exe", "qmlformat", "qmlformat.exe"]
    for name in possible_names:
        try:
            result = subprocess.run(
                ["where" if sys.platform == "win32" else "which", name], capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                return result.stdout.strip().split("\n")[0]
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    return None


def format_qml_files(files: list[Path], qmlformat_path: str) -> int:
    """Format QML files"""
    has_changes = False
    for file_path in files:
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()
        except Exception as e:
            print(f"ERROR: {file_path}: {e}", file=sys.stderr)
            return 1
        try:
            subprocess.run([qmlformat_path, "-i", str(file_path)], capture_output=True, text=True, check=True)
            with open(file_path, encoding="utf-8") as f:
                new_content = f.read()
            if original_content != new_content:
                has_changes = True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: {file_path}: {e.stderr}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"ERROR: {file_path}: {e}", file=sys.stderr)
            return 1

    return 1 if has_changes else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main function"""
    parser = argparse.ArgumentParser(description="QML formatter pre-commit hook")
    parser.add_argument("filenames", nargs="*", help="Files to format")
    parser.add_argument("--qmlformat-path", help="Path to pyside6-qmlformat")
    args = parser.parse_args(argv)
    qmlformat_path = args.qmlformat_path or find_qmlformat()
    if not qmlformat_path:
        print("Error: not found qmlformat", file=sys.stderr)
        return 1
    files = [Path(filename) for filename in args.filenames if Path(filename).exists()]
    if not files:
        return 0
    return format_qml_files(files, qmlformat_path)


if __name__ == "__main__":
    sys.exit(main())
