#!/usr/bin/env python3

"""
Simple test for pie chart functionality
"""

import sys
sys.path.insert(0, '../src')

try:
    import plotext_plus as plt
    print("✓ plotext_plus imported successfully")
    
    # Test basic pie chart function
    print("Testing basic pie chart...")
    labels = ["A", "B", "C", "D"]
    values = [25, 30, 20, 25]
    colors = ["red", "blue", "green", "orange"]
    
    plt.clear_figure()
    plt.pie(labels, values, colors=colors, title="Test Pie Chart")
    plt.show()
    print("✓ Basic pie chart function works")
    
    # Test Chart class
    print("\nTesting Chart class pie method...")
    chart = plt.Chart()
    chart.pie(labels, values, colors=colors)
    chart.title("Chart Class Pie Test")
    chart.show()
    print("✓ Chart class pie method works")
    
    # Test quick_pie function
    print("\nTesting quick_pie function...")
    plt.quick_pie(labels, values, colors=colors, title="Quick Pie Test")
    print("✓ quick_pie function works")
    
    print("\n🎉 All pie chart tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()