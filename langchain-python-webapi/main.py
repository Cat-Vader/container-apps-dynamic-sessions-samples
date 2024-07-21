import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langchain import agents, hub
from langchain.llms import Ollama
from langchain_community.tools import PythonREPLTool

app = FastAPI()

@app.get("/")
async def root():
    return RedirectResponse("/docs")

@app.get("/chat")
async def chat(message: str):
    # Initialize Ollama LLM
    llm = Ollama(model="llama2")  # You can change this to your preferred Ollama model

    # Initialize Python REPL tool
    repl = PythonREPLTool()

    tools = [repl]
    prompt = hub.pull("hwchase17/openai-functions-agent")
    agent = agents.create_tool_calling_agent(llm, tools, prompt)

    agent_executor = agents.AgentExecutor(
        agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
    )

    response = agent_executor.invoke({"input": message})

    return {"output": response["output"]}