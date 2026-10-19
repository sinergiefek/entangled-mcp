"""
CLI entrypoint for running the Entangled MCP server over stdio.
"""

import sys
import argparse
from .server import create_entangled_server

def main():
    parser = argparse.ArgumentParser(description="Entangled-MCP: Quantum Telepathy Mesh for AI Agents")
    parser.add_argument("--db", type=str, default=None, help="Custom path to SQLite WAL database file")
    args = parser.parse_args()

    # Log strictly to stderr to keep stdout 100% clean for JSON-RPC 2.0
    sys.stderr.write("⚛️ Starting Entangled-MCP Quantum Telepathy Engine...\n")
    sys.stderr.flush()

    server = create_entangled_server(args.db)
    server.run()

if __name__ == "__main__":
    main()
