
import argparse
import json
import logging
import networkx as nx
import trio

from api import settings
from api.db import LLMType
from api.db.services.document_service import DocumentService
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.services.llm_service import LLMBundle
from api.db.services.user_service import TenantService
from graphrag.general.graph_extractor import GraphExtractor
from graphrag.general.index import update_graph, with_resolution, with_community

settings.init_settings()


def callback(prog=None, msg="Processing..."):
    logging.info(msg)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tenant_id",
        default=False,
        help="Tenant ID",
        action="store",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--doc_id",
        default=False,
        help="Document ID",
        action="store",
        required=True,
    )
    args = parser.parse_args()
    e, doc = DocumentService.get_by_id(args.doc_id)
    if not e:
        raise LookupError("Document not found.")
    kb_id = doc.kb_id

    chunks = [
        d["content_with_weight"]
        for d in settings.retrievaler.chunk_list(
            args.doc_id,
            args.tenant_id,
            [kb_id],
            max_count=6,
            fields=["content_with_weight"],
        )
    ]

    _, tenant = TenantService.get_by_id(args.tenant_id)
    llm_bdl = LLMBundle(args.tenant_id, LLMType.CHAT, tenant.llm_id)
    _, kb = KnowledgebaseService.get_by_id(kb_id)
    embed_bdl = LLMBundle(args.tenant_id, LLMType.EMBEDDING, kb.embd_id)

    graph, doc_ids = await update_graph(
        GraphExtractor,
        args.tenant_id,
        kb_id,
        args.doc_id,
        chunks,
        "English",
        llm_bdl,
        embed_bdl,
        callback,
    )
    print(json.dumps(nx.node_link_data(graph), ensure_ascii=False, indent=2))

    await with_resolution(
        args.tenant_id, kb_id, args.doc_id, llm_bdl, embed_bdl, callback
    )
    community_structure, community_reports = await with_community(
        args.tenant_id, kb_id, args.doc_id, llm_bdl, embed_bdl, callback
    )

    print(
        "------------------ COMMUNITY STRUCTURE--------------------\n",
        json.dumps(community_structure, ensure_ascii=False, indent=2),
    )
    print(
        "------------------ COMMUNITY REPORTS----------------------\n",
        community_reports,
    )


if __name__ == "__main__":
    trio.run(main)
