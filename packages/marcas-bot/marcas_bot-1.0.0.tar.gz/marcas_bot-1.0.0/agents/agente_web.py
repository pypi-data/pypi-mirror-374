from models.agentic_llm import AgenticLLM
from langchain_openai import ChatOpenAI
from config.params import OPENAI_API_KEY
from config.prompts import search_prompt
from tools.web_search import web_search_tool

search_agent = AgenticLLM(
    model=ChatOpenAI(
        model="gpt-4.1-mini",
        api_key=OPENAI_API_KEY,
        temperature=0.1,
        top_p=0.9,
        max_tokens=2000,
    ),
    tools=[web_search_tool],
    sys_prompt=search_prompt,
)
