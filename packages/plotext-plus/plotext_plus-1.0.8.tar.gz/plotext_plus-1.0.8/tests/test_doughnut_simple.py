#!/usr/bin/env python3
"""
Simple test case for doughnut chart functionality.
Tests basic doughnut rendering with hollow center.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotext_plus as plt

def test_basic_doughnut():
    """Test basic doughnut chart rendering"""
    print("Testing basic doughnut chart...")
    
    # Simple 3-segment doughnut
    labels = ['A', 'B', 'C']
    values = [40, 35, 25]
    colors = ['red', 'blue', 'green']
    
    # Get full terminal dimensions
    terminal_width, terminal_height = plt.terminal_size()
    
    plt.clear_figure()
    plt.plotsize(terminal_width, terminal_height - 5)  # Leave space for text
    
    # Print plot dimensions and radius info
    plot_width, plot_height = terminal_width, terminal_height - 5
    outer_radius = (min(plot_width, plot_height) - 4) / 2.0
    inner_radius = outer_radius / 3.0
    print(f"Plot dimensions: {plot_width} x {plot_height}")
    print(f"Outer radius: {outer_radius}")
    print(f"Inner radius: {inner_radius}")
    
    plt.pie(labels, values, colors=colors, donut=True, 
           title='Basic Doughnut Test')
    plt.show()
    
    print("✓ Basic doughnut test completed")

def test_single_value_doughnut():
    """Test single-value doughnut (progress indicator style)"""
    print("\nTesting single-value doughnut...")
    
    # Get full terminal dimensions
    terminal_width, terminal_height = plt.terminal_size()
    
    plt.clear_figure()
    plt.plotsize(terminal_width, terminal_height - 5)  # Leave space for text
    
    # Print plot dimensions and radius info
    plot_width, plot_height = terminal_width, terminal_height - 5
    outer_radius = (min(plot_width, plot_height) - 4) / 2.0
    inner_radius = outer_radius / 3.0
    print(f"Plot dimensions: {plot_width} x {plot_height}")
    print(f"Outer radius: {outer_radius}")
    print(f"Inner radius: {inner_radius}")
    
    plt.pie(['Progress', 'Remaining'], [75, 25], 
           colors=['cyan', 'default'], donut=True,
           show_values=False, show_percentages=True,
           title='Progress: 75%')
    plt.show()
    
    print("✓ Single-value doughnut test completed")

def test_doughnut_with_remaining_color():
    """Test doughnut with colored remaining slice"""
    print("\nTesting doughnut with remaining color...")
    
    # Get full terminal dimensions
    terminal_width, terminal_height = plt.terminal_size()
    
    plt.clear_figure()
    plt.plotsize(terminal_width, terminal_height - 5)  # Leave space for text
    
    # Print plot dimensions and radius info
    plot_width, plot_height = terminal_width, terminal_height - 5
    outer_radius = (min(plot_width, plot_height) - 4) / 2.0
    inner_radius = outer_radius / 3.0
    print(f"Plot dimensions: {plot_width} x {plot_height}")
    print(f"Outer radius: {outer_radius}")
    print(f"Inner radius: {inner_radius}")
    
    plt.pie(['Complete', 'Remaining'], [60, 40],
           colors=['green', 'default'], donut=True,
           remaining_color='gray',
           show_values=False, show_percentages=True,
           title='Task: 60% Complete')
    plt.show()
    
    print("✓ Doughnut with remaining color test completed")

def test_remaining_color_comparison():
    """Test comparison between remaining color and no remaining color"""
    print("\nTesting remaining color comparison...")
    
    # Get full terminal dimensions for maximum visual impact
    terminal_width, terminal_height = plt.terminal_size()
    
    # Create subplot comparison
    plt.clear_figure()
    plt.subplots(1, 2)  # 1 row, 2 columns
    plt.plotsize(terminal_width, terminal_height - 5)  # Use full terminal height
    
    # Print plot dimensions and radius info
    plot_width, plot_height = terminal_width, terminal_height - 5
    subplot_width = plot_width // 2
    outer_radius = (min(subplot_width, plot_height) - 4) / 2.0
    inner_radius = outer_radius / 3.0
    print(f"Plot dimensions: {plot_width} x {plot_height} (each subplot: ~{subplot_width} x {plot_height})")
    print(f"Outer radius: {outer_radius}")
    print(f"Inner radius: {inner_radius}")
    
    # Left subplot: No remaining color (spaces)
    plt.subplot(1, 1)
    plt.pie(['Complete', 'Remaining'], [65, 35],
           colors=['blue', 'default'], donut=True,
           show_values=False, show_percentages=True,
           title='Without Remaining Color')
    
    # Right subplot: With remaining color
    plt.subplot(1, 2)
    plt.pie(['Complete', 'Remaining'], [65, 35],
           colors=['blue', 'default'], donut=True,
           remaining_color='gray',
           show_values=False, show_percentages=True,
           title='With Remaining Color')
    
    plt.show()
    
    print("✓ Remaining color comparison test completed")

if __name__ == '__main__':
    print("Doughnut Chart Test Suite")
    print("=" * 40)
    
    test_basic_doughnut()
    test_single_value_doughnut() 
    test_doughnut_with_remaining_color()
    test_remaining_color_comparison()
    
    print("\n" + "=" * 40)
    print("All doughnut tests completed successfully!")
    print("Each chart should show:")
    print("- Hollow center (no characters inside)")
    print("- Colored ring segments")
    print("- Proper legend display")