import csv
import re
from pathlib import Path

def validate():
    csv_path = Path("data/困难词库/27.csv")
    assert csv_path.exists(), "File does not exist"

    # Check UTF-8 BOM
    with open(csv_path, "rb") as f:
        content = f.read()
        assert content.startswith(b'\xef\xbb\xbf'), "Missing UTF-8 BOM header"

    # Read rows
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = list(csv.reader(f))

    print(f"Total rows: {len(reader)}")
    assert len(reader) > 0, "CSV is empty"

    forbidden_patterns = [
        re.compile(r"\(人名\)"),
        re.compile(r"\(姓氏\)"),
        re.compile(r"\(等于"),
        re.compile(r"\[物\]"),
        re.compile(r"\[生物\]"),
        re.compile(r"的过去式"),
        re.compile(r"的现在分词"),
    ]

    for i, row in enumerate(reader, 1):
        assert len(row) == 4, f"Row {i} has {len(row)} columns instead of 4"
        word, us_ph, uk_ph, defn = row
        assert word.strip(), f"Row {i}: Word is empty"
        assert us_ph != "-", f"Row {i}: US Phonetic is placeholder '-'"
        assert uk_ph != "-", f"Row {i}: UK Phonetic is placeholder '-'"
        assert defn.strip(), f"Row {i}: Definition is empty"

        for pat in forbidden_patterns:
            assert not pat.search(defn), f"Row {i}: Definition '{defn}' contains forbidden pattern {pat.pattern}"

    print("ALL VALIDATION CHECKS PASSED!")

if __name__ == "__main__":
    validate()
