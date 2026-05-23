import json
import os
from typing import Dict, List, Any, Optional

DB_FILE = "reviews.json"

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

def get_all_reviews() -> Dict[str, Any]:
    init_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_all_reviews(reviews: Dict[str, Any]):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2)

def get_review(pr_id: str) -> Optional[Dict[str, Any]]:
    return get_all_reviews().get(pr_id)

def save_review(pr_id: str, data: Dict[str, Any]):
    reviews = get_all_reviews()
    reviews[pr_id] = data
    save_all_reviews(reviews)

def delete_review(pr_id: str):
    reviews = get_all_reviews()
    if pr_id in reviews:
        del reviews[pr_id]
        save_all_reviews(reviews)
