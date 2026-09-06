import sys
import io

# ========== Windows UTF-8 编码修复 ==========
# 在导入其他模块之前，强制设置 stdout/stderr 为 UTF-8 编码
# 这是处理 Windows 终端乱码问题的关键

# 1. 强制设置 Python 输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True
)
sys.stderr = io.TextIOWrapper(
    sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True
)

# 2. Windows 专用：强制切换终端代码页为 UTF-8 (65001)
if sys.platform == 'win32':
    import ctypes
    # 设置输出代码页为 UTF-8
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    # 设置输入代码页为 UTF-8
    ctypes.windll.kernel32.SetConsoleCP(65001)

import csv
import os
from pathlib import Path
from typing import List, Dict, Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel

from utils.youdao import fetch_word, console

def get_existing_words_in_folder(folder_path: Path, exclude_file: Path | None = None) -> set:
    """Collect all words (first column) from all .csv files in the specified folder (lowercase), excluding exclude_file."""
    existing_words = set()
    if not folder_path.exists() or not folder_path.is_dir():
        return existing_words

    exclude_abs = exclude_file.resolve() if exclude_file else None

    for csv_file in folder_path.glob("*.csv"):
        if exclude_abs and csv_file.resolve() == exclude_abs:
            continue
        try:
            with open(csv_file, "r", encoding="utf-8-sig", errors="ignore") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        w = row[0].strip().strip('"').strip("'").lower()
                        if w:
                            existing_words.add(w)
        except Exception as e:
            console.print(f"[yellow]Warning:[/] Failed to read existing csv {csv_file}: {e}")
    return existing_words


def process_file(file_base_path: Path):
    """Read words from .txt and save results to .csv, skipping duplicates in existing CSVs and input TXT."""
    input_path = file_base_path.with_suffix(".txt")
    output_path = file_base_path.with_suffix(".csv")
    
    if not input_path.exists():
        console.print(f"[bold red]Error:[/] Input file {input_path} does not exist.")
        return

    print(f"Reading from {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        raw_words = [line.strip() for line in f if line.strip()]

    if not raw_words:
        console.print("[yellow]Warning:[/] Input file is empty.")
        return

    parent_folder = input_path.parent
    existing_words = get_existing_words_in_folder(parent_folder, exclude_file=output_path)

    # Filter out duplicate words (from existing folder CSVs & within raw_words itself)
    seen_in_txt = set()
    words = []
    skipped_count = 0

    for w in raw_words:
        w_lower = w.lower()
        if w_lower in existing_words or w_lower in seen_in_txt:
            skipped_count += 1
            continue
        seen_in_txt.add(w_lower)
        words.append(w)

    if skipped_count > 0:
        console.print(f"[yellow]Skipped {skipped_count} duplicate word(s) already in directory CSVs or duplicated in input TXT.[/]")

    if not words:
        console.print("[yellow]No new unique words to process.[/]")
        return

    results: List[Dict[str, str]] = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Processing words...", total=len(words))
        
        for word in words:
            progress.update(task, description=f"[cyan]Processing: [bold]{word}[/]")
            results.append(fetch_word(word))
            progress.advance(task)

    if not results:
        return

    # Use keys from the first result as CSV headers
    fieldnames = list(results[0].keys())
    
    console.print(f"Saving to [green]{output_path}[/]...")
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        # writer.writeheader()
        writer.writerows(results)
    
    console.print("[bold green]✔ Done![/]")


def process_file_raw(file_raw_path: str):
    process_file(Path(file_raw_path).absolute())

def main():
    data_dir = Path("data")
    if not data_dir.exists():
        print(f"Error: '{data_dir}' directory not found.")
        return

    console.print(Panel("[bold blue]Anki E-Words Fetcher[/]", subtitle="Youdao API Edition"))
    
    folders = sorted([d for d in data_dir.iterdir() if d.is_dir()])
    
    if not folders:
        console.print(f"[yellow]No folders found in '{data_dir}'.[/]")
        return

    table = Table(title="Available Folders", show_header=True, header_style="bold magenta")
    table.add_column("No.", style="dim", width=6)
    table.add_column("Folder Name")
    
    for i, folder in enumerate(folders, 1):
        table.add_row(str(i), folder.name)
    
    console.print(table)
    
    folder_idx = IntPrompt.ask("\nSelect folder number", choices=[str(i) for i in range(1, len(folders) + 1)]) - 1
    selected_folder = folders[folder_idx]
    
    # List .txt files in the selected folder
    txt_files = sorted([f.name for f in selected_folder.glob("*.txt")])
    
    if not txt_files:
        console.print(f"[yellow]No .txt files found in '{selected_folder.name}'.[/]")
        return

    file_table = Table(title=f"Files in '{selected_folder.name}'", show_header=False)
    file_table.add_column("File")
    for f in txt_files:
        file_table.add_row(f"[blue]- {f}[/]")
    console.print(file_table)
            
    file_name = Prompt.ask("\nEnter file name (without .txt)").strip()
    if not file_name:
        return
        
    target_path = selected_folder / file_name
    process_file(target_path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
