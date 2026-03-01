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

def process_file(file_base_path: Path):
    """Read words from .txt and save results to .csv."""
    input_path = file_base_path.with_suffix(".txt")
    output_path = file_base_path.with_suffix(".csv")
    
    if not input_path.exists():
        console.print(f"[bold red]Error:[/] Input file {input_path} does not exist.")
        return

    print(f"Reading from {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]

    if not words:
        console.print("[yellow]Warning:[/] Input file is empty.")
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
        writer.writeheader()
        writer.writerows(results)
    
    console.print("[bold green]✔ Done![/]")


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
