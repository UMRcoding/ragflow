

from time import sleep

import pytest
from common import batch_add_chunks
from pytest import FixtureRequest
from ragflow_sdk import Chunk, DataSet, Document
from utils import wait_for


@wait_for(30, 1, "Document parsing timeout")
def condition(_dataset: DataSet):
    documents = _dataset.list_documents(page_size=1000)
    for document in documents:
        if document.run != "DONE":
            return False
    return True


@pytest.fixture(scope="function")
def add_chunks_func(request: FixtureRequest, add_document: tuple[DataSet, Document]) -> tuple[DataSet, Document, list[Chunk]]:
    def cleanup():
        try:
            document.delete_chunks(ids=[])
        except Exception:
            pass

    request.addfinalizer(cleanup)

    dataset, document = add_document
    dataset.async_parse_documents([document.id])
    condition(dataset)
    chunks = batch_add_chunks(document, 4)
    # issues/6487
    sleep(1)
    return dataset, document, chunks
