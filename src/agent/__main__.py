import asyncio
import os
import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from .main import logger, toolset, root_agent

port = int(os.getenv("AGENT_PORT", 10000))
a2a_app = to_a2a(root_agent, port=port)


async def serve():
    config = uvicorn.Config(a2a_app, host="localhost", port=port)
    server = uvicorn.Server(config)
    logger.info("agent_server_started", port=port)
    try:
        await server.serve()
    finally:
        logger.info("agent_server_stopping")
        await toolset.close()
        logger.info("agent_server_stopped")


asyncio.run(serve())
