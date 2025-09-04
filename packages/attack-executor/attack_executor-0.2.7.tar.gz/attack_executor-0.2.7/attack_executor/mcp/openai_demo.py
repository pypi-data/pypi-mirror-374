import asyncio
import os
from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings
from dotenv import load_dotenv

#load .env
load_dotenv()

# run fastmcp run mcp-server-openai.py:mcp --transport sse
#before running this, run the mcp-server-openai.py file

async def main():
    
    server = MCPServerSse(
        name="SSE Python Server",
        params={
            "url": "http://localhost:8000/sse",
        },
        client_session_timeout_seconds = 300
    )
    await server.connect()  # Initialize the server connection
    
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=[server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    message = "Help me do the penetration testing to the IP address 10.129.10.68"

    i = 0
    while i < 3:
        i += 1
        print(f"Running: {message}")
        result = await Runner.run(starting_agent=agent, input=message)
        # print(result.to_input_list())
        message = result.to_input_list()
        # print(result.final_output)

    await server.cleanup()  # Clean up the server connection

if __name__ == "__main__":
    asyncio.run(main())