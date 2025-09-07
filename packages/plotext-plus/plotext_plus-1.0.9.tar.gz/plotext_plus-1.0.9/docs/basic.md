# Basic Plots

- [Introduction](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#introduction)
- [Scatter Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#scatter-plot)
- [Line Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#line-plot)
- [Log Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#log-plot)
- [Stem Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#stem-plot)
- [Pie Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#pie-plot)
- [Multiple Data Sets](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#multiple-data-sets)
- [Multiple Axes Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#multiple-axes-plot)

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide)

## Introduction

Plotext+ provides multiple ways to create terminal-based visualizations. Choose the approach that fits your needs:

### Quick Start - Functional API

```python
import plotext_plus as plt
plt.scatter([1, 2, 3, 4], [1, 4, 2, 3])
plt.title("My First Plot")
plt.show()
```

### Modern Object-Oriented API

```python
import plotext_plus as plt

# Create specialized chart classes with method chaining
chart = plt.ScatterChart([1, 2, 3, 4], [1, 4, 2, 3], color='blue')
chart.title("Modern Chart").xlabel("X Data").ylabel("Y Data").show()
```

### Clean Public API Structure

```python
# Organized by functionality for clarity
from plotext_plus import plotting, charts, themes, utilities

plotting.scatter(x, y)     # Core plotting functions
chart = charts.LineChart(x, y)    # Object-oriented charts
themes.apply_theme('dracula')     # Theme system
utilities.terminal_width()        # Helper functions
```

**Key Features**:

- **Adaptive sizing** - Plot dimensions automatically adapt to terminal size, or use `plotsize()` for custom dimensions
- **Multiple plot types** - Scatter, line, bar, histogram, candlestick, heatmap, matrix, and more 
- **Subplots** - Create subplot matrices with `subplots()` and `subplot()`
- **High definition markers** - Including `"hd"`, `"fhd"`, and `"braille"` for crisp visuals
- **Rich theming** - Pre-built themes including chuk-term compatible schemes via `theme()`
- **Interactive mode** - Dynamic plotting without `show()` using `interactive(True)`
- **Chart classes** - Modern object-oriented interface with method chaining
- **File utilities** - Built-in data reading, downloading, and file management
- **Video/image support** - Stream videos, GIFs, and display images in terminal

**Common Patterns**:

```python
# Basic plotting (matplotlib-style)
plt.scatter(x, y, marker='braille', color='blue', label='Data')
plt.title("Analysis Results")
plt.show()

# Object-oriented approach
chart = plt.ScatterChart(x, y, color='blue', use_banners=True, banner_title="📊 Analysis")
chart.title("Modern Chart").theme('dracula').show()

# Theme-aware visualization  
plt.theme('scientific')
plt.plot(x, y)
plt.xlabel("Time").ylabel("Value").show()
```

**Getting Help**:

- Documentation: Use `plt.doc.scatter()` for colored docstrings
- Testing: Use `plt.test()` for quick installation verification  
- Issues: Report bugs at [GitHub Issues](https://github.com/ccmitchellusa/plotext_plus/issues/new) 

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Basic Plots](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#basic-plots)

## Scatter Plot

Here is a simple scatter plot:

```python
import plotext_plus as plt
y = plt.sin() # sinusoidal test signal
plt.scatter(y) 
plt.title("Scatter Plot") # to apply a title
plt.show() # to finally plot
```

or directly on terminal:

```console
python3 -c "import plotext_plus as plt; y = plt.sin(); plt.scatter(y); plt.title('Scatter Plot'); plt.show()"
```

![scatter](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/scatter.png)

More documentation can be accessed with `doc.scatter()`.

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Basic Plots](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#basic-plots)

## Line Plot

For a line plot use the `plot()` function instead:

```python
import plotext_plus as plt
y = plt.sin()
plt.plot(y)
plt.title("Line Plot")
plt.show()
```

or directly on terminal:

```console
python3 -c "import plotext_plus as plt; y = plt.sin(); plt.plot(y); plt.title('Line Plot'); plt.show()"
```

![plot](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/plot.png)

More documentation can be accessed with `doc.plot()`.

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Basic Plots](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#basic-plots)

## Log Plot

For a logarithmic plot use the the `xscale("log")` or `yscale("log")` methods:

- `xscale()` accepts the parameter `xside` to independently set the scale on each `x` axis , `"lower"` or `"upper"` (in short `1` or `2`).
- Analogously `yscale()` accepts the parameter `yside` to independently set the scale on each `y` axis , `"left"` or `"right"` (in short `1` or `2`).
- The log function used is `math.log10`.

Here is an example:

```python
import plotext_plus as plt

l = 10 ** 4
y = plt.sin(periods = 2, length = l)

plt.plot(y)

plt.xscale("log")    # for logarithmic x scale
plt.yscale("linear") # for linear y scale
plt.grid(0, 1)       # to add vertical grid lines

plt.title("Logarithmic Plot")
plt.xlabel("logarithmic scale")
plt.ylabel("linear scale")

plt.show()
```

or directly on terminal:

```console
python3 -c "import plotext_plus as plt; l = 10 ** 4; y = plt.sin(periods = 2, length = l); plt.plot(y); plt.xscale('log'); plt.yscale('linear'); plt.grid(0, 1); plt.title('Logarithmic Plot'); plt.xlabel('logarithmic scale'); plt.ylabel('linear scale'); plt.show();"
```

![example](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/log.png)

More documentation is available with `doc.xscale()` or `doc.yscale()` .

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Basic Plots](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#basic-plots)

## Stem Plot

For a [stem plot](https://matplotlib.org/stable/gallery/lines_bars_and_markers/stem_plot.html) use either the `fillx` or `filly` parameters (available for most plotting functions), in order to fill the canvas with data points till the `y = 0` or `x = 0` level, respectively.  

If a numerical value is passed to the `fillx` or `filly` parameters, it is intended as the `y` or `x` level respectively, where the filling should stop. If the string value `"internal"` is passed instead, the filling will stop when another data point is reached respectively vertically or horizontally (if it exists).

Here is an example:

```python
import plotext_plus as plt
y = plt.sin()
plt.plot(y, fillx = True)
plt.title("Stem Plot")
plt.show()
```

or directly on terminal:

```console
python3 -c "import plotext_plus as plt; y = plt.sin(); plt.plot(y, fillx = True); plt.title('Stem Plot'); plt.show()"
```

![stem](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/stem.png)
[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Basic Plots](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#basic-plots)

## Pie Plot

For a pie chart visualization use the `pie()` function. Pie charts are ideal for showing proportional data and work best with a small number of segments for better terminal readability.

![pie](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/pie-chart.png)

**Best Practices for Pie Charts**:

- Use full terminal dimensions for optimal resolution: `plt.plotsize(terminal_width, terminal_height - 5)`
- Limit to 4-6 data segments for clarity in terminal environment
- Each segment will be rendered with solid block characters and proper aspect ratio

Here is an example:

```python
import plotext_plus as plt

# Sample data
labels = ["Python", "JavaScript", "Go", "Rust"]
values = [45, 30, 15, 10]
colors = ["blue", "green", "orange", "red"]

# Create pie chart using full terminal dimensions
terminal_width, terminal_height = plt.terminal_size()
plt.clear_figure()
plt.plotsize(terminal_width, terminal_height - 5)

plt.pie(labels, values, colors=colors, title="Programming Languages Usage")
plt.show()
```

or directly on terminal:

```console
python3 -c "import plotext_plus as plt; labels = ['Python', 'JS', 'Go', 'Rust']; values = [45, 30, 15, 10]; w, h = plt.terminal_size(); plt.clear_figure(); plt.plotsize(w, h-5); plt.pie(labels, values, title='Languages'); plt.show()"
```

**Key Features**:

- **Colored block legend**: Each data label is prefixed with a colored block (█) matching the segment
- **Percentage display**: Shows both values and percentages in the legend
- **Dynamic sizing**: Radius automatically adjusts to terminal dimensions
- **Aspect ratio correction**: Ensures circular appearance across different plot sizes
- **Gap-free rendering**: Comprehensive scanning ensures solid segment filling

**Parameters**:

- `labels`: List of segment labels
- `values`: List of corresponding values (will be converted to percentages)
- `colors`: Optional list of colors for segments (defaults to standard palette)
- `radius`: Optional custom radius (defaults to optimal size for terminal)
- `show_values`: Show numeric values in legend (default: True)
- `show_percentages`: Show percentage values in legend (default: True)
- `show_values_on_slices`: Display values directly on pie segments (default: False)
- `title`: Chart title

### Single-Value Pie Charts

Single-value pie charts are perfect for progress indicators, completion rates, and other single-metric visualizations. They show a colored segment for the data value and handle the remainder specially.

![pie single-value](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/pie-single-value.png)

```python
import plotext_plus as plt

# Basic single-value pie chart (remainder as spaces)
plt.clear_figure()
plt.plotsize(50, 12)
plt.pie(["Progress", "Remaining"], [75, 25], colors=["green", "default"], 
       show_values=False, show_percentages=True,
       title="Project Progress: 75%")
plt.show()

# Single-value pie with colored remainder
plt.clear_figure()
plt.pie(["Complete", "Remaining"], [60, 40], colors=["blue", "default"], 
       remaining_color="gray",  # Colors the remaining slice
       show_values=False, show_percentages=True,
       title="Task Completion: 60%")
plt.show()
```

**Key Features**:

- **Smart legend filtering**: Only shows the data value, hides "Remaining" entry by default
- **Remaining area options**: 
  - Without `remaining_color`: Remaining area stays as blank spaces
  - With `remaining_color`: Remaining area gets colored and appears in legend
- **Perfect for dashboards**: Progress bars, completion meters, utilization rates

### Doughnut Charts

Doughnut charts are pie charts with a hollow center, providing a modern aesthetic and emphasizing the ring structure of the data. The inner radius is automatically set to 1/3 of the outer radius.

![doughnut](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/doughnut-chart.png)

![doughnut single-values](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/doughnut-single-value-comparison.png)

```python
import plotext_plus as plt

# Basic doughnut chart
labels = ["Sales", "Marketing", "Support", "Development"]
values = [40, 25, 15, 20]
colors = ["blue", "orange", "green", "red"]

plt.clear_figure()
plt.plotsize(60, 15)
plt.pie(labels, values, colors=colors, donut=True,
       show_values=False, show_percentages=True,
       title="Department Budget - Doughnut Chart")
plt.show()

# Single-value doughnut for progress indicator
plt.clear_figure()
plt.pie(["Completed", "Remaining"], [85, 15], colors=["cyan", "default"], 
       donut=True, show_values=False, show_percentages=True,
       title="Project Progress - 85% Complete")
plt.show()

# Quick doughnut using convenience function
plt.quick_donut(["Task A", "Task B", "Task C"], [30, 45, 25],
               colors=["purple", "yellow", "green"],
               title="Task Distribution")
```

**Key Features**:

- **Hollow center**: Inner circle remains completely empty (no block characters)
- **Modern appearance**: Ring structure emphasizes proportional relationships
- **All pie chart features**: Supports single-value, remaining_color, legends, etc.
- **Convenience function**: `plt.quick_donut()` for rapid creation
- **Perfect for**: Progress indicators, resource allocation, modern dashboards

**Additional Parameters for Pie and Doughnut Charts**:

- `donut`: Set to `True` for doughnut chart (hollow center)
- `remaining_color`: Color for remaining slice in single-value charts (optional)

More documentation can be accessed with `doc.pie()`.

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Basic Plots](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#basic-plots)

## Multiple Data Sets

Multiple data sets can be plotted using consecutive plotting functions. The `label` parameter, available in most plotting function, is used to add an entry in the **plot legend**, shown in the upper left corner of the plot canvas.

Here is an example:

```python
import plotext_plus as plt

y1 = plt.sin()
y2 = plt.sin(phase = -1)

plt.plot(y1, label = "plot")
plt.scatter(y2, label = "scatter")

plt.title("Multiple Data Set")
plt.show()
```

or directly on terminal:

```console
python3 -c "import plotext_plus as plt; y1 = plt.sin(); y2 = plt.sin(phase = -1); plt.plot(y1, label = 'plot'); plt.scatter(y2, label = 'scatter'); plt.title('Multiple Data Set'); plt.show()"
```

![multiple-data](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/multiple-data.png)

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Basic Plots](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#basic-plots)

## Multiple Axes Plot

Data could be plotted on the lower or upper `x` axis, as well as on the left or right `y` axis, using respectively the `xside` and `yside` parameters of most plotting functions. 

On the left side of each legend entry, a symbol is introduce to easily identify on which couple of axes the data has been plotted to: its interpretation should be intuitive.

Here is an example:

```python
import plotext_plus as plt

y1 = plt.sin()
y2 = plt.sin(2, phase = -1)

plt.plot(y1, xside = "lower", yside = "left", label = "lower left")
plt.plot(y2, xside = "upper", yside = "right", label = "upper right")

plt.title("Multiple Axes Plot")
plt.show()
```

or directly on terminal:

```console
python3 -c "import plotext_plus as plt; y1 = plt.sin(); y2 = plt.sin(2, phase = -1); plt.plot(y1, xside = 'lower', yside = 'left', label = 'lower left'); plt.plot(y2, xside = 'upper', yside = 'right', label = 'upper right'); plt.title('Multiple Axes Plot'); plt.show()"
```

![multiple-axes](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/multiple-axes.png)

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Basic Plots](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#basic-plots)