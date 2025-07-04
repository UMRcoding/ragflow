
from common import HOST_ADDRESS
from ragflow_sdk import RAGFlow
from ragflow_sdk.modules.chat import Chat


def test_create_chat_with_name(get_api_key_fixture):
    API_KEY = get_api_key_fixture
    rag = RAGFlow(API_KEY, HOST_ADDRESS)
    kb = rag.create_dataset(name="test_create_chat")
    display_name = "ragflow.txt"
    with open("test_data/ragflow.txt", "rb") as file:
        blob = file.read()
    document = {"display_name": display_name, "blob": blob}
    documents = []
    documents.append(document)
    docs = kb.upload_documents(documents)
    for doc in docs:
        doc.add_chunk("This is a test to add chunk")
    llm = Chat.LLM(
        rag,
        {
            "model_name": "glm-4-flash@ZHIPU-AI",
            "temperature": 0.1,
            "top_p": 0.3,
            "presence_penalty": 0.4,
            "frequency_penalty": 0.7,
            "max_tokens": 512,
        },
    )
    rag.create_chat("test_create_chat", dataset_ids=[kb.id], llm=llm)


def test_update_chat_with_name(get_api_key_fixture):
    API_KEY = get_api_key_fixture
    rag = RAGFlow(API_KEY, HOST_ADDRESS)
    kb = rag.create_dataset(name="test_update_chat")
    display_name = "ragflow.txt"
    with open("test_data/ragflow.txt", "rb") as file:
        blob = file.read()
    document = {"display_name": display_name, "blob": blob}
    documents = []
    documents.append(document)
    docs = kb.upload_documents(documents)
    for doc in docs:
        doc.add_chunk("This is a test to add chunk")
    llm = Chat.LLM(
        rag,
        {
            "model_name": "glm-4-flash@ZHIPU-AI",
            "temperature": 0.1,
            "top_p": 0.3,
            "presence_penalty": 0.4,
            "frequency_penalty": 0.7,
            "max_tokens": 512,
        },
    )
    chat = rag.create_chat("test_update_chat", dataset_ids=[kb.id], llm=llm)
    chat.update({"name": "new_chat"})


def test_delete_chats_with_success(get_api_key_fixture):
    API_KEY = get_api_key_fixture
    rag = RAGFlow(API_KEY, HOST_ADDRESS)
    kb = rag.create_dataset(name="test_delete_chat")
    display_name = "ragflow.txt"
    with open("test_data/ragflow.txt", "rb") as file:
        blob = file.read()
    document = {"display_name": display_name, "blob": blob}
    documents = []
    documents.append(document)
    docs = kb.upload_documents(documents)
    for doc in docs:
        doc.add_chunk("This is a test to add chunk")
    llm = Chat.LLM(
        rag,
        {
            "model_name": "glm-4-flash@ZHIPU-AI",
            "temperature": 0.1,
            "top_p": 0.3,
            "presence_penalty": 0.4,
            "frequency_penalty": 0.7,
            "max_tokens": 512,
        },
    )
    chat = rag.create_chat("test_delete_chat", dataset_ids=[kb.id], llm=llm)
    rag.delete_chats(ids=[chat.id])


def test_list_chats_with_success(get_api_key_fixture):
    API_KEY = get_api_key_fixture
    rag = RAGFlow(API_KEY, HOST_ADDRESS)
    kb = rag.create_dataset(name="test_list_chats")
    display_name = "ragflow.txt"
    with open("test_data/ragflow.txt", "rb") as file:
        blob = file.read()
    document = {"display_name": display_name, "blob": blob}
    documents = []
    documents.append(document)
    docs = kb.upload_documents(documents)
    for doc in docs:
        doc.add_chunk("This is a test to add chunk")
    llm = Chat.LLM(
        rag,
        {
            "model_name": "glm-4-flash@ZHIPU-AI",
            "temperature": 0.1,
            "top_p": 0.3,
            "presence_penalty": 0.4,
            "frequency_penalty": 0.7,
            "max_tokens": 512,
        },
    )
    rag.create_chat("test_list_1", dataset_ids=[kb.id], llm=llm)
    rag.create_chat("test_list_2", dataset_ids=[kb.id], llm=llm)
    rag.list_chats()
