SCHEMA = """
CREATE TABLE IF NOT EXISTS vocab (
    id              INTEGER PRIMARY KEY,
    word            TEXT,
    transliteration TEXT,
    gloss           TEXT,
    root            TEXT,
    pos             TEXT,
    grammar_point   TEXT,
    related_to      INTEGER REFERENCES vocab(id),
    date_learned    DATE,
    source          TEXT,
    CHECK (word IS NOT NULL OR grammar_point IS NOT NULL)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_vocab_label_source
ON vocab(COALESCE(word, grammar_point), source);

CREATE TABLE IF NOT EXISTS vocab_tag (
    vocab_id INTEGER NOT NULL REFERENCES vocab(id),
    tag      TEXT NOT NULL,
    PRIMARY KEY (vocab_id, tag)
);
"""

import sqlite3
from datetime import date

def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA)
    return conn

def insert_vocab(conn, word=None, translit=None, gloss=None, root=None, pos=None, grammar_point=None, related_to=None, date_learned=None, source=None, tags=None):
    try:
        if not word and not grammar_point:
            print("Error: provide either word or grammar_point")
            return None

        date_learned = date_learned or date.today().isoformat()

        cur = conn.execute(
            """
            INSERT INTO vocab
                (word, transliteration, gloss, root, pos, grammar_point, related_to, date_learned, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                word,
                translit,
                gloss,
                root,
                pos,
                grammar_point,
                related_to,
                date_learned,
                source,
            ),
        )
        vocab_id = cur.lastrowid

        for tag in (tags or []):
            conn.execute(
                "INSERT OR IGNORE INTO vocab_tag (vocab_id, tag) VALUES (?, ?)",
                (vocab_id, tag)
            )

        conn.commit()
        return vocab_id
    except sqlite3.IntegrityError:
        return None