
import string
from concurrent.futures import ThreadPoolExecutor

import pytest
import requests
from common import DOCUMENT_NAME_LIMIT, FILE_API_URL, HOST_ADDRESS, INVALID_API_TOKEN, list_datasets, upload_documnets
from libs.auth import RAGFlowHttpApiAuth
from libs.utils.file_utils import create_txt_file
from requests_toolbelt import MultipartEncoder


@pytest.mark.p1
@pytest.mark.usefixtures("clear_datasets")
class TestAuthorization:
    @pytest.mark.parametrize(
        "auth, expected_code, expected_message",
        [
            (None, 0, "`Authorization` can't be empty"),
            (
                RAGFlowHttpApiAuth(INVALID_API_TOKEN),
                109,
                "Authentication error: API key is invalid!",
            ),
        ],
    )
    def test_invalid_auth(self, auth, expected_code, expected_message):
        res = upload_documnets(auth, "dataset_id")
        assert res["code"] == expected_code
        assert res["message"] == expected_message


class TestDocumentsUpload:
    @pytest.mark.p1
    def test_valid_single_upload(self, get_http_api_auth, add_dataset_func, tmp_path):
        dataset_id = add_dataset_func
        fp = create_txt_file(tmp_path / "ragflow_test.txt")
        res = upload_documnets(get_http_api_auth, dataset_id, [fp])
        assert res["code"] == 0
        assert res["data"][0]["dataset_id"] == dataset_id
        assert res["data"][0]["name"] == fp.name

    @pytest.mark.p1
    @pytest.mark.parametrize(
        "generate_test_files",
        [
            "docx",
            "excel",
            "ppt",
            "image",
            "pdf",
            "txt",
            "md",
            "json",
            "eml",
            "html",
        ],
        indirect=True,
    )
    def test_file_type_validation(self, get_http_api_auth, add_dataset_func, generate_test_files, request):
        dataset_id = add_dataset_func
        fp = generate_test_files[request.node.callspec.params["generate_test_files"]]
        res = upload_documnets(get_http_api_auth, dataset_id, [fp])
        assert res["code"] == 0
        assert res["data"][0]["dataset_id"] == dataset_id
        assert res["data"][0]["name"] == fp.name

    @pytest.mark.p2
    @pytest.mark.parametrize(
        "file_type",
        ["exe", "unknown"],
    )
    def test_unsupported_file_type(self, get_http_api_auth, add_dataset_func, tmp_path, file_type):
        dataset_id = add_dataset_func
        fp = tmp_path / f"ragflow_test.{file_type}"
        fp.touch()
        res = upload_documnets(get_http_api_auth, dataset_id, [fp])
        assert res["code"] == 500
        assert res["message"] == f"ragflow_test.{file_type}: This type of file has not been supported yet!"

    @pytest.mark.p2
    def test_missing_file(self, get_http_api_auth, add_dataset_func):
        dataset_id = add_dataset_func
        res = upload_documnets(get_http_api_auth, dataset_id)
        assert res["code"] == 101
        assert res["message"] == "No file part!"

    @pytest.mark.p3
    def test_empty_file(self, get_http_api_auth, add_dataset_func, tmp_path):
        dataset_id = add_dataset_func
        fp = tmp_path / "empty.txt"
        fp.touch()

        res = upload_documnets(get_http_api_auth, dataset_id, [fp])
        assert res["code"] == 0
        assert res["data"][0]["size"] == 0

    @pytest.mark.p3
    def test_filename_empty(self, get_http_api_auth, add_dataset_func, tmp_path):
        dataset_id = add_dataset_func
        fp = create_txt_file(tmp_path / "ragflow_test.txt")
        url = f"{HOST_ADDRESS}{FILE_API_URL}".format(dataset_id=dataset_id)
        fields = (("file", ("", fp.open("rb"))),)
        m = MultipartEncoder(fields=fields)
        res = requests.post(
            url=url,
            headers={"Content-Type": m.content_type},
            auth=get_http_api_auth,
            data=m,
        )
        assert res.json()["code"] == 101
        assert res.json()["message"] == "No file selected!"

    @pytest.mark.p2
    def test_filename_exceeds_max_length(self, get_http_api_auth, add_dataset_func, tmp_path):
        dataset_id = add_dataset_func
        # filename_length = 129
        fp = create_txt_file(tmp_path / f"{'a' * (DOCUMENT_NAME_LIMIT - 3)}.txt")
        res = upload_documnets(get_http_api_auth, dataset_id, [fp])
        assert res["code"] == 101
        assert res["message"] == "File name should be less than 128 bytes."

    @pytest.mark.p2
    def test_invalid_dataset_id(self, get_http_api_auth, tmp_path):
        fp = create_txt_file(tmp_path / "ragflow_test.txt")
        res = upload_documnets(get_http_api_auth, "invalid_dataset_id", [fp])
        assert res["code"] == 100
        assert res["message"] == """LookupError("Can\'t find the dataset with ID invalid_dataset_id!")"""

    @pytest.mark.p2
    def test_duplicate_files(self, get_http_api_auth, add_dataset_func, tmp_path):
        dataset_id = add_dataset_func
        fp = create_txt_file(tmp_path / "ragflow_test.txt")
        res = upload_documnets(get_http_api_auth, dataset_id, [fp, fp])
        assert res["code"] == 0
        assert len(res["data"]) == 2
        for i in range(len(res["data"])):
            assert res["data"][i]["dataset_id"] == dataset_id
            expected_name = fp.name
            if i != 0:
                expected_name = f"{fp.stem}({i}){fp.suffix}"
            assert res["data"][i]["name"] == expected_name

    @pytest.mark.p2
    def test_same_file_repeat(self, get_http_api_auth, add_dataset_func, tmp_path):
        dataset_id = add_dataset_func
        fp = create_txt_file(tmp_path / "ragflow_test.txt")
        for i in range(10):
            res = upload_documnets(get_http_api_auth, dataset_id, [fp])
            assert res["code"] == 0
            assert len(res["data"]) == 1
            assert res["data"][0]["dataset_id"] == dataset_id
            expected_name = fp.name
            if i != 0:
                expected_name = f"{fp.stem}({i}){fp.suffix}"
            assert res["data"][0]["name"] == expected_name

    @pytest.mark.p3
    def test_filename_special_characters(self, get_http_api_auth, add_dataset_func, tmp_path):
        dataset_id = add_dataset_func
        illegal_chars = '<>:"/\\|?*'
        translation_table = str.maketrans({char: "_" for char in illegal_chars})
        safe_filename = string.punctuation.translate(translation_table)
        fp = tmp_path / f"{safe_filename}.txt"
        fp.write_text("Sample text content")

        res = upload_documnets(get_http_api_auth, dataset_id, [fp])
        assert res["code"] == 0
        assert len(res["data"]) == 1
        assert res["data"][0]["dataset_id"] == dataset_id
        assert res["data"][0]["name"] == fp.name

    @pytest.mark.p1
    def test_multiple_files(self, get_http_api_auth, add_dataset_func, tmp_path):
        dataset_id = add_dataset_func
        expected_document_count = 20
        fps = []
        for i in range(expected_document_count):
            fp = create_txt_file(tmp_path / f"ragflow_test_{i}.txt")
            fps.append(fp)
        res = upload_documnets(get_http_api_auth, dataset_id, fps)
        assert res["code"] == 0

        res = list_datasets(get_http_api_auth, {"id": dataset_id})
        assert res["data"][0]["document_count"] == expected_document_count

    @pytest.mark.p3
    def test_concurrent_upload(self, get_http_api_auth, add_dataset_func, tmp_path):
        dataset_id = add_dataset_func

        expected_document_count = 20
        fps = []
        for i in range(expected_document_count):
            fp = create_txt_file(tmp_path / f"ragflow_test_{i}.txt")
            fps.append(fp)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(upload_documnets, get_http_api_auth, dataset_id, fps[i : i + 1]) for i in range(expected_document_count)]
        responses = [f.result() for f in futures]
        assert all(r["code"] == 0 for r in responses)

        res = list_datasets(get_http_api_auth, {"id": dataset_id})
        assert res["data"][0]["document_count"] == expected_document_count
