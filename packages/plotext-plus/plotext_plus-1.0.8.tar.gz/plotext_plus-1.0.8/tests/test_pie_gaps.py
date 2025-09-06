#!/usr/bin/env python3

"""
Specific test to identify and highlight gaps in pie chart rendering
"""

import sys
sys.path.insert(0, '../src')

try:
    import plotext_plus as plt
    print("✓ plotext_plus imported successfully")
    
    # Get full terminal dimensions for maximum resolution testing
    terminal_width, terminal_height = plt.terminal_size()
    print(f"📏 Using full terminal dimensions: {terminal_width}x{terminal_height}")
    
    # Test pie chart with simple, equal segments to make gaps more visible
    print("\nTesting pie chart gap detection...")
    labels = ["A", "B", "C", "D"]
    values = [25, 25, 25, 25]  # Equal segments make gaps more obvious
    colors = ["red", "blue", "green", "orange"]
    
    plt.clear_figure()
    plt.plotsize(terminal_width, terminal_height - 5)  # Use full terminal size
    
    # Create a pie chart that should have no gaps
    plt.pie(labels, values, colors=colors, title="Gap Detection Test - Equal Segments")
    plt.show()
    
    print("\n" + "="*60)
    print("GAP ANALYSIS:")
    print("="*60)
    print("Look at the pie chart above and check for:")
    print("1. Black spaces between colored segments")
    print("2. Incomplete filling within segments") 
    print("3. Jagged or uneven edges")
    print("4. Missing blocks in what should be solid areas")
    print()
    print("If you see any black gaps between the red, blue, green,")
    print("and orange segments, the algorithm needs improvement.")
    print("="*60)
    
    # Test with unequal segments
    print("\nTesting with unequal segments...")
    labels2 = ["Large", "Medium", "Small", "Tiny"]  
    values2 = [50, 30, 15, 5]
    colors2 = ["red", "blue", "green", "orange"]
    
    plt.clear_figure()
    plt.plotsize(terminal_width, terminal_height - 5)  # Use full terminal size again
    plt.pie(labels2, values2, colors=colors2, title="Gap Detection Test - Unequal Segments")
    plt.show()
    
    print("\n" + "="*60)
    print("UNEQUAL SEGMENTS ANALYSIS:")
    print("="*60)
    print("Check especially:")
    print("1. Small segments (like 'Tiny' at 5%) for complete filling")
    print("2. Boundaries between different-sized segments")
    print("3. Whether thin segments have gaps or missing blocks")
    print("="*60)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()