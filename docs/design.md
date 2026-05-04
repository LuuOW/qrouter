# qrouter design notes

A research diary, not a spec. Update as the work moves.

## Why this exists

Test the hypothesis that **compositional quantum-semantic structure** —
parsing text into pregroup grammars (Lambek 1958), interpreting them in
the category of finite-dimensional Hilbert spaces and linear maps
(FdHilb), then ranking via Born-rule overlap — produces qualitatively
different retrieval behavior than classical dense embeddings on small
domains where the *grammar* of the query carries information that bag-
of-tokens models discard.

This is not a bet that QNLP retrieves *better* on standard benchmarks
at scale. It's a bet that there exist regimes (small specialized
corpora, queries where word order changes meaning, scientific
literature where compositional structure is high-information) where
the geometric and grammatical structure of the encoding matters.

## Scope at day 1

Pre-arXiv toy fixture (5 short quant-ph one-liners) that the demo can
rank without any network or HF download. All circuits ≤ 2 qubits to
keep simulation latency invisible. Single ansatz family (IQP).

## Open design questions

- **Type system.** AtomicType.NOUN vs SENTENCE — for retrieval, probably
  every doc + query is at type S. But noun-phrase queries are a real
  use case ("entanglement entropy"). Strategy TBD: type-coerce, or
  maintain two parallel indices?
- **Sentence length.** lambeq's CCG parser fails on long sentences and
  the resulting circuit gets deep. We may need to split, or accept the
  limit and use it as a forcing function (titles + abstracts only).
- **Ansatz choice.** IQP at n_layers=1 is the floor. SimAnsatz, Sim14,
  Sim15 from Sim et al. (2019) are the obvious next test set. The
  expressivity-vs-trainability tradeoff matters even though we're
  *not* training in the day-1 demo (the structure alone provides the
  encoding).
- **Eval.** No benchmark exists for "QNLP retrieval on quant-ph". We
  will need to either build one (annotate ~100 query-doc pairs) or use
  a coarse semantic-similarity proxy. The benchmark itself may be
  publishable.

## Where this points

If the day-1 to day-30 work shows promise, two natural next steps:

1. **Real backend.** Compile the same circuits to Quantinuum H-series
   (gate-based) or Xanadu X-series (photonic / Gaussian boson sampling).
   Quantinuum offers free academic time; Xanadu's Borealis is metered
   but cheap by photonics standards.

2. **Photonic reservoir as a front-end.** Replace the variational
   circuit ansatz with a *physical* photonic reservoir — a fiber loop
   with nonlinearity that maps text-derived modulation to high-
   dimensional photon-statistics features, with a learned classical
   readout that targets the same overlap geometry. Then qrouter is
   not just *quantum-inspired* — it has actual photons in the loop.

## Non-goals (for now)

- Beating BERT / E5 / bge-m3 on MTEB.
- Production performance.
- Anything involving training a quantum-classical hybrid until we have
  a baseline geometry.
