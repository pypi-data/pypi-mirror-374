# /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plotext Modern Chart Classes - Clean Public API
==============================================

This module provides the modern, object-oriented chart classes for more
structured plotting workflows. These classes offer a cleaner, more intuitive
interface compared to the traditional function-based API.
"""

# Import all chart classes from the internal API module
from ._api import (
    # Base classes
    Chart, Legend, PlotextAPI, api,
    
    # Specific chart types
    ScatterChart, LineChart, BarChart, HistogramChart,
    CandlestickChart, HeatmapChart, MatrixChart, StemChart,
    
    # Convenience functions
    create_chart, quick_scatter, quick_line, quick_bar, quick_pie, quick_donut,
    
    # Banner and logging utilities
    enable_banners, log_info, log_success, log_warning, log_error,
)

__all__ = [
    # Base classes
    'Chart', 'Legend', 'PlotextAPI', 'api',
    
    # Chart types
    'ScatterChart', 'LineChart', 'BarChart', 'HistogramChart', 
    'CandlestickChart', 'HeatmapChart', 'MatrixChart', 'StemChart',
    
    # Convenience functions
    'create_chart', 'quick_scatter', 'quick_line', 'quick_bar', 'quick_pie', 'quick_donut',
    
    # Utilities
    'enable_banners', 'log_info', 'log_success', 'log_warning', 'log_error',
]