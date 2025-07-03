

import pytest
from common import bulk_upload_documents, delete_documnets


@pytest.fixture(scope="function")
def add_document_func(request, get_http_api_auth, add_dataset, ragflow_tmp_dir):
    dataset_id = add_dataset
    document_ids = bulk_upload_documents(get_http_api_auth, dataset_id, 1, ragflow_tmp_dir)

    def cleanup():
        delete_documnets(get_http_api_auth, dataset_id, {"ids": document_ids})

    request.addfinalizer(cleanup)
    return dataset_id, document_ids[0]


@pytest.fixture(scope="class")
def add_documents(request, get_http_api_auth, add_dataset, ragflow_tmp_dir):
    dataset_id = add_dataset
    document_ids = bulk_upload_documents(get_http_api_auth, dataset_id, 5, ragflow_tmp_dir)

    def cleanup():
        delete_documnets(get_http_api_auth, dataset_id, {"ids": document_ids})

    request.addfinalizer(cleanup)
    return dataset_id, document_ids


@pytest.fixture(scope="function")
def add_documents_func(get_http_api_auth, add_dataset_func, ragflow_tmp_dir):
    dataset_id = add_dataset_func
    document_ids = bulk_upload_documents(get_http_api_auth, dataset_id, 3, ragflow_tmp_dir)

    return dataset_id, document_ids
