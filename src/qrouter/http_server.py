"""Minimal FastAPI wrapper exposing qrouter as a public HTTP endpoint.

Lives behind qrouter.ask-meridian.uk (Cloudflare Tunnel → uvicorn on
127.0.0.1:8004 on meridian-vm).

Endpoints:
    GET  /                 banner + status
    GET  /health           liveness probe
    GET  /rank?q=...       Born-rule retrieval over the bundled fixture
                           (graceful-degrades if lambeq is not installed:
                           returns the unranked fixture with score=0 and
                           a `mode: "stub"` flag, so the deployment plumbing
                           can be verified before the heavy quantum stack
                           is ready).
    GET  /version          package version + backend mode

Deliberately tiny. No auth, no rate limit yet — the corpus is a 5-item
fixture, the entire response is bounded. Add gates when there's a real
corpus or per-user state to protect.
"""

import os

from fastapi            import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from qrouter            import __version__
from qrouter.corpus     import load_fixture
from qrouter.retrieve   import born_overlap   # noqa: F401  (re-export hint)


# Detect whether the heavy quantum stack is importable. We don't import
# it eagerly because (a) it's expensive and (b) it might fail on
# unsupported Python versions — in which case we still want /health and
# /rank to respond, just in stub mode.
def _detect_backend() -> str:
    try:
        import lambeq        # noqa: F401
        import pennylane     # noqa: F401
        return "lambeq"
    except ImportError:
        return "stub"


BACKEND = _detect_backend()


app = FastAPI(
    title       = "qrouter",
    description = "Quantum natural-language retrieval (DisCoCat + variational circuits).",
    version     = __version__,
    docs_url    = "/docs",
    redoc_url   = None,
)

# Open CORS for now — research artifact, no per-user data. Lock down
# when we add an auth path.
app.add_middleware(
    CORSMiddleware,
    allow_origins   = ["*"],
    allow_methods   = ["GET"],
    allow_headers   = ["*"],
    max_age         = 86400,
)


@app.get("/")
def root():
    return {
        "service":  "qrouter",
        "version":  __version__,
        "backend":  BACKEND,
        "endpoints": {
            "health":  "/health",
            "rank":    "/rank?q=<your+query>",
            "version": "/version",
            "docs":    "/docs",
        },
        "repo":     "https://github.com/LuuOW/qrouter",
        "note":     (
            "Quantum NLP retrieval research artifact. "
            "Fixture corpus only — no production data or auth. "
            "When backend == 'stub', lambeq isn't installed yet and "
            "/rank returns the fixture unranked with score=0."
        ),
    }


@app.get("/health")
def health():
    return {"ok": True, "backend": BACKEND, "fixture_size": len(load_fixture())}


@app.get("/version")
def version():
    return {"version": __version__, "backend": BACKEND}


@app.get("/rank")
def rank(
    q:     str = Query(..., min_length=1, max_length=500, description="The query string to rank against the fixture"),
    top_k: int = Query(5,   ge=1, le=20,                  description="How many ranked results to return"),
):
    if BACKEND != "lambeq":
        # Stub mode — return the fixture documents in their natural order
        # so deployment + tunnel plumbing can be verified before the
        # quantum stack is ready.
        docs = load_fixture()
        return {
            "query":   q,
            "backend": "stub",
            "note":    "lambeq not installed on this server yet — returning fixture unranked. Real Born-rule overlap activates once the quantum stack is in place.",
            "results": [
                {"rank": i + 1, "score": 0.0, "text": d.text, "meta": d.meta}
                for i, d in enumerate(docs[:top_k])
            ],
        }

    # Real backend.
    from qrouter.encode   import encode_corpus
    from qrouter.retrieve import rank_against
    try:
        corpus = encode_corpus(load_fixture())
        scored = rank_against(corpus, q, top_k=top_k)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"qnlp pipeline failed: {e!r}")
    return {
        "query":   q,
        "backend": "lambeq",
        "results": [
            {"rank": i + 1, "score": s.score, "text": s.doc.doc.text, "meta": s.doc.doc.meta}
            for i, s in enumerate(scored)
        ],
    }


def main_run():
    """Entrypoint for `qrouter-serve`. Reads QROUTER_HOST + QROUTER_PORT
    from the environment so systemd can configure them without code changes."""
    import uvicorn
    uvicorn.run(
        "qrouter.http_server:app",
        host = os.environ.get("QROUTER_HOST", "127.0.0.1"),
        port = int(os.environ.get("QROUTER_PORT", "8004")),
        log_level = "info",
    )


# Allow running directly: `python -m qrouter.http_server`
if __name__ == "__main__":
    main_run()
