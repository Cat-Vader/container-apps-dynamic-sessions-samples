import os
from typing import Any, List, Optional
from langchain.tools import BaseTool
from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, AgentType
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError
import requests
from pydantic import Field
from dotenv import load_dotenv


#Passing Environment Variables

load_dotenv()



class AzureDynamicSessionsTool(BaseTool):
    name = "Azure Dynamic Sessions Python REPL"
    description = "A Python REPL connected to Azure Dynamic Sessions. Use this to execute Python code in the cloud."

    pool_management_endpoint: str= Field(..., description="The endpoint for the Azure Dynamic Sessions pool")
    credential: Optional[DefaultAzureCredential] =Field(default=None, description="The credential for the Azure Dynamic Sessions pool")

    def __init__(self, pool_management_endpoint: str):
        super().__init__()
        self.pool_management_endpoint = pool_management_endpoint
        self.credential = self._get_azure_credential()

    def _get_azure_credential(self) -> Optional[DefaultAzureCredential]:
        try:
            credential = DefaultAzureCredential()
            # Test the credential
            credential.get_token("https://management.azure.com/.default")
            print("Successfully authenticated with Azure")
            return credential
        except ClientAuthenticationError as e:
            print(f"Authentication failed: {str(e)}")
            return None

    def _run(self, code: str) -> str:
        if not self.credential:
            raise ValueError("Azure authentication failed")

        token = self.credential.get_token("https://dynamicsessions.io/.default")
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json"
        }

        body = {
            "properties": {
                "codeInputType": "inline",
                "executionType": "synchronous",
                "code": code
            }
        }

        response = requests.post(
            f"{self.pool_management_endpoint}code/execute",
            headers=headers,
            json=body
        )
        response.raise_for_status()

        result = response.json().get("properties", {})
        return f"Result: {result.get('result')}\nStdout: {result.get('stdout')}\nStderr: {result.get('stderr')}"

    async def _arun(self, code: str) -> str:
        # For simplicity, we're using the synchronous version
        # In a real async environment, you'd want to use aiohttp for async HTTP requests
        return self._run(code)

# Create an instance of the AzureDynamicSessionsTool
azure_tool = AzureDynamicSessionsTool(
    pool_management_endpoint=os.environ['POOL_MANAGEMENT_ENDPOINT']
)

# Initialize the Ollama LLM
llm = Ollama(model="codellama")

# Create an agent that uses the Ollama LLM and the Azure Dynamic Sessions tool
agent = initialize_agent(
    tools=[azure_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Example usage of the agent
task = "Calculate the factorial of 5 and print the result"
result = agent.run(task)
print(result)