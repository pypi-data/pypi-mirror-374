#!/usr/bin/env python3

"""
Test to identify unfilled areas WITHIN pie chart segments
"""

import sys
sys.path.insert(0, '../src')

try:
    import plotext_plus as plt
    print("✓ plotext_plus imported successfully")
    
    # Test with a single large segment to make gaps obvious
    print("\nTesting single large segment for internal gaps...")
    labels = ["Single"]
    values = [100]
    colors = ["red"]
    
    plt.clear_figure()
    plt.pie(labels, values, colors=colors, title="Single Segment - Gap Detection")
    plt.show()
    
    print("\n" + "="*60)
    print("SINGLE SEGMENT ANALYSIS:")
    print("="*60)
    print("This should be a SOLID RED CIRCLE with NO black gaps inside.")
    print("Look carefully within the red area for:")
    print("1. Black spaces inside what should be solid red")
    print("2. Sparse/patchy areas with missing red blocks")
    print("3. Any non-red pixels within the circle boundary")
    print("="*60)
    
    # Test with two equal segments
    print("\nTesting two equal segments...")
    labels2 = ["Half A", "Half B"]
    values2 = [50, 50]
    colors2 = ["blue", "orange"]
    
    plt.clear_figure()
    plt.pie(labels2, values2, colors=colors2, title="Two Halves - Internal Fill Test")
    plt.show()
    
    print("\n" + "="*60)
    print("TWO SEGMENT ANALYSIS:")  
    print("="*60)
    print("Each half should be COMPLETELY SOLID:")
    print("- Left half: solid blue with no black gaps inside")
    print("- Right half: solid orange with no black gaps inside")
    print("- Clean boundary between blue and orange")
    print("="*60)
    
    print("\nIf you see scattered individual blocks or black gaps")
    print("WITHIN the colored areas, the fill algorithm needs fixing.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()