# /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plotext Utilities - Clean Public API
===================================

This module provides utility functions for terminal operations, file handling,
and other helper functionality that users might need.
"""

# Import utility functions from internal modules
from ._utility import (
    terminal_width,
    colorize, no_color,
    matrix_size,
    delete_file,
    download,
)

# Import global utilities - check what's actually available
from ._global import (
    test_data_url, test_bar_data_url, 
    test_image_url, test_gif_url, test_video_url,
)

# Import output utilities
from ._output import (
    info as log_info, 
    success as log_success, 
    warning as log_warning, 
    error as log_error,
)

__all__ = [
    # Terminal utilities
    'terminal_width',
    'colorize', 'no_color',
    
    # Matrix utilities  
    'matrix_size',
    
    # File utilities
    'delete_file', 'download',
    
    # Test data URLs
    'test_data_url', 'test_bar_data_url',
    'test_image_url', 'test_gif_url', 'test_video_url',
    
    # Logging utilities
    'log_info', 'log_success', 'log_warning', 'log_error',
]