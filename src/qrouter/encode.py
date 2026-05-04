"""Encode text → diagram → variational quantum circuit.

Two parser backends, gated by the QROUTER_PARSER env var:
  spider   — SpiderReader. Zero remote downloads, no CCG. Each word is
             a spider node; sentence diagram is a chain. Sufficient for
             day-1 Born-rule overlap; loses linguistic structure that
             distinguishes "cat chases dog" from "dog chases cat".
  bobcat   — BobcatParser. Real CCG parsing → DisCoCat. Needs a model
             download from qnlp.cambridgequantum.com on first use.
             Currently DOWN (CQ's CDN); we re-enable bobcat once the
             upstream is back or we self-host the weights on HF.

Default is `spider` — it's the only one that boots reliably right now.

The ansatz layer is shared: AtomicType {N,S} → 1 qubit each, IQPAnsatz
n_layers=1. Small enough to simulate fast on CPU, structured enough to
show non-trivial overlap.
"""

from dataclasses import dataclass
import os
from typing import Any

from qrouter.corpus import Document


@dataclass
class EncodedDoc:
    """A document plus its quantum circuit. The circuit is an opaque
    lambeq object — the retrieval layer treats it as a black-box that
    can be `evaluate()`d into a state vector."""
    doc: Document
    circuit: Any   # lambeq.backend.quantum.Diagram (avoid heavy import here)


PARSER_BACKEND = os.environ.get("QROUTER_PARSER", "spider").lower()

# Lazily build the parser + ansatz so importing qrouter doesn't pay the
# (very large) lambeq + spaCy + Bobcat model load cost unless we're
# actually encoding something.
_parser = None
_ansatz = None


def _get_parser():
    global _parser
    if _parser is None:
        if PARSER_BACKEND == "bobcat":
            from lambeq import BobcatParser
            _parser = BobcatParser(verbose="suppress")
        else:
            # SpiderReader needs no model download. Each word becomes a
            # spider node; sentence is the chain composition.
            from lambeq import spiders_reader
            _parser = spiders_reader
    return _parser


def _get_ansatz():
    global _ansatz
    if _ansatz is None:
        from lambeq import AtomicType, IQPAnsatz
        N = AtomicType.NOUN
        S = AtomicType.SENTENCE
        # 1 qubit per atomic type, 1 IQP layer.
        _ansatz = IQPAnsatz({N: 1, S: 1}, n_layers=1)
    return _ansatz


def encode_one(text: str) -> Any:
    """Parse a single string → diagram → quantum circuit."""
    parser = _get_parser()
    ansatz = _get_ansatz()
    diagram = parser.sentence2diagram(text)
    if diagram is None:
        raise ValueError(f"parser could not handle: {text!r}")
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
