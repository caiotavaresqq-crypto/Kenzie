"""Demonstrates starter-pack retrieval and SQLite import."""
from pathlib import Path
from tempfile import TemporaryDirectory
from kenzie_cognition.knowledge_base import KnowledgeBase
from kenzie_cognition.knowledge_store import KnowledgeStore


kb = KnowledgeBase()
print(f"Knowledge pack: {len(kb.entries)} entries in {len(kb.domains())} domains")
query = input("Ask a knowledge question (or Enter for demo): ").strip() or "how can I debug an error and verify tests"
print("\nRelevant entries:")
for item in kb.search(query, limit=5):
    print(f"\n- {item['title']} | {item['domain']} | score={item['score']}")
    print(item["content"])
    if item.get("example"):
        print("Example:", item["example"])
with TemporaryDirectory() as tmp:
    store = KnowledgeStore(Path(tmp) / "demo.sqlite")
    print("\nSQLite import:", kb.import_into_store(store))
