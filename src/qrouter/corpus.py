"""Corpus loaders. Day-1 has just a hand-curated quant-ph fixture so the
demo runs offline — arXiv ingestion comes later."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    """A single corpus item. `text` is what gets parsed/encoded; `meta`
    carries arbitrary identifiers (arXiv id, slug, source URL)."""
    text: str
    meta: dict


# Tiny hand-built fixture for the day-1 demo. Real titles + paraphrased
# one-liners from quant-ph abstracts — short enough that lambeq's
# CCG parser won't choke on them.
QUANT_PH_FIXTURE: list[Document] = [
    Document(
        text="photons interfere through beam splitters",
        meta={"id": "fixture-001", "topic": "linear-optics"},
    ),
    Document(
        text="electrons tunnel through potential barriers",
        meta={"id": "fixture-002", "topic": "tunneling"},
    ),
    Document(
        text="atoms absorb light at specific frequencies",
        meta={"id": "fixture-003", "topic": "spectroscopy"},
    ),
    Document(
        text="cats observe boxes with opening lids",
        meta={"id": "fixture-004", "topic": "measurement"},
    ),
    Document(
        text="qubits entangle across distant detectors",
        meta={"id": "fixture-005", "topic": "entanglement"},
    ),
]


def load_fixture() -> list[Document]:
    """Return the bundled toy corpus. No I/O."""
    return list(QUANT_PH_FIXTURE)
