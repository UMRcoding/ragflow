
import pytest


def validate_document_parse_done(dataset, document_ids):
    documents = dataset.list_documents(page_size=1000)
    for document in documents:
        if document.id in document_ids:
            assert document.run == "DONE"
            assert len(document.process_begin_at) > 0
            assert document.process_duation > 0
            assert document.progress > 0
            assert "Task done" in document.progress_msg


def validate_document_parse_cancel(dataset, document_ids):
    documents = dataset.list_documents(page_size=1000)
    for document in documents:
        assert document.run == "CANCEL"
        assert len(document.process_begin_at) > 0
        assert document.progress == 0.0


@pytest.mark.skip
class TestDocumentsParseStop:
    pass
