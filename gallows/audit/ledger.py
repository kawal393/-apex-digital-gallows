"""
DIGITAL GALLOWS - Core Audit Ledger
Article 12 Compliance (Record-Keeping)
"""

import sqlite3
import hashlib
import json
import time
from typing import Dict, Any

class ImmutableLedger:
    def __init__(self, db_path: str = "compliance_ledger.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                event_type TEXT NOT NULL,
                model_id TEXT NOT NULL,
                payload_hash TEXT NOT NULL,
                payload_data TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                current_hash TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def _get_last_hash(self) -> str:
        cursor = self.conn.cursor()
        cursor.execute('SELECT current_hash FROM audit_log ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        return row[0] if row else "0" * 64

    def _calculate_hash(self, timestamp: float, event_type: str, model_id: str, payload_hash: str, previous_hash: str) -> str:
        data = f"{timestamp}{event_type}{model_id}{payload_hash}{previous_hash}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def log_event(self, event_type: str, model_id: str, payload: Dict[str, Any]) -> str:
        timestamp = time.time()
        payload_json = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_json.encode('utf-8')).hexdigest()
        
        previous_hash = self._get_last_hash()
        current_hash = self._calculate_hash(timestamp, event_type, model_id, payload_hash, previous_hash)

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO audit_log 
            (timestamp, event_type, model_id, payload_hash, payload_data, previous_hash, current_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, event_type, model_id, payload_hash, payload_json, previous_hash, current_hash))
        self.conn.commit()
        return current_hash

    def verify_chain(self) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT timestamp, event_type, model_id, payload_hash, previous_hash, current_hash FROM audit_log ORDER BY id ASC')
        rows = cursor.fetchall()

        expected_previous = "0" * 64
        for row in rows:
            timestamp, event_type, model_id, payload_hash, previous_hash, current_hash = row
            if previous_hash != expected_previous:
                return False
            calculated = self._calculate_hash(timestamp, event_type, model_id, payload_hash, previous_hash)
            if calculated != current_hash:
                return False
            expected_previous = current_hash
        return True

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    ledger = ImmutableLedger(":memory:")
    print("Testing Immutable Ledger...")
    h1 = ledger.log_event("MODEL_INFERENCE", "gpt-4", {"input_tokens": 100})
    h2 = ledger.log_event("OVERSIGHT_FLAG", "gpt-4", {"reason": "Toxicity"})
    print(f"Logged 1: {h1}")
    print(f"Logged 2: {h2}")
    print(f"Chain Valid: {ledger.verify_chain()}")
    ledger.close()