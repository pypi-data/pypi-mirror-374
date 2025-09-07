# Basic Plots

- [Introduction](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#introduction)
- [Scatter Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#scatter-plot)
- [Line Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#line-plot)
- [Log Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#log-plot)
- [Stem Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/basic.md#stem-plot)
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