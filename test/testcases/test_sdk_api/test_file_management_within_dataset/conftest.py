

import pytest
from common import bulk_upload_documents
from pytest import FixtureRequest
from ragflow_sdk import DataSet, Document


@pytest.fixture(scope="function")
def add_document_func(request: FixtureRequest, add_dataset: DataSet, ragflow_tmp_dir) -> tuple[DataSet, Document]:
    dataset = add_dataset
    documents = bulk_upload_documents(dataset, 1, ragflow_tmp_dir)

    def cleanup():
        dataset.delete_documents(ids=None)

    request.addfinalizer(cleanup)
    return dataset, documents[0]


@pytest.fixture(scope="class")
def add_documents(request: FixtureRequest, add_dataset: DataSet, ragflow_tmp_dir) -> tuple[DataSet, list[Document]]:
    dataset = add_dataset
    documents = bulk_upload_documents(dataset, 5, ragflow_tmp_dir)

    def cleanup():
        dataset.delete_documents(ids=None)

    request.addfinalizer(cleanup)
    return dataset, documents


@pytest.fixture(scope="function")
def add_documents_func(request: FixtureRequest, add_dataset_func: DataSet, ragflow_tmp_dir) -> tuple[DataSet, list[Document]]:
    dataset = add_dataset_func
    documents = bulk_upload_documents(dataset, 3, ragflow_tmp_dir)

    def cleanup():
        dataset.delete_documents(ids=None)

    request.addfinalizer(cleanup)
    return dataset, documents
