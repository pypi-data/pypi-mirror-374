# collepedia/client.py

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal

import feedparser
import requests

from .exceptions import CollepediaConnectionError

@dataclass
class PostEntry:
    """Represents the metadata for a single post."""
    id: str
    title: str
    link: str
    published_iso: Optional[str]
    published_dt: Optional[datetime]
    categories: List[str]
    author: Optional[str]

    @classmethod
    def from_feed_entry(cls, entry) -> "PostEntry":
        post_id = getattr(entry, "id", getattr(entry, "link", str(hash(str(entry)))))
        
        published_iso, published_dt = None, None
        
        # **IMPROVED DATE PARSING LOGIC**
        # Primary method: Use feedparser's parsed tuple
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published_dt = datetime(*entry.published_parsed[:6])
                published_iso = published_dt.isoformat()
            except (ValueError, TypeError):
                published_dt, published_iso = None, None # Reset on failure

        # Fallback method: Try to parse the raw string if the first method failed
        if not published_dt and hasattr(entry, "published") and entry.published:
            try:
                # Handle common ISO formats, removing 'Z' and trimming timezone info
                date_str = entry.published.replace('Z', '')
                if '+' in date_str:
                    date_str = date_str.split('+')[0]
                if '.' in date_str: # handle microseconds
                    date_str = date_str.split('.')[0]
                
                published_dt = datetime.fromisoformat(date_str)
                published_iso = published_dt.isoformat()
            except (ValueError, TypeError):
                 pass # Could not parse the string

        categories = [tag.get("term", "") for tag in getattr(entry, "tags", []) if tag.get("term")]
        return cls(id=str(post_id), title=getattr(entry, "title", "No Title"),
                   link=getattr(entry, "link", ""), published_iso=published_iso,
                   published_dt=published_dt, categories=categories,
                   author=getattr(entry, "author", None))

    def to_dict(self) -> Dict[str, Any]:
        # Updated to use the correct fields from the dataclass
        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "published": self.published_iso,
            "categories": self.categories,
            "author": self.author,
        }


class CollepediaClient:
    """A dedicated client for fetching post metadata from Collepedia."""
    _FEED_URL = "https://colle-pedia.blogspot.com/feeds/posts/default"

    def __init__(self, user_agent: str = "Collepedia/1.0.1"): # Version bump
        self._posts: List[PostEntry] = []
        self._id_map: Dict[str, PostEntry] = {}
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})

    def fetch_posts(self, max_posts: int = 100, per_request: int = 25, category: Optional[str] = None) -> int:
        self.clear_cache()
        fetched_count = 0
        fetch_url = self._FEED_URL
        if category:
            fetch_url += f"/-/{category}"
        while fetched_count < max_posts:
            params = {"alt": "rss", "start-index": fetched_count + 1,
                      "max-results": min(per_request, max_posts - fetched_count, 500)}
            try:
                response = self._session.get(fetch_url, params=params, timeout=15)
                response.raise_for_status()
            except requests.RequestException as e:
                raise CollepediaConnectionError(f"Failed to connect to Collepedia: {e}")
            entries = feedparser.parse(response.content).entries
            if not entries: break
            for entry in entries:
                post = PostEntry.from_feed_entry(entry)
                if post.id not in self._id_map:
                    self._posts.append(post)
                    self._id_map[post.id] = post
            fetched_count += len(entries)
            if len(entries) < params["max-results"]: break
        return self.count()

    def get_all_posts(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self._posts]

    def filter(self, author_contains: Optional[str] = None, category: Optional[str] = None,
               date_start: Optional[str] = None, date_end: Optional[str] = None) -> List[Dict[str, Any]]:
        results = self._posts
        if author_contains: results = [p for p in results if p.author and author_contains.lower() in p.author.lower()]
        if category: results = [p for p in results if any(category.lower() == c.lower() for c in p.categories)]
        if date_start: results = [p for p in results if p.published_dt and p.published_dt >= datetime.fromisoformat(date_start)]
        if date_end: results = [p for p in results if p.published_dt and p.published_dt <= datetime.fromisoformat(date_end)]
        return [p.to_dict() for p in results]

    def sort(self, by: Literal["published", "title"] = "published", reverse: bool = True) -> List[Dict[str, Any]]:
        key_map = {"published": lambda p: p.published_dt or datetime.min, "title": lambda p: p.title.lower()}
        return [p.to_dict() for p in sorted(self._posts, key=key_map[by], reverse=reverse)]

    def count(self) -> int:
        return len(self._posts)

    def clear_cache(self):
        self._posts, self._id_map = [], {}

    def save_cache(self, path: str):
        with open(path, "w", encoding="utf8") as f:
            json.dump([p.to_dict() for p in self._posts], f, ensure_ascii=False, indent=2)

    def load_cache(self, path: str):
        with open(path, "r", encoding="utf8") as f: data = json.load(f)
        self.clear_cache()
        for item in data:
            published_dt = datetime.fromisoformat(item["published"]) if item.get("published") else None
            post = PostEntry(id=item["id"], title=item["title"], link=item["link"],
                             published_iso=item.get("published"), published_dt=published_dt,
                             categories=item.get("categories", []), author=item.get("author"))
            if post.id not in self._id_map: self._posts.append(post); self._id_map[post.id] = post


