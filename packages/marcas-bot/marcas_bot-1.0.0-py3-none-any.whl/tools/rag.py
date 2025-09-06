from utils.rag import studies_rag
from schemas.rag_input import ChunkedRagInput
from langchain.tools import StructuredTool

studies_rag_tool = StructuredTool.from_function(
    func=studies_rag,
    name="search_chunked_rag",
    description=(
        "Buscar documentos fragmentados utilizando similitud de vectores. Mejor utilizado con doc_ids de la herramienta filter_studies "
        "para restringir la búsqueda a años/países específicos. Devuelve fragmentos de texto relevantes con puntuaciones de similitud."
    ),
    args_schema=ChunkedRagInput,
)
