import pytest
from common import batch_create_datasets
from libs.auth import RAGFlowWebApiAuth
from pytest import FixtureRequest
from ragflow_sdk import RAGFlow


@pytest.fixture(scope="class")
def add_datasets(request: FixtureRequest, client: RAGFlow, WebApiAuth: RAGFlowWebApiAuth) -> list[str]:
    def cleanup():
        client.delete_datasets(ids=None)

    request.addfinalizer(cleanup)
    return batch_create_datasets(WebApiAuth, 5)


@pytest.fixture(scope="function")
def add_datasets_func(request: FixtureRequest, client: RAGFlow, WebApiAuth: RAGFlowWebApiAuth) -> list[str]:
    def cleanup():
        client.delete_datasets(ids=None)

    request.addfinalizer(cleanup)
    return batch_create_datasets(WebApiAuth, 3)
