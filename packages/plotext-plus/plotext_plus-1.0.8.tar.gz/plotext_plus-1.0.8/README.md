# 📊 Plotext+ - Modern Terminal Plotting

[![PyPi](https://badge.fury.io/py/plotext_plus.svg)](https://badge.fury.io/py/plotext_plus)
[![Downloads](https://pepy.tech/badge/plotext_plus/month)](https://pepy.tech/project/plotext_plus)
[![GitHubIssues](https://img.shields.io/badge/issue_tracking-github-blue.svg)](https://github.com/ccmitchellusa/plotext_plus/issues)
[![GitTutorial](https://img.shields.io/badge/PR-Welcome-%23FF8300.svg?)](https://github.com/ccmitchellusa/plotext_plus/pulls)

![logo](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/refs/heads/main/data/logo.png)

**Plotext+ plots directly in your terminal** with stunning visuals, modern APIs, and professional styling.  Plotext+ is a redesigned version of the original [plotext](https://github.com/piccolomo/plotext) library by Savino Piccolomo. New features include an updated API with object oriented features, an MCP server to make the project easily usable with AI & LLM scenarios, new themes and integration with chuk-term to make sure it works in the awesome [mcp-cli](https://github.com/chrishayuk/mcp-cli) by Chris Hay.

## ✨ Key Features

🎯 **Multiple Plot Types**: [scatter](docs/basic.md#scatter-plot), [line](docs/basic.md#line-plot), [bar](docs/bar.md), [histogram](docs/bar.md#histogram-plot), [candlestick](docs/datetime.md#candlestick-plot), [heatmap](docs/special.md), [confusion matrix](docs/special.md#confusion-matrix), [pie](docs/basic.md#pie-plot), [doughnut](docs/basic.md#doughnut-charts) and more

🎨 **Rich Visuals**: [Banner mode](docs/chart_classes.md), [themes](docs/themes.md), [colored text](docs/utilities.md#colored-text), automatic terminal width detection

📊 **Advanced Features**: [Subplots](docs/subplots.md), [datetime plots](docs/datetime.md), [image/GIF display](docs/image.md), [video streaming](docs/video.md) (including YouTube)

🔧 **Modern APIs**: Clean public API, object-oriented charts, quick functions, 100% backward compatible

🤖 **AI Integration**: [MCP server](docs/mcp-server.md) for direct AI client access (Claude, etc.)

⚡ **Zero Dependencies**: No required dependencies (optional packages for multimedia and AI integration)

![subplots](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/refs/heads/main/data/subplots.png)

## 🚀 Quick Start

### Installation

```bash
# Modern Python package management
uv add plotext_plus

# Traditional installation
pip install plotext_plus

# With optional dependencies
pip install plotext_plus[image,video]      # Multimedia support
pip install plotext_plus[mcp]              # AI integration (MCP server)
pip install plotext_plus[image,video,mcp]  # All features
```

### Basic Usage

```python
import plotext_plus as plt

# Simple scatter plot
plt.scatter([1, 2, 3, 4], [1, 4, 9, 16])
plt.title("My First Plot")
plt.show()
```

### Enhanced Visual Styling ✨

```python
import plotext_plus as plt

# Enable beautiful banner mode
plt.banner_mode(True, "📊 Data Analysis Dashboard")

# Apply professional themes
plt.theme('professional')

# Create styled plot
plt.plot([1, 2, 3, 4], [1, 4, 2, 3], label="Data Series")
plt.title("Enhanced Line Plot")
plt.xlabel("Time")
plt.ylabel("Values")
plt.show()
```

### Modern Chart Classes 🎯

```python
import plotext_plus as plt

# Object-oriented chart creation with method chaining
chart = (plt.ScatterChart([1, 2, 3, 4], [1, 4, 9, 16])
         .title("Scientific Analysis")
         .xlabel("X Variable")
         .ylabel("Y Variable")
         .color('blue')
         .show())

# Quick one-liner plots
plt.quick_scatter(x_data, y_data, title="Quick Analysis")
```

### Public API 🔧

```python
import plotext_plus as plt

# Access organized functionality
plt.plotting.bar(categories, values)      # Main plotting functions
plt.themes.apply_theme('dark_mode')       # Theme management  
plt.utilities.log_success("Plot ready!")  # Helper utilities
```

### AI Integration 🤖

```bash
# Install with MCP (Model Context Protocol) support  
pip install plotext_plus[mcp]

# Start the MCP server for AI clients like Claude
plotext-mcp
```

**Use with Claude Desktop**: Add to your `claude_desktop_config.json`:

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

Now AI clients can create plots directly:

```text
"Create a scatter plot showing x=[1,2,3,4,5] vs y=[1,4,9,16,25] with title 'Quadratic Function'"
```

## 🏗️ Architecture & API

### Public API Structure

```python
# 🎯 Main Modules (Public API - no underscores)
plotext_plus.plotting    # Core plotting functions
plotext_plus.charts      # Object-oriented chart classes  
plotext_plus.themes      # Theme and styling system
plotext_plus.utilities   # Helper functions and tools

# 📁 Internal Modules (Private - with underscores)
plotext_plus._core       # Internal implementation
plotext_plus._api        # Internal API details
plotext_plus._themes     # Theme internals
# ... other internal modules
```

### Project Structure

```bash
plotext_plus/
├── src/plotext_plus/              # Modern src-layout
│   ├── plotting.py           # 🎯 Main plotting functions (PUBLIC)
│   ├── charts.py             # 🎯 Chart classes (PUBLIC)
│   ├── themes.py             # 🎯 Theme system (PUBLIC)
│   ├── utilities.py          # 🎯 Utilities (PUBLIC)
│   └── _*.py                 # 🔒 Internal modules (PRIVATE)
├── examples/                 # Interactive demos
│   ├── interactive_demo.py   # Full interactive showcase
│   └── theme_showcase_demo.py # Theme comparison tool
├── tests/                    # Test suites
├── docs/                     # Comprehensive documentation
└── pyproject.toml            # Modern packaging
```

## 🎨 Enhanced Features

### 🎭 Visual Enhancements

- **Professional Banners**: Automatic width detection and border styling
- **Advanced Theming**: Multiple built-in themes with chuk-term integration
- **Smart Layouts**: Charts automatically resize to fit terminal dimensions
- **Rich Colors**: 24-bit color support with automatic fallbacks

### 🚀 Developer Experience  

- **Clean API**: Public modules clearly separated from internals
- **Method Chaining**: Fluent interface for complex plot creation
- **Quick Functions**: One-liner plots for rapid prototyping
- **Type Safety**: Better IDE support and autocomplete
- **Zero Breaking Changes**: 100% backward compatibility guaranteed

## 🧪 Try It Now

```bash
# Install and run interactive demo
pip install plotext_plus
python -c "
import plotext_plus as plt
plt.banner_mode(True, '🎨 Plotext Plus Demo')
plt.scatter([1,2,3,4], [1,4,2,3], color='blue')
plt.title('Welcome to Plotext Plus!')
plt.show()
"

# Run comprehensive demos
git clone https://github.com/ccmitchellusa/plotext_plus.git
cd plotext_plus
python examples/interactive_demo.py      # Full interactive showcase  
python examples/theme_showcase_demo.py   # Theme comparison
```

## 📚 Complete Documentation

### 🎯 **Core Plotting**

- **[📊 Basic Plots](docs/basic.md)** - Scatter, line, and fundamental plotting
- **[📈 Bar Charts](docs/bar.md)** - Bar plots, histograms, and variations  
- **[📅 DateTime Plots](docs/datetime.md)** - Time series and candlestick charts
- **[🔬 Special Plots](docs/special.md)** - Heatmaps, confusion matrices, error bars
- **[🎨 Decorator Plots](docs/decorator.md)** - Text, lines, and shape overlays

### 🖼️ **Multimedia & Advanced**

- **[🖼️ Image Plotting](docs/image.md)** - Display images and GIFs in terminal
- **[🎬 Video Streaming](docs/video.md)** - Play videos and YouTube content
- **[📐 Subplots](docs/subplots.md)** - Multiple plots and complex layouts

### ⚙️ **Configuration & Styling**

- **[🎨 Themes](docs/themes.md)** - Built-in themes and customization
- **[⚙️ Settings](docs/settings.md)** - Plot configuration and options
- **[📏 Aspect](docs/aspect.md)** - Size, scaling, and layout control
- **[🔧 Chart Classes](docs/chart_classes.md)** - Object-oriented API reference

### 🛠️ **Tools & Integration**  

- **[🔧 Utilities](docs/utilities.md)** - Helper functions and command-line tools
- **[🤖 MCP Server](docs/mcp-server.md)** - AI integration via Model Context Protocol
- **[🌐 Environments](docs/environments.md)** - IDE and platform compatibility
- **[🏗️ API Structure](docs/api.md)** - Clean public API organization
- **[📝 Notes](docs/notes.md)** - Installation, tips, and troubleshooting

### 🚀 **Getting Started Guides**

1. **[👋 Introduction](docs/basic.md#introduction)** - First steps with Plotext
2. **[📦 Installation](docs/notes.md#install)** - Setup and dependencies  
3. **[🎯 Quick Examples](#-quick-start)** - Jump right in with code samples
4. **[🎨 Theming Guide](docs/themes.md)** - Make your plots beautiful
5. **[🔧 Modern API Guide](docs/api.md)** - Use the clean public interface

## 💡 Migration & Compatibility

**For Existing Users**: All your current code works unchanged! The new features are purely additive.

**For New Users**: Take advantage of the modern APIs and enhanced styling while learning the fundamentals.

```python
# ✅ Your existing code still works
import plotext_plus as plt
plt.plot([1,2,3], [1,4,2])
plt.show()

# 🆕 Enhanced with new features  
plt.banner_mode(True, "📊 My Analysis")
plt.theme('professional')
plt.plot([1,2,3], [1,4,2])
plt.show()
```
