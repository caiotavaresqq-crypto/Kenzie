"""Memória persistente local da Kenzie baseada em SQLite."""
import os, re, sqlite3
from datetime import datetime

class MemoryStore:
    def __init__(self, database_path):
        self.database_path = database_path
        os.makedirs(os.path.dirname(os.path.abspath(database_path)), exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS facts (id INTEGER PRIMARY KEY, category TEXT NOT NULL, fact_key TEXT NOT NULL UNIQUE, fact_value TEXT NOT NULL, updated_at TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_messages_id ON messages(id DESC)")

    def _connect(self):
        db=sqlite3.connect(self.database_path, timeout=10)
        db.row_factory=sqlite3.Row
        return db

    def _category(self, key):
        if key in {"nome", "tratamento", "nome_assistente", "papel_kenzie"}: return "identidade"
        if "projeto" in key: return "projeto"
        if key.startswith(("informação_", "informacao_")): return "fato"
        return "geral"

    def set_fact(self, key, value, category=None):
        if not key or value is None: return False
        with self._connect() as db:
            db.execute("""INSERT INTO facts(category,fact_key,fact_value,updated_at) VALUES(?,?,?,?)
            ON CONFLICT(fact_key) DO UPDATE SET category=excluded.category,fact_value=excluded.fact_value,updated_at=excluded.updated_at""",
            (category or self._category(str(key)), str(key), str(value), datetime.now().isoformat(timespec="seconds")))
        return True

    def set_facts(self, facts):
        for key,value in facts.items(): self.set_fact(key,value)

    def get_all_facts(self):
        with self._connect() as db:
            rows=db.execute("SELECT fact_key,fact_value FROM facts ORDER BY category,fact_key").fetchall()
        return {r["fact_key"]:r["fact_value"] for r in rows}

    def add_message(self, role, content):
        if content:
            with self._connect() as db:
                db.execute("INSERT INTO messages(role,content,created_at) VALUES(?,?,?)",(role,str(content),datetime.now().isoformat(timespec="seconds")))

    def get_recent_messages(self, limit=20):
        with self._connect() as db:
            rows=db.execute("SELECT role,content FROM messages ORDER BY id DESC LIMIT ?",(int(limit),)).fetchall()
        return [{"role":r["role"],"content":r["content"]} for r in reversed(rows)]

    def search_facts(self, query, limit=18):
        facts=self.get_all_facts()
        words=set(re.findall(r"[a-zA-ZÀ-ÿ0-9_]{3,}",query.lower()))
        priority={"nome","tratamento","nome_assistente","papel_kenzie"}
        ranked=[]
        for key,value in facts.items():
            hay=f"{key} {value}".lower()
            score=sum(1 for word in words if word in hay)+(2 if key in priority else 0)
            ranked.append((score,key,value))
        ranked.sort(reverse=True)
        selected=dict((key,value) for score,key,value in ranked if score>0)
        selected=dict(list(selected.items())[:limit])
        for key in priority:
            if key in facts: selected.setdefault(key,facts[key])
        return selected

    def build_prompt_memory(self, query):
        facts=self.search_facts(query)
        return "\n".join(f"- {k}: {v}" for k,v in facts.items()) if facts else "Nenhuma informação persistente foi salva ainda."
