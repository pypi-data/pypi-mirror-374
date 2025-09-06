# /usr/bin/env python3
# -*- coding: utf-8 -*-

# This file contains the output handling system using chuk-term
# It provides both the traditional direct output and new banner-based output modes

import sys
from chuk_term import ui
from rich.panel import Panel
from rich.console import Console
from rich.text import Text


class PlotextOutput:
    """
    Unified output handler for plotext that supports both traditional
    terminal output and chuk-term enhanced output with banners and themes.
    """
    
    def __init__(self, use_banners=False, banner_title=None):
        self.use_banners = use_banners
        self.banner_title = banner_title or "Plotext Chart"
        self._buffer = []
        self.console = Console()
    
    def write(self, content):
        """
        Main output method that handles both traditional and banner-based output.
        
        Args:
            content (str): The content to output (typically the chart canvas)
        """
        if self.use_banners:
            self._write_with_banner(content)
        else:
            self._write_direct(content)
    
    def _write_direct(self, content):
        """Traditional direct output to stdout (maintains backward compatibility)"""
        sys.stdout.write(content)
    
    def _write_with_banner(self, content):
        """Output content within a chuk-term banner/panel using Rich panels"""
        # Rich panels need consistent line widths for proper alignment
        # We need to ensure all lines have exactly the same visible width
        
        from rich.text import Text
        
        # Convert content to Rich Text object to properly handle ANSI codes
        # This ensures consistent width calculations
        rich_text = Text.from_ansi(content)
        
        # Create a Rich panel with the processed content
        panel = Panel(
            rich_text,
            title=f"📊 {self.banner_title}",
            border_style="bright_blue",
            padding=(0, 1),
            expand=False  # Don't auto-expand, use content width
        )
        
        # Use Rich console to print the panel
        self.console.print()  # Add spacing before
        self.console.print(panel)
        self.console.print()  # Add spacing after
    
    def _clean_ansi_codes(self, content):
        """Remove ANSI escape codes for cleaner display in Rich panels"""
        import re
        # This removes basic ANSI codes but preserves the chart structure
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
        return ansi_escape.sub('', content)
    
    def set_banner_mode(self, enabled, title=None):
        """Enable or disable banner mode"""
        self.use_banners = enabled
        if title:
            self.banner_title = title
    
    def info(self, message):
        """Output informational message using chuk-term"""
        ui.info(message)
    
    def success(self, message):
        """Output success message using chuk-term"""
        ui.success(message)
    
    def warning(self, message):
        """Output warning message using chuk-term"""
        ui.warning(message)
    
    def error(self, message):
        """Output error message using chuk-term"""
        ui.error(message)


# Global output instance
_output = PlotextOutput()

def write(string):
    """
    The main write function used by plotext (maintains API compatibility).
    This replaces the original write function in _utility.py
    """
    _output.write(string)

def set_output_mode(use_banners=False, banner_title=None):
    """
    Configure output mode for plotext.
    
    Args:
        use_banners (bool): Whether to use chuk-term banners
        banner_title (str): Title for the banner (optional)
    """
    _output.set_banner_mode(use_banners, banner_title)

def get_output_instance():
    """Get the global output instance for advanced usage"""
    return _output

# Convenience functions for chuk-term output
def info(message):
    """Output info message via chuk-term"""
    _output.info(message)

def success(message):
    """Output success message via chuk-term"""
    _output.success(message)

def warning(message):
    """Output warning message via chuk-term"""
    _output.warning(message)

def error(message):
    """Output error message via chuk-term"""
    _output.error(message)