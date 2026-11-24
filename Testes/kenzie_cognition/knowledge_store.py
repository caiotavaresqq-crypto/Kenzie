"""Local SQLite knowledge store with explicit source/confidence and timestamps."""
import sqlite3
from contextlib import closing
from pathlib import Path
from datetime import datetime, timezone



class KnowledgeStore:
    def __init__(self, path="kenzie_knowledge.sqlite3"):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.path)



    def _initialize(self):
        with closing(self._connect()) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'user_or_model',
                confidence REAL NOT NULL DEFAULT 0.5 CHECK(confidence >= 0 AND confidence <= 1),
                verified INTEGER NOT NULL DEFAULT 0 CHECK(verified IN (0,1)),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )""")
            db.execute("CREATE INDEX IF NOT EXISTS knowledge_topic_idx ON knowledge(topic)")
            db.commit()

    def add(self, topic, content, source="user_or_model", confidence=0.5, verified=False):
        topic, content = str(topic).strip(), str(content).strip()
        if not topic or not content:
            raise ValueError("topic and content must not be blank")
        if not 0 <= float(confidence) <= 1:
            raise ValueError("confidence must be between 0 and 1")
        now = datetime.now(timezone.utc).isoformat()
        with closing(self._connect()) as db:
            cur = db.execute("INSERT INTO knowledge(topic,content,source,confidence,verified,created_at,updated_at) VALUES(?,?,?,?,?,?,?)",
                (topic, content, str(source), float(confidence), int(bool(verified)), now, now))
            db.commit()
            return cur.lastrowid

    def search_topic(self, topic, limit=25):
        with closing(self._connect()) as db:
            rows = db.execute("SELECT id,topic,content,source,confidence,verified,created_at,updated_at FROM knowledge WHERE topic LIKE ? ORDER BY updated_at DESC LIMIT ?",
                (f"%{topic}%", max(1, min(int(limit), 100)))).fetchall()
        return [dict(zip(["id","topic","content","source","confidence","verified","created_at","updated_at"], row)) for row in rows]



    def mark_verified(self, entry_id, verified=True):
        now = datetime.now(timezone.utc).isoformat()
        with closing(self._connect()) as db:
            cur = db.execute("UPDATE knowledge SET verified=?,updated_at=? WHERE id=?", (int(bool(verified)), now, int(entry_id)))
            db.commit()
            return cur.rowcount > 0
