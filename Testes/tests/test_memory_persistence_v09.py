import tempfile
import unittest
from pathlib import Path
from memory_store import MemoryStore

class MemoryPersistenceV09Tests(unittest.TestCase):
    def test_short_term_history_survives_store_reinitialization(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / 'memory.db'
            first = MemoryStore(str(db_path))
            first.add_message('user', 'Mensagem para continuidade')
            first.add_message('assistant', 'Resposta local')
            restarted = MemoryStore(str(db_path))
            history = restarted.get_recent_messages(10)
            self.assertEqual(history[-2]['content'], 'Mensagem para continuidade')
            self.assertEqual(history[-1]['content'], 'Resposta local')

    def test_long_term_fact_survives_reinitialization(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / 'memory.db'
            first = MemoryStore(str(db_path))
            first.set_fact('project_name', 'Kenzie 0.9')
            restarted = MemoryStore(str(db_path))
            self.assertEqual(restarted.get_all_facts()['project_name'], 'Kenzie 0.9')

if __name__ == '__main__': unittest.main()
