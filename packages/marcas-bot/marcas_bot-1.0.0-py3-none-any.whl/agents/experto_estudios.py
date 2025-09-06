from models.agentic_llm import AgenticLLM
from config.prompts import experto_estudios_prompt
from tools.rag import studies_rag_tool
from tools.filter_studies import filter_studies_tool
from langchain_openai import ChatOpenAI
from config.params import OPENAI_API_KEY


market_study_agent = AgenticLLM(
    model=ChatOpenAI(
        model="gpt-4.1-mini",
        api_key=OPENAI_API_KEY,
        temperature=0.1,
        top_p=0.9,
        max_tokens=5000,
    ),
    tools=[studies_rag_tool, filter_studies_tool],
    sys_prompt=experto_estudios_prompt,
)
