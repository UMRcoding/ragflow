

import pytest
from common import add_chunk, delete_chunks, list_documnets, parse_documnets
from libs.utils import wait_for


@wait_for(30, 1, "Document parsing timeout")
def condition(_auth, _dataset_id):
    res = list_documnets(_auth, _dataset_id)
    for doc in res["data"]["docs"]:
        if doc["run"] != "DONE":
            return False
    return True


@pytest.fixture(scope="function")
def add_chunks_func(request, get_http_api_auth, add_document):
    dataset_id, document_id = add_document
    parse_documnets(get_http_api_auth, dataset_id, {"document_ids": [document_id]})
    condition(get_http_api_auth, dataset_id)

    chunk_ids = []
    for i in range(4):
        res = add_chunk(get_http_api_auth, dataset_id, document_id, {"content": f"chunk test {i}"})
        chunk_ids.append(res["data"]["chunk"]["id"])

    # issues/6487
    from time import sleep

    sleep(1)

    def cleanup():
        delete_chunks(get_http_api_auth, dataset_id, document_id, {"chunk_ids": chunk_ids})

    request.addfinalizer(cleanup)
    return dataset_id, document_id, chunk_ids
