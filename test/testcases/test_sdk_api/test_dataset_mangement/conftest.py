

import pytest
from common import batch_create_datasets


@pytest.fixture(scope="class")
def add_datasets(client, request):
    def cleanup():
        client.delete_datasets(**{"ids": None})

    request.addfinalizer(cleanup)

    return batch_create_datasets(client, 5)


@pytest.fixture(scope="function")
def add_datasets_func(client, request):
    def cleanup():
        client.delete_datasets(**{"ids": None})

    request.addfinalizer(cleanup)

    return batch_create_datasets(client, 3)
