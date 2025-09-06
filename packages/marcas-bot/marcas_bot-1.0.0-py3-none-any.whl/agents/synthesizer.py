from models.agentic_llm import AgenticLLM
from config.prompts import synthesizer_prompt
from config.params import OPENAI_API_KEY
from langchain_openai import ChatOpenAI

synthesizer_agent = AgenticLLM(
    model=ChatOpenAI(
        model="gpt-4.1",
        api_key=OPENAI_API_KEY,
        temperature=0.2,
        top_p=0.95,
        max_tokens=5000,
    ),
    sys_prompt=synthesizer_prompt,
)
