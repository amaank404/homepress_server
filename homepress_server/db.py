import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .config import config

persistent_db = sqlite3.connect(config.working_directory / "homepress_server.db", check_same_thread=False)
temp_db = sqlite3.connect(":memory:", check_same_thread=False)

with persistent_db:
    cur = persistent_db.cursor()
    # Script for persistent db's data
    cur.executescript(
"""
DROP TABLE logs;

CREATE TABLE IF NOT EXISTS logs (
    time INTEGER,
    message VARCHAR(256),
    priority SMALLINT
);
"""
    )

with temp_db:
    cur = temp_db.cursor()
    cur.executescript(
"""
CREATE TABLE sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    token VARCHAR(128)
);

CREATE TABLE files (
    session_id INTEGER,
    id VARCHAR(64),
    size INTEGER,
    mime VARCHAR(64),
    name VARCHAR(32),

    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
"""
    )

def get_db_timestamp_now():
    return datetime.now(timezone.utc).timestamp()

def get_time_from_timestamp(t: int):
    return datetime.fromtimestamp(t, timezone.utc)

class SessionContext():
    def __init__(self, token):
        self.token = token
        
        cur = temp_db.cursor()
        self.session_id = cur.execute("SELECT session_id FROM sessions WHERE token=?", (token,)).fetchone()
        if self.session_id is None:
            raise ValueError("Invalid session id")
        else:
            self.session_id = self.session_id[0]

    def files(self):
        cur = temp_db.cursor()
        cur.execute("SELECT id, size, mime FROM files WHERE session_id=?", (self.session_id,))

    def add_file(self, id, size, mime, name):
        with temp_db:
            cur = temp_db.cursor()
            cur.execute("INSERT INTO files VALUES (?, ?, ?, ?, ?)", (self.session_id, id, size, mime, name))

class SessionsManager():
    def __init__(self):
        pass
 
    def add(self) -> str:
        with temp_db:
            cur = temp_db.cursor()
            token = secrets.token_urlsafe(128)
            cur.execute("INSERT INTO sessions (token) VALUES (?)", (token,))
        return token

    def remove(self, token):
        with temp_db:
            cur = temp_db.cursor()
            cur.execute("DELETE FROM sessions WHERE token=?", (token,))

    def sessions(self):
        cur = temp_db.cursor()
        return cur.execute("SELECT * FROM sessions").fetchall()
    
    def get_context(self, token):
        return SessionContext(token)