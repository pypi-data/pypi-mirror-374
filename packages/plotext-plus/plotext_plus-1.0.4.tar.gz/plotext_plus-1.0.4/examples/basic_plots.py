#!/usr/bin/env python3
"""
Basic plotting examples using the new Plotext API with chuk-term integration.
Demonstrates simple scatter plots, line plots, and bar charts.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotext_plus as plt

def basic_scatter_example():
    """Simple scatter plot example"""
    plt.log_info("Creating basic scatter plot...")
    
    # Sample data
    x = list(range(10))
    y = [i**2 for i in x]
    
    # Traditional API
    plt.scatter(x, y, color='blue')
    plt.title("Basic Scatter Plot - Traditional API")
    plt.xlabel("X Values")
    plt.ylabel("Y Values")
    plt.show()

def enhanced_scatter_example():
    """Enhanced scatter plot with banner mode"""
    plt.log_info("Creating enhanced scatter plot with banners...")
    
    # Sample data
    x = list(range(15))
    y = [i*1.5 + (i%3)*2 for i in x]
    
    # New object-oriented API with banner
    chart = (plt.Chart(use_banners=True, banner_title="📊 Enhanced Visualization")
             .scatter(x, y, color='red', label='Data Points')
             .title("Enhanced Scatter Plot")
             .xlabel("Time Steps")
             .ylabel("Measurements")
             .show())

def line_plot_example():
    """Simple line plot example"""
    plt.log_info("Creating line plot...")
    
    # Sample data
    x = list(range(20))
    y = [i + (i%5)*1.5 for i in x]
    
    # Quick function API
    plt.quick_line(
        x, y,
        title="Quick Line Plot",
        xlabel="Time",
        ylabel="Value",
        use_banners=True,
        banner_title="📈 Trend Analysis"
    )

def bar_chart_example():
    """Simple bar chart example"""
    plt.log_info("Creating bar chart...")
    
    # Sample data
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [23, 17, 35, 29, 12]
    
    # Quick bar chart
    plt.quick_bar(
        categories, values,
        title="Sample Bar Chart",
        use_banners=True,
        banner_title="📊 Category Analysis"
    )

def multiple_series_example():
    """Multiple data series on one chart"""
    plt.log_info("Creating multi-series plot...")
    
    x = list(range(12))
    y1 = [i*2 for i in x]
    y2 = [i**1.5 for i in x]
    
    # Object-oriented API with multiple series
    chart = (plt.Chart(use_banners=True, banner_title="📈 Comparison Chart")
             .line(x, y1, color='blue', label='Linear')
             .scatter(x, y2, color='red', label='Power')
             .title("Multiple Data Series")
             .xlabel("X Axis")
             .ylabel("Y Axis")
             .show())

def main():
    """Run all basic examples"""
    plt.log_success("🚀 Starting Basic Plotext Examples")
    
    basic_scatter_example()
    print("\n" + "="*50 + "\n")
    
    enhanced_scatter_example()
    print("\n" + "="*50 + "\n")
    
    line_plot_example()
    print("\n" + "="*50 + "\n")
    
    bar_chart_example()
    print("\n" + "="*50 + "\n")
    
    multiple_series_example()
    
    plt.log_success("✅ All basic examples completed!")

if __name__ == "__main__":
    main()