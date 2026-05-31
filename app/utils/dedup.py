import re
from difflib import SequenceMatcher
from typing import Optional
from sqlalchemy.orm import Session
from app.database import Sources, Timeline

def clean_url(url: str) -> str:
    """
    Standardize URLs to avoid duplicates caused by trailing slashes, 
    http vs https, www vs non-www, or query parameters.
    """
    if not url:
        return ""
    # Remove protocol
    url_clean = re.sub(r"^https?://", "", url.lower())
    # Remove www
    url_clean = re.sub(r"^www\.", "", url_clean)
    # Remove query parameters (optional but good for tracking links)
    url_clean = url_clean.split("?")[0]
    # Remove trailing slash
    if url_clean.endswith("/"):
        url_clean = url_clean[:-1]
    return url_clean.strip()

def calculate_similarity(s1: str, s2: str) -> float:
    """
    Calculate textual similarity ratio between two strings.
    0.0 represents completely different, 1.0 represents identical.
    """
    if not s1 or not s2:
        return 0.0
    # Clean text to compare (lowercase, strip, remove extra spaces)
    s1_clean = " ".join(s1.lower().split())
    s2_clean = " ".join(s2.lower().split())
    return SequenceMatcher(None, s1_clean, s2_clean).ratio()

def get_duplicate_source(db: Session, url: str) -> Optional[Sources]:
    """
    Check if a standardized URL already exists in the Sources table.
    Returns the duplicate Sources object if found, else None.
    """
    if not url:
        return None
    target_clean = clean_url(url)
    
    # Query all sources and compare cleaned versions
    all_sources = db.query(Sources).all()
    for src in all_sources:
        if clean_url(src.url) == target_clean:
            return src
    return None

def is_duplicate_url(db: Session, url: str) -> bool:
    """
    Check if a standardized URL already exists in the Sources table.
    """
    return get_duplicate_source(db, url) is not None

def check_duplicate_timeline_item(db: Session, title: str, year: int, type_str: str, threshold: float = 0.85) -> bool:
    """
    Scan the Timeline table for items of the same type and year that 
    have a title similarity higher than the given threshold.
    """
    # Query potential duplicates from the same year and type
    existing_items = db.query(Timeline).filter(
        Timeline.year == year,
        Timeline.type == type_str
    ).all()
    
    for item in existing_items:
        similarity = calculate_similarity(item.title, title)
        if similarity >= threshold:
            print(f"[DEDUPLICADOR] Item duplicado detectado! Similaridade: {similarity:.2f}")
            print(f"  Existente: '{item.title}'")
            print(f"  Novo: '{title}'")
            return True
            
    return False
