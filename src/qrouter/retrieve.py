"""Retrieval = quantum overlap.

Given a query circuit |q⟩ and a corpus of document circuits {|d_i⟩},
the score for d_i is the Born-rule overlap |⟨q|d_i⟩|².

We evaluate each circuit through PennyLane's default.qubit simulator
(or a future photonic simulator), get a state vector, then take the
squared magnitude of the inner product. Pure linear algebra, runs on
laptop CPU for small corpora.

The point isn't speed; it's whether the *geometry* of compositional
quantum semantics gives different rankings than classical embeddings
for the same text — and on what kinds of input that difference matters.
"""

from dataclasses import dataclass

import numpy as np

from qrouter.encode import EncodedDoc, encode_one


@dataclass
class ScoredDoc:
    """A retrieval result. `score` is the Born-rule overlap, in [0, 1].
    Higher = more semantically aligned with the query under this model."""
    doc: EncodedDoc
    score: float


def _state_vector(circuit) -> np.ndarray:
    """Evaluate a lambeq quantum circuit to a complex state vector.

    Lambeq's IQPAnsatz emits circuits with symbolic parameters (the
    variational angles you would normally TRAIN). Calling `.eval()`
    directly on a symbolic circuit raises:

      "Attempting to access modules for a symbolic expression."

    For day-1 retrieval we don't have a labelled training set yet, so
    we bind every free symbol to a deterministic angle derived from a
    SHA-256 hash of the symbol's string name. Concretely: distinct
    words/types → distinct angles → distinct circuits → distinct
    states. This gives a *meaningful* (non-trivial, deterministic,
    unlearned) geometry — sufficient for "does the pipeline work end
    to end" testing. The real research switches `subs_strategy="zero"`
    or `subs_strategy="trained"` once we have the eval set + a learned
    parameter dict.
    """
    from lambeq.backend.quantum import Measure  # noqa: F401  presence guard

    syms = list(getattr(circuit, "free_symbols", []) or [])
    if syms:
        import hashlib
        vals = []
        for s in syms:
            h = int(hashlib.sha256(str(s).encode("utf-8")).hexdigest(), 16) % 1024
            vals.append((h / 1024.0) * 2 * np.pi)
        # lambeq Diagram.lambdify(*syms)(*vals) returns a concrete diagram
        # with all parameters substituted. The resulting object is then
        # safe to .eval().
        circuit = circuit.lambdify(*syms)(*vals)

    result = circuit.eval()
    # Lambeq's eval returns either its Tensor wrapper (with .array) or a
    # raw numpy ndarray, depending on whether substitution happened first.
    arr = np.asarray(getattr(result, "array", result)).flatten().astype(np.complex128)
    norm = np.linalg.norm(arr)
    if norm == 0:
        return arr
    return arr / norm


def born_overlap(a, b) -> float:
    """Compute |⟨a|b⟩|² for two lambeq circuits or state vectors.

    Accepts either circuits (will be evaluated) or pre-computed
    np.ndarray state vectors. Returns a float in [0, 1] if the input
    state vectors are properly normalized."""
    va = a if isinstance(a, np.ndarray) else _state_vector(a)
    vb = b if isinstance(b, np.ndarray) else _state_vector(b)
    if va.shape != vb.shape:
        raise ValueError(f"state-vector shape mismatch: {va.shape} vs {vb.shape}")
    overlap = np.vdot(va, vb)
    return float(np.abs(overlap) ** 2)


def rank_against(corpus: list[EncodedDoc], query: str, top_k: int | None = None) -> list[ScoredDoc]:
    """Encode `query`, score every document, return them sorted descending."""
    q_circuit = encode_one(query)
    q_vec = _state_vector(q_circuit)

    scored: list[ScoredDoc] = []
    for d in corpus:
        try:
            d_vec = _state_vector(d.circuit)
            score = born_overlap(q_vec, d_vec)
        except (ValueError, TypeError):
            # Shape mismatch happens when documents have different
            # sentence types (e.g. a noun-phrase vs a sentence). For
            # day-1 we just skip those — handling type-coercion is a
            # later concern.
            score = 0.0
        scored.append(ScoredDoc(doc=d, score=score))

    scored.sort(key=lambda s: s.score, reverse=True)
    if top_k is not None:
        scored = scored[:top_k]
    return scored
