import pytest
from common import batch_add_sessions_with_chat_assistant
from pytest import FixtureRequest
from ragflow_sdk import Chat, DataSet, Document, Session


@pytest.fixture(scope="class")
def add_sessions_with_chat_assistant(request: FixtureRequest, add_chat_assistants: tuple[DataSet, Document, list[Chat]]) -> tuple[Chat, list[Session]]:
    def cleanup():
        for chat_assistant in chat_assistants:
            try:
                chat_assistant.delete_sessions(ids=None)
            except Exception:
                pass

    request.addfinalizer(cleanup)

    _, _, chat_assistants = add_chat_assistants
    return chat_assistants[0], batch_add_sessions_with_chat_assistant(chat_assistants[0], 5)


@pytest.fixture(scope="function")
def add_sessions_with_chat_assistant_func(request: FixtureRequest, add_chat_assistants: tuple[DataSet, Document, list[Chat]]) -> tuple[Chat, list[Session]]:
    def cleanup():
        for chat_assistant in chat_assistants:
            try:
                chat_assistant.delete_sessions(ids=None)
            except Exception:
                pass

    request.addfinalizer(cleanup)

    _, _, chat_assistants = add_chat_assistants
    return chat_assistants[0], batch_add_sessions_with_chat_assistant(chat_assistants[0], 5)
