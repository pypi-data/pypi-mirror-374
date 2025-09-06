#!/usr/bin/env python3

"""
Test pie chart aspect ratio and color matching
"""

import sys
sys.path.insert(0, '../src')

try:
    import plotext_plus as plt
    print("Testing pie chart aspect ratio and colors...")
    
    labels = ["Red", "Blue", "Green", "Orange"]
    values = [25, 25, 25, 25]
    colors = ["red", "blue", "green", "orange"]
    
    # Test 1: Square plot (should show circular pie)
    print("\n1. Square plot (40x20) - should be circular:")
    plt.clear_figure()
    plt.plotsize(40, 20)
    plt.pie(labels, values, colors=colors, title="Square Plot")
    plt.show()
    
    # Test 2: Wide plot (should show elliptical if not corrected)
    print("\n2. Wide plot (60x20) - testing aspect ratio:")
    plt.clear_figure()
    plt.plotsize(60, 20)
    plt.pie(labels, values, colors=colors, title="Wide Plot")
    plt.show()
    
    # Test 3: Tall plot (should show elliptical if not corrected)
    print("\n3. Tall plot (40x30) - testing aspect ratio:")
    plt.clear_figure()
    plt.plotsize(40, 30)
    plt.pie(labels, values, colors=colors, title="Tall Plot")
    plt.show()
    
    print("\n" + "="*60)
    print("ASPECT RATIO CHECK:")
    print("="*60)
    print("All three pies should appear CIRCULAR, not elliptical.")
    print("If any appear stretched, aspect ratio needs correction.")
    print("="*60)
    print("\nCOLOR CHECK:")
    print("="*60)
    print("Legend colors should match:")
    print("1. Red slice -> Red legend entry")
    print("2. Blue slice -> Blue legend entry")
    print("3. Green slice -> Green legend entry")
    print("4. Orange slice -> Orange legend entry")
    print("="*60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()