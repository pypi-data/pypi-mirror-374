from databricks.vector_search.client import VectorSearchClient
from typing import Optional, List
import json
import os
from utils.logger import logger

client = VectorSearchClient(
    "https://" + os.environ.get("DATABRICKS_HOST"), os.environ.get("DATABRICKS_TOKEN")
)

index = client.get_index(
    endpoint_name="delisoy_memory",
    index_name="silver.external_data.delisoy_chunked_rag",
)


def studies_rag(
    query_text: str,
    doc_ids: Optional[List[str]] = None,  # file_path list from filter_summaries_sql
    num_results: int = 100,
) -> str:
    """
    Search the chunked RAG index with vector similarity.

    Args:
        query_text: Semantic query text
        doc_ids: List of file_path values to restrict search to (from filter_summaries_sql)
        num_results: Max results to return

    Results structure: [doc_id, chunk_text, similarity_score] (only 3 columns now)
    """
    # Build parameter description for logging
    search_params = [f"query='{query_text[:50]}...'", f"num_results={num_results}"]
    if doc_ids:
        search_params.append(f"doc_filter={len(doc_ids)} documents")
    else:
        search_params.append("no document filter")

    params_description = ", ".join(search_params)
    logger.info(f"Starting RAG search: {params_description}")

    try:
        # Cap results to prevent context overflow
        original_num_results = num_results
        num_results = min(num_results, 500)
        if original_num_results != num_results:
            logger.debug(
                f"Capped num_results from {original_num_results} to {num_results}"
            )

        # Build Databricks native filters if doc_ids provided
        search_filters = None
        if doc_ids:
            # Use Databricks native filtering with correct dictionary format
            search_filters = {"doc_id": doc_ids}
            logger.debug(f"Using Databricks native filter: {search_filters}")
        else:
            logger.debug("No document filtering - searching all documents")

        # Get results from vector index with native filtering
        search_params = {
            "columns": ["doc_id", "chunk_text"],  # Only these 2 columns
            "query_text": query_text,
            "num_results": num_results,
            "disable_notice": True,
        }

        # Add filters if we have them
        if search_filters:
            search_params["filters"] = search_filters

        logger.debug(f"Requesting {num_results} results with native filtering")
        results = index.similarity_search(**search_params)

        logger.debug(
            f"Vector search completed, raw result keys: {list(results.keys())}"
        )

        # Parse results (expecting 3-column structure: [doc_id, chunk_text, score])
        chunks = []
        raw_data = results.get("result", {}).get("data_array", [])
        logger.debug(
            f"Processing {len(raw_data)} results from vector index (no post-filtering needed)"
        )

        for result in raw_data:
            if len(result) >= 3:  # Expecting 3 columns: doc_id, chunk_text, score
                doc_id, chunk_text, score = result[:3]  # Updated parsing

                chunks.append(
                    {
                        "doc_id": doc_id,
                        "text": chunk_text,
                        "score": round(float(score), 4)
                        if isinstance(score, (int, float))
                        else score,
                    }
                )

        # Log successful completion with summary
        docs_found = set(chunk["doc_id"] for chunk in chunks)
        avg_score = (
            sum(
                chunk["score"]
                for chunk in chunks
                if isinstance(chunk["score"], (int, float))
            )
            / len(chunks)
            if chunks
            else 0
        )

        result_summary = [f"{len(chunks)} chunks"]
        if docs_found:
            result_summary.append(f"{len(docs_found)} documents")
        if avg_score > 0:
            result_summary.append(f"avg_score: {avg_score:.3f}")

        logger.info(
            f"RAG search completed: {', '.join(result_summary)} - {params_description}"
        )

        # Log sample results at debug level
        if chunks:
            sample_chunks = chunks[:3]
            for i, chunk in enumerate(sample_chunks):
                text_preview = chunk["text"][:100].replace("\n", " ")
                logger.debug(
                    f"Result {i + 1}: doc={chunk['doc_id']}, score={chunk['score']}, text='{text_preview}...'"
                )
        else:
            logger.warning(
                f"No relevant chunks found for query: '{query_text[:50]}...'"
            )

        # Build response
        return json.dumps(
            {
                "index": "silver.external_data.delisoy_chunked_rag",
                "query": query_text,
                "doc_filter": f"Restricted to {len(doc_ids)} documents"
                if doc_ids
                else "No document restriction",
                "result_count": len(chunks),
                "results": chunks,
            },
            ensure_ascii=False,
        )

    except Exception as e:
        logger.error(f"RAG search failed: {str(e)} - {params_description}")
        return json.dumps(
            {
                "index": "silver.external_data.delisoy_chunked_rag",
                "query": query_text,
                "doc_filter": f"Restricted to {len(doc_ids)} documents"
                if doc_ids
                else "No document restriction",
                "result_count": 0,
                "results": [],
                "error": str(e),
            },
            ensure_ascii=False,
        )
