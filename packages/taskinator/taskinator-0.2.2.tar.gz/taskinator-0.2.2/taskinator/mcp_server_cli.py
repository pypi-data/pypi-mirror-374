#!/usr/bin/env python3
"""
CLI entry point for the Taskinator MCP server.
"""

import os
import sys
import argparse
import asyncio
import logging

from taskinator.mcp_server import TaskinatorMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("taskinator-mcp-cli")

async def start_server(args):
    """Start the MCP server with the given arguments."""
    server = TaskinatorMCPServer()
    
    # Handle graceful shutdown
    try:
        await server.start()
    except Exception as e:
        logger.error(f"Failed to start MCP server: {str(e)}")
        sys.exit(1)
    finally:
        await server.stop()

def main():
    """Main entry point for the MCP server CLI."""
    parser = argparse.ArgumentParser(description="Taskinator MCP Server")
    parser.add_argument("--project-root", type=str, help="Project root directory")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(start_server(args))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
