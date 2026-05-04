"""qrouter — quantum natural-language retrieval (DisCoCat + variational circuits).

Public surface (deliberately small while the design is unstable):

    from qrouter import encode_corpus, rank_against
    docs   = encode_corpus(["the cat sleeps", "the dog runs"])
    scored = rank_against(docs, query="a cat is napping")

Everything else is internal until we know what should stay.
"""

from qrouter.encode   import encode_corpus, encode_one
from qrouter.retrieve import rank_against, born_overlap

__all__ = ["encode_corpus", "encode_one", "rank_against", "born_overlap"]
__version__ = "0.0.1"
