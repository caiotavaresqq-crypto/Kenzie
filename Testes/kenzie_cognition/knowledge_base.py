"""Phase 4: curated starter knowledge and lightweight local retrieval."""
from __future__ import annotations
import json
import re
from pathlib import Path
from collections import Counter



class KnowledgeBase:
    def __init__(self, pack_path=None):
        self.pack_path = Path(pack_path) if pack_path else Path(__file__).resolve().parent.parent / "knowledge_pack" / "domains"
        self.entries = self.load_pack(self.pack_path)

    @staticmethod
    def load_pack(path):
        path = Path(path)
        files = sorted(path.glob("*.json")) if path.is_dir() else [path]
        entries = []
        for file in files:
            with file.open("r", encoding="utf-8") as stream:
                payload = json.load(stream)
            if not isinstance(payload, list):
                raise ValueError(f"Knowledge file must contain a list: {file.name}")
            for item in payload:
                if not isinstance(item, dict) or not item.get("id") or not item.get("title") or not item.get("content"):
                    raise ValueError(f"Malformed knowledge entry in {file.name}")
                item = dict(item)
                item.setdefault("domain", file.stem)
                item["source"] = f"curated_starter_pack:{file.name}"
                item["confidence"] = 0.72
                item["verified"] = False
                entries.append(item)
        ids = [e["id"] for e in entries]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate knowledge IDs in pack")
        return entries


    @staticmethod
    def _tokens(text):
        return {t for t in re.findall(r"[\wÀ-ÿ]+", str(text).lower()) if len(t) > 1}



    def search(self, query, limit=5, domain=None):
        query_tokens = self._tokens(query)
        if not query_tokens:
            return []
        scored = []
        for entry in self.entries:
            if domain and entry.get("domain") != domain:
                continue
            searchable = " ".join([entry.get("title", ""), entry.get("content", ""), " ".join(entry.get("tags", [])), entry.get("example", ""), entry.get("cautions", "")])
            tokens = self._tokens(searchable)
            overlap = query_tokens & tokens
            if not overlap:
                continue
            tag_tokens = self._tokens(" ".join(entry.get("tags", [])))
            title_tokens = self._tokens(entry.get("title", ""))
            score = len(overlap) / max(1, len(query_tokens))
            score += 0.30 * (len(overlap & tag_tokens) / max(1, len(query_tokens)))
            score += 0.25 * (len(overlap & title_tokens) / max(1, len(query_tokens)))
            if query.strip().lower() in entry.get("title", "").lower():
                score += 0.5
            scored.append((score, entry))
        scored.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
        return [{"score": round(score, 4), **entry} for score, entry in scored[:max(1, min(int(limit), 25))]]

    def domains(self):
        return sorted({entry.get("domain", "general") for entry in self.entries})



    def import_into_store(self, store, replace=False):
        """Import starter pack to SQLite. Existing entries are retained unless replace=True."""
        imported = 0
        skipped = 0
        for entry in self.entries:
            topic = f"{entry['domain']}::{entry['title']}::{entry['id']}"
            existing = store.search_topic(entry["id"], limit=5)
            if existing and not replace:
                skipped += 1
                continue
            content_parts = [entry["content"]]
            if entry.get("example"):
                content_parts.append("Example: " + entry["example"])
            if entry.get("cautions"):
                content_parts.append("Cautions: " + entry["cautions"])
            store.add(topic, "\n".join(content_parts), source=entry["source"], confidence=entry["confidence"], verified=entry["verified"])
            imported += 1
        return {"imported": imported, "skipped": skipped, "total": len(self.entries)}



if __name__ == "__main__":
    kb = KnowledgeBase()
    print(f"Loaded {len(kb.entries)} starter knowledge items across {len(kb.domains())} domains.")
    for result in kb.search("how to debug an error and run tests", limit=3):
        print(f"[{result['score']}] {result['title']} ({result['domain']})")
