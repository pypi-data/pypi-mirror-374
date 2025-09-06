# Chart Classes

- [Overview](#overview)
- [ScatterChart](#scatterchart)
- [LineChart](#linechart)
- [BarChart](#barchart)
- [HistogramChart](#histogramchart)
- [CandlestickChart](#candlestickchart)
- [HeatmapChart](#heatmapchart)
- [MatrixChart](#matrixchart)
- [StemChart](#stemchart)
- [Chart Class Methods](#chart-class-methods)

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide)

## Overview

Plotext+ provides specialized chart classes that offer type-specific APIs for different data visualizations. These classes inherit from the base `Chart` class and provide enhanced functionality for specific chart types while maintaining the familiar method chaining interface.

### Key Benefits

- **Type-specific APIs** - Each chart class provides methods tailored to its visualization type
- **Method chaining** - Fluent programming interface for building charts
- **Banner support** - Built-in integration with chuk-term banner mode
- **Enhanced functionality** - Additional features beyond the core plotext_plus API
- **Easy to use** - Simplified creation of complex visualizations

### Basic Usage Pattern

```python
import plotext_plus as plt

# Create specialized chart with data
chart = plt.ScatterChart(x, y, color='blue', use_banners=True, banner_title="Analysis")
chart.title("My Analysis").xlabel("X Data").ylabel("Y Data").show()

# Or use method chaining
plt.LineChart(x, y).title("Trend").xlabel("Time").ylabel("Value").show()
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Chart Classes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/chart_classes.md#chart-classes)

## ScatterChart

Specialized class for creating scatter plots with trend analysis features.

### Constructor

```python
ScatterChart(x, y, marker=None, color=None, label=None, use_banners=False, banner_title=None)
```

### Enhanced Methods

- `add_trend_line(x, y, color='red', label='Trend')` - Add a trend line to the scatter plot
- `add_regression()` - Add linear regression line (future enhancement)

### Example

```python
import plotext_plus as plt

# Sample data with some correlation
x = list(range(20))
y = [2*i + random.uniform(-3, 3) for i in x]

# Create scatter plot with trend
chart = plt.ScatterChart(x, y, color='blue', label='Data Points',
                        use_banners=True, banner_title="📈 Correlation Analysis")

# Add theoretical trend line
trend_x = x
trend_y = [2*i for i in x]
chart.add_trend_line(trend_x, trend_y, color='red', label='Expected Trend')

chart.title("Experimental vs Theoretical Results")
chart.xlabel("Time (hours)")
chart.ylabel("Response Value")
chart.show()
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Chart Classes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/chart_classes.md#chart-classes)

## LineChart

Specialized class for creating line charts with enhanced time series features.

### Constructor

```python
LineChart(x, y, marker=None, color=None, label=None, use_banners=False, banner_title=None)
```

### Enhanced Methods

- `add_fill(fillx=False, filly=False)` - Add fill under the line (future enhancement)
- `smooth(window_size=3)` - Apply smoothing to the line (future enhancement)

### Example

```python
import plotext_plus as plt
import math

# Time series data
time = list(range(50))
signal = [10 + 5*math.sin(t/5) + random.uniform(-1, 1) for t in time]
smooth_signal = [10 + 5*math.sin(t/5) for t in time]

# Create line chart
chart = plt.LineChart(time, signal, color='green', label='Raw Signal',
                     use_banners=True, banner_title="🌊 Signal Processing")

# Add smoothed version
chart.line(time, smooth_signal, color='red', label='Smoothed')

chart.title("Signal Processing - Raw vs Smoothed")
chart.xlabel("Time Steps")
chart.ylabel("Amplitude")
chart.show()
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Chart Classes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/chart_classes.md#chart-classes)

## BarChart

Specialized class for creating bar charts with sorting and comparison features.

### Constructor

```python
BarChart(labels, values, color=None, horizontal=False, use_banners=False, banner_title=None)
```

### Enhanced Methods

- `sort_by_value(ascending=True)` - Sort bars by value
- `stack(values, color=None, label=None)` - Add stacked bars (future enhancement)
- `group(values, color=None, label=None)` - Add grouped bars (future enhancement)

### Example

```python
import plotext_plus as plt

# Sales data by region
regions = ['North', 'South', 'East', 'West', 'Central']
sales = [120, 145, 98, 167, 134]

# Create bar chart
chart = plt.BarChart(regions, sales, color='green',
                    use_banners=True, banner_title="💼 Regional Performance")

chart.title("Q2 Sales by Region")
chart.ylabel("Sales ($K)")
chart.show()

# Sorted version for better comparison
sorted_chart = plt.BarChart(regions, sales, color='blue',
                          use_banners=True, banner_title="📊 Ranked Performance")
sorted_chart.sort_by_value(ascending=False)
sorted_chart.title("Q2 Sales - Ranked by Performance")
sorted_chart.show()
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Chart Classes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/chart_classes.md#chart-classes)

## HistogramChart

Specialized class for creating histograms with statistical analysis features.

### Constructor

```python
HistogramChart(data, bins=20, color=None, use_banners=False, banner_title=None)
```

### Enhanced Methods

- `add_normal_curve()` - Overlay normal distribution curve (future enhancement)
- `add_statistics()` - Add mean, median, std dev lines (future enhancement)

### Example

```python
import plotext_plus as plt
import random

# Generate random normal data
data = [random.gauss(0, 1) for _ in range(1000)]

# Create histogram
chart = plt.HistogramChart(data, bins=25, color='purple',
                          use_banners=True, banner_title="📊 Distribution Analysis")

chart.title("Sample Distribution - Normal Data")
chart.xlabel("Value")
chart.ylabel("Frequency")
chart.show()
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Chart Classes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/chart_classes.md#chart-classes)

## CandlestickChart

Specialized class for financial candlestick charts with trading analysis features.

### Constructor

```python
CandlestickChart(dates, data, colors=None, use_banners=False, banner_title=None)
```

**Data format**: Each element in `data` should be `[open, high, low, close]`

### Enhanced Methods

- `add_volume(volumes, color='blue')` - Add volume bars (future enhancement)
- `add_moving_average(period=20, color='orange')` - Add moving average (future enhancement)

### Example

```python
import plotext_plus as plt
import random

# Generate sample stock price data
dates = list(range(1, 21))  # 20 trading days
data = []
price = 100.0

for day in dates:
    open_price = price
    close_price = price + random.uniform(-3, 3)
    high_price = max(open_price, close_price) + random.uniform(0, 2)
    low_price = min(open_price, close_price) - random.uniform(0, 2)
    data.append([open_price, high_price, low_price, close_price])
    price = close_price

# Create candlestick chart
chart = plt.CandlestickChart(dates, data, colors=['green', 'red'],
                           use_banners=True, banner_title="📈 Stock Analysis")

chart.title("ACME Corp - 20 Day Price Chart")
chart.xlabel("Trading Day")
chart.ylabel("Price ($)")
chart.show()
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Chart Classes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/chart_classes.md#chart-classes)

## HeatmapChart

Specialized class for creating heatmaps and correlation visualizations.

### Constructor

```python
HeatmapChart(data, colorscale=None, use_banners=False, banner_title=None)
```

### Enhanced Methods

- `annotate(show_values=True)` - Add value annotations to cells (future enhancement)

### Example

```python
import plotext_plus as plt
import random

# Generate correlation-like matrix
size = 8
data = []
for i in range(size):
    row = []
    for j in range(size):
        if i == j:
            correlation = 1.0
        else:
            correlation = random.uniform(-0.5, 0.8)
        row.append(int(correlation * 50) + 50)  # Scale to 0-100
    data.append(row)

# Create heatmap
chart = plt.HeatmapChart(data, colorscale='plasma',
                        use_banners=True, banner_title="🔗 Correlation Matrix")

chart.title("Feature Correlation Heatmap")
chart.show()
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Chart Classes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/chart_classes.md#chart-classes)

## MatrixChart

Specialized class for matrix plotting with pattern visualization.

### Constructor

```python
MatrixChart(matrix, marker=None, style=None, fast=False, use_banners=False, banner_title=None)
```

### Example

```python
import plotext_plus as plt
import random

# Generate binary pattern matrix
width, height = 40, 15
matrix = []
for row in range(height):
    matrix_row = []
    for col in range(width):
        # Create some pattern
        value = random.choice([0, 1]) if row < 3 else \
               (matrix[row-1][max(0,col-1)] ^ matrix[row-1][col])
        matrix_row.append(value)
    matrix.append(matrix_row)

# Create matrix plot
chart = plt.MatrixChart(matrix, marker='█', style='bold',
                       use_banners=True, banner_title="🧮 Pattern Analysis")

chart.title("Binary Pattern Evolution")
chart.show()
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Chart Classes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/chart_classes.md#chart-classes)

## StemChart

Specialized class for stem plots (lollipop charts) for discrete data.

### Constructor

```python
StemChart(x, y, color=None, orientation='vertical', use_banners=False, banner_title=None)
```

### Example

```python
import plotext_plus as plt
import random

# Survey response data
ratings = list(range(1, 11))  # 1-10 scale
responses = [random.randint(5, 50) for _ in ratings]

# Create stem chart
chart = plt.StemChart(ratings, responses, color='magenta',
                     use_banners=True, banner_title="📋 Survey Results")

chart.title("Product Satisfaction - Rating Distribution")
chart.xlabel("Rating (1-10 scale)")
chart.ylabel("Number of Responses")
chart.show()
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Chart Classes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/chart_classes.md#chart-classes)

## Chart Class Methods

All chart classes inherit these methods from the base `Chart` class:

### Configuration Methods

- `title(title)` - Set chart title
- `xlabel(label)` - Set x-axis label  
- `ylabel(label)` - Set y-axis label
- `size(width=None, height=None)` - Set chart dimensions
- `theme(theme_name)` - Apply a color theme
- `banner_title(title)` - Set banner title (if banner mode enabled)

### Data Methods

- `scatter(x, y, marker=None, color=None, label=None)` - Add scatter data
- `line(x, y, marker=None, color=None, label=None)` - Add line data
- `bar(labels, values, color=None, horizontal=False)` - Add bar data

### Display Methods

- `show()` - Render and display the chart
- `save(path, format='txt')` - Save chart to file

### Example of Method Chaining

```python
import plotext_plus as plt

# Create and configure chart with method chaining
chart = (plt.Chart(use_banners=True, banner_title="📊 Analysis")
         .scatter(x_data, y_data, color='blue', label='Observations')
         .line(x_theory, y_theory, color='red', label='Theory')
         .title("Experimental Analysis")
         .xlabel("Input Variable")
         .ylabel("Response")
         .theme('scientific')
         .show())
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Chart Classes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/chart_classes.md#chart-classes)