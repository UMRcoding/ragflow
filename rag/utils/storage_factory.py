
import os
from enum import Enum

from rag.utils.azure_sas_conn import RAGFlowAzureSasBlob
from rag.utils.azure_spn_conn import RAGFlowAzureSpnBlob
from rag.utils.minio_conn import RAGFlowMinio
from rag.utils.opendal_conn import OpenDALStorage
from rag.utils.s3_conn import RAGFlowS3
from rag.utils.oss_conn import RAGFlowOSS


class Storage(Enum):
    MINIO = 1
    AZURE_SPN = 2
    AZURE_SAS = 3
    AWS_S3 = 4
    OSS = 5
    OPENDAL = 6


class StorageFactory:
    storage_mapping = {
        Storage.MINIO: RAGFlowMinio,
        Storage.AZURE_SPN: RAGFlowAzureSpnBlob,
        Storage.AZURE_SAS: RAGFlowAzureSasBlob,
        Storage.AWS_S3: RAGFlowS3,
        Storage.OSS: RAGFlowOSS,
        Storage.OPENDAL: OpenDALStorage
    }

    @classmethod
    def create(cls, storage: Storage):
        return cls.storage_mapping[storage]()


STORAGE_IMPL_TYPE = os.getenv('STORAGE_IMPL', 'MINIO')
STORAGE_IMPL = StorageFactory.create(Storage[STORAGE_IMPL_TYPE])
