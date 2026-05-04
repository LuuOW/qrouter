"""Encode text → DisCoCat diagram → variational quantum circuit.

This module is a thin wrapper around lambeq so the rest of the codebase
doesn't have to know whether we're using the BobcatParser, a smaller
spider parser, or a future replacement. If lambeq's API moves, this is
the only file that needs to update.

The encoding is deliberately simple at day-1:
  text → BobcatParser → DisCoCat diagram → AtomicType ansatz
       → IQPAnsatz circuit (n_layers=1, n_qubits per type=1)

That's enough to exercise the geometry; we'll tune the ansatz once
we have a real evaluation set.
"""

from dataclasses import dataclass
from typing import Any

from qrouter.corpus import Document


@dataclass
class EncodedDoc:
    """A document plus its quantum circuit. The circuit is an opaque
    lambeq object — the retrieval layer treats it as a black-box that
    can be `evaluate()`d into a state vector."""
    doc: Document
    circuit: Any   # lambeq.backend.quantum.Diagram (avoid heavy import here)


# Lazily build the parser + ansatz so importing qrouter doesn't pay the
# (very large) lambeq + spaCy + Bobcat model load cost unless we're
# actually encoding something.
_parser = None
_ansatz = None


def _get_parser():
    global _parser
    if _parser is None:
        from lambeq import BobcatParser
        _parser = BobcatParser(verbose="suppress")
    return _parser


def _get_ansatz():
    global _ansatz
    if _ansatz is None:
        from lambeq import AtomicType, IQPAnsatz
        N = AtomicType.NOUN
        S = AtomicType.SENTENCE
        # 1 qubit per atomic type, 1 IQP layer: small enough to simulate
        # quickly, structured enough to show non-trivial overlap.
        _ansatz = IQPAnsatz({N: 1, S: 1}, n_layers=1)
    return _ansatz


def encode_one(text: str) -> Any:
    """Parse a single string → DisCoCat diagram → quantum circuit."""
    parser = _get_parser()
    ansatz = _get_ansatz()
    diagram = parser.sentence2diagram(text)
    if diagram is None:
        raise ValueError(f"lambeq could not parse: {text!r}")
    return ansatz(diagram)


def encode_corpus(items: list[Document] | list[str]) -> list[EncodedDoc]:
    """Encode every document in `items`. Strings are wrapped in a
    minimal Document so the return shape is uniform."""
    out: list[EncodedDoc] = []
    for item in items:
        if isinstance(item, str):
            doc = Document(text=item, meta={})
        else:
            doc = item
        out.append(EncodedDoc(doc=doc, circuit=encode_one(doc.text)))
    return out
