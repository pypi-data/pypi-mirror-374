#!/usr/bin/env python3

# This script creates a Flask API server that wraps attack_executor tools

import argparse
import json
import logging
import os
import sys
import traceback
import tempfile
import asyncio
from typing import Dict, Any
from flask import Flask, request, jsonify

# Import attack_executor tools
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from attack_executor.scan.nmap import NmapExecutor
from attack_executor.scan.gobuster import GobusterExecutor
from attack_executor.bash.Shell import ShellExecutor


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_PORT = int(os.environ.get("API_PORT", 5001))
DEBUG_MODE = os.environ.get("DEBUG_MODE", "0").lower() in ("1", "true", "yes", "y")

app = Flask(__name__)

# Global tool instances
nmap_executor = NmapExecutor()
gobuster_executor = GobusterExecutor()
shell_executor = ShellExecutor()


# Global configuration
config = None

def safe_execute(func, *args, **kwargs) -> Dict[str, Any]:
    """Safely execute a function and return standardized results"""
    try:
        result = func(*args, **kwargs)
        return {
            "success": True,
            "result": result,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error executing function {func.__name__}: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "result": None,
            "error": str(e)
        }

@app.route("/api/scan/nmap", methods=["POST"])
def nmap_scan():
    """Execute Nmap scan using NmapExecutor"""
    try:
        params = request.json
        target = params.get("target", "")
        options = params.get("options", "-sS -sV -O -A")
        
        if not target:
            return jsonify({
                "success": False,
                "error": "Target parameter is required"
            }), 400
        
        if options == "xml":
            # Use XML parsing version
            result = safe_execute(nmap_executor.scan_xml, target)
        else:
            # Use regular scan version
            result = safe_execute(nmap_executor.scan, target, options)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in nmap endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/scan/gobuster", methods=["POST"])
def gobuster_scan():
    """Execute Gobuster scan using GobusterExecutor"""
    try:
        params = request.json
        target = params.get("target", "")
        mode = params.get("mode", "dir")
        wordlist = params.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
        extensions = params.get("extensions", None)
        threads = params.get("threads", 10)
        
        if not target:
            return jsonify({
                "success": False,
                "error": "Target parameter is required"
            }), 400
        
        gobuster_executor.start_session(target)
        
        if mode == "dir":
            result = safe_execute(gobuster_executor.enumerate_dir, target, wordlist, extensions, threads)
        elif mode == "subdomain":
            result = safe_execute(gobuster_executor.enumerate_subdomain, target, wordlist, threads)
        elif mode == "fuzz":
            endchar = params.get("endchar", "/")
            result = safe_execute(gobuster_executor.fuzz_directory, wordlist, endchar, threads)
        else:
            return jsonify({
                "success": False,
                "error": f"Invalid mode: {mode}. Must be one of: dir, subdomain, fuzz"
            }), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in gobuster endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route("/api/shell/execute", methods=["POST"])
def shell_execute():
    """Execute shell commands using ShellExecutor"""
    try:
        params = request.json
        command = params.get("command", "")
        
        if not command:
            return jsonify({
                "success": False,
                "error": "Command parameter is required"
            }), 400
        
        def run_shell_command():
            stdout, stderr, returncode = shell_executor.execute_command(command)
            return {
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode
            }
        
        result = safe_execute(run_shell_command)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in shell endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        # Test basic functionality
        test_result = shell_executor.execute_command("echo 'Health check'")
        return jsonify({
            "status": "healthy",
            "message": "Attack Executor API Server is running",
            # TODO: Add tools availability based on the tools installed
            "tools_available": {
                "nmap": True,
                "gobuster": True,
                "nessus": False,
                "metasploit": False,
                "sliver": False,
                "linpeas": False,
                "searchsploit": False,
                "shell": True
            }
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}"
        }), 500

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run the Attack Executor API Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--port", type=int, default=API_PORT, help=f"Port for the API server (default: {API_PORT})")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Load configuration if provided
    if args.config:
        try:
            config = load_config(args.config)
            logger.info(f"Loaded configuration from {args.config}")
        except Exception as e:
            logger.warning(f"Failed to load configuration: {e}")
    
    # Set configuration from command line arguments
    if args.debug:
        DEBUG_MODE = True
        os.environ["DEBUG_MODE"] = "1"
        logger.setLevel(logging.DEBUG)
    
    if args.port != API_PORT:
        API_PORT = args.port
    
    logger.info(f"Starting Attack Executor API Server on port {API_PORT}")
    app.run(host="0.0.0.0", port=API_PORT, debug=DEBUG_MODE) 