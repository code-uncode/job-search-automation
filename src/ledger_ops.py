import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional

LEDGER_FILE = "data/ledger.jsonl"
ARCHIVE_DIR = "data/archive"

def generate_job_hash(company: str, title: str) -> str:
    """Generates an MD5 hash for a job based on company name and title."""
    unique_string = f"{company.strip().lower()}|{title.strip().lower()}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def is_duplicate(job_hash: str) -> bool:
    """Checks if a job hash already exists in the ledger or archive."""
    if not os.path.exists(LEDGER_FILE):
        return False
    
    with open(LEDGER_FILE, "r") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("hash") == job_hash:
                return True
                
    # Also check the archive folder for files
    if os.path.exists(ARCHIVE_DIR):
        for archive_file in os.listdir(ARCHIVE_DIR):
            archive_path = os.path.join(ARCHIVE_DIR, archive_file)
            with open(archive_path, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get("hash") == job_hash:
                        return True
                        
    return False

def add_to_ledger(job_data: Dict):
    """Adds a new job entry to the ledger.jsonl file."""
    job_data["last_seen_at"] = datetime.now().isoformat()
    if "applied" not in job_data:
        job_data["applied"] = 0
        
    with open(LEDGER_FILE, "a") as f:
        f.write(json.dumps(job_data) + "\n")

def archive_old_jobs(retention_days: int = 30):
    """Moves old unapplied jobs to the archive directory."""
    if not os.path.exists(LEDGER_FILE):
        return
    
    remaining_entries = []
    archived_entries = []
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    with open(LEDGER_FILE, "r") as f:
        for line in f:
            entry = json.loads(line)
            last_seen = datetime.fromisoformat(entry["last_seen_at"])
            
            # Keep if applied or if it's within the retention period
            if entry.get("applied") == 1 or last_seen > cutoff_date:
                remaining_entries.append(entry)
            else:
                archived_entries.append(entry)
                
    # Update the ledger file with remaining entries
    with open(LEDGER_FILE, "w") as f:
        for entry in remaining_entries:
            f.write(json.dumps(entry) + "\n")
            
    # Write archived entries to a new file in the archive directory
    if archived_entries:
        if not os.path.exists(ARCHIVE_DIR):
            os.makedirs(ARCHIVE_DIR)
        
        archive_file = os.path.join(ARCHIVE_DIR, f"archive_{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(archive_file, "a") as f:
            for entry in archived_entries:
                f.write(json.dumps(entry) + "\n")
