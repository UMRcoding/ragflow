
'''
The example is about CRUD operations (Create, Read, Update, Delete) on a dataset.
'''

from ragflow_sdk import RAGFlow
import sys

HOST_ADDRESS = "http://127.0.0.1"
API_KEY = "ragflow-IzZmY1MGVhYTBhMjExZWZiYTdjMDI0Mm"

try:
    # create a ragflow instance
    ragflow_instance = RAGFlow(api_key=API_KEY, base_url=HOST_ADDRESS)

    # crate a dataset instance
    dataset_instance = ragflow_instance.create_dataset(name="dataset_instance")

    # update the dataset instance
    updated_message = {"name":"updated_dataset"}
    updated_dataset = dataset_instance.update(updated_message)

    # get the dataset (list datasets)
    dataset_list = ragflow_instance.list_datasets(id=dataset_instance.id)
    dataset_instance_2 = dataset_list[0]
    print(dataset_instance)
    print(dataset_instance_2)

    # delete the dataset (delete datasets)
    to_be_deleted_datasets = [dataset_instance.id]
    ragflow_instance.delete_datasets(ids=to_be_deleted_datasets)

    print("test done")
    sys.exit(0)

except Exception as e:
    print(str(e))
    sys.exit(-1)


