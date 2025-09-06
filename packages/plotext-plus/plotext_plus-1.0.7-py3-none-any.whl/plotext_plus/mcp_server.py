# /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plotext Plus MCP Server - Model Context Protocol Integration
==========================================================

This module provides a Model Context Protocol (MCP) server that exposes
the plotext_plus API as MCP tools for use with AI clients like Claude.

The server uses chuk-mcp-server for zero-configuration MCP functionality.
"""

try:
    from chuk_mcp_server import tool, resource, prompt, run
except ImportError:
    raise ImportError(
        "chuk-mcp-server is required for MCP functionality. "
        "Install it with: uv add --optional mcp plotext_plus"
    )

import asyncio
from typing import List, Optional, Union, Dict, Any
import json
import base64
from io import StringIO
import sys

# Import public plotext_plus APIs
from . import plotting
from . import charts
from . import themes
from . import utilities

# Keep track of the current plot state
_current_plot_buffer = StringIO()


def _capture_plot_output(func, *args, **kwargs):
    """Capture plot output and return as string"""
    # Save current stdout
    old_stdout = sys.stdout
    
    try:
        # Redirect stdout to capture plot output
        sys.stdout = _current_plot_buffer
        result = func(*args, **kwargs)
        plot_output = _current_plot_buffer.getvalue()
        _current_plot_buffer.truncate(0)
        _current_plot_buffer.seek(0)
        return result, plot_output
    finally:
        # Restore stdout
        sys.stdout = old_stdout


# Core Plotting Tools
@tool
async def scatter_plot(x: List[Union[int, float]], y: List[Union[int, float]], 
                      marker: Optional[str] = None, color: Optional[str] = None,
                      title: Optional[str] = None) -> str:
    """Create a scatter plot with given x and y data points.
    
    Args:
        x: List of x-coordinates
        y: List of y-coordinates  
        marker: Marker style (optional)
        color: Plot color (optional)
        title: Plot title (optional)
        
    Returns:
        The rendered plot as text
    """
    plotting.clear_figure()
    if title:
        plotting.title(title)
    
    _, output = _capture_plot_output(plotting.scatter, x, y, marker=marker, color=color)
    _, show_output = _capture_plot_output(plotting.show)
    
    return output + show_output


@tool
async def line_plot(x: List[Union[int, float]], y: List[Union[int, float]], 
                   color: Optional[str] = None, title: Optional[str] = None) -> str:
    """Create a line plot with given x and y data points.
    
    Args:
        x: List of x-coordinates
        y: List of y-coordinates
        color: Line color (optional)
        title: Plot title (optional)
        
    Returns:
        The rendered plot as text
    """
    plotting.clear_figure()
    if title:
        plotting.title(title)
    
    _, output = _capture_plot_output(plotting.plot, x, y, color=color)
    _, show_output = _capture_plot_output(plotting.show)
    
    return output + show_output


@tool
async def bar_chart(labels: List[str], values: List[Union[int, float]], 
                   color: Optional[str] = None, title: Optional[str] = None) -> str:
    """Create a bar chart with given labels and values.
    
    Args:
        labels: List of bar labels
        values: List of bar values
        color: Bar color (optional)
        title: Plot title (optional)
        
    Returns:
        The rendered plot as text
    """
    plotting.clear_figure()
    if title:
        plotting.title(title)
    
    _, output = _capture_plot_output(plotting.bar, labels, values, color=color)
    _, show_output = _capture_plot_output(plotting.show)
    
    return output + show_output


@tool
async def matrix_plot(data: List[List[Union[int, float]]], title: Optional[str] = None) -> str:
    """Create a matrix/heatmap plot from 2D data.
    
    Args:
        data: 2D list representing matrix data
        title: Plot title (optional)
        
    Returns:
        The rendered plot as text
    """
    plotting.clear_figure()
    if title:
        plotting.title(title)
    
    _, output = _capture_plot_output(plotting.matrix_plot, data)
    _, show_output = _capture_plot_output(plotting.show)
    
    return output + show_output


# Chart Class Tools
@tool
async def quick_scatter(x: List[Union[int, float]], y: List[Union[int, float]], 
                       title: Optional[str] = None, theme_name: Optional[str] = None) -> str:
    """Create a quick scatter chart using the chart classes API.
    
    Args:
        x: List of x-coordinates
        y: List of y-coordinates
        title: Chart title (optional)
        theme_name: Theme to apply (optional)
        
    Returns:
        The rendered chart as text
    """
    _, output = _capture_plot_output(charts.quick_scatter, x, y, title=title, theme=theme_name)
    return output


@tool
async def quick_line(x: List[Union[int, float]], y: List[Union[int, float]], 
                    title: Optional[str] = None, theme_name: Optional[str] = None) -> str:
    """Create a quick line chart using the chart classes API.
    
    Args:
        x: List of x-coordinates
        y: List of y-coordinates
        title: Chart title (optional)
        theme_name: Theme to apply (optional)
        
    Returns:
        The rendered chart as text
    """
    _, output = _capture_plot_output(charts.quick_line, x, y, title=title, theme=theme_name)
    return output


@tool
async def quick_bar(labels: List[str], values: List[Union[int, float]], 
                   title: Optional[str] = None, theme_name: Optional[str] = None) -> str:
    """Create a quick bar chart using the chart classes API.
    
    Args:
        labels: List of bar labels
        values: List of bar values
        title: Chart title (optional)
        theme_name: Theme to apply (optional)
        
    Returns:
        The rendered chart as text
    """
    _, output = _capture_plot_output(charts.quick_bar, labels, values, title=title, theme=theme_name)
    return output


# Theme Tools
@tool
async def get_available_themes() -> Dict[str, Any]:
    """Get information about available themes.
    
    Returns:
        Dictionary containing theme information
    """
    from .themes import get_theme_info
    return get_theme_info()


@tool
async def apply_plot_theme(theme_name: str) -> str:
    """Apply a theme to the current plot.
    
    Args:
        theme_name: Name of the theme to apply
        
    Returns:
        Confirmation message
    """
    plotting.clear_figure()
    plotting.theme(theme_name)
    return f"Applied theme: {theme_name}"


# Utility Tools
@tool
async def get_terminal_width() -> int:
    """Get the current terminal width.
    
    Returns:
        Terminal width in characters
    """
    return utilities.terminal_width()


@tool
async def colorize_text(text: str, color: str) -> str:
    """Apply color formatting to text.
    
    Args:
        text: Text to colorize
        color: Color name or code
        
    Returns:
        Colorized text
    """
    return utilities.colorize(text, color)


@tool
async def log_info(message: str) -> str:
    """Log an informational message.
    
    Args:
        message: Message to log
        
    Returns:
        Formatted log message
    """
    utilities.log_info(message)
    return f"INFO: {message}"


@tool
async def log_success(message: str) -> str:
    """Log a success message.
    
    Args:
        message: Message to log
        
    Returns:
        Formatted log message
    """
    utilities.log_success(message)
    return f"SUCCESS: {message}"


@tool
async def log_warning(message: str) -> str:
    """Log a warning message.
    
    Args:
        message: Message to log
        
    Returns:
        Formatted log message
    """
    utilities.log_warning(message)
    return f"WARNING: {message}"


@tool
async def log_error(message: str) -> str:
    """Log an error message.
    
    Args:
        message: Message to log
        
    Returns:
        Formatted log message
    """
    utilities.log_error(message)
    return f"ERROR: {message}"


# Configuration and Plot Management
@tool
async def set_plot_size(width: int, height: int) -> str:
    """Set the plot size.
    
    Args:
        width: Plot width
        height: Plot height
        
    Returns:
        Confirmation message
    """
    plotting.plotsize(width, height)
    return f"Plot size set to {width}x{height}"


@tool
async def enable_banner_mode(enabled: bool = True, title: Optional[str] = None, 
                           subtitle: Optional[str] = None) -> str:
    """Enable or disable banner mode.
    
    Args:
        enabled: Whether to enable banner mode
        title: Banner title (optional)
        subtitle: Banner subtitle (optional)
        
    Returns:
        Confirmation message
    """
    plotting.banner_mode(enabled, title=title, subtitle=subtitle)
    status = "enabled" if enabled else "disabled"
    return f"Banner mode {status}"


@tool
async def clear_plot() -> str:
    """Clear the current plot.
    
    Returns:
        Confirmation message
    """
    plotting.clear_figure()
    return "Plot cleared"


# Resource for plot configuration
@resource("config://plotext")
async def get_plot_config() -> Dict[str, Any]:
    """Get current plot configuration."""
    from .themes import get_theme_info
    return {
        "terminal_width": utilities.terminal_width(),
        "available_themes": get_theme_info(),
        "library_version": "plotext_plus",
        "mcp_enabled": True
    }


# MCP Prompts for common plotting scenarios
@prompt("basic_scatter")
async def basic_scatter_prompt() -> str:
    """Create a simple scatter plot example"""
    return "Create a scatter plot showing the relationship between x=[1,2,3,4,5] and y=[1,4,9,16,25] with the title 'Quadratic Function'."


@prompt("basic_bar_chart")
async def basic_bar_chart_prompt() -> str:
    """Generate a bar chart example"""
    return "Make a bar chart showing sales data: categories=['Q1','Q2','Q3','Q4'] and values=[120,150,180,200] with title 'Quarterly Sales'."


@prompt("line_plot_with_theme")
async def line_plot_with_theme_prompt() -> str:
    """Create a line plot with theme example"""
    return "Plot a line chart of temperature data over time: x=[1,2,3,4,5,6,7] and y=[20,22,25,28,26,24,21] using the 'dark' theme with title 'Weekly Temperature'."


@prompt("matrix_heatmap")
async def matrix_heatmap_prompt() -> str:
    """Matrix heatmap visualization example"""
    return "Create a heatmap from this 3x3 correlation matrix: [[1.0,0.8,0.3],[0.8,1.0,0.5],[0.3,0.5,1.0]] with title 'Feature Correlation'."


@prompt("multi_step_workflow")
async def multi_step_workflow_prompt() -> str:
    """Multi-step visualization workflow example"""
    return """1. First, show me available themes
2. Set the plot size to 100x30
3. Apply the 'elegant' theme
4. Create a scatter plot comparing dataset A=[1,3,5,7,9] vs B=[2,6,10,14,18]
5. Add title 'Linear Relationship Analysis'"""


@prompt("professional_bar_chart")
async def professional_bar_chart_prompt() -> str:
    """Custom styling and configuration example"""
    return """Create a professional-looking bar chart with:
- Data: ['Product A', 'Product B', 'Product C'] with values [45, 67, 23]
- Enable banner mode with title 'Sales Report' and subtitle 'Q3 2024'
- Use a custom color scheme
- Set appropriate plot dimensions"""


@prompt("theme_exploration")
async def theme_exploration_prompt() -> str:
    """Theme exploration example"""
    return "Show me all available themes, then create the same scatter plot [1,2,3,4] vs [10,20,15,25] using three different themes for comparison."


@prompt("banner_mode_demo")
async def banner_mode_demo_prompt() -> str:
    """Banner mode demonstration example"""
    return "Enable banner mode with title 'Data Analysis Dashboard' and create a line plot showing trend data: months=['Jan','Feb','Mar','Apr','May'] and growth=[100,110,125,140,160]."


@prompt("terminal_width_optimization")
async def terminal_width_optimization_prompt() -> str:
    """Terminal and environment info example"""
    return "What's my current terminal width? Then create a plot that optimally uses the full width for displaying time series data."


@prompt("colorized_output")
async def colorized_output_prompt() -> str:
    """Colorized output example"""
    return "Use the colorize function to create colored status messages, then generate a plot showing system performance metrics."


@prompt("regional_sales_analysis")
async def regional_sales_analysis_prompt() -> str:
    """Data analysis workflow example"""
    return """I have sales data by region: East=[100,120,110], West=[80,95,105], North=[60,75,85], South=[90,100,115] over 3 quarters. 

Please:
1. Create individual plots for each region
2. Show a comparative bar chart
3. Use appropriate themes and titles
4. Provide insights on the trends"""


@prompt("comparative_visualization")
async def comparative_visualization_prompt() -> str:
    """Comparative visualization example"""
    return """Compare two datasets using multiple visualization types:
- Dataset 1: [5,10,15,20,25]  
- Dataset 2: [3,8,18,22,28]
- Show both as scatter plot and line plot
- Use different colors and add meaningful titles"""


@prompt("error_handling_test")
async def error_handling_test_prompt() -> str:
    """Error handling example"""
    return """Try to create plots with various data scenarios and show how the system handles edge cases:
- Empty datasets
- Mismatched array lengths  
- Invalid color names
- Non-existent themes"""


@prompt("performance_testing")
async def performance_testing_prompt() -> str:
    """Performance testing example"""
    return """Generate and plot large datasets (100+ points) to test performance:
- Create random data arrays
- Time the plotting operations
- Show memory usage if possible
- Compare different plot types"""


@prompt("complete_workflow")
async def complete_workflow_prompt() -> str:
    """Complete workflow test example"""
    return """Execute a complete visualization workflow:
1. Check system configuration
2. List available themes
3. Set optimal plot size for terminal
4. Create multiple chart types with sample data
5. Apply different themes to each
6. Generate a summary report"""


# Main server entry point
def start_server():
    """Start the MCP server."""
    print("Starting Plotext Plus MCP Server...")
    run()


if __name__ == "__main__":
    start_server()