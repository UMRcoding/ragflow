

import pytest
from common import batch_create_datasets, delete_datasets


@pytest.fixture(scope="class")
def add_datasets(get_http_api_auth, request):
    def cleanup():
        delete_datasets(get_http_api_auth, {"ids": None})

    request.addfinalizer(cleanup)

    return batch_create_datasets(get_http_api_auth, 5)


@pytest.fixture(scope="function")
def add_datasets_func(get_http_api_auth, request):
    def cleanup():
        delete_datasets(get_http_api_auth, {"ids": None})

    request.addfinalizer(cleanup)

    return batch_create_datasets(get_http_api_auth, 3)
