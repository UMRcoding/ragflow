import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from random import randint

import pytest
from common import delete_documents, update_chunk
from configs import INVALID_API_TOKEN
from libs.auth import RAGFlowHttpApiAuth


@pytest.mark.p1
class TestAuthorization:
    @pytest.mark.parametrize(
        "invalid_auth, expected_code, expected_message",
        [
            (None, 0, "`Authorization` can't be empty"),
            (
                RAGFlowHttpApiAuth(INVALID_API_TOKEN),
                109,
                "Authentication error: API key is invalid!",
            ),
        ],
    )
    def test_invalid_auth(self, invalid_auth, expected_code, expected_message):
        res = update_chunk(invalid_auth, "dataset_id", "document_id", "chunk_id")
        assert res["code"] == expected_code
        assert res["message"] == expected_message


class TestUpdatedChunk:
    @pytest.mark.p1
    @pytest.mark.parametrize(
        "payload, expected_code, expected_message",
        [
            ({"content": None}, 100, "TypeError('expected string or bytes-like object')"),
            pytest.param(
                {"content": ""},
                100,
                """APIRequestFailedError(\'Error code: 400, with error text {"error":{"code":"1213","message":"未正常接收到prompt参数。"}}\')""",
                marks=pytest.mark.skip(reason="issues/6541"),
            ),
            pytest.param(
                {"content": 1},
                100,
                "TypeError('expected string or bytes-like object')",
                marks=pytest.mark.skip,
            ),
            ({"content": "update chunk"}, 0, ""),
            pytest.param(
                {"content": " "},
                100,
                """APIRequestFailedError(\'Error code: 400, with error text {"error":{"code":"1213","message":"未正常接收到prompt参数。"}}\')""",
                marks=pytest.mark.skip(reason="issues/6541"),
            ),
            ({"content": "\n!?。；！？\"'"}, 0, ""),
        ],
    )
    def test_content(self, HttpApiAuth, add_chunks, payload, expected_code, expected_message):
        dataset_id, document_id, chunk_ids = add_chunks
        res = update_chunk(HttpApiAuth, dataset_id, document_id, chunk_ids[0], payload)
        assert res["code"] == expected_code
        if expected_code != 0:
            assert res["message"] == expected_message

    @pytest.mark.p2
    @pytest.mark.parametrize(
        "payload, expected_code, expected_message",
        [
            ({"important_keywords": ["a", "b", "c"]}, 0, ""),
            ({"important_keywords": [""]}, 0, ""),
            ({"important_keywords": [1]}, 100, "TypeError('sequence item 0: expected str instance, int found')"),
            ({"important_keywords": ["a", "a"]}, 0, ""),
            ({"important_keywords": "abc"}, 102, "`important_keywords` should be a list"),
            ({"important_keywords": 123}, 102, "`important_keywords` should be a list"),
        ],
    )
    def test_important_keywords(self, HttpApiAuth, add_chunks, payload, expected_code, expected_message):
        dataset_id, document_id, chunk_ids = add_chunks
        res = update_chunk(HttpApiAuth, dataset_id, document_id, chunk_ids[0], payload)
        assert res["code"] == expected_code
        if expected_code != 0:
            assert res["message"] == expected_message

    @pytest.mark.p2
    @pytest.mark.parametrize(
        "payload, expected_code, expected_message",
        [
            ({"questions": ["a", "b", "c"]}, 0, ""),
            ({"questions": [""]}, 0, ""),
            ({"questions": [1]}, 100, "TypeError('sequence item 0: expected str instance, int found')"),
            ({"questions": ["a", "a"]}, 0, ""),
            ({"questions": "abc"}, 102, "`questions` should be a list"),
            ({"questions": 123}, 102, "`questions` should be a list"),
        ],
    )
    def test_questions(self, HttpApiAuth, add_chunks, payload, expected_code, expected_message):
        dataset_id, document_id, chunk_ids = add_chunks
        res = update_chunk(HttpApiAuth, dataset_id, document_id, chunk_ids[0], payload)
        assert res["code"] == expected_code
        if expected_code != 0:
            assert res["message"] == expected_message

    @pytest.mark.p2
    @pytest.mark.parametrize(
        "payload, expected_code, expected_message",
        [
            ({"available": True}, 0, ""),
            pytest.param({"available": "True"}, 100, """ValueError("invalid literal for int() with base 10: \'True\'")""", marks=pytest.mark.skip),
            ({"available": 1}, 0, ""),
            ({"available": False}, 0, ""),
            pytest.param({"available": "False"}, 100, """ValueError("invalid literal for int() with base 10: \'False\'")""", marks=pytest.mark.skip),
            ({"available": 0}, 0, ""),
        ],
    )
    def test_available(
        self,
        HttpApiAuth,
        add_chunks,
        payload,
        expected_code,
        expected_message,
    ):
        dataset_id, document_id, chunk_ids = add_chunks
        res = update_chunk(HttpApiAuth, dataset_id, document_id, chunk_ids[0], payload)
        assert res["code"] == expected_code
        if expected_code != 0:
            assert res["message"] == expected_message

    @pytest.mark.p3
    @pytest.mark.parametrize(
        "dataset_id, expected_code, expected_message",
        [
            ("", 100, "<NotFound '404: Not Found'>"),
            pytest.param("invalid_dataset_id", 102, "You don't own the dataset invalid_dataset_id.", marks=pytest.mark.skipif(os.getenv("DOC_ENGINE") == "infinity", reason="infinity")),
            pytest.param("invalid_dataset_id", 102, "Can't find this chunk", marks=pytest.mark.skipif(os.getenv("DOC_ENGINE") in [None, "opensearch", "elasticsearch"], reason="elasticsearch")),
        ],
    )
    def test_invalid_dataset_id(self, HttpApiAuth, add_chunks, dataset_id, expected_code, expected_message):
        _, document_id, chunk_ids = add_chunks
        res = update_chunk(HttpApiAuth, dataset_id, document_id, chunk_ids[0])
        assert res["code"] == expected_code
        assert expected_message in res["message"]

    @pytest.mark.p3
    @pytest.mark.parametrize(
        "document_id, expected_code, expected_message",
        [
            ("", 100, "<NotFound '404: Not Found'>"),
            (
                "invalid_document_id",
                102,
                "You don't own the document invalid_document_id.",
            ),
        ],
    )
    def test_invalid_document_id(self, HttpApiAuth, add_chunks, document_id, expected_code, expected_message):
        dataset_id, _, chunk_ids = add_chunks
        res = update_chunk(HttpApiAuth, dataset_id, document_id, chunk_ids[0])
        assert res["code"] == expected_code
        assert res["message"] == expected_message

    @pytest.mark.p3
    @pytest.mark.parametrize(
        "chunk_id, expected_code, expected_message",
        [
            ("", 100, "<MethodNotAllowed '405: Method Not Allowed'>"),
            (
                "invalid_document_id",
                102,
                "Can't find this chunk invalid_document_id",
            ),
        ],
    )
    def test_invalid_chunk_id(self, HttpApiAuth, add_chunks, chunk_id, expected_code, expected_message):
        dataset_id, document_id, _ = add_chunks
        res = update_chunk(HttpApiAuth, dataset_id, document_id, chunk_id)
        assert res["code"] == expected_code
        assert res["message"] == expected_message

    @pytest.mark.p3
    def test_repeated_update_chunk(self, HttpApiAuth, add_chunks):
        dataset_id, document_id, chunk_ids = add_chunks
        res = update_chunk(HttpApiAuth, dataset_id, document_id, chunk_ids[0], {"content": "chunk test 1"})
        assert res["code"] == 0

        res = update_chunk(HttpApiAuth, dataset_id, document_id, chunk_ids[0], {"content": "chunk test 2"})
        assert res["code"] == 0

    @pytest.mark.p3
    @pytest.mark.parametrize(
        "payload, expected_code, expected_message",
        [
            ({"unknown_key": "unknown_value"}, 0, ""),
            ({}, 0, ""),
            pytest.param(None, 100, """TypeError("argument of type \'NoneType\' is not iterable")""", marks=pytest.mark.skip),
        ],
    )
    def test_invalid_params(self, HttpApiAuth, add_chunks, payload, expected_code, expected_message):
        dataset_id, document_id, chunk_ids = add_chunks
        res = update_chunk(HttpApiAuth, dataset_id, document_id, chunk_ids[0], payload)
        assert res["code"] == expected_code
        if expected_code != 0:
            assert res["message"] == expected_message

    @pytest.mark.p3
    @pytest.mark.skipif(os.getenv("DOC_ENGINE") == "infinity", reason="issues/6554")
    def test_concurrent_update_chunk(self, HttpApiAuth, add_chunks):
        count = 50
        dataset_id, document_id, chunk_ids = add_chunks

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(
                    update_chunk,
                    HttpApiAuth,
                    dataset_id,
                    document_id,
                    chunk_ids[randint(0, 3)],
                    {"content": f"update chunk test {i}"},
                )
                for i in range(count)
            ]
        responses = list(as_completed(futures))
        assert len(responses) == count, responses
        assert all(future.result()["code"] == 0 for future in futures)

    @pytest.mark.p3
    def test_update_chunk_to_deleted_document(self, HttpApiAuth, add_chunks):
        dataset_id, document_id, chunk_ids = add_chunks
        delete_documents(HttpApiAuth, dataset_id, {"ids": [document_id]})
        res = update_chunk(HttpApiAuth, dataset_id, document_id, chunk_ids[0])
        assert res["code"] == 102
        assert res["message"] == f"Can't find this chunk {chunk_ids[0]}"
