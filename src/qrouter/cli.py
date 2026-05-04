"""Tiny CLI for the day-1 demo: rank the bundled fixture against a query.

    $ qrouter "what happens when light hits a barrier"

Prints the corpus sorted by Born-rule overlap. No arguments → uses a
default query so a fresh user can verify the toolchain in one command.
"""

import sys

from qrouter.corpus   import load_fixture
from qrouter.encode   import encode_corpus
from qrouter.retrieve import rank_against


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    query = " ".join(argv) if argv else "photons travel through optical apparatus"

    print(f"query: {query!r}")
    print("encoding fixture…")
    corpus = encode_corpus(load_fixture())
    print(f"  {len(corpus)} documents encoded")

    print("ranking…")
    scored = rank_against(corpus, query)

    print()
    print("rank  score    text")
    print("----  -------  --------------------------------------------------")
    for i, s in enumerate(scored, 1):
        print(f"{i:>4}  {s.score:>7.4f}  {s.doc.doc.text}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
