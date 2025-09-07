#!/usr/bin/env python3

"""
Test specifically for colored blocks in pie chart legend
"""

import sys
sys.path.insert(0, '../src')

try:
    import plotext_plus as plt
    print("✓ plotext_plus imported successfully")
    
    # Test with simple data to clearly see legend
    print("\nTesting pie chart legend with colored blocks...")
    labels = ["Red", "Blue"] 
    values = [60, 40]
    colors = ["red", "blue"]
    
    plt.clear_figure()
    plt.pie(labels, values, colors=colors, title="Legend Color Test")
    plt.show()
    
    print("\n" + "="*60)
    print("LEGEND COLOR VERIFICATION:")
    print("="*60)
    print("Look for these in the legend area (right side):")
    print("1. Red block (█) followed by 'Red: 60 (60.0%)'")
    print("2. Blue block (█) followed by 'Blue: 40 (40.0%)'") 
    print("Each legend entry should start with a colored block!")
    print("="*60)
    
    # Test for black gaps with single segment
    print("\n\nTesting single segment for black gaps...")
    plt.clear_figure()
    plt.pie(["Single"], [100], colors=["red"], title="Gap Test - Single Segment")
    plt.show()
    
    print("\n" + "="*60)
    print("BLACK GAP VERIFICATION:")
    print("="*60)
    print("The red circle above should be COMPLETELY SOLID.")
    print("If you see ANY black spaces inside the red area,")
    print("there are still gaps that need to be fixed!")
    print("="*60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()