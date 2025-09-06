#!/usr/bin/env python3
"""
Demonstration of specialized chart classes in the new Plotext API
Shows how to use ScatterChart, LineChart, BarChart, and other specialized types
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotext_plus as plt
import random
import math

def demo_scatter_chart():
    """Demonstrate ScatterChart with trend analysis"""
    plt.log_info("📊 ScatterChart Demo - Data Analysis")
    
    # Generate sample experimental data with some correlation
    x = list(range(20))
    y = [2*i + random.uniform(-5, 5) for i in x]
    trend_x = x
    trend_y = [2*i for i in x]  # Perfect linear trend
    
    # Create scatter plot with trend line
    chart = plt.ScatterChart(
        x, y, 
        color='blue', 
        label='Experimental Data',
        use_banners=True, 
        banner_title="📈 Scientific Analysis"
    )
    chart.add_trend_line(trend_x, trend_y, color='red', label='Theoretical Trend')
    chart.title("Experimental vs Theoretical Results")
    chart.xlabel("Time (hours)")
    chart.ylabel("Response Value")
    chart.show()

def demo_line_chart():
    """Demonstrate LineChart with multiple series"""
    plt.log_info("📈 LineChart Demo - Time Series Analysis")
    
    # Generate time series data
    time = list(range(50))
    signal = [10 + 5*math.sin(t/5) + random.uniform(-1, 1) for t in time]
    smooth_signal = [10 + 5*math.sin(t/5) for t in time]
    
    chart = plt.LineChart(
        time, signal,
        color='green',
        label='Raw Signal',
        use_banners=True,
        banner_title="🌊 Signal Processing"
    )
    chart.line(time, smooth_signal, color='red', label='Smoothed')
    chart.title("Signal Processing - Raw vs Smoothed")
    chart.xlabel("Time Steps")
    chart.ylabel("Amplitude")
    chart.show()

def demo_bar_chart():
    """Demonstrate BarChart with sorting and comparison"""
    plt.log_info("📊 BarChart Demo - Performance Metrics")
    
    # Sales data by region
    regions = ['North', 'South', 'East', 'West', 'Central']
    q1_sales = [random.randint(50, 150) for _ in regions]
    q2_sales = [random.randint(60, 180) for _ in regions]
    
    # Q1 Results
    chart1 = plt.BarChart(
        regions, q1_sales,
        color='blue',
        use_banners=True,
        banner_title="💼 Q1 Performance"
    )
    chart1.title("Q1 Sales by Region")
    chart1.ylabel("Sales ($K)")
    chart1.show()
    
    # Q2 Results - Sorted for better comparison
    chart2 = plt.BarChart(
        regions, q2_sales,
        color='green',
        use_banners=True,
        banner_title="🚀 Q2 Performance (Sorted)"
    )
    chart2.sort_by_value(ascending=False)
    chart2.title("Q2 Sales by Region (Highest to Lowest)")
    chart2.ylabel("Sales ($K)")
    chart2.show()

def demo_candlestick_chart():
    """Demonstrate CandlestickChart for financial data"""
    plt.log_info("💹 CandlestickChart Demo - Stock Analysis")
    
    # Generate realistic stock price data
    dates = list(range(1, 31))  # 30 trading days
    data = []
    price = 100.0
    
    for day in dates:
        # Simulate daily price movement
        open_price = price
        price_change = random.uniform(-3, 3)
        close_price = price + price_change
        
        # High and low based on volatility
        daily_range = abs(price_change) + random.uniform(1, 4)
        high_price = max(open_price, close_price) + random.uniform(0, daily_range/2)
        low_price = min(open_price, close_price) - random.uniform(0, daily_range/2)
        
        data.append([open_price, high_price, low_price, close_price])
        price = close_price
    
    chart = plt.CandlestickChart(
        dates, data,
        colors=['green', 'red'],  # Up/down colors
        use_banners=True,
        banner_title="📈 Stock Market Analysis"
    )
    chart.title("ACME Corp Stock Price - 30 Day Chart")
    chart.xlabel("Trading Day")
    chart.ylabel("Price ($)")
    chart.show()

def demo_heatmap_chart():
    """Demonstrate HeatmapChart for correlation analysis"""
    plt.log_info("🔥 HeatmapChart Demo - Correlation Matrix")
    
    # Generate correlation-like data
    size = 8
    data = []
    for i in range(size):
        row = []
        for j in range(size):
            if i == j:
                correlation = 1.0  # Perfect self-correlation
            else:
                # Random correlation with some structure
                base_corr = random.uniform(-1, 1)
                if abs(i - j) == 1:  # Adjacent items more correlated
                    correlation = base_corr * 0.8
                else:
                    correlation = base_corr * 0.3
            row.append(int(correlation * 50) + 50)  # Scale to 0-100
        data.append(row)
    
    chart = plt.HeatmapChart(
        data,
        colorscale='plasma',
        use_banners=True,
        banner_title="🔗 Feature Correlation Matrix"
    )
    chart.title("ML Feature Correlation Heatmap")
    chart.show()

def demo_matrix_chart():
    """Demonstrate MatrixChart for pattern visualization"""
    plt.log_info("🎯 MatrixChart Demo - Pattern Recognition")
    
    # Generate a pattern matrix (simple cellular automata)
    width, height = 50, 20
    matrix = []
    
    for row in range(height):
        matrix_row = []
        for col in range(width):
            # Create some interesting patterns
            if row == 0:
                # Random initial condition
                matrix_row.append(random.choice([0, 1]))
            else:
                # Simple rule based on previous row
                prev_row = matrix[row-1]
                left = prev_row[max(0, col-1)]
                center = prev_row[col]
                right = prev_row[min(width-1, col+1)]
                
                # Rule 30-like behavior
                new_val = left ^ (center | right)
                matrix_row.append(new_val)
        matrix.append(matrix_row)
    
    chart = plt.MatrixChart(
        matrix,
        marker='█',
        style='bold',
        use_banners=True,
        banner_title="🧮 Cellular Automaton Pattern"
    )
    chart.title("Pattern Evolution - Rule-Based Matrix")
    chart.show()

def demo_stem_chart():
    """Demonstrate StemChart for discrete data"""
    plt.log_info("🌸 StemChart Demo - Survey Results")
    
    categories = list(range(1, 11))  # Rating 1-10
    responses = [random.randint(5, 50) for _ in categories]
    
    chart = plt.StemChart(
        categories, responses,
        color='magenta',
        use_banners=True,
        banner_title="📋 Customer Satisfaction Survey"
    )
    chart.title("Rating Distribution - Product Satisfaction")
    chart.xlabel("Rating (1-10 scale)")
    chart.ylabel("Number of Responses")
    chart.show()

def demo_combined_analysis():
    """Show how different chart types work together for comprehensive analysis"""
    plt.log_info("🎨 Combined Analysis Demo")
    
    # Dataset: Monthly sales data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    sales_data = [120, 135, 158, 142, 167, 181]
    growth_rates = [(sales_data[i]/sales_data[i-1] - 1)*100 if i > 0 else 0 for i in range(len(sales_data))]
    
    # 1. Line chart for trend
    trend_chart = plt.LineChart(
        list(range(len(months))), sales_data,
        color='blue',
        label='Monthly Sales',
        use_banners=True,
        banner_title="📈 Sales Trend Analysis"
    )
    trend_chart.title("Monthly Sales Trend (Line View)")
    trend_chart.xlabel("Month Index")
    trend_chart.ylabel("Sales ($K)")
    trend_chart.show()
    
    # 2. Bar chart for comparison
    bar_chart = plt.BarChart(
        months, sales_data,
        color='green',
        use_banners=True,
        banner_title="📊 Sales Comparison"
    )
    bar_chart.title("Monthly Sales Comparison (Bar View)")
    bar_chart.ylabel("Sales ($K)")
    bar_chart.show()
    
    # 3. Stem chart for growth rates
    stem_chart = plt.StemChart(
        list(range(1, len(months))), growth_rates[1:],  # Skip first month (no growth calculation)
        color='red',
        use_banners=True,
        banner_title="📈 Growth Rate Analysis"
    )
    stem_chart.title("Month-over-Month Growth Rates")
    stem_chart.xlabel("Month")
    stem_chart.ylabel("Growth Rate (%)")
    stem_chart.show()

def main():
    """Run all chart class demonstrations"""
    plt.log_success("🚀 Starting Chart Classes Demonstration")
    plt.log_info("Showcasing specialized chart classes in the new Plotext API\n")
    
    try:
        demo_scatter_chart()
        input("\nPress Enter to continue to LineChart demo...")
        
        demo_line_chart()
        input("\nPress Enter to continue to BarChart demo...")
        
        demo_bar_chart()
        input("\nPress Enter to continue to CandlestickChart demo...")
        
        demo_candlestick_chart()
        input("\nPress Enter to continue to HeatmapChart demo...")
        
        demo_heatmap_chart()
        input("\nPress Enter to continue to MatrixChart demo...")
        
        demo_matrix_chart()
        input("\nPress Enter to continue to StemChart demo...")
        
        demo_stem_chart()
        input("\nPress Enter to continue to Combined Analysis demo...")
        
        demo_combined_analysis()
        
        plt.log_success("\n🎉 All chart class demonstrations completed!")
        plt.log_info("✨ The new specialized chart classes provide:")
        plt.log_info("   • Type-specific APIs for different data visualizations")
        plt.log_info("   • Method chaining for fluent programming")
        plt.log_info("   • Built-in banner mode support")
        plt.log_info("   • Enhanced functionality for each chart type")
        
    except KeyboardInterrupt:
        plt.log_info("\n👋 Demo interrupted by user")
    except Exception as e:
        plt.log_error(f"❌ Demo failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()