"""\nplotext plots directly on terminal"""
    
__name__ = "plotext"
__version__ = "5.3.2"

# Clean Public API - Organized by functionality
# ===========================================

# Main plotting functions (most commonly used)
from .plotting import *

# Modern chart classes (object-oriented interface)  
from .charts import *

# Theme system
from .themes import *

# Utilities and helpers
from .utilities import *

# Backward compatibility - Import original API
from ._core import *

# Legacy imports for backward compatibility
from ._api import (
    Chart, Legend, PlotextAPI, api,
    ScatterChart, LineChart, BarChart, HistogramChart,
    CandlestickChart, HeatmapChart, MatrixChart, StemChart,
    create_chart, quick_scatter, quick_line, quick_bar, quick_pie, quick_donut,
    enable_banners, log_info, log_success, log_warning, log_error
)
