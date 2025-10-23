"""QML formatter pre-commit hook"""

import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, Sequence


def find_qmlformat() -> Optional[str]:
    """Find pyside6-qmlformat executable"""
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


def format_single_file(
    file_path: Path,
    qmlformat_path: str,
    use_spaces: bool = False,
    check_only: bool = False,
    inplace: bool = True,
    tab_size: int = 4,
) -> tuple[Path, bool, Optional[str]]:
    """Format a single QML file. Returns (file_path, success, error_message)"""
    cmd = [qmlformat_path]
    if use_spaces:
        cmd.append("--use-spaces")
    if check_only:
        cmd.append("--check")
    elif inplace:
        cmd.append("--inplace")
    if tab_size != 4:
        cmd.extend(["--tab-size", str(tab_size)])
    cmd.append(str(file_path))
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return (file_path, True, None)
    except subprocess.CalledProcessError as e:
        if check_only and e.returncode == 1:
            return (file_path, False, "needs formatting")
        return (file_path, False, e.stderr or str(e))
    except Exception as e:
        return (file_path, False, str(e))


def format_qml_files(
    files: list[Path],
    qmlformat_path: str,
    use_spaces: bool = False,
    check_only: bool = False,
    inplace: bool = True,
    tab_size: int = 4,
    max_workers: Optional[int] = None,
) -> int:
    """Format QML files using multithreading"""
    if not files:
        return 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(
                format_single_file, file_path, qmlformat_path, use_spaces, check_only, inplace, tab_size
            ): file_path
            for file_path in files
        }
        for future in as_completed(future_to_file):
            file_path, success, error_msg = future.result()
            if not success:
                if check_only and error_msg == "needs formatting":
                    return 1
                # print(f"ERROR: {file_path}: {error_msg}", file=sys.stderr)
                return 1

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main function"""
    parser = argparse.ArgumentParser(description="QML formatter pre-commit hook")
    parser.add_argument("filenames", nargs="*", help="Files to format")
    parser.add_argument("--qmlformat-path", help="Path to pyside6-qmlformat")
    parser.add_argument("--use-spaces", action="store_true", help="Use spaces instead of tabs")
    parser.add_argument("--check", action="store_true", help="Check if files need formatting without modifying them")
    parser.add_argument("--inplace", action="store_true", default=True, help="Format files in place (default: True)")
    parser.add_argument("--tab-size", type=int, default=4, help="Tab size (default: 4)")
    parser.add_argument("--max-workers", type=int, help="Maximum number of worker threads (default: auto)")
    args = parser.parse_args(argv)
    qmlformat_path = args.qmlformat_path or find_qmlformat()
    if not qmlformat_path:
        return 1
    files = [Path(filename) for filename in args.filenames if Path(filename).exists()]
    if not files:
        return 0

    return format_qml_files(
        files,
        qmlformat_path,
        use_spaces=args.use_spaces,
        check_only=args.check,
        inplace=args.inplace,
        tab_size=args.tab_size,
        max_workers=args.max_workers,
    )


if __name__ == "__main__":
    sys.exit(main())
