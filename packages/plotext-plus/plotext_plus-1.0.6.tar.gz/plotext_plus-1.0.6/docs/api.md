# Plotext+ API Structure

## Overview

The Plotext+ library has a public API that makes it clear what functionality is available to users. All user-facing modules are organized without underscores, making the API structure intuitive and professional.

## New Module Structure

### 🎯 Core Modules (Public API)

1. **`plotext_plus.plotting`** - Main plotting functions
2. **`plotext_plus.charts`** - Modern chart classes  
3. **`plotext_plus.themes`** - Theme system
4. **`plotext_plus.utilities`** - Helper functions and utilities

### 📁 Internal Modules (Private)

All modules with `_` prefixes are internal implementation details and should not be used directly by users.

## Usage Examples

### Traditional Function-Based API

```python
import plotext_plus as plt

# All functions still available at the top level
plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.title("My Plot")
plt.xlabel("X Axis")
plt.ylabel("Y Axis")  
plt.theme('chuk_dark')
plt.show()
```

### Organized Module Access

```python
import plotext_plus as plt

# Access through organized modules
plt.plotting.scatter([1, 2, 3], [1, 4, 2])
plt.plotting.title("Scatter Plot")

# Apply themes
plt.themes.apply_theme('professional')

# Use utilities
width = plt.utilities.terminal_width()
plt.utilities.log_info("Terminal width: " + str(width))
```

### Modern Chart Classes

```python
import plotext_plus as plt

# Object-oriented chart creation
chart = plt.ScatterChart([1, 2, 3, 4], [1, 4, 2, 3])
chart.title("Modern Scatter Chart")
chart.show()

# Quick creation functions
plt.quick_scatter([1, 2, 3], [1, 4, 2], title="Quick Plot")
```

## Available Functions by Module

### plotext_plus.plotting

- **Basic plotting**: `scatter`, `plot`, `bar`, `matrix_plot`, `candlestick`
- **Plot customization**: `title`, `xlabel`, `ylabel`, `xlim`, `ylim`, `xscale`, `yscale`, `grid`, `frame`
- **Colors and themes**: `theme`, `colorize`
- **Layout and display**: `show`, `build`, `sleep`, `clear_figure`, `clear_data`, `clear_terminal`, `clear_color`
- **Figure management**: `plotsize`, `limitsize`, `subplots`, `subplot`
- **Utilities**: `save_fig`, `terminal_width`, `terminal_height`, `banner_mode`
- **Media handling**: `download_file`, `delete_file`, `image_plot`, `play_gif`, `play_video`

### plotext_plus.charts  

- **Base classes**: `Chart`, `Legend`, `PlotextAPI`, `api`
- **Chart types**: `ScatterChart`, `LineChart`, `BarChart`, `HistogramChart`, `CandlestickChart`, `HeatmapChart`, `MatrixChart`, `StemChart`
- **Convenience functions**: `create_chart`, `quick_scatter`, `quick_line`, `quick_bar`
- **Utilities**: `enable_banners`, `log_info`, `log_success`, `log_warning`, `log_error`

### plotext_plus.themes

- **Theme management**: `get_theme_info`, `apply_theme`, `apply_chuk_theme_to_chart`
- **Banner themes**: `get_chuk_theme_for_banner_mode`
- **Theme creation**: `create_chuk_term_themes`

### plotext_plus.utilities

- **Terminal utilities**: `terminal_width`, `colorize`, `no_color`
- **Matrix utilities**: `matrix_size`
- **File utilities**: `delete_file`, `download`
- **Test data URLs**: `test_data_url`, `test_bar_data_url`, `test_image_url`, `test_gif_url`, `test_video_url`
- **Logging utilities**: `log_info`, `log_success`, `log_warning`, `log_error`

## Migration Guide

### For Existing Users

All existing code continues to work! The API is additive - all functions are still available at the top level:

```python
# This still works exactly as before
import plotext_plus as plt
plt.plot([1, 2, 3], [1, 4, 2])
plt.show()
```

### For New Users

New users can take advantage of the organized structure:

```python
# More organized approach
import plotext_plus as plt

# Use specific modules for clarity
plt.plotting.scatter(x, y)
plt.themes.apply_theme('professional')
plt.utilities.log_info("Plot created successfully")
```

## Benefits

1. **🔍 Clear API Surface** - Easy to understand what's public vs private
2. **📚 Organized Functionality** - Related functions grouped together
3. **🔄 Backward Compatible** - All existing code continues to work  
4. **🎯 Better Discoverability** - Logical grouping makes finding functions easier
5. **📖 Self-Documenting** - Module names indicate their purpose

## File Structure

```bash
src/plotext_plus/
├── __init__.py          # Main entry point
├── plotting.py          # Main plotting functions (PUBLIC)
├── charts.py            # Chart classes (PUBLIC)
├── themes.py            # Theme system (PUBLIC)
├── utilities.py         # Helper utilities (PUBLIC)
├── _core.py            # Core implementation (PRIVATE)
├── _api.py             # Internal API (PRIVATE)
├── _themes.py          # Theme internals (PRIVATE)
├── _utility.py         # Internal utilities (PRIVATE)
└── ...                 # Other internal modules (PRIVATE)
```
