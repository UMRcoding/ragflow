
import json

from .base import Base
from .chunk import Chunk


class Document(Base):
    class ParserConfig(Base):
        def __init__(self, rag, res_dict):
            super().__init__(rag, res_dict)

    def __init__(self, rag, res_dict):
        self.id = ""
        self.name = ""
        self.thumbnail = None
        self.dataset_id = None
        self.chunk_method = "naive"
        self.parser_config = {"pages": [[1, 1000000]]}
        self.source_type = "local"
        self.type = ""
        self.created_by = ""
        self.size = 0
        self.token_count = 0
        self.chunk_count = 0
        self.progress = 0.0
        self.progress_msg = ""
        self.process_begin_at = None
        self.process_duation = 0.0
        self.run = "0"
        self.status = "1"
        for k in list(res_dict.keys()):
            if k not in self.__dict__:
                res_dict.pop(k)
        super().__init__(rag, res_dict)

    def update(self, update_message: dict):
        if "meta_fields" in update_message:
            if not isinstance(update_message["meta_fields"], dict):
                raise Exception("meta_fields must be a dictionary")
        res = self.put(f"/datasets/{self.dataset_id}/documents/{self.id}", update_message)
        res = res.json()
        if res.get("code") != 0:
            raise Exception(res["message"])

        self._update_from_dict(self.rag, res.get("data", {}))
        return self

    def download(self):
        res = self.get(f"/datasets/{self.dataset_id}/documents/{self.id}")
        error_keys = set(["code", "message"])
        try:
            response = res.json()
            actual_keys = set(response.keys())
            if actual_keys == error_keys:
                raise Exception(res.get("message"))
            else:
                return res.content
        except json.JSONDecodeError:
            return res.content

    def list_chunks(self, page=1, page_size=30, keywords="", id=""):
        data = {"keywords": keywords, "page": page, "page_size": page_size, "id": id}
        res = self.get(f"/datasets/{self.dataset_id}/documents/{self.id}/chunks", data)
        res = res.json()
        if res.get("code") == 0:
            chunks = []
            for data in res["data"].get("chunks"):
                chunk = Chunk(self.rag, data)
                chunks.append(chunk)
            return chunks
        raise Exception(res.get("message"))

    def add_chunk(self, content: str, important_keywords: list[str] = [], questions: list[str] = []):
        res = self.post(f"/datasets/{self.dataset_id}/documents/{self.id}/chunks", {"content": content, "important_keywords": important_keywords, "questions": questions})
        res = res.json()
        if res.get("code") == 0:
            return Chunk(self.rag, res["data"].get("chunk"))
        raise Exception(res.get("message"))

    def delete_chunks(self, ids: list[str] | None = None):
        res = self.rm(f"/datasets/{self.dataset_id}/documents/{self.id}/chunks", {"chunk_ids": ids})
        res = res.json()
        if res.get("code") != 0:
            raise Exception(res.get("message"))
