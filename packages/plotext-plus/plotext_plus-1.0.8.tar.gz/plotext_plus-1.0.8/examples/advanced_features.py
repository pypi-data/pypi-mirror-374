#!/usr/bin/env python3
"""
Advanced Plotext features demonstration.
Shows banner customization, themes, and complex visualizations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotext_plus as plt
import math
import random

def custom_banner_example():
    """Demonstrate custom banner titles and styling"""
    plt.log_info("🎨 Demonstrating custom banners...")
    
    x = list(range(25))
    y = [10 + 5*math.sin(i/3) + random.randint(-2, 2) for i in x]
    
    # Custom themed banner
    chart = (plt.Chart(use_banners=True, banner_title="🌊 Signal Processing")
             .line(x, y, color='cyan', label='Noisy Signal')
             .title("Real-time Data Analysis")
             .xlabel("Time Samples")
             .ylabel("Amplitude")
             .show())

def scientific_visualization():
    """Scientific data visualization example"""
    plt.log_info("🔬 Creating scientific visualization...")
    
    # Generate experimental data
    temperature = list(range(20, 101, 5))
    pressure = [t*0.8 + random.randint(-5, 5) for t in temperature]
    theoretical = [t*0.75 for t in temperature]
    
    chart = (plt.Chart(use_banners=True, banner_title="🧪 Laboratory Results")
             .scatter(temperature, pressure, color='red', label='Experimental')
             .line(temperature, theoretical, color='blue', label='Theoretical')
             .title("Temperature vs Pressure Analysis")
             .xlabel("Temperature (°C)")
             .ylabel("Pressure (kPa)")
             .show())

def business_dashboard():
    """Business dashboard example"""
    plt.log_info("📊 Creating business dashboard...")
    
    # Revenue data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue = [120, 135, 158, 142, 167, 181]
    target = [150] * len(months)
    
    chart = (plt.Chart(use_banners=True, banner_title="💼 Revenue Dashboard")
             .bar(months, revenue, color='green')
             .line(list(range(len(months))), target, color='red', label='Target')
             .title("Monthly Revenue Performance")
             .show())

def mathematical_functions():
    """Mathematical function plotting"""
    plt.log_info("📐 Plotting mathematical functions...")
    
    x = [i/10 for i in range(-50, 51)]
    sin_values = [math.sin(val) for val in x]
    cos_values = [math.cos(val) for val in x]
    
    chart = (plt.Chart(use_banners=True, banner_title="📈 Mathematical Functions")
             .line(x, sin_values, color='blue', label='sin(x)')
             .line(x, cos_values, color='red', label='cos(x)')
             .title("Trigonometric Functions")
             .xlabel("x")
             .ylabel("f(x)")
             .show())

def performance_comparison():
    """Performance comparison chart"""
    plt.log_info("⚡ Creating performance comparison...")
    
    algorithms = ['Algorithm A', 'Algorithm B', 'Algorithm C', 'Algorithm D']
    execution_times = [2.3, 1.8, 3.1, 1.2]
    memory_usage = [45, 32, 67, 28]
    
    # Time comparison
    plt.quick_bar(
        algorithms, execution_times,
        title="Execution Time Comparison",
        use_banners=True,
        banner_title="⏱️ Performance Metrics"
    )
    
    print("\n" + "-"*40 + "\n")
    
    # Memory comparison
    plt.quick_bar(
        algorithms, memory_usage,
        title="Memory Usage Comparison", 
        use_banners=True,
        banner_title="💾 Memory Analysis"
    )

def output_features_demo():
    """Demonstrate chuk-term output features"""
    plt.log_info("🎯 Demonstrating output features...")
    
    # Various output levels
    plt.log_info("📋 Processing data...")
    plt.log_success("✅ Data loaded successfully")
    plt.log_warning("⚠️ Using default parameters")
    plt.log_error("❌ Minor calculation error detected")
    
    # Simple visualization with context
    x = list(range(8))
    y = [i**1.5 for i in x]
    
    plt.log_info("📊 Generating final visualization...")
    
    chart = (plt.Chart(use_banners=True, banner_title="🎯 Final Results")
             .scatter(x, y, color='purple', label='Growth Curve')
             .title("Project Completion Analysis")
             .xlabel("Weeks")
             .ylabel("Progress")
             .show())
    
    plt.log_success("🎉 Analysis complete!")

def main():
    """Run all advanced examples"""
    plt.log_success("🌟 Starting Advanced Plotext Features Demo")
    
    custom_banner_example()
    print("\n" + "="*60 + "\n")
    
    scientific_visualization()
    print("\n" + "="*60 + "\n")
    
    business_dashboard()
    print("\n" + "="*60 + "\n")
    
    mathematical_functions()
    print("\n" + "="*60 + "\n")
    
    performance_comparison()
    print("\n" + "="*60 + "\n")
    
    output_features_demo()
    
    plt.log_success("✨ All advanced examples completed!")

if __name__ == "__main__":
    main()