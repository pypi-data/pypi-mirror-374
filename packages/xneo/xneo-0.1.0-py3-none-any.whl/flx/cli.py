"""
XNeo Command Line Interface
"""
import argparse
from typing import Optional
from . import __version__, execute_flow, serve

def main():
    """Main entry point for the XNeo CLI."""
    parser = argparse.ArgumentParser(
        description="XNeo - A lightweight CLI tool for executing and serving AI flows"
    )
    parser.add_argument(
        "-v", "--version", 
        action="version", 
        version=f"XNeo {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Execute an AI flow")
    run_parser.add_argument("flow_path", help="Path to the flow configuration file")
    
    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the XNeo server")
    serve_parser.add_argument(
        "-p", "--port", 
        type=int, 
        default=8000, 
        help="Port to run the server on (default: 8000)"
    )
    serve_parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    
    args = parser.parse_args()
    
    if args.command == "run":
        result = execute_flow(args.flow_path)
        print(f"Flow execution result: {result}")
    elif args.command == "serve":
        serve(port=args.port, host=args.host)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
