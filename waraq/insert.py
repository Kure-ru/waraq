from dataclasses import dataclass
from datetime import date
import sqlite3
from typing import Optional

@dataclass
class InsertResult:
    vocab_id: Optional[int]
    status: str
    detail: Optional[str] = None

def insert_vocab(conn, word=None, translit=None, gloss=None, root=None, pos=None, grammar_point=None, related_to=None, date_learned=None, source=None, tags=None):

    if not word and not grammar_point:
        return InsertResult(None, "Error: provide either word or grammar_point")

    date_resolved = date_learned or date.today().isoformat()

    try:
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
                date_resolved,
                source,
            ),
        )
    except sqlite3.IntegrityError as error:
        conn.rollback()
        status = "duplicate" if "idx_vocab_label_source" in str(error) else "error"
        return InsertResult(None, status, str(error))

    vocab_id = cur.lastrowid

    try:
        for tag in (tags or []):
            conn.execute(
                "INSERT OR IGNORE INTO vocab_tag (vocab_id, tag) VALUES (?, ?)",
                (vocab_id, tag)
            )
    except sqlite3.IntegrityError as error:
        conn.rollback()
        return InsertResult(None, "error", f"tag insert failed: {error}")

    conn.commit()
    return InsertResult(vocab_id, "inserted")