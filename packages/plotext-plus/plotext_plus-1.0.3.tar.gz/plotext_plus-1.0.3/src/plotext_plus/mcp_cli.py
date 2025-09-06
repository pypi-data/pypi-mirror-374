#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plotext Plus MCP Server CLI
==========================

Command-line interface for starting the Plotext Plus MCP server.
"""

import sys
import argparse


def main():
    """Main entry point for the MCP server CLI."""
    parser = argparse.ArgumentParser(
        description="Plotext Plus MCP Server - Terminal plotting for AI clients"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="plotext_plus MCP server"
    )
    parser.add_argument(
        "--info", 
        action="store_true",
        help="Show MCP server information"
    )
    
    args = parser.parse_args()
    
    if args.info:
        print("Plotext Plus MCP Server")
        print("======================")
        print("Terminal plotting library with MCP (Model Context Protocol) support")
        print("Exposes plotting, charting, theming, and utility functions as MCP tools")
        print("")
        print("Available tools:")
        print("- scatter_plot: Create scatter plots")
        print("- line_plot: Create line plots")  
        print("- bar_chart: Create bar charts")
        print("- matrix_plot: Create matrix/heatmap plots")
        print("- quick_scatter/line/bar: Quick chart creation")
        print("- theme management tools")
        print("- utility functions")
        print("")
        print("Available prompts:")
        print("- basic_scatter: Simple scatter plot example")
        print("- basic_bar_chart: Bar chart example")
        print("- multi_step_workflow: Complex multi-step analysis")
        print("- theme_exploration: Theme comparison examples")
        print("- regional_sales_analysis: Interactive data analysis")
        print("- performance_testing: Large dataset testing")
        print("- error_handling_test: Edge case testing")
        print("- complete_workflow: End-to-end visualization workflow")
        print("- And 7 more prompts covering all use cases")
        print("")
        print("Available resources:")
        print("- config://plotext: Server configuration and capabilities")
        print("")
        print("To start the server, run: plotext-mcp")
        return
    
    try:
        from .mcp_server import start_server
        start_server()
    except ImportError as e:
        if "chuk-mcp-server" in str(e):
            print("ERROR: MCP functionality requires chuk-mcp-server")
            print("Install it with: uv add --optional mcp plotext_plus")
            print("Or: pip install 'plotext_plus[mcp]'")
            sys.exit(1)
        else:
            raise


if __name__ == "__main__":
    main()