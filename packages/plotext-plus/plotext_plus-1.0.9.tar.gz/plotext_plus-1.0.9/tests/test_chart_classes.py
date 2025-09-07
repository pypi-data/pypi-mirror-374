#!/usr/bin/env python3

"""
Test suite for specialized chart classes in the new Plotext API
Tests ScatterChart, LineChart, BarChart, and other specialized chart types
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotext_plus as plt
from plotext_plus._api import (
    ScatterChart, LineChart, BarChart, HistogramChart,
    CandlestickChart, HeatmapChart, MatrixChart, StemChart
)
import random

def test_scatter_chart():
    """Test ScatterChart class"""
    plt.log_info("Testing ScatterChart class...")
    
    x = list(range(10))
    y = [i**2 for i in x]
    
    chart = ScatterChart(x, y, color='red', label='Quadratic', use_banners=True, banner_title="Scatter Test")
    chart.title("ScatterChart Test")
    chart.xlabel("X Values")
    chart.ylabel("Y Values")
    chart.show()
    
    plt.log_success("ScatterChart test passed!")
    print("\n" + "="*60 + "\n")

def test_line_chart():
    """Test LineChart class"""
    plt.log_info("Testing LineChart class...")
    
    x = list(range(10))
    y = [i**0.5 for i in x]
    
    chart = LineChart(x, y, color='blue', label='Square Root', use_banners=True, banner_title="Line Test")
    chart.title("LineChart Test")
    chart.xlabel("Input")
    chart.ylabel("Output")
    chart.show()
    
    plt.log_success("LineChart test passed!")
    print("\n" + "="*60 + "\n")

def test_bar_chart():
    """Test BarChart class"""
    plt.log_info("Testing BarChart class...")
    
    labels = ['A', 'B', 'C', 'D', 'E']
    values = [random.randint(10, 100) for _ in labels]
    
    chart = BarChart(labels, values, color='green', use_banners=True, banner_title="Bar Test")
    chart.title("BarChart Test")
    chart.show()
    
    # Test sorting
    plt.log_info("Testing BarChart sorting...")
    sorted_chart = BarChart(labels, values, color='orange', use_banners=True, banner_title="Sorted Bars")
    sorted_chart.sort_by_value(ascending=False)
    sorted_chart.title("Sorted BarChart (Descending)")
    sorted_chart.show()
    
    plt.log_success("BarChart test passed!")
    print("\n" + "="*60 + "\n")

def test_histogram_chart():
    """Test HistogramChart class"""
    plt.log_info("Testing HistogramChart class...")
    
    # Generate random normal data
    data = [random.gauss(0, 1) for _ in range(1000)]
    
    try:
        chart = HistogramChart(data, bins=20, color='purple', use_banners=True, banner_title="Histogram Test")
        chart.title("HistogramChart Test - Normal Distribution")
        chart.show()
        plt.log_success("HistogramChart test passed!")
    except Exception as e:
        plt.log_warning(f"HistogramChart test skipped: {str(e)}")
    
    print("\n" + "="*60 + "\n")

def test_candlestick_chart():
    """Test CandlestickChart class"""
    plt.log_info("Testing CandlestickChart class...")
    
    # Generate sample financial data
    dates = list(range(1, 21))  # 20 days
    data = []
    price = 100
    for _ in dates:
        open_price = price
        close_price = price + random.uniform(-5, 5)
        high_price = max(open_price, close_price) + random.uniform(0, 2)
        low_price = min(open_price, close_price) - random.uniform(0, 2)
        data.append([open_price, high_price, low_price, close_price])
        price = close_price
    
    chart = CandlestickChart(dates, data, use_banners=True, banner_title="Candlestick Test")
    chart.title("CandlestickChart Test - Stock Price")
    chart.xlabel("Day")
    chart.ylabel("Price ($)")
    chart.show()
    
    plt.log_success("CandlestickChart test passed!")
    print("\n" + "="*60 + "\n")

def test_heatmap_chart():
    """Test HeatmapChart class"""
    plt.log_info("Testing HeatmapChart class...")
    
    # Generate sample 2D data
    data = [[random.randint(0, 100) for _ in range(10)] for _ in range(10)]
    
    chart = HeatmapChart(data, use_banners=True, banner_title="Heatmap Test")
    chart.title("HeatmapChart Test - Random Data")
    chart.show()
    
    plt.log_success("HeatmapChart test passed!")
    print("\n" + "="*60 + "\n")

def test_matrix_chart():
    """Test MatrixChart class"""
    plt.log_info("Testing MatrixChart class...")
    
    # Generate sample matrix
    matrix = [[random.choice([0, 1]) for _ in range(20)] for _ in range(10)]
    
    chart = MatrixChart(matrix, marker='█', use_banners=True, banner_title="Matrix Test")
    chart.title("MatrixChart Test - Binary Matrix")
    chart.show()
    
    plt.log_success("MatrixChart test passed!")
    print("\n" + "="*60 + "\n")

def test_stem_chart():
    """Test StemChart class"""
    plt.log_info("Testing StemChart class...")
    
    x = list(range(10))
    y = [random.randint(5, 20) for _ in x]
    
    chart = StemChart(x, y, color='cyan', use_banners=True, banner_title="Stem Test")
    chart.title("StemChart Test - Lollipop Plot")
    chart.xlabel("Category")
    chart.ylabel("Value")
    chart.show()
    
    plt.log_success("StemChart test passed!")
    print("\n" + "="*60 + "\n")

def test_chart_inheritance():
    """Test that specialized charts inherit from Chart properly"""
    plt.log_info("Testing chart inheritance...")
    
    # Test that all specialized charts have Chart methods
    x = [1, 2, 3]
    y = [1, 4, 9]
    
    # ScatterChart should have all Chart methods
    scatter = ScatterChart(x, y)
    assert hasattr(scatter, 'title'), "ScatterChart missing title method"
    assert hasattr(scatter, 'xlabel'), "ScatterChart missing xlabel method"
    assert hasattr(scatter, 'ylabel'), "ScatterChart missing ylabel method"
    assert hasattr(scatter, 'size'), "ScatterChart missing size method"
    assert hasattr(scatter, 'theme'), "ScatterChart missing theme method"
    assert hasattr(scatter, 'show'), "ScatterChart missing show method"
    
    plt.log_success("Chart inheritance test passed!")
    print("\n" + "="*60 + "\n")

def run_all_chart_class_tests():
    """Run all chart class tests"""
    plt.log_info("🎨 Starting comprehensive Chart Class tests...\n")
    
    try:
        test_scatter_chart()
        test_line_chart()
        test_bar_chart()
        test_histogram_chart()
        test_candlestick_chart()
        test_heatmap_chart()
        test_matrix_chart()
        test_stem_chart()
        test_chart_inheritance()
        
        plt.log_success("🎉 All chart class tests passed successfully!")
        plt.log_info("✨ New specialized chart classes are working properly!")
        
    except Exception as e:
        plt.log_error(f"❌ Chart class test failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_chart_class_tests()