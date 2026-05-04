---
title:        qrouter
emoji:        🔬
colorFrom:    indigo
colorTo:      purple
sdk:          docker
app_port:     7860
pinned:       false
license:      mit
short_description: "QNLP retrieval — DisCoCat + Born-rule overlap"
---

# qrouter

> 📘 **New:** [Build Your Own MCP Server With Auth + Billing — the 60-page guide ($29)](https://kempefire.gumroad.com/l/build-your-own-mcp)
> Production stack used to ship this Space + ask-meridian.uk.

Quantum natural-language retrieval for scientific knowledge.

A research artifact: route queries to relevant text by encoding both as
quantum states (DisCoCat tensor diagrams compiled to variational circuits)
and ranking via Born-rule overlap. Classically simulable now; designed to
also run on Quantinuum H-series and (with embedding) Xanadu photonic
processors.

**Live demo:** [`https://qrouter.ask-meridian.uk`](https://qrouter.ask-meridian.uk)

```
$ curl 'https://qrouter.ask-meridian.uk/rank?q=photons+going+through+barriers&top_k=3'
```

See [`docs/deploy.md`](./docs/deploy.md) for the hosting architecture
(systemd + Cloudflare Tunnel on a shared VM) and how to flip the server
between `stub` and `lambeq` backends.

## Status

Working name. Day-1 scaffold. Not a product. Not stable. Not even
opinionated yet.

## What this is and is not

**Is:** an experiment in whether compositional quantum-semantic structure
(à la Coecke et al.) gives meaningfully different retrieval behavior than
classical dense embeddings — particularly on small corpora where
the geometric structure matters more than scale.

**Is not:** a faster retriever, a better embedder, or anything you should
use in production. Quantum circuit simulation is slower than `cosine(a, b)`
on classical hardware. The point is *whether the structure matters*, not
whether it's fast.

## Stack

- Python 3.12+
- [lambeq](https://cqcl.github.io/lambeq/) — DisCoCat parsing + circuit compilation
- [PennyLane](https://pennylane.ai/) — variational quantum circuits + autodiff
- JAX — gradients (lambeq supports this backend)
- pytest, ruff
- uv for env management

## First-week plan

1. Day 1-2: read Coecke "Mathematical Foundations of QNLP" (2020) +
   Lorenz et al. "QNLP in Practice" (2023). Run lambeq's MNIST tutorial.
2. Day 3-4: 50 arXiv quant-ph abstracts → DisCoCat parses → simulated
   circuits → pairwise Born-rule overlap → toy retrieval demo.
3. Day 5-6: wire to MCP stdio so `qrouter` is callable from Claude /
   Cursor / Windsurf as a tool.
4. Day 7: decide — go deeper into pure QNLP, or branch toward photonic
   reservoir front-end.

## References

- Coecke, B., de Felice, G., Meichanetzidis, K., Toumi, A. (2020).
  *Foundations for Near-Term Quantum Natural Language Processing*.
- Lorenz, R., Pearson, A., Meichanetzidis, K., Kartsaklis, D., Coecke, B.
  (2023). *QNLP in Practice: Running Compositional Models of Meaning on
  a Quantum Computer*. JAIR 76.
- Quantinuum lambeq: https://github.com/CQCL/lambeq

## License

MIT (see LICENSE).
