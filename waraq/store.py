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

def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA)
    conn.row_factory = sqlite3.Row
    return conn

def _build_filters(tag, before_date):
    filters = [
        (tag, "vt.tag = ?"),
        (before_date, "v.date_learned < ?"),
    ]
    clauses = [frag for value, frag in filters if value is not None]
    params = [value for value, frag in filters if value is not None]
    return clauses, params

def get_known_vocab(conn, tag=None, before_date=None):
        clauses, params = _build_filters(tag, before_date)

        join_clauses = "JOIN vocab_tag vt ON vt.vocab_id = v.id" if tag is not None else ""
        where_clauses = "WHERE " + " AND ".join(clauses) if clauses else ""

        sql = f"""
            SELECT *
            FROM vocab v
            {join_clauses}
            {where_clauses}
            ORDER BY v.date_learned
            """

        return conn.execute(sql, params).fetchall()
