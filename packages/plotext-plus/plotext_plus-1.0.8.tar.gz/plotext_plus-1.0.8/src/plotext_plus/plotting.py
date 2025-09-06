# /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plotext Core Plotting Functions - Clean Public API
=================================================

This module provides the main plotting functions that users interact with.
All the core plotting capabilities are exposed through clean, public interfaces.
"""

# Import all main plotting functions from the internal core module
from ._core import (
    # Basic plotting functions
    scatter, plot, bar, pie,
    matrix_plot, candlestick,
    
    # Plot customization
    title, xlabel, ylabel,
    xlim, ylim,
    xscale, yscale,
    grid, frame,
    
    # Colors and themes
    theme, colorize,
    
    # Layout and display
    show, build, sleep,
    clear_figure, clear_data, clear_terminal, clear_color,
    clf, cld, clt, clc,
    
    # Figure management
    plotsize, limitsize,
    subplots, subplot,
    
    # Data utilities
    save_fig,
    
    # Interactive features
    banner_mode,
)

# Import utilities that users might need
from ._utility import (
    terminal_width, terminal_height,
    colorize as color_text,
    delete_file,
    download as download_file,
)

# Import global functions for media handling
from ._global import (
    play_video,
    play_gif,
)

# Import core functions for media handling
from ._core import (
    image_plot,
)

__all__ = [
    # Basic plotting
    'scatter', 'plot', 'bar',
    'matrix_plot', 'candlestick',
    
    # Plot customization  
    'title', 'xlabel', 'ylabel',
    'xlim', 'ylim',
    'xscale', 'yscale',
    'grid', 'frame',
    
    # Colors and themes
    'theme', 'colorize', 'color_text',
    
    # Layout and display
    'show', 'build', 'sleep',
    'clear_figure', 'clear_data', 'clear_terminal', 'clear_color',
    'clf', 'cld', 'clt', 'clc',
    
    # Figure management
    'plotsize', 'limitsize', 'subplots', 'subplot',
    
    # Utilities
    'save_fig',
    'terminal_width', 'terminal_height',
    'banner_mode',
    
    # Media handling
    'download_file', 'delete_file',
    'image_plot', 'play_gif', 'play_video',
]