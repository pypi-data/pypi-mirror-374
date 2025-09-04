#!/usr/bin/env python3

# This script connects the MCP AI agent to the Attack Executor API Server

import sys
import os
import argparse
import logging
from typing import Dict, Any, Optional, List
import requests

from fastmcp import FastMCP

from attack_executor.scan.nmap import NmapExecutor
from attack_executor.scan.whatweb import WhatwebExecutor
from attack_executor.scan.gobuster import GobusterExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_ATTACK_EXECUTOR_SERVER = "http://192.168.50.80:5001"
DEFAULT_REQUEST_TIMEOUT = 600  # 10 minutes default timeout for API requests

# class AttackExecutorClient:
#     """Client for communicating with the Attack Executor API Server"""
    
#     def __init__(self, server_url: str, timeout: int = DEFAULT_REQUEST_TIMEOUT):
#         """
#         Initialize the Attack Executor Client
        
#         Args:
#             server_url: URL of the Attack Executor API Server
#             timeout: Request timeout in seconds
#         """
#         self.server_url = server_url.rstrip("/")
#         self.timeout = timeout
#         logger.info(f"Initialized Attack Executor Client connecting to {server_url}")
        
#     def safe_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#         """
#         Perform a GET request with optional query parameters.
        
#         Args:
#             endpoint: API endpoint path (without leading slash)
#             params: Optional query parameters
            
#         Returns:
#             Response data as dictionary
#         """
#         if params is None:
#             params = {}

#         url = f"{self.server_url}/{endpoint}"

#         try:
#             logger.debug(f"GET {url} with params: {params}")
#             response = requests.get(url, params=params, timeout=self.timeout)
#             response.raise_for_status()
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Request failed: {str(e)}")
#             return {"error": f"Request failed: {str(e)}", "success": False}
#         except Exception as e:
#             logger.error(f"Unexpected error: {str(e)}")
#             return {"error": f"Unexpected error: {str(e)}", "success": False}

#     def safe_post(self, endpoint: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Perform a POST request with JSON data.
        
#         Args:
#             endpoint: API endpoint path (without leading slash)
#             json_data: JSON data to send
            
#         Returns:
#             Response data as dictionary
#         """
#         url = f"{self.server_url}/{endpoint}"
        
#         try:
#             logger.debug(f"POST {url} with data: {json_data}")
#             response = requests.post(url, json=json_data, timeout=self.timeout)
#             response.raise_for_status()
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Request failed: {str(e)}")
#             return {"error": f"Request failed: {str(e)}", "success": False}
#         except Exception as e:
#             logger.error(f"Unexpected error: {str(e)}")
#             return {"error": f"Unexpected error: {str(e)}", "success": False}

#     def check_health(self) -> Dict[str, Any]:
#         """
#         Check the health of the Attack Executor API Server
        
#         Returns:
#             Health status information
#         """
#         return self.safe_get("health")

def setup_mcp_server() -> FastMCP:
    """
    Set up the MCP server with all Attack Executor tool functions
    
    Args:
        attack_executor_client: Initialized AttackExecutorClient
        
    Returns:
        Configured FastMCP instance
    """
    mcp = FastMCP("attack-executor-mcp")
    
    # @mcp.tool()
    # def nmap_scan(target: str, options: str = None) -> Dict[str, Any]:
    #     """
    #     Execute an Nmap scan using the Attack Executor NmapExecutor.
        
    #     Args:
    #         target: The IP address or hostname to scan
    #         options: Nmap scan options (e.g., "-sS -sV -O -A") or "xml" for XML parsing
            
    #     Returns:
    #         Scan results from NmapExecutor
    #     """
    #     nmap = NmapExecutor()
    #     if options:
    #         return nmap.scan(target=target, options = options)
    #     else:
    #         return nmap.scan(target=target)

    @mcp.tool()
    def nmap_scan(target: str) -> Dict[str, Any]:
        """
        Execute an Nmap scan using the Attack Executor NmapExecutor.
        
        Args:
            target: The IP address or hostname to scan
            
        Returns:
            Scan results from NmapExecutor
        """
        nmap = NmapExecutor()
        return nmap.scan(target=target)

    @mcp.tool
    def roll_dice(n_dice: int) -> list[int]:
        """Roll `n_dice` 6-sided dice and return the results."""
        import random
        return [random.randint(1, 6) for _ in range(n_dice)]

    # @mcp.tool()
    # def gobuster_dir_enumerate(target: str) -> Dict[str, Any]:
    #     """
    #     Execute Gobuster scan using the Attack Executor GobusterExecutor.
        
    #     Args:
    #         target: The target URL or domain
            
    #     Returns:
    #         Scan results from GobusterExecutor
    #     """
    #     scanner = GobusterExecutor()
    #     return scanner.enumerate_dir(target)
    
    @mcp.tool()
    def whatweb_scan(target: str) -> Dict[str, Any]:
        """
        Execute Whatweb scan on the target URL
        
        Args:
            target: The web address (URL, domain, or IP) that serves HTTP or HTTPS content.
            
        Returns:
            Scan results from Whatweb
        """
        scanner = WhatwebExecutor()
        return scanner.scan(target = target)
    
    # @mcp.tool()
    # def nuclei_scan(
    #     target: str
    # ) -> Dict[str, Any]:
    #     """
    #     Execute Gobuster scan using the Attack Executor GobusterExecutor.
        
    #     Args:
    #         target: The target URL or domain
            
    #     Returns:
    #         Scan results from Nuclei
    #     """
    #     data = {
    #         "target": target,
    #         "mode": mode,
    #         "wordlist": wordlist,
    #         "extensions": extensions,
    #         "threads": threads,
    #         "endchar": endchar
    #     }
    #     return attack_executor_client.safe_post("api/scan/gobuster", data)

    # @mcp.tool()
    # def shell_execute(command: str) -> Dict[str, Any]:
    #     """
    #     Execute shell commands using the Attack Executor ShellExecutor.
        
    #     Args:
    #         command: Shell command to execute
            
    #     Returns:
    #         Command execution results with stdout, stderr, and return code
    #     """
    #     data = {
    #         "command": command
    #     }
    #     return attack_executor_client.safe_post("api/shell/execute", data)

    return mcp

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Attack Executor MCP Client")
    parser.add_argument("--server", type=str, default=DEFAULT_ATTACK_EXECUTOR_SERVER, 
                      help=f"Attack Executor API server URL (default: {DEFAULT_ATTACK_EXECUTOR_SERVER})")
    parser.add_argument("--timeout", type=int, default=DEFAULT_REQUEST_TIMEOUT,
                      help=f"Request timeout in seconds (default: {DEFAULT_REQUEST_TIMEOUT})")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser.parse_args()

def main():
    """Main entry point for the MCP server."""
    args = parse_args()
    
    # Configure logging based on debug flag
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Set up and run the MCP server
    mcp = setup_mcp_server()
    logger.info("Starting Attack Executor MCP server")
    mcp.run(transport="sse")

def test():
    import asyncio
    from fastmcp import Client
    mcp = setup_mcp_server()
    client = Client(mcp)
    async def call_tool(target: str):
        async with client:
            result = await client.call_tool("nmap_scan", {"target": target})
            print(result)

    asyncio.run(call_tool("10.129.99.21"))

if __name__ == "__main__":
    main()
    # test() 