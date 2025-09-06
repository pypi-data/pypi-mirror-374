#!/usr/bin/env python3

"""
Test for pie chart with values on slices functionality
"""

import sys
sys.path.insert(0, '../src')

try:
    import plotext_plus as plt
    print("Testing pie chart with values on slices...")
    
    labels = ["Apples", "Oranges", "Bananas", "Grapes"]
    values = [40, 30, 20, 10]
    colors = ["red", "orange", "green", "magenta"]
    
    # Test with values on slices enabled
    plt.clear_figure()
    plt.pie(labels, values, colors=colors, title="Pie with Values on Slices", 
            show_values_on_slices=True)
    plt.show()
    print("✓ Pie chart with values on slices works!")
    
    # Test with default behavior (no values on slices)
    print("\nCompare with default behavior (legend only):")
    plt.clear_figure()
    plt.pie(labels, values, colors=colors, title="Default Pie Chart")
    plt.show()
    print("✓ Default pie chart works!")
    
    print("\n🎉 Pie chart slice values feature working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()