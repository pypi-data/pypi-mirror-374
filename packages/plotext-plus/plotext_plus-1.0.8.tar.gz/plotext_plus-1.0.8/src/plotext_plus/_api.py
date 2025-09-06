# /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modern Plotext API - A cleaner, more intuitive interface for creating terminal charts
This module provides both object-oriented and functional interfaces while maintaining
backward compatibility with the existing plotext API.
"""

import plotext_plus._core as _core
from plotext_plus._output import set_output_mode, info, success, warning, error


class Chart:
    """
    Modern object-oriented interface for creating charts.
    
    This class provides a chainable API for building charts with method chaining
    and cleaner separation of concerns.
    """
    
    def __init__(self, use_banners=False, banner_title=None):
        """
        Initialize a new chart.
        
        Args:
            use_banners (bool): Whether to display charts in chuk-term banners
            banner_title (str): Title for the banner (if enabled)
        """
        self.use_banners = use_banners
        self.banner_title = banner_title
        self._data = []
        self._legend = None
        self._config = {
            'title': None,
            'x_label': None,
            'y_label': None,
            'width': None,
            'height': None,
            'theme': 'default'
        }
        
        # Configure output mode
        if use_banners:
            set_output_mode(True, banner_title)
            # When using banners, automatically set appropriate size to fit within banner
            from plotext_plus import _utility as _ut
            banner_width = _ut.terminal_width()  # This now returns adjusted width for banners
            if banner_width:
                self._config['width'] = banner_width
    
    def scatter(self, x, y, marker=None, color=None, label=None):
        """Add scatter plot data"""
        self._data.append({
            'type': 'scatter',
            'x': x,
            'y': y,
            'marker': marker,
            'color': color,
            'label': label
        })
        return self
    
    def line(self, x, y, marker=None, color=None, label=None):
        """Add line plot data"""
        self._data.append({
            'type': 'line',
            'x': x,
            'y': y,
            'marker': marker,
            'color': color,
            'label': label
        })
        return self
    
    def bar(self, labels, values, color=None, horizontal=False):
        """Add bar chart data"""
        self._data.append({
            'type': 'bar',
            'labels': labels,
            'values': values,
            'color': color,
            'horizontal': horizontal
        })
        return self
    
    def pie(self, labels, values, colors=None, radius=None, show_values=True, show_percentages=True, show_values_on_slices=False, donut=False, remaining_color=None):
        """Add pie chart data"""
        self._data.append({
            'type': 'pie',
            'labels': labels,
            'values': values,
            'colors': colors,
            'radius': radius,
            'show_values': show_values,
            'show_percentages': show_percentages,
            'show_values_on_slices': show_values_on_slices,
            'donut': donut,
            'remaining_color': remaining_color
        })
        return self
    
    def title(self, title):
        """Set chart title"""
        self._config['title'] = title
        return self
    
    def xlabel(self, label):
        """Set x-axis label"""
        self._config['x_label'] = label
        return self
    
    def ylabel(self, label):
        """Set y-axis label"""
        self._config['y_label'] = label
        return self
    
    def size(self, width=None, height=None):
        """Set chart size"""
        self._config['width'] = width
        self._config['height'] = height
        return self
    
    def theme(self, theme_name):
        """Set chart theme"""
        self._config['theme'] = theme_name
        return self
    
    def banner_title(self, title):
        """Set banner title (if banner mode is enabled)"""
        self.banner_title = title
        if self.use_banners:
            set_output_mode(True, title)
        return self
    
    def legend(self, legend_instance=None):
        """
        Set or get legend for this chart
        
        Args:
            legend_instance (Legend): Legend instance to apply to chart
            
        Returns:
            Chart: Self for chaining, or current legend if no args provided
        """
        if legend_instance is None:
            return self._legend
        
        self._legend = legend_instance
        legend_instance.apply_to_chart(self)
        return self
    
    def show(self):
        """Render and display the chart"""
        # Clear any existing plot data
        _core.clear_figure()
        
        # Configure plot settings
        if self._config['title']:
            _core.title(self._config['title'])
        if self._config['x_label']:
            _core.xlabel(self._config['x_label'])
        if self._config['y_label']:
            _core.ylabel(self._config['y_label'])
        if self._config['width'] or self._config['height']:
            _core.plot_size(self._config['width'], self._config['height'])
        
        # Add data to plot
        for data_item in self._data:
            if data_item['type'] == 'scatter':
                _core.scatter(
                    data_item['x'], 
                    data_item['y'], 
                    marker=data_item['marker'],
                    color=data_item['color'],
                    label=data_item['label']
                )
            elif data_item['type'] == 'line':
                _core.plot(
                    data_item['x'], 
                    data_item['y'],
                    marker=data_item['marker'],
                    color=data_item['color'],
                    label=data_item['label']
                )
            elif data_item['type'] == 'bar':
                if data_item['horizontal']:
                    _core.horizontal_bar(data_item['labels'], data_item['values'], color=data_item['color'])
                else:
                    _core.bar(data_item['labels'], data_item['values'], color=data_item['color'])
            elif data_item['type'] == 'pie':
                _core.pie(
                    data_item['labels'], 
                    data_item['values'], 
                    colors=data_item['colors'],
                    radius=data_item['radius'],
                    show_values=data_item['show_values'],
                    show_percentages=data_item['show_percentages'],
                    show_values_on_slices=data_item['show_values_on_slices'],
                    donut=data_item.get('donut', False),
                    remaining_color=data_item.get('remaining_color', None)
                )
            elif data_item['type'] == 'histogram':
                _core.hist(data_item['data'], bins=data_item['bins'], color=data_item['color'])
        
        # Display the chart
        _core.show()
        return self
    
    def save(self, path, format='txt'):
        """Save chart to file"""
        if format == 'html':
            _core.save_fig(path, keep_colors=True)
        else:
            _core.save_fig(path)
        return self


class ScatterChart(Chart):
    """
    Specialized class for creating scatter plots with a focused API
    """
    
    def __init__(self, x, y, marker=None, color=None, label=None, use_banners=False, banner_title=None):
        """Initialize a scatter chart with data"""
        super().__init__(use_banners, banner_title)
        self.scatter(x, y, marker, color, label)
    
    def add_trend_line(self, x, y, color='red', label='Trend'):
        """Add a trend line to the scatter plot"""
        self.line(x, y, color=color, label=label)
        return self
    
    def add_regression(self):
        """Add linear regression line (future enhancement)"""
        # Placeholder for regression functionality
        return self


class LineChart(Chart):
    """
    Specialized class for creating line charts with enhanced features
    """
    
    def __init__(self, x, y, marker=None, color=None, label=None, use_banners=False, banner_title=None):
        """Initialize a line chart with data"""
        super().__init__(use_banners, banner_title)
        self.line(x, y, marker, color, label)
    
    def add_fill(self, fillx=False, filly=False):
        """Add fill under the line (future enhancement)"""
        # Placeholder for fill functionality
        return self
    
    def smooth(self, window_size=3):
        """Apply smoothing to the line (future enhancement)"""
        # Placeholder for smoothing functionality
        return self


class BarChart(Chart):
    """
    Specialized class for creating bar charts with extensive customization
    """
    
    def __init__(self, labels, values, color=None, horizontal=False, use_banners=False, banner_title=None):
        """Initialize a bar chart with data"""
        super().__init__(use_banners, banner_title)
        self.bar(labels, values, color, horizontal)
        self.labels = labels
        self.values = values
    
    def stack(self, values, color=None, label=None):
        """Add stacked bars (future enhancement)"""
        # Placeholder for stacked bar functionality
        return self
    
    def group(self, values, color=None, label=None):
        """Add grouped bars (future enhancement)"""
        # Placeholder for grouped bar functionality
        return self
    
    def sort_by_value(self, ascending=True):
        """Sort bars by value"""
        # Simple implementation for sorting
        sorted_pairs = sorted(zip(self.values, self.labels), reverse=not ascending)
        self.values, self.labels = zip(*sorted_pairs)
        return self


class HistogramChart(Chart):
    """
    Specialized class for creating histograms with statistical features
    """
    
    def __init__(self, data, bins=20, color=None, use_banners=False, banner_title=None):
        """Initialize a histogram with data"""
        super().__init__(use_banners, banner_title)
        self.data = data
        self.bins = bins
        self._create_histogram(data, bins, color)
    
    def _create_histogram(self, data, bins, color):
        """Create histogram from raw data"""
        # Add histogram data to the chart
        self._data.append({
            'type': 'histogram',
            'data': data,
            'bins': bins,
            'color': color
        })
        return self
    
    def add_normal_curve(self):
        """Overlay a normal distribution curve (future enhancement)"""
        # Placeholder for normal curve overlay
        return self
    
    def add_statistics(self):
        """Add mean, median, std dev lines (future enhancement)"""
        # Placeholder for statistical lines
        return self


class CandlestickChart(Chart):
    """
    Specialized class for financial candlestick charts
    """
    
    def __init__(self, dates, data, colors=None, use_banners=False, banner_title=None):
        """
        Initialize a candlestick chart
        
        Args:
            dates: List of dates
            data: List of [open, high, low, close] values
            colors: Optional color scheme for up/down candles
        """
        super().__init__(use_banners, banner_title)
        self.dates = dates
        self.data = data
        self._data.append({
            'type': 'candlestick',
            'dates': dates,
            'data': data,
            'colors': colors
        })
    
    def add_volume(self, volumes, color='blue'):
        """Add volume bars below candlesticks (future enhancement)"""
        # Placeholder for volume functionality
        return self
    
    def add_moving_average(self, period=20, color='orange'):
        """Add moving average line (future enhancement)"""
        # Placeholder for moving average
        return self
    
    def show(self):
        """Render and display the candlestick chart"""
        _core.clear_figure()
        
        if self._config['title']:
            _core.title(self._config['title'])
        if self._config['x_label']:
            _core.xlabel(self._config['x_label'])
        if self._config['y_label']:
            _core.ylabel(self._config['y_label'])
        if self._config['width'] or self._config['height']:
            _core.plot_size(self._config['width'], self._config['height'])
        
        for data_item in self._data:
            if data_item['type'] == 'candlestick':
                # Convert list format to dictionary format expected by plotext
                dates = data_item['dates']
                ohlc_data = data_item['data']
                
                # Format data as expected by plotext candlestick function
                formatted_data = {
                    'Open': [item[0] for item in ohlc_data],
                    'High': [item[1] for item in ohlc_data],
                    'Low': [item[2] for item in ohlc_data],
                    'Close': [item[3] for item in ohlc_data]
                }
                
                _core.candlestick(
                    dates,
                    formatted_data,
                    colors=data_item['colors']
                )
        
        _core.show()
        return self


class HeatmapChart(Chart):
    """
    Specialized class for creating heatmaps and matrix visualizations
    """
    
    def __init__(self, data, colorscale=None, use_banners=False, banner_title=None):
        """
        Initialize a heatmap chart
        
        Args:
            data: 2D matrix or pandas DataFrame
            colorscale: Color scale for the heatmap
        """
        super().__init__(use_banners, banner_title)
        self.data = data
        self.colorscale = colorscale
        self._data.append({
            'type': 'heatmap',
            'data': data,
            'colorscale': colorscale
        })
    
    def annotate(self, show_values=True):
        """Add value annotations to cells (future enhancement)"""
        # Placeholder for annotations
        return self
    
    def show(self):
        """Render and display the heatmap"""
        _core.clear_figure()
        
        # Set appropriate plot size for heatmaps FIRST - ensure full width usage
        if self._config['width'] or self._config['height']:
            _core.plotsize(self._config['width'], self._config['height'])
        else:
            # Default to full terminal width for better heatmap display
            import plotext_plus._utility as _ut
            terminal_width = _ut.terminal_width()
            if terminal_width:
                # Set reasonable dimensions for heatmap display
                heatmap_height = max(20, len(self.data) * 6 + 10)
                _core.plotsize(terminal_width - 4, heatmap_height)
        
        # Configure plot settings (same as base Chart class)
        if self._config['title']:
            _core.title(self._config['title'])
        if self._config['x_label']:
            _core.xlabel(self._config['x_label'])
        if self._config['y_label']:
            _core.ylabel(self._config['y_label'])
        
        for data_item in self._data:
            if data_item['type'] == 'heatmap':
                data = data_item['data']
                
                # Check if data is a pandas DataFrame
                if hasattr(data, 'columns'):
                    # It's already a DataFrame
                    _core.heatmap(data, color=data_item['colorscale'])
                else:
                    # It's a list/matrix, create filled heatmap blocks
                    self._draw_filled_heatmap(data, data_item['colorscale'])
        
        _core.show()
        return self
    
    def _draw_list_heatmap(self, matrix, colorscale):
        """Draw a heatmap using continuous colored blocks"""
        if not matrix or not matrix[0]:
            return
        
        rows = len(matrix)
        cols = len(matrix[0])
        
        # Flatten and normalize the data for color mapping
        flat_data = [val for row in matrix for val in row]
        min_val = min(flat_data)
        max_val = max(flat_data)
        value_range = max_val - min_val if max_val != min_val else 1
        
        # Define color palette
        color_palettes = {
            'plasma': ['black', 'purple', 'magenta', 'red', 'orange', 'yellow'],
            'viridis': ['black', 'blue', 'green', 'bright green', 'yellow'],
            'cool': ['cyan', 'blue', 'magenta', 'white'],
            'hot': ['black', 'red', 'orange', 'yellow', 'white'],
            'default': ['blue', 'cyan', 'green', 'yellow', 'red', 'magenta']
        }
        colors = color_palettes.get(colorscale, color_palettes['default'])
        
        # Create heatmap using continuous filled rectangles for each cell
        for row_idx in range(rows):
            row_data = matrix[row_idx]
            y_level = rows - row_idx - 1  # Flip so row 0 is at top
            
            for col_idx, value in enumerate(row_data):
                # Normalize value to get color
                normalized = (value - min_val) / value_range
                color_idx = int(normalized * (len(colors) - 1))
                color = colors[min(color_idx, len(colors) - 1)]
                
                # Create a continuous filled rectangle for this cell
                # Use multiple closely spaced points to fill the area
                cell_points_x = []
                cell_points_y = []
                
                # Fill the cell with dense points to create solid appearance
                for x_offset in [-0.45, -0.35, -0.25, -0.15, -0.05, 0.05, 0.15, 0.25, 0.35, 0.45]:
                    for y_offset in [-0.45, -0.35, -0.25, -0.15, -0.05, 0.05, 0.15, 0.25, 0.35, 0.45]:
                        cell_points_x.append(col_idx + x_offset)
                        cell_points_y.append(y_level + y_offset)
                
                # Draw all points for this cell at once with the same color
                if cell_points_x and cell_points_y:
                    _core.scatter(cell_points_x, cell_points_y, color=color, marker='█')
        
        # Set axis limits and labels to show the grid properly
        _core.xlim(-0.5, cols - 0.5)
        _core.ylim(-0.5, rows - 0.5)
        _core.xlabel('Column')
        _core.ylabel('Row')
    
    def _draw_filled_heatmap(self, matrix, colorscale):
        """Draw a heatmap using filled rectangular blocks for each cell"""
        if not matrix or not matrix[0]:
            return
        
        rows = len(matrix)
        cols = len(matrix[0])
        
        # Flatten and normalize the data for color mapping
        flat_data = [val for row in matrix for val in row]
        min_val = min(flat_data)
        max_val = max(flat_data)
        value_range = max_val - min_val if max_val != min_val else 1
        
        # Define color palette
        color_palettes = {
            'plasma': ['black', 'purple', 'magenta', 'red', 'orange', 'yellow'],
            'viridis': ['black', 'blue', 'green', 'bright green', 'yellow'],
            'cool': ['cyan', 'blue', 'magenta', 'white'],
            'hot': ['black', 'red', 'orange', 'yellow', 'white'],
            'default': ['blue', 'cyan', 'green', 'yellow', 'red', 'magenta']
        }
        colors = color_palettes.get(colorscale, color_palettes['default'])
        
        # Create filled rectangles for each cell using bar charts
        for row_idx in range(rows):
            row_data = matrix[row_idx]
            y_center = rows - row_idx - 1  # Flip so row 0 is at top
            
            for col_idx, value in enumerate(row_data):
                # Normalize value to get color
                normalized = (value - min_val) / value_range
                color_idx = int(normalized * (len(colors) - 1))
                color = colors[min(color_idx, len(colors) - 1)]
                
                # Create a filled rectangle using horizontal bar at this cell position
                # Bar from col_idx-0.4 to col_idx+0.4, at y_center with height 0.8
                x_positions = []
                y_positions = []
                
                # Fill the rectangle with a dense grid of points
                x_steps = 20  # More density for smoother appearance
                y_steps = 8
                
                for i in range(x_steps + 1):
                    for j in range(y_steps + 1):
                        x_offset = (i / x_steps - 0.5) * 0.9  # -0.45 to +0.45
                        y_offset = (j / y_steps - 0.5) * 0.9  # -0.45 to +0.45
                        x_positions.append(col_idx + x_offset)
                        y_positions.append(y_center + y_offset)
                
                # Draw all points for this cell with the same color
                if x_positions and y_positions:
                    _core.scatter(x_positions, y_positions, color=color, marker='█')
        
        # Set axis limits and labels to show the grid properly
        _core.xlim(-0.5, cols - 0.5)
        _core.ylim(-0.5, rows - 0.5)
        _core.xlabel('Column')
        _core.ylabel('Row')


class MatrixChart(Chart):
    """
    Specialized class for matrix plotting with advanced features
    """
    
    def __init__(self, matrix, marker=None, style=None, fast=False, use_banners=False, banner_title=None):
        """Initialize a matrix plot"""
        super().__init__(use_banners, banner_title)
        self.matrix = matrix
        self._data.append({
            'type': 'matrix',
            'matrix': matrix,
            'marker': marker,
            'style': style,
            'fast': fast
        })
    
    def show(self):
        """Render and display the matrix plot"""
        _core.clear_figure()
        
        if self._config['title']:
            _core.title(self._config['title'])
        if self._config['width'] or self._config['height']:
            _core.plot_size(self._config['width'], self._config['height'])
        
        for data_item in self._data:
            if data_item['type'] == 'matrix':
                _core.matrix_plot(
                    data_item['matrix'],
                    marker=data_item['marker'],
                    style=data_item['style'],
                    fast=data_item['fast']
                )
        
        _core.show()
        return self


class StemChart(Chart):
    """
    Specialized class for stem plots (lollipop charts)
    """
    
    def __init__(self, x, y, color=None, orientation='vertical', use_banners=False, banner_title=None):
        """Initialize a stem chart"""
        super().__init__(use_banners, banner_title)
        self.x = x
        self.y = y
        self.orientation = orientation
        # Use vertical lines to create stem effect
        self._data.append({
            'type': 'stem',
            'x': x,
            'y': y,
            'color': color,
            'orientation': orientation
        })
    
    def show(self):
        """Render and display the stem chart"""
        _core.clear_figure()
        
        if self._config['title']:
            _core.title(self._config['title'])
        if self._config['x_label']:
            _core.xlabel(self._config['x_label'])
        if self._config['y_label']:
            _core.ylabel(self._config['y_label'])
        if self._config['width'] or self._config['height']:
            _core.plot_size(self._config['width'], self._config['height'])
        
        for data_item in self._data:
            if data_item['type'] == 'stem':
                # Create stem plot using scatter points only for now
                # Full stem functionality would require extending core API
                _core.scatter(data_item['x'], data_item['y'], 
                            color=data_item['color'], 
                            marker='●')  # Use solid dot for stem heads
        
        _core.show()
        return self


class Legend:
    """
    Legend class for adding legends to any chart type
    """
    
    def __init__(self):
        self.items = []
        self.position = 'upper right'
        self.style = 'box'
        self.show_border = True
    
    def add(self, label, color=None, marker=None, line_style=None):
        """
        Add an item to the legend
        
        Args:
            label (str): Text label for the legend item
            color (str): Color for the legend item
            marker (str): Marker style for the legend item
            line_style (str): Line style for the legend item
        """
        self.items.append({
            'label': label,
            'color': color or 'default',
            'marker': marker or '■',
            'line_style': line_style or 'solid'
        })
        return self
    
    def set_position(self, pos):
        """Set legend position ('upper right', 'upper left', 'lower right', 'lower left')"""
        self.position = pos
        return self
    
    def set_style(self, style_name):
        """Set legend style ('box', 'plain')"""
        self.style = style_name
        return self
    
    def set_border(self, show=True):
        """Show or hide legend border"""
        self.show_border = show
        return self
    
    def apply_to_chart(self, chart_instance):
        """Apply this legend to a chart instance"""
        # Set this legend as the chart's legend (replace any existing legend)
        chart_instance._legend = self
        return self
    
    def render_legend_text(self):
        """Generate legend text representation"""
        if not self.items:
            return []
        
        legend_lines = []
        if self.show_border and self.style == 'box':
            legend_lines.append("┌─ Legend ─┐")
        
        for item in self.items:
            marker = item['marker']
            label = item['label']
            # Use color-coded markers if available
            if self.style == 'box':
                legend_lines.append(f"│ {marker} {label}")
            else:
                legend_lines.append(f"{marker} {label}")
        
        if self.show_border and self.style == 'box':
            legend_lines.append("└──────────┘")
        
        return legend_lines
    
    def show(self):
        """Display the legend independently"""
        legend_text = self.render_legend_text()
        for line in legend_text:
            print(line)
        return self


class PlotextAPI:
    """
    Modern functional API that provides cleaner function-based interface
    while maintaining the flexibility of the original plotext.
    """
    
    @staticmethod
    def create_chart(use_banners=False, banner_title=None):
        """Create a new Chart instance"""
        return Chart(use_banners, banner_title)
    
    @staticmethod
    def quick_scatter(x, y, title=None, xlabel=None, ylabel=None, use_banners=False, banner_title=None):
        """Quickly create and display a scatter plot"""
        chart = Chart(use_banners, banner_title)
        chart.scatter(x, y)
        if title:
            chart.title(title)
        if xlabel:
            chart.xlabel(xlabel)
        if ylabel:
            chart.ylabel(ylabel)
        chart.show()
        return chart
    
    @staticmethod
    def quick_line(x, y, title=None, xlabel=None, ylabel=None, use_banners=False, banner_title=None):
        """Quickly create and display a line plot"""
        chart = Chart(use_banners, banner_title)
        chart.line(x, y)
        if title:
            chart.title(title)
        if xlabel:
            chart.xlabel(xlabel)
        if ylabel:
            chart.ylabel(ylabel)
        chart.show()
        return chart
    
    @staticmethod
    def quick_bar(labels, values, title=None, horizontal=False, use_banners=False, banner_title=None):
        """Quickly create and display a bar chart"""
        chart = Chart(use_banners, banner_title)
        chart.bar(labels, values, horizontal=horizontal)
        if title:
            chart.title(title)
        chart.show()
        return chart
    
    @staticmethod 
    def quick_pie(labels, values, colors=None, title=None, use_banners=False, banner_title=None, 
                  show_values=True, show_percentages=True, show_values_on_slices=False, donut=False, remaining_color=None):
        """Quickly create and display a pie chart"""
        chart = Chart(use_banners, banner_title)
        chart.pie(labels, values, colors=colors, show_values=show_values, show_percentages=show_percentages, show_values_on_slices=show_values_on_slices, donut=donut, remaining_color=remaining_color)
        if title:
            chart.title(title)
        chart.show()
        return chart
    
    @staticmethod
    def quick_donut(labels, values, colors=None, title=None, use_banners=False, banner_title=None, 
                    show_values=True, show_percentages=True, show_values_on_slices=False, remaining_color=None):
        """Quickly create and display a doughnut chart"""
        return api.quick_pie(labels, values, colors=colors, title=title, use_banners=use_banners, 
                           banner_title=banner_title, show_values=show_values, 
                           show_percentages=show_percentages, show_values_on_slices=show_values_on_slices, donut=True, remaining_color=remaining_color)
    
    @staticmethod
    def enable_banners(enabled=True, default_title="Plotext Chart"):
        """Globally enable or disable banner mode"""
        set_output_mode(enabled, default_title)
    
    @staticmethod
    def log_info(message):
        """Output info message using chuk-term"""
        info(message)
    
    @staticmethod
    def log_success(message):
        """Output success message using chuk-term"""
        success(message)
    
    @staticmethod
    def log_warning(message):
        """Output warning message using chuk-term"""
        warning(message)
    
    @staticmethod
    def log_error(message):
        """Output error message using chuk-term"""
        error(message)


# Create a default API instance
api = PlotextAPI()

# Convenience functions for quick access
create_chart = api.create_chart
quick_scatter = api.quick_scatter
quick_line = api.quick_line
quick_bar = api.quick_bar
quick_pie = api.quick_pie
quick_donut = api.quick_donut
enable_banners = api.enable_banners
log_info = api.log_info
log_success = api.log_success
log_warning = api.log_warning
log_error = api.log_error

# Export specialized chart classes
__all__ = [
    'Chart',
    'ScatterChart',
    'LineChart',
    'BarChart',
    'HistogramChart',
    'CandlestickChart',
    'HeatmapChart',
    'MatrixChart',
    'StemChart',
    'Legend',
    'PlotextAPI',
    'create_chart',
    'quick_scatter',
    'quick_line',
    'quick_bar',
    'quick_pie',
    'quick_donut',
    'enable_banners',
    'log_info',
    'log_success',
    'log_warning',
    'log_error'
]