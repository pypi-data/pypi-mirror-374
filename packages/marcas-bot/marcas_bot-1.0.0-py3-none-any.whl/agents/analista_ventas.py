from langchain_openai import ChatOpenAI
from config.params import OPENAI_API_KEY
from config.prompts import analista_ventas_prompt
from models.agentic_llm import AgenticLLM
from tools.polars_data_tool import polars_analysis_tool

# Refactored: Use shared AgenticLLM directly and move preprocessing into the node layer
# to align with the core base agent/node architecture.

sales_agent = AgenticLLM(
    model=ChatOpenAI(
        model="gpt-4.1",
        api_key=OPENAI_API_KEY,
        temperature=0.1,
        top_p=0.9,
        max_tokens=2000,
    ),
    tools=[polars_analysis_tool],
    sys_prompt=analista_ventas_prompt,
)
