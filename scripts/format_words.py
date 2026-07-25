import sys
import re
from pathlib import Path


def process_file(file_path: Path) -> None:
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    processed_lines = []
    for line in lines:
        stripped_line = line.rstrip()
        if not stripped_line:
            continue
        # Remove leading sequence number (digits followed by whitespace)
        cleaned_line = re.sub(r"^\d+\s+", "", stripped_line)
        processed_lines.append(cleaned_line)

    # Sort lines in ascending dictionary order (case-insensitive)
    sorted_lines = sorted(processed_lines, key=lambda s: s.lower())

    # Save processed content back to file
    file_path.write_text("\n".join(sorted_lines) + "\n", encoding="utf-8")
    print(f"Successfully processed {len(sorted_lines)} lines in {file_path.name}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            process_file(Path(arg))
    else:
        # Default files to process if no arguments provided
        data_dir = Path(__file__).parent.parent / "data"
        for target in [
            data_dir / "2025年4月课标新增196词.txt",
            data_dir / "2026年英语高考大纲新增183词.txt",
        ]:
            if target.exists():
                process_file(target)
