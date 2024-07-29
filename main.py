import os
from typing import Optional

import dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from langchain import agents, hub
from langchain_groq import ChatGroq
from langchain_azure_dynamic_sessions import SessionsPythonREPLTool

dotenv.load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return RedirectResponse("/docs")


@app.get("/chat")
async def chat(message: Optional[str] = Query(None, description="The message to process")):
    if not message:
        raise HTTPException(status_code=400, detail="Message parameter is required")

    try:
        pool_management_endpoint = os.getenv("POOL_MANAGEMENT_ENDPOINT")
        if not pool_management_endpoint:
            raise ValueError("POOL_MANAGEMENT_ENDPOINT environment variable is not set")

        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")

        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama3-groq-70b-8192-tool-use-preview",  # Replace with the appropriate Groq model
            temperature=0,
        )

        repl = SessionsPythonREPLTool(pool_management_endpoint=pool_management_endpoint)

        tools = [repl]
        prompt = hub.pull("hwchase17/openai-functions-agent")
        agent = agents.create_tool_calling_agent(llm, tools, prompt)

        agent_executor = agents.AgentExecutor(
            agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
        )

        response = agent_executor.invoke({"input": message})

        return {"output": response["output"]}

    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")