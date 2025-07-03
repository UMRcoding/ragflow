
import pytest
from common import (
    list_kbs,
    rm_kb,
)
from configs import INVALID_API_TOKEN
from libs.auth import RAGFlowWebApiAuth


class TestAuthorization:
    @pytest.mark.p1
    @pytest.mark.parametrize(
        "invalid_auth, expected_code, expected_message",
        [
            (None, 401, "<Unauthorized '401: Unauthorized'>"),
            (RAGFlowWebApiAuth(INVALID_API_TOKEN), 401, "<Unauthorized '401: Unauthorized'>"),
        ],
    )
    def test_auth_invalid(self, invalid_auth, expected_code, expected_message):
        res = rm_kb(invalid_auth)
        assert res["code"] == expected_code, res
        assert res["message"] == expected_message, res


class TestDatasetsDelete:
    @pytest.mark.p1
    def test_kb_id(self, WebApiAuth, add_datasets_func):
        kb_ids = add_datasets_func
        payload = {"kb_id": kb_ids[0]}
        res = rm_kb(WebApiAuth, payload)
        assert res["code"] == 0, res

        res = list_kbs(WebApiAuth)
        assert len(res["data"]["kbs"]) == 2, res

    @pytest.mark.p2
    @pytest.mark.usefixtures("add_dataset_func")
    def test_id_wrong_uuid(self, WebApiAuth):
        payload = {"kb_id": "d94a8dc02c9711f0930f7fbc369eab6d"}
        res = rm_kb(WebApiAuth, payload)
        assert res["code"] == 109, res
        assert "No authorization." in res["message"], res

        res = list_kbs(WebApiAuth)
        assert len(res["data"]["kbs"]) == 1, res
