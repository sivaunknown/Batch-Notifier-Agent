from dotenv import load_dotenv
load_dotenv()
from langchain.agents import create_agent
from langchain.tools import tool
from utils.dependency_mapper import lookup
import os

@tool
def search_jobs(job_name: str):
    """Use this tool to search the job.
       This will provide the mapping of the job, and the list it's predecessor and successor."""
    config_map = os.getenv("DEPENDENCY_MAP")
    job_map = lookup(config_map,job_name)
    return job_map


agent = create_agent(model='groq:openai/gpt-oss-20b', tools=[search_jobs],
                     system_prompt="""You are a job monitoring and managing agent.
                      Rules:
                            - Answer the user's exact question only.
                            - Be concise. Use 1-2 sentences maximum.
                            - Do not provide explanations, tables, or extra details unless requested.""")

response = agent.invoke({"messages": "can you provide entire dependency chain for DBARRT_FIN_LIQUIDITY_RATIO_DAILY_VNM_V10 ?"})

print(response["messages"][-1].content)
