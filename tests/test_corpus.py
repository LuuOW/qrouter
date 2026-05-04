"""Tests that don't require the lambeq/pennylane install — kept here so
CI can run a fast smoke check without the heavy quantum stack."""

from qrouter.corpus import Document, load_fixture


def test_fixture_loads_documents():
    docs = load_fixture()
    assert len(docs) >= 5
    assert all(isinstance(d, Document) for d in docs)
    assert all(d.text and isinstance(d.text, str) for d in docs)


def test_fixture_metadata_has_id_and_topic():
    for d in load_fixture():
        assert "id" in d.meta
        assert "topic" in d.meta


def test_documents_are_frozen():
    d = Document(text="x", meta={})
    try:
        d.text = "y"
    except (AttributeError, TypeError):
        return
    raise AssertionError("Document should be frozen")
