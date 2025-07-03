import pytest
from common import batch_create_chat_assistants
from pytest import FixtureRequest
from ragflow_sdk import Chat, DataSet, Document, RAGFlow
from utils import wait_for


@wait_for(30, 1, "Document parsing timeout")
def condition(_dataset: DataSet):
    documents = _dataset.list_documents(page_size=1000)
    for document in documents:
        if document.run != "DONE":
            return False
    return True


@pytest.fixture(scope="function")
def add_chat_assistants_func(request: FixtureRequest, client: RAGFlow, add_document: tuple[DataSet, Document]) -> tuple[DataSet, Document, list[Chat]]:
    def cleanup():
        client.delete_chats(ids=None)

    request.addfinalizer(cleanup)

    dataset, document = add_document
    dataset.async_parse_documents([document.id])
    condition(dataset)
    return dataset, document, batch_create_chat_assistants(client, 5)
