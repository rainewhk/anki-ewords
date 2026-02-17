import csv
import os
from pathlib import Path
from typing import List, Dict, Any

from utils.youdao import fetch_word

# Global counter for progress display
count = 0


def get_data_map(text: str) -> Dict[str, str]:
    """Fetch word info and print progress."""
    global count
    count += 1
    print(f"[{count}] Processing: {text}")
    return fetch_word(text)


def process_file(file_base_path: Path):
    """Read words from .txt and save results to .csv."""
    input_path = file_base_path.with_suffix(".txt")
    output_path = file_base_path.with_suffix(".csv")
    
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.")
        return

    results: List[Dict[str, str]] = []
    
    print(f"Reading from {input_path}...")
    with open(input_path, "r", encoding="utf-8") as f:
        # Filter out empty lines and whitespace
        words = [line.strip() for line in f if line.strip()]

    if not words:
        print("Warning: Input file is empty.")
        return

    for word in words:
        results.append(get_data_map(word))

    if not results:
        return

    # Use keys from the first result as CSV headers
    fieldnames = list(results[0].keys())
    
    print(f"Saving to {output_path}...")
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(results)
    
    print("Done!")


def main():
    data_dir = Path("data")
    if not data_dir.exists():
        print(f"Error: '{data_dir}' directory not found.")
        return

    # List only directories inside data/
    folders = sorted([d for d in data_dir.iterdir() if d.is_dir()])
    
    if not folders:
        print(f"No folders found in '{data_dir}'.")
        return

    print("\n--- Available Folders ---")
    for i, folder in enumerate(folders, 1):
        print(f"{i}. {folder.name}")
    
    try:
        choice = input("\nSelect folder number: ").strip()
        if not choice: return
        folder_idx = int(choice) - 1
        if not (0 <= folder_idx < len(folders)):
            print("Invalid folder selection.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    selected_folder = folders[folder_idx]
    
    # List .txt files in the selected folder
    print(f"\n--- .txt files in '{selected_folder.name}' ---")
    txt_files = sorted([f.name for f in selected_folder.glob("*.txt")])
    
    if not txt_files:
        print("No .txt files found in this folder.")
        return

    for f in txt_files:
        print(f" - {f}")
            
    file_name = input("\nEnter file name (without .txt): ").strip()
    if not file_name:
        return
        
    target_path = selected_folder / file_name
    process_file(target_path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
