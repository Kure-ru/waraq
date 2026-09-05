#!/usr/bin/env python3

"""
vocab_cli.py — add one vocab (or grammar) entry to the known-vocab store.

Usage:
  python vocab_cli.py add --word "كتاب" --translit "kitab" --gloss "book" \
      --root "k-t-b" --pos noun --date-learned 2026-09-12 \
      --source "Assimil unit 3" --tags "ordering-coffee,introducing-yourself"

  python vocab_cli.py add --grammar-point "negating equational sentences (ma/laysa)" \
      --date-learned 2026-09-12 --source "teacher notes session 12" \
      --tags "introducing-yourself"

  python vocab_cli.py list --tag ordering-coffee
"""
import argparse
from store import get_conn, insert_vocab

def cmd_add(args, conn):
    tags = [t.strip() for t in (args.tags or "").split(",") if t.strip()]

    vocab_id = insert_vocab(conn, word=args.word, translit=args.translit, gloss=args.gloss, root=args.root, pos=args.pos, grammar_point=args.grammar_point, related_to=args.related_to, date_learned=args.date_learned, source=args.source, tags=tags)

    if vocab_id is None:
        return

    label = args.word or args.grammar_point
    tag_str = f" [{', '.join(tags)}]" if tags else ""
    print(f"Added #{vocab_id}: {label}{tag_str}")


def cmd_list(args, conn):
    if args.tag:
        rows = conn.execute(
            """
            SELECT v.id, COALESCE(v.word, v.grammar_point) AS label, v.gloss
            FROM vocab v
            JOIN vocab_tag vt ON vt.vocab_id = v.id
            WHERE vt.tag = ?
            ORDER BY v.date_learned
            """,
            (args.tag,),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT id, COALESCE(word, grammar_point) AS label, gloss
            FROM vocab ORDER BY date_learned
            """
        ).fetchall()

    if not rows:
        print("No entries found.")
        return

    for vocab_id, label, gloss in rows:
        gloss_str = f" - {gloss}" if gloss else ""
        print(f"#{vocab_id}: {label}{gloss_str}")



def main():
    parser = argparse.ArgumentParser(description="Known-vocab store CLI")
    parser.add_argument("--db", default="waraq.db", help="path to sqlite db file, default path is 'waraq.db'")

    sub = parser.add_subparsers(dest="command", required=True)
    p_add = sub.add_parser("add", help="add one vocab or grammar entry")

    p_add.add_argument("--word", help="word written in arabic script")
    p_add.add_argument("--translit", help="transliteration of word", dest="translit")
    p_add.add_argument("--gloss", help="meaning in English")
    p_add.add_argument("--root")
    p_add.add_argument("--pos")
    p_add.add_argument("--grammar-point", dest="grammar_point")
    p_add.add_argument("--date-learned", dest="date_learned")
    p_add.add_argument("--related-to", dest="related_to", type=int)
    p_add.add_argument("--source")
    p_add.add_argument("--tags", help="comma-separated, e.g 'ordering-coffee,introducing-yourself'")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="list entries, optionally by tag")
    p_list.add_argument("-t", "--tag")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    conn = get_conn(args.db)
    args.func(args, conn)
    conn.close()

if __name__ == "__main__":
    main()



