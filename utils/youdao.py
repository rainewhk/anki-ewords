import json
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import requests

from rich.console import Console

# Constants
ENDPOINT = "https://dict.youdao.com/jsonapi"
DEFAULT_PARAMS = {
    "jsonversion": 2,
    "client": "mobile",
    "dicts": '{"count": 99, "dicts": [["syno", "ec"]]}'
}
CACHE_DB_PATH = Path("data/youdaio_cache.db")
ONE_WEEK = 7 * 24 * 3600  # 1 week in seconds
CACHE_MEM: Dict[str, Tuple[Dict[str, Any], int]] = {}

# Global console for rich output
console = Console()

# Session for persistent connections
session = requests.Session()


def _get_db_connection() -> sqlite3.Connection:
    """Helper to create a high-performance SQLite connection."""
    conn = sqlite3.connect(CACHE_DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = OFF")
    # Optimize for large memory (if requested)
    conn.execute("PRAGMA cache_size = -2000000")  # ~2GB
    conn.execute("PRAGMA mmap_size = 2147483648") # 2GB
    return conn


def init_cache():
    """Initialize the cache from SQLite database and load into memory."""
    global CACHE_MEM
    CACHE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with _get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                word TEXT PRIMARY KEY,
                data TEXT,
                timestamp INTEGER
            )
        """)
        
        cursor = conn.execute("SELECT word, data, timestamp FROM cache")
        for word, data_str, ts in cursor:
            try:
                CACHE_MEM[word] = (json.loads(data_str), ts)
            except (json.JSONDecodeError, MemoryError):
                continue


def save_to_cache(word: str, data: Dict[str, Any]):
    """Write to memory cache first, then persist to the database."""
    ts = int(time.time())
    CACHE_MEM[word] = (data, ts)
    
    try:
        with _get_db_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (word, data, timestamp) VALUES (?, ?, ?)",
                (word, json.dumps(data, ensure_ascii=False), ts)
            )
            conn.commit()
    except Exception as e:
        console.print(f"[bold red]Cache Error[/] Failed to persist '{word}': {e}")


def fetch_word_origin(word: str, retries: int = 5) -> Optional[Dict[str, Any]]:
    """Fetch raw word data from Youdao API with cache and retry logic."""
    # 1. Memory Check
    if word in CACHE_MEM:
        data, ts = CACHE_MEM[word]
        if time.time() - ts < ONE_WEEK:
            return data

    # 2. API Fetch
    params = DEFAULT_PARAMS | {"q": word}
    try:
        response = session.get(ENDPOINT, params=params, timeout=10)
        if 200 <= response.status_code < 300:
            data = response.json()
            if data:
                save_to_cache(word, data)
                return data
    except Exception as e:
        console.print(f"[bold red]Fetch Error[/] Request failed for '{word}': {e}")

    # 3. Retry
    if retries > 0:
        time.sleep(1)
        return fetch_word_origin(word, retries - 1)
    
    return None


def fetch_word(word: str) -> Dict[str, str]:
    """Parse raw Youdao data into a simplified dictionary."""
    origin = fetch_word_origin(word)
    
    # User's specific fallback logic
    default_result = {
        "value": word,
        "usphone": "-",
        "ukphone": "-",
        "translation": "-"
    }
    
    if not origin:
        return default_result

    try:
        ec_data = origin.get("ec", {}).get("word", [{}])[0]
        
        translations = []
        for tr in ec_data.get("trs", []):
            # Extract phonetic translations using user's specific path
            l_data = tr.get("tr", [{}])[0].get("l", {}).get("i", [])
            if l_data:
                translations.append(l_data[0])

        result = {
            "value": word,
            "usphone": f"/{ec_data['usphone']}/" if "usphone" in ec_data else "-",
            "ukphone": f"/{ec_data['ukphone']}/" if "ukphone" in ec_data else "-",
            "translation": "<br>".join(translations) or "-"
        }
        return result
        
    except (KeyError, IndexError, TypeError):
        return default_result


# Auto-initialize on import
init_cache()

