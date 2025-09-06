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


@tool
async def image_plot(image_path: str, title: Optional[str] = None, 
                    marker: Optional[str] = None, style: Optional[str] = None, 
                    fast: bool = False, grayscale: bool = False) -> str:
    """Display an image in the terminal using ASCII art.
    
    Args:
        image_path: Path to the image file to display
        title: Plot title (optional)
        marker: Custom marker for image rendering (optional)
        style: Style for image rendering (optional)
        fast: Enable fast rendering mode for better performance (optional)
        grayscale: Render image in grayscale (optional)
        
    Returns:
        The rendered image plot as text
    """
    plotting.clear_figure()
    if title:
        plotting.title(title)
    
    _, output = _capture_plot_output(plotting.image_plot, image_path, 
                                   marker=marker, style=style, 
                                   fast=fast, grayscale=grayscale)
    _, show_output = _capture_plot_output(plotting.show)
    
    return output + show_output


@tool
async def play_gif(gif_path: str) -> str:
    """Play a GIF animation in the terminal.
    
    Args:
        gif_path: Path to the GIF file to play
        
    Returns:
        Confirmation message (GIF plays automatically)
    """
    plotting.clear_figure()
    
    # play_gif handles its own output and doesn't need show()
    plotting.play_gif(gif_path)
    
    return f"Playing GIF: {gif_path}"


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


@tool
async def quick_pie(labels: List[str], values: List[Union[int, float]], 
                   colors: Optional[List[str]] = None, title: Optional[str] = None, 
                   show_values: bool = True, show_percentages: bool = True,
                   show_values_on_slices: bool = False, donut: bool = False,
                   remaining_color: Optional[str] = None) -> str:
    """Create a quick pie chart using the chart classes API.
    
    Args:
        labels: List of pie segment labels
        values: List of pie segment values
        colors: List of colors for segments (optional)
        title: Chart title (optional)
        show_values: Show values in legend (optional, default True)
        show_percentages: Show percentages in legend (optional, default True)
        show_values_on_slices: Show values directly on pie slices (optional, default False)
        donut: Create doughnut chart with hollow center (optional, default False)
        remaining_color: Color for remaining slice in single-value charts (optional)
        
    Returns:
        The rendered pie chart as text
    """
    _, output = _capture_plot_output(charts.quick_pie, labels, values, colors=colors, 
                                   title=title, show_values=show_values, 
                                   show_percentages=show_percentages,
                                   show_values_on_slices=show_values_on_slices,
                                   donut=donut, remaining_color=remaining_color)
    return output


@tool
async def quick_donut(labels: List[str], values: List[Union[int, float]], 
                     colors: Optional[List[str]] = None, title: Optional[str] = None, 
                     show_values: bool = True, show_percentages: bool = True,
                     show_values_on_slices: bool = False,
                     remaining_color: Optional[str] = None) -> str:
    """Create a quick doughnut chart (pie chart with hollow center) using the chart classes API.
    
    Args:
        labels: List of pie segment labels
        values: List of pie segment values
        colors: List of colors for segments (optional)
        title: Chart title (optional)
        show_values: Show values in legend (optional, default True)
        show_percentages: Show percentages in legend (optional, default True)
        show_values_on_slices: Show values directly on pie slices (optional, default False)
        remaining_color: Color for remaining slice in single-value charts (optional)
        
    Returns:
        The rendered doughnut chart as text
    """
    _, output = _capture_plot_output(charts.quick_donut, labels, values, colors=colors, 
                                   title=title, show_values=show_values, 
                                   show_percentages=show_percentages,
                                   show_values_on_slices=show_values_on_slices,
                                   remaining_color=remaining_color)
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


# Resource for tool documentation/info
@resource("info://plotext")
async def get_tool_info() -> Dict[str, Any]:
    """Get comprehensive information about all available plotting tools."""
    return {
        "server_info": {
            "name": "Plotext Plus MCP Server",
            "description": "Model Context Protocol server for plotext_plus terminal plotting library",
            "version": "1.0.0",
            "capabilities": ["plotting", "theming", "multimedia", "charts"]
        },
        "plotting_tools": {
            "scatter_plot": "Create scatter plots with x/y data points",
            "line_plot": "Create line plots for time series and continuous data", 
            "bar_chart": "Create bar charts for categorical data",
            "matrix_plot": "Create heatmaps from 2D matrix data",
            "image_plot": "Display images in terminal using ASCII art",
            "play_gif": "Play animated GIFs in the terminal"
        },
        "quick_chart_tools": {
            "quick_scatter": "Quickly create scatter charts with theming",
            "quick_line": "Quickly create line charts with theming",
            "quick_bar": "Quickly create bar charts with theming", 
            "quick_pie": "Quickly create pie charts with custom colors, donut mode, and remaining_color options",
            "quick_donut": "Quickly create doughnut charts (hollow center pie charts)"
        },
        "theme_tools": {
            "get_available_themes": "List all available color themes",
            "apply_plot_theme": "Apply a theme to plots"
        },
        "utility_tools": {
            "get_terminal_width": "Get current terminal width",
            "colorize_text": "Apply colors to text output",
            "log_info": "Output informational messages",
            "log_success": "Output success messages", 
            "log_warning": "Output warning messages",
            "log_error": "Output error messages"
        },
        "configuration_tools": {
            "set_plot_size": "Set plot dimensions",
            "enable_banner_mode": "Enable/disable banner mode",
            "clear_plot": "Clear current plot"
        },
        "supported_formats": {
            "image_formats": ["PNG", "JPG", "JPEG", "BMP", "GIF (static)"],
            "gif_formats": ["GIF (animated)"],
            "chart_types": ["scatter", "line", "bar", "pie", "doughnut", "matrix/heatmap", "image"],
            "themes": "20+ built-in themes including solarized, dracula, cyberpunk"
        },
        "usage_tips": {
            "pie_charts": "Best for 3-7 categories, use full terminal dimensions",
            "doughnut_charts": "Modern alternative to pie charts with hollow center, great for progress indicators",
            "single_value_charts": "Perfect for progress/completion rates: ['Complete', 'Remaining'] with 'default' color",
            "images": "Use fast=True for better performance with large images",
            "themes": "Apply themes before creating plots for consistent styling",
            "banners": "Enable banner mode for professional-looking outputs"
        }
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


@prompt("image_display")
async def image_display_prompt() -> str:
    """Image plotting example"""
    return """Display an image in the terminal:
1. First download the test cat image using utilities.download() with the test_image_url
2. Display it using image_plot with title 'Test Image Display'
3. Try both normal and grayscale versions
4. Clean up by deleting the file afterward"""


@prompt("gif_animation")
async def gif_animation_prompt() -> str:
    """GIF animation example"""
    return """Play a GIF animation in terminal:
1. Download the test Homer Simpson GIF using utilities.download() with test_gif_url
2. Play the GIF animation using play_gif
3. Clean up the file afterward
Note: The GIF will play automatically in the terminal"""


@prompt("image_styling")
async def image_styling_prompt() -> str:
    """Custom image styling example"""
    return """Experiment with image rendering styles:
1. Display the same image with different markers (try 'CuteCat' as marker)
2. Use 'inverted' style for visual effects
3. Compare fast vs normal rendering modes
4. Show both color and grayscale versions"""


@prompt("multimedia_showcase")
async def multimedia_showcase_prompt() -> str:
    """Complete multimedia demonstration"""
    return """Showcase multimedia capabilities:
1. Download and display a static image with custom styling
2. Download and play an animated GIF
3. Set appropriate plot sizes for optimal viewing
4. Add descriptive titles to each display
5. Clean up all downloaded files"""


@prompt("basic_pie_chart")
async def basic_pie_chart_prompt() -> str:
    """Basic pie chart example"""
    return """Create a simple pie chart showing market share data:
- Categories: ['iOS', 'Android', 'Windows', 'Other']  
- Values: [35, 45, 15, 5]
- Use colors: ['blue', 'green', 'orange', 'gray']
- Add title 'Mobile OS Market Share'
- Use quick_pie tool for fast creation"""


@prompt("pie_chart_styling")
async def pie_chart_styling_prompt() -> str:
    """Advanced pie chart styling example"""
    return """Create a styled pie chart with advanced features:
1. Use quick_pie with show_values_on_slices=True
2. Data: Budget categories ['Housing', 'Food', 'Transport', 'Entertainment'] 
3. Values: [1200, 400, 300, 200] (monthly budget)
4. Custom colors for each category
5. Add meaningful title and ensure full terminal usage"""


@prompt("pie_chart_comparison")
async def pie_chart_comparison_prompt() -> str:
    """Pie chart comparison example"""
    return """Create multiple pie charts for comparison:
1. Q1 Sales: ['Product A', 'Product B', 'Product C'] = [30, 45, 25]
2. Q2 Sales: ['Product A', 'Product B', 'Product C'] = [25, 50, 25] 
3. Show both charts with different colors
4. Use appropriate titles ('Q1 Sales Distribution', 'Q2 Sales Distribution')
5. Discuss the trends visible in the comparison"""


@prompt("pie_chart_best_practices")
async def pie_chart_best_practices_prompt() -> str:
    """Pie chart best practices demonstration"""
    return """Demonstrate pie chart best practices:
1. Start with many categories: ['A', 'B', 'C', 'D', 'E', 'F', 'G'] = [5, 8, 12, 15, 25, 20, 15]
2. Show why this is problematic (too many small segments)
3. Combine small categories: ['A+B+C', 'D', 'E', 'F', 'G'] = [25, 15, 25, 20, 15] 
4. Create the improved version with title 'Improved: Combined Small Categories'
5. Explain the improvement in readability"""


@prompt("single_value_pie_chart")
async def single_value_pie_chart_prompt() -> str:
    """Single-value pie chart for progress indicators"""
    return """Create single-value pie charts perfect for progress indicators:
1. Basic progress chart: ['Complete', 'Remaining'] = [75, 25], colors=['green', 'default']
2. Title: 'Project Progress: 75%'  
3. Show only percentages (show_values=False, show_percentages=True)
4. Note: Remaining area appears as spaces, legend only shows 'Complete' entry
5. Perfect for dashboards, completion meters, utilization rates"""


@prompt("single_value_pie_with_remaining_color")
async def single_value_pie_with_remaining_color_prompt() -> str:
    """Single-value pie chart with colored remaining area"""
    return """Create single-value pie chart with remaining_color parameter:
1. Data: ['Complete', 'Remaining'] = [60, 40], colors=['blue', 'default']
2. Add remaining_color='gray' to color the remaining slice
3. Title: 'Task Completion: 60%'
4. Compare with version without remaining_color
5. Note: When remaining_color is specified, 'Remaining' appears in legend"""


@prompt("doughnut_chart_basic")
async def doughnut_chart_basic_prompt() -> str:
    """Basic doughnut chart with hollow center"""
    return """Create a doughnut chart with hollow center:
1. Data: ['Sales', 'Marketing', 'Support', 'Development'] = [40, 25, 15, 20]
2. Colors: ['blue', 'orange', 'green', 'red']  
3. Add donut=True parameter to create hollow center
4. Title: 'Department Budget - Doughnut Chart'
5. Note: Inner radius automatically set to 1/3 of outer radius, center remains empty"""


@prompt("doughnut_progress_indicator")
async def doughnut_progress_indicator_prompt() -> str:
    """Doughnut chart as progress indicator"""
    return """Create a doughnut chart progress indicator:
1. Single-value data: ['Completed', 'Remaining'] = [85, 15]
2. Colors: ['cyan', 'default'] 
3. Use both donut=True and show only percentages
4. Title: 'Project Progress - 85% Complete'
5. Perfect for modern dashboards - combines hollow center with progress visualization"""


@prompt("quick_donut_convenience")
async def quick_donut_convenience_prompt() -> str:
    """Using quick_donut convenience function"""
    return """Demonstrate the quick_donut convenience function:
1. Use quick_donut instead of quick_pie with donut=True
2. Data: ['Task A', 'Task B', 'Task C'] = [30, 45, 25]
3. Colors: ['purple', 'yellow', 'green']
4. Title: 'Task Distribution'
5. Show how quick_donut automatically creates hollow center charts"""


# Main server entry point
def start_server():
    """Start the MCP server."""
    print("Starting Plotext Plus MCP Server...")
    run()


if __name__ == "__main__":
    start_server()