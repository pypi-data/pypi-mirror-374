# /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plotext Themes - Clean Public API
===============================

This module provides access to all available themes and theme-related functionality.
Users can easily access, apply, and customize themes for their plots.
"""

# Import theme functionality from internal modules
from ._themes import (
    get_theme_info,
    apply_chuk_theme_to_chart,
    get_chuk_theme_for_banner_mode,
    create_chuk_term_themes,
)

# Import theme application from core
from ._core import theme as apply_theme

__all__ = [
    # Theme management
    'get_theme_info', 'apply_theme',
    'apply_chuk_theme_to_chart',
    'get_chuk_theme_for_banner_mode',
    'create_chuk_term_themes',
]