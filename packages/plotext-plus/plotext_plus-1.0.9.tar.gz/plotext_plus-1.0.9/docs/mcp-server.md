# MCP Server - Model Context Protocol Integration

## Overview

The Plotext Plus MCP (Model Context Protocol) server provides standardized tool interfaces that allow AI clients like Claude to use all plotext_plus functionality directly. This enables AI systems to create terminal-based plots, charts, and visualizations programmatically.

## Features

- **Zero Configuration**: Built on chuk-mcp-server for automatic setup
- **Complete API Coverage**: All public plotext_plus functions exposed as MCP tools
- **Type-Safe**: Proper type hints and async support for all tools
- **Error Handling**: Graceful fallback when MCP dependencies unavailable
- **Resource Access**: Configuration and state information available via MCP resources

## Installation

### Requirements

- Python 3.11+ (required by chuk-mcp-server)
- plotext_plus with MCP optional dependencies

### Install Commands

```bash
# Install plotext_plus with MCP support
uv add plotext_plus[mcp]

# Or with pip
pip install plotext_plus[mcp]

# Install all optional features
uv add plotext_plus[image,video,mcp]

# Install as UV tool for easy access
uv tool install plotext_plus
```

## Usage

### Starting the Server

#### Method 1: Direct Installation (Recommended)

If you've installed plotext_plus as a UV tool or globally:

```bash
# Start the MCP server
plotext-mcp

# Get server information
plotext-mcp --info

# Show version
plotext-mcp --version
```

#### Method 2: Using uvx (Alternative)

If you encounter issues with direct installation, use UV tool installation:

```bash
# Install plotext_plus as a UV tool
uv tool install plotext_plus

# Then run the MCP server directly
plotext-mcp

# Or use UV run for one-time execution
uv run plotext-mcp --info
```

**Note**: The uvx command `uvx --from plotext_plus plotext-mcp` doesn't work correctly because uvx tries to run the main plotext script with plotext-mcp as an argument. Use the methods above instead.

### Server Information

The `--info` command displays:
```
Plotext Plus MCP Server
======================
Terminal plotting library with MCP (Model Context Protocol) support
Exposes plotting, charting, theming, and utility functions as MCP tools

Available tools:
- scatter_plot: Create scatter plots
- line_plot: Create line plots
- bar_chart: Create bar charts
- matrix_plot: Create matrix/heatmap plots
- image_plot: Display images as ASCII art
- play_gif: Play animated GIFs
- quick_scatter/line/bar/pie: Quick chart creation
- theme management tools
- utility functions

To start the server, run: plotext-mcp
```

## Available MCP Tools

### Core Plotting Tools

#### scatter_plot

```python
async def scatter_plot(
    x: List[Union[int, float]], 
    y: List[Union[int, float]], 
    marker: Optional[str] = None,
    color: Optional[str] = None,
    title: Optional[str] = None
) -> str
```

Creates a scatter plot and returns the rendered plot as text.

#### line_plot

```python
async def line_plot(
    x: List[Union[int, float]], 
    y: List[Union[int, float]], 
    color: Optional[str] = None,
    title: Optional[str] = None
) -> str
```

Creates a line plot and returns the rendered plot as text.

#### bar_chart

```python
async def bar_chart(
    labels: List[str], 
    values: List[Union[int, float]], 
    color: Optional[str] = None,
    title: Optional[str] = None
) -> str
```

Creates a bar chart and returns the rendered plot as text.

#### matrix_plot

```python
async def matrix_plot(
    data: List[List[Union[int, float]]], 
    title: Optional[str] = None
) -> str
```

Creates a matrix/heatmap plot from 2D data.

#### image_plot

```python
async def image_plot(
    image_path: str, 
    title: Optional[str] = None, 
    marker: Optional[str] = None, 
    style: Optional[str] = None, 
    fast: bool = False, 
    grayscale: bool = False
) -> str
```

Display an image in the terminal using ASCII art. Supports various image formats and styling options.

#### play_gif

```python
async def play_gif(gif_path: str) -> str
```

Play a GIF animation in the terminal. The animation runs automatically without requiring additional show() calls.

### Chart Class Tools

#### quick_scatter

```python
async def quick_scatter(
    x: List[Union[int, float]], 
    y: List[Union[int, float]], 
    title: Optional[str] = None,
    theme_name: Optional[str] = None
) -> str
```

Creates a quick scatter chart using the chart classes API.

#### quick_line

```python
async def quick_line(
    x: List[Union[int, float]], 
    y: List[Union[int, float]], 
    title: Optional[str] = None,
    theme_name: Optional[str] = None
) -> str
```

Creates a quick line chart using the chart classes API.

#### quick_bar

```python
async def quick_bar(
    labels: List[str], 
    values: List[Union[int, float]], 
    title: Optional[str] = None,
    theme_name: Optional[str] = None
) -> str
```

Creates a quick bar chart using the chart classes API.

#### quick_pie

```python
async def quick_pie(
    labels: List[str], 
    values: List[Union[int, float]], 
    colors: Optional[List[str]] = None, 
    title: Optional[str] = None, 
    show_values: bool = True, 
    show_percentages: bool = True,
    show_values_on_slices: bool = False
) -> str
```

Creates a quick pie chart using the chart classes API. Best for small numbers of categories (3-7).

### Theme Tools

#### get_available_themes

```python
async def get_available_themes() -> Dict[str, Any]
```

Returns information about all available themes.

#### apply_plot_theme

```python
async def apply_plot_theme(theme_name: str) -> str
```

Applies a theme to the current plot context.

### Utility Tools

#### get_terminal_width

```python
async def get_terminal_width() -> int
```

Returns the current terminal width in characters.

#### colorize_text

```python
async def colorize_text(text: str, color: str) -> str
```

Applies color formatting to text using plotext_plus color system.

#### Logging Tools

```python
async def log_info(message: str) -> str
async def log_success(message: str) -> str
async def log_warning(message: str) -> str
async def log_error(message: str) -> str
```

Logging functions that format and display messages with appropriate styling.

### Plot Management Tools

#### set_plot_size

```python
async def set_plot_size(width: int, height: int) -> str
```

Sets the plot dimensions for subsequent plots.

#### enable_banner_mode

```python
async def enable_banner_mode(
    enabled: bool = True,
    title: Optional[str] = None,
    subtitle: Optional[str] = None
) -> str
```

Enables or disables banner mode with optional title and subtitle.

#### clear_plot

```python
async def clear_plot() -> str
```

Clears the current plot context.


## MCP Prompts

The plotext_plus MCP server provides ready-to-use prompts via the MCP prompt API. These prompts are directly accessible by MCP clients and provide comprehensive examples for various plotting scenarios.

### Available Prompts

#### Basic Plotting Prompts

- **basic_scatter**: Simple scatter plot example
- **basic_bar_chart**: Bar chart with sample data  
- **line_plot_with_theme**: Line plot with theme application
- **basic_pie_chart**: Simple pie chart example with market share data

#### Advanced Plotting Prompts

- **matrix_heatmap**: Correlation matrix visualization
- **multi_step_workflow**: Complex multi-step analysis workflow
- **professional_bar_chart**: Styled bar chart with banner mode
- **pie_chart_styling**: Advanced pie chart with values on slices
- **pie_chart_comparison**: Multiple pie charts for quarterly comparison
- **pie_chart_best_practices**: Educational example for data grouping
- **image_display**: Basic image plotting workflow
- **gif_animation**: GIF playback example
- **image_styling**: Advanced image rendering with custom markers
- **multimedia_showcase**: Complete multimedia demonstration

#### Theme and Styling Prompts

- **theme_exploration**: Compare multiple themes on same data
- **banner_mode_demo**: Banner mode demonstration with dashboard styling

#### Utility Function Prompts

- **terminal_width_optimization**: Terminal-aware plot sizing
- **colorized_output**: Color formatting and system metrics

#### Interactive Analysis Prompts

- **regional_sales_analysis**: Multi-dataset regional comparison
- **comparative_visualization**: Side-by-side data comparison

#### Testing and Workflow Prompts

- **error_handling_test**: Edge case and error handling testing
- **performance_testing**: Large dataset performance evaluation
- **complete_workflow**: End-to-end visualization pipeline

## MCP Resources

### config://plotext

The server provides a configuration resource at `config://plotext` containing:

```python
{
    "terminal_width": int,           # Current terminal width
    "available_themes": dict,        # Theme information
    "library_version": "plotext_plus",
    "mcp_enabled": True
}
```

### info://plotext

The server also provides comprehensive tool information at `info://plotext` containing:

```python
{
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
        "quick_pie": "Quickly create pie charts with custom colors and options"
    },
    "usage_tips": {
        "pie_charts": "Best for 3-7 categories, use full terminal dimensions",
        "images": "Use fast=True for better performance with large images"
    }
}
```

## Implementation Details

### Architecture

- Built on `chuk-mcp-server` for zero-configuration MCP functionality
- Uses async/await pattern for all tool functions
- Captures plot output using stdout redirection
- Maintains plot state between tool calls when needed

### Error Handling

- Graceful import fallback when chuk-mcp-server not available
- Clear error messages for missing dependencies
- Type validation for all tool parameters

### Performance

- High-performance server (chuk-mcp-server provides 39,651+ RPS)
- Async native capabilities for concurrent requests
- Efficient plot output capture and return

## Testing

### Manual Testing

```bash
# Test basic import
python -c "from plotext_plus.mcp_server import start_server; print('✓ MCP ready')"

# Test CLI functionality
plotext-mcp --info

# Test individual tool execution
python -c "
import asyncio
from plotext_plus.mcp_server import scatter_plot

async def test():
    result = await scatter_plot([1,2,3], [1,4,9], title='Test Plot')
    print(f'✓ Plot generated: {len(result)} characters')

asyncio.run(test())
"
```

### Integration Testing

```python
import asyncio
from plotext_plus.mcp_server import (
    scatter_plot, get_available_themes, 
    set_plot_size, apply_plot_theme
)

async def integration_test():
    # Test theme system
    themes = await get_available_themes()
    print(f"Available themes: {type(themes)}")
    
    # Test plot configuration
    await set_plot_size(80, 24)
    await apply_plot_theme("dark")
    
    # Test plotting
    result = await scatter_plot([1,2,3,4], [1,4,9,16], 
                               title="Integration Test", 
                               color="red")
    print(f"Generated plot: {len(result)} chars")

asyncio.run(integration_test())
```

## Development Notes

### Adding New Tools

To add new MCP tools:

1. Add the function to `mcp_server.py` with `@tool` decorator
2. Ensure proper type hints and docstrings
3. Handle async execution appropriately
4. Test with manual verification

### Debugging

- Use `plotext-mcp --info` to verify server setup
- Check import errors for missing dependencies
- Test individual tools with async execution
- Monitor stdout capture for plot output issues

## Troubleshooting

### Common Issues

**ImportError for chuk-mcp-server**

```bash
# Solution: Install MCP dependencies
uv add plotext_plus[mcp]
```

**Python version incompatibility**

```bash
# chuk-mcp-server requires Python 3.11+
python --version  # Check your Python version
```

**Plot output not captured**

- Ensure `_capture_plot_output` function is working
- Check that `show()` is called in plotting tools
- Verify stdout redirection is functioning

### Support

For MCP-specific issues:

1. Check plotext_plus public API compatibility
2. Verify chuk-mcp-server documentation
3. Test with minimal reproduction case
4. Report issues with detailed error messages

## Configuration

### [mcp-cli](https://github.com/chrishayuk/mcp-cli) Configuration

To use the plotext_plus MCP server with mcp-cli--an awesome terminal-based MCP host application, add this configuration to your `server_config.json`:

```json
{
  "mcpServers": {
    "plotext-plus": {
      "command": "plotext-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

### Alternative Configuration Using UV

If you prefer to use UV directly:

```json
{
  "mcpServers": {
    "plotext-plus": {
      "command": "uv",
      "args": ["run", "plotext-mcp"],
      "env": {}
    }
  }
}
```

## Using plotext_plus with mcp-cli for Charting

The plotext_plus MCP server provides seamless integration with mcp-cli, enabling powerful terminal-based data visualization workflows. Here's how to set up and use it effectively:

### Quick Setup Guide

1. **Install plotext_plus with MCP support**:
   ```bash
   pip install plotext_plus[mcp]
   # or with uv
   uv add plotext_plus[mcp]
   ```

2. **Create MCP server configuration**:
   Create a `plotext_config.json` file:
   ```json
   {
     "mcpServers": {
       "plotext-plus": {
         "command": "uv",
         "args": ["run", "plotext-mcp"],
         "cwd": "/path/to/your/project",
         "env": {}
       }
     }
   }
   ```

3. **Start mcp-cli with plotext_plus**:
   ```bash
   cd /path/to/mcp-cli
   uv run python -m mcp_cli --config-file /path/to/plotext_config.json chat
   ```

### Exploring Available Features

Before creating charts, explore what's available:

#### List Available Tools

```bash
uv run python -m mcp_cli --config-file plotext_config.json tools
```

This shows all plotting tools like `scatter_plot`, `line_plot`, `bar_chart`, etc.

#### Browse Available Prompts

```bash
uv run python -m mcp_cli --config-file plotext_config.json prompts
```

This displays ready-to-use example prompts for common charting scenarios.

#### Check Server Status

```bash
uv run python -m mcp_cli --config-file plotext_config.json servers
```

Verify the plotext-plus server is connected and ready.

### Creating Charts with mcp-cli

Once connected, you can create charts using natural language prompts or by directly using MCP prompts:

#### Method 1: Natural Language (Recommended)

Start a chat session and describe what you want:

```text
> Create a scatter plot showing the relationship between x=[1,2,3,4,5] and y=[1,4,9,16,25] with title "Quadratic Function"
```

```text
> Make a bar chart with categories ["Q1","Q2","Q3","Q4"] and values [120,150,180,200] titled "Quarterly Sales"
```

```text
> Plot a line chart of temperature data: x=[1,2,3,4,5,6,7] and y=[20,22,25,28,26,24,21] using dark theme
```

#### Method 2: Using MCP Prompts

Use the built-in prompts directly in your chat:

```text
> Use the "basic_scatter" prompt
```

```text
> Apply the "multi_step_workflow" prompt for complex analysis
```

```text
> Run the "theme_exploration" prompt to compare different visual styles
```

### Advanced Charting Workflows

#### Multi-Step Data Analysis

```text
> I have sales data by region: East=[100,120,110], West=[80,95,105], North=[60,75,85], South=[90,100,115] over 3 quarters.

Please:
1. Create individual plots for each region
2. Show a comparative bar chart  
3. Use appropriate themes and titles
4. Provide insights on the trends
```

#### Theme and Styling Exploration

```text
> Show me all available themes, then create the same scatter plot using three different themes for comparison
```

#### Performance Testing

```text
> Generate large datasets (100+ points) and test plotting performance with different chart types
```

### Configuration Tips for Optimal Experience

#### For Development Environments

```json
{
  "mcpServers": {
    "plotext-plus-dev": {
      "command": "uv",
      "args": ["run", "plotext-mcp"],
      "cwd": "/path/to/plotext_plus/development",
      "env": {
        "PYTHONPATH": "/path/to/plotext_plus/src"
      }
    }
  }
}
```

#### For Production Use

```json
{
  "mcpServers": {
    "plotext-plus": {
      "command": "plotext-mcp",
      "args": ["--quiet"],
      "env": {
        "PLOTEXT_THEME": "professional",
        "PLOTEXT_BANNER_MODE": "true"
      }
    }
  }
}
```

#### For Specific Project Contexts

```json
{
  "mcpServers": {
    "project-charts": {
      "command": "uv",
      "args": ["run", "plotext-mcp"],
      "cwd": "/path/to/your/data/project",
      "env": {
        "DATA_PATH": "/path/to/data",
        "OUTPUT_PATH": "/path/to/outputs"
      }
    }
  }
}
```

### Common Use Cases and Examples

#### 1. Data Analysis Dashboard

Start with banner mode and create multiple visualizations:

```text
> Enable banner mode with title "Data Analysis Dashboard"
> Create a line plot showing trend data over time
> Add a bar chart for category comparisons
> Apply professional theme for presentation
```

#### 2. Statistical Visualization

```text
> Create a heatmap from correlation matrix: [[1.0,0.8,0.3],[0.8,1.0,0.5],[0.3,0.5,1.0]]
> Add appropriate color scheme and title "Feature Correlation"
```

#### 3. Performance Monitoring

```text
> Plot system metrics over time with multiple data series
> Use different colors for CPU, memory, and disk usage
> Enable real-time update capability
```

#### 4. Report Generation

```text
> Create professional charts for quarterly business review
> Include revenue trends, growth metrics, and regional performance
> Export charts with consistent branding and themes
```

### Troubleshooting Common Issues

#### Server Connection Issues

If plotext-plus server doesn't appear in `servers` list:

1. **Check Configuration**: Verify `plotext_config.json` syntax
2. **Test Command**: Run `plotext-mcp --info` manually
3. **Check Dependencies**: Ensure `plotext_plus[mcp]` is installed
4. **Verify Path**: Check that `cwd` points to correct directory

#### Chart Rendering Issues

If charts don't display properly:

1. **Check Terminal Size**: Use `get_terminal_width` tool
2. **Adjust Plot Size**: Use `set_plot_size` before plotting  
3. **Theme Compatibility**: Try different themes for your terminal
4. **Clear Plot**: Use `clear_plot` between visualizations

#### Performance Optimization

For large datasets:

1. **Use Appropriate Chart Types**: Bar charts for categories, scatter for correlations
2. **Limit Data Points**: Sample large datasets before plotting
3. **Theme Selection**: Choose themes optimized for your data type
4. **Memory Management**: Clear plots between operations

### Integration Examples

#### With Data Processing Pipelines

```bash
# Process data and visualize results
cat data.csv | python process.py | mcp-cli --config plotext_config.json cmd "create bar chart from stdin"
```

#### With CI/CD Workflows

```yaml
# GitHub Actions example
- name: Generate Performance Charts
  run: |
    mcp-cli --config plotext_config.json cmd "plot performance metrics from test results"
```

#### With Jupyter Integration

```python
# In Jupyter notebook
from plotext_plus.mcp_server import scatter_plot
import asyncio

result = await scatter_plot(x_data, y_data, title="Analysis Results")
print(result)
```

This comprehensive integration makes plotext_plus a powerful tool for terminal-based data visualization workflows through mcp-cli.

### Advanced Configuration

For custom environments or specific setups:

```json
{
  "mcpServers": {
    "plotext-plus": {
      "command": "python",
      "args": ["-m", "plotext_plus.mcp_cli"],
      "env": {
        "PYTHONPATH": "/path/to/your/project"
      }
    }
  }
}
```

### Development Configuration

For development with local plotext_plus installation:

```json
{
  "mcpServers": {
    "plotext-plus-dev": {
      "command": "uv",
      "args": ["run", "plotext-mcp"],
      "cwd": "/path/to/plotext_plus",
      "env": {}
    }
  }
}
```

## Accessing MCP Prompts

The plotext_plus MCP server provides example prompts directly through the MCP prompt API. MCP clients can access these prompts natively without requiring additional tools or resources.

### How MCP Prompts Work

MCP prompts are pre-defined templates that clients can discover and use. Each prompt provides a complete example scenario that can be sent directly to the AI assistant.

### Using Prompts in MCP Clients

MCP clients typically provide a prompt picker or command palette where users can:

1. **Browse available prompts** by category and description
2. **Preview prompt content** before selection
3. **Apply prompts directly** to start conversations
4. **Customize prompts** as needed for specific use cases

### Prompt Categories

The prompts are organized into logical categories for easy discovery:

- **Basic Plotting**: Fundamental plot types and simple examples
- **Advanced Plotting**: Complex visualizations and multi-step workflows  
- **Theme and Styling**: Visual customization and banner mode examples
- **Utility Functions**: Terminal operations and helper functions
- **Interactive Analysis**: Multi-dataset analysis and comparative workflows
- **Testing and Validation**: Error handling, performance, and edge cases

## Example Prompts for AI Clients

### Basic Plotting Examples

**Create a Simple Scatter Plot**

```text
Create a scatter plot showing the relationship between x=[1,2,3,4,5] and y=[1,4,9,16,25] with the title "Quadratic Function".
```

**Generate a Bar Chart**

```text
Make a bar chart showing sales data: categories=["Q1","Q2","Q3","Q4"] and values=[120,150,180,200] with title "Quarterly Sales".
```

**Create a Line Plot with Theme**

```text
Plot a line chart of temperature data over time: x=[1,2,3,4,5,6,7] and y=[20,22,25,28,26,24,21] using the "dark" theme with title "Weekly Temperature".
```

**Create a Simple Pie Chart**

```text
Create a pie chart showing mobile OS market share: categories=['iOS', 'Android', 'Windows', 'Other'], values=[35, 45, 15, 5], colors=['blue', 'green', 'orange', 'gray'] with title 'Mobile OS Market Share'.
```

### Advanced Plotting Examples

**Matrix Heatmap Visualization**

```text
Create a heatmap from this 3x3 correlation matrix: [[1.0,0.8,0.3],[0.8,1.0,0.5],[0.3,0.5,1.0]] with title "Feature Correlation".
```

**Multi-step Visualization Workflow**

```text
1. First, show me available themes
2. Set the plot size to 100x30
3. Apply the "elegant" theme
4. Create a scatter plot comparing dataset A=[1,3,5,7,9] vs B=[2,6,10,14,18]
5. Add title "Linear Relationship Analysis"
```

**Custom Styling and Configuration**

```text
Create a professional-looking bar chart with:
- Data: ["Product A", "Product B", "Product C"] with values [45, 67, 23]
- Enable banner mode with title "Sales Report" and subtitle "Q3 2024"
- Use a custom color scheme
- Set appropriate plot dimensions
```

**Pie Chart with Advanced Features**

```text
Create a budget pie chart with show_values_on_slices=True: categories=['Housing', 'Food', 'Transport', 'Entertainment'], values=[1200, 400, 300, 200], custom colors, and title 'Monthly Budget Breakdown'.
```

**Display Image as ASCII Art**

```text
Display an image in the terminal:
1. Download a test image using utilities.download()
2. Display it using image_plot with title 'ASCII Art Demo'
3. Try both normal and grayscale versions
4. Clean up the file afterward
```

**Play Animated GIF**

```text
Play a GIF animation in terminal:
1. Download a test GIF file
2. Play the animation using play_gif
3. Clean up the file afterward
Note: The GIF will play automatically
```

### Theme and Styling Examples

**Theme Exploration**

```text
Show me all available themes, then create the same scatter plot [1,2,3,4] vs [10,20,15,25] using three different themes for comparison.
```

**Banner Mode Demonstration**

```text
Enable banner mode with title "Data Analysis Dashboard" and create a line plot showing trend data: months=["Jan","Feb","Mar","Apr","May"] and growth=[100,110,125,140,160].
```

### Utility Function Examples

**Terminal and Environment Info**

```text
What's my current terminal width? Then create a plot that optimally uses the full width for displaying time series data.
```

**Colorized Output**

```text
Use the colorize function to create colored status messages, then generate a plot showing system performance metrics.
```

### Interactive Analysis Prompts

**Data Analysis Workflow**

```text
I have sales data by region: East=[100,120,110], West=[80,95,105], North=[60,75,85], South=[90,100,115] over 3 quarters. 

Please:
1. Create individual plots for each region
2. Show a comparative bar chart
3. Use appropriate themes and titles
4. Provide insights on the trends
```

**Comparative Visualization**

```text
Compare two datasets using multiple visualization types:
- Dataset 1: [5,10,15,20,25]  
- Dataset 2: [3,8,18,22,28]
- Show both as scatter plot and line plot
- Use different colors and add meaningful titles
```

### Error Handling Examples

**Handling Invalid Data**

```text
Try to create plots with various data scenarios and show how the system handles edge cases:
- Empty datasets
- Mismatched array lengths  
- Invalid color names
- Non-existent themes
```

### Performance Testing Prompts

**Large Dataset Visualization**

```text
Generate and plot large datasets (100+ points) to test performance:
- Create random data arrays
- Time the plotting operations
- Show memory usage if possible
- Compare different plot types
```

### Integration Testing Prompts

**Complete Workflow Test**

```text
Execute a complete visualization workflow:
1. Check system configuration
2. List available themes
3. Set optimal plot size for terminal
4. Create multiple chart types with sample data
5. Apply different themes to each
6. Generate a summary report
```

## Configuration Tips

### Performance Optimization

- Set appropriate plot sizes for your terminal
- Use themes optimized for your display
- Consider data size limitations for large datasets

### Display Compatibility  

- Test with different terminal types and sizes
- Verify color support in your environment
- Check banner mode compatibility

### Debugging Configuration

- Use `plotext-mcp --info` to verify setup
- Test individual tools before complex workflows
- Monitor resource usage for large operations

## Related Documentation

- [Clean API](clean-api.md) - Understanding the public API structure
- [Themes](themes.md) - Theme system documentation  
- [Charts](charts.md) - Object-oriented chart classes
- [Utilities](utilities.md) - Helper functions and utilities
- [Examples](../examples/) - Usage examples and demos