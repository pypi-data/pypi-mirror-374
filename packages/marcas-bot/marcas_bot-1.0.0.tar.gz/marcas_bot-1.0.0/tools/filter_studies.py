from langchain.tools import StructuredTool
from utils.filter_studies import filter_studies
from schemas.filter_studies_input import StudiesFilterInput

filter_studies_tool = StructuredTool.from_function(
    func=filter_studies,
    name="filter_studies",
    description=(
        "Filtrar una tabla de Databricks compuesta por estudios internos realizados para diferentes marcas por año extraídos de file_path "
        "y/o por país (Nicaragua, Internacional). Devuelve un JSON compacto con file_path, país, año. "
        "Entradas: año (int), rango de años ([inicio, fin]), países (['Nicaragua', 'Internacional']), límite (<=1200)."
    ),
    args_schema=StudiesFilterInput,
)
