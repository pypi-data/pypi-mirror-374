import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent.parent

Seconds = int  # just an alias for readability

def get_default_output_dir() -> Path:
    """Get platform-appropriate output directory."""
    home = Path.home()
    
    # First try to use Documents/LinkedInJobs
    docs_dir = home / 'Documents'
    if docs_dir.exists() and os.access(docs_dir, os.W_OK):
        output_dir = docs_dir / 'LinkedInJobs'
        output_dir.mkdir(exist_ok=True)
        return output_dir
    
    # Fallback to .linkedin_job_scraper in home directory
    output_dir = home / '.linkedin_job_scraper'
    output_dir.mkdir(exist_ok=True)
    return output_dir

@dataclass(frozen=True)
class Config:
    """Application configuration constants."""
    BASE_OUTPUT_DIR: Path = field(default_factory=get_default_output_dir)
    LOG_FILE: Path = BASE_DIR / "logs" / "scraper.log"
    RAND_DELAY: Seconds = 5
    PROXIES: List[str] = field(default_factory=lambda: [
        # "http://102.177.176.109:80"
    ])

config = Config()
config.BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
