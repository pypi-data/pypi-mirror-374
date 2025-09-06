#!/usr/bin/env python3

"""
Comprehensive test suite for the new Plotext API
Tests both the new modern interface and backward compatibility
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotext_plus as plt

def test_backward_compatibility():
    """Test that all existing plotext functionality still works"""
    plt.log_info("Testing backward compatibility...")
    
    # Test original API - should work exactly as before
    x = list(range(10))
    y = [i**2 for i in x]
    
    plt.clear_figure()
    plt.scatter(x, y, color='red')
    plt.title("Backward Compatibility Test")
    plt.xlabel("X Values")
    plt.ylabel("Y Values")
    plt.show()
    
    plt.log_success("Backward compatibility test passed!")
    print("\n" + "="*60 + "\n")

def test_new_oo_api():
    """Test the new object-oriented Chart API with method chaining"""
    plt.log_info("Testing new object-oriented API...")
    
    # Test method chaining
    x = list(range(10))
    y = [i**2 for i in x]
    
    chart = (plt.Chart(use_banners=True, banner_title="OO API Demo")
             .scatter(x, y, color='blue', label='Quadratic')
             .title("Object-Oriented API Test")
             .xlabel("X Values")
             .ylabel("Y² Values")
             .size(width=80, height=20)
             .show())
    
    plt.log_success("Object-oriented API test passed!")
    print("\n" + "="*60 + "\n")

def test_quick_functions():
    """Test the quick convenience functions"""
    plt.log_info("Testing quick convenience functions...")
    
    # Enable banners for all quick functions
    plt.enable_banners(True, "Quick Functions Demo")
    
    # Test quick_scatter
    x = list(range(5))
    y = [i*2 for i in x]
    plt.quick_scatter(
        x, y, 
        title="Quick Scatter Plot", 
        xlabel="Time", 
        ylabel="Value",
        use_banners=True,
        banner_title="Quick Scatter Demo"
    )
    
    # Test quick_line
    x2 = list(range(8))
    y2 = [i**0.5 for i in x2]
    plt.quick_line(
        x2, y2,
        title="Quick Line Plot",
        xlabel="Input",
        ylabel="Square Root",
        use_banners=True,
        banner_title="Quick Line Demo"
    )
    
    # Test quick_bar
    labels = ['A', 'B', 'C', 'D']
    values = [10, 25, 15, 30]
    plt.quick_bar(
        labels, values,
        title="Quick Bar Chart",
        use_banners=True,
        banner_title="Quick Bar Demo"
    )
    
    plt.log_success("Quick functions test passed!")
    print("\n" + "="*60 + "\n")

def test_multiple_series():
    """Test plotting multiple data series on the same chart"""
    plt.log_info("Testing multiple data series...")
    
    x = list(range(10))
    y1 = [i**2 for i in x]
    y2 = [i*3 for i in x]
    y3 = [20 - i for i in x]
    
    chart = (plt.Chart(use_banners=True, banner_title="Multi-Series Chart")
             .scatter(x, y1, color='red', label='Quadratic')
             .line(x, y2, color='blue', label='Linear')
             .scatter(x, y3, color='green', label='Inverse')
             .title("Multiple Data Series")
             .xlabel("X Values")
             .ylabel("Y Values")
             .show())
    
    plt.log_success("Multiple series test passed!")
    print("\n" + "="*60 + "\n")

def test_chuk_term_integration():
    """Test chuk-term output integration"""
    plt.log_info("Testing chuk-term output integration...")
    
    # Test all output types
    plt.log_info("This is an informational message")
    plt.log_success("This indicates successful completion")
    plt.log_warning("This is a warning message")
    plt.log_error("This indicates an error condition")
    
    plt.log_success("Chuk-term integration test passed!")
    print("\n" + "="*60 + "\n")

def test_banner_modes():
    """Test different banner modes and configurations"""
    plt.log_info("Testing banner mode configurations...")
    
    # Test with custom banner titles
    x = list(range(5))
    y = [i**3 for i in x]
    
    chart1 = (plt.Chart(use_banners=True, banner_title="🚀 Cubic Growth")
              .scatter(x, y, color='magenta')
              .title("Banner Mode: Custom Title")
              .show())
    
    # Test banner title change
    chart2 = plt.Chart(use_banners=True, banner_title="📈 Dynamic Analysis")
    chart2.scatter(x, y, color='cyan')
    chart2.title("Banner Mode: Dynamic Title")
    chart2.show()
    
    plt.log_success("Banner modes test passed!")
    print("\n" + "="*60 + "\n")

def run_all_tests():
    """Run all test suites"""
    plt.log_info("🧪 Starting comprehensive Plotext API tests...\n")
    
    try:
        test_backward_compatibility()
        test_new_oo_api()
        test_quick_functions()
        test_multiple_series()
        test_chuk_term_integration()
        test_banner_modes()
        
        plt.log_success("🎉 All tests passed successfully!")
        plt.log_info("✨ New API is ready for use!")
        
    except Exception as e:
        plt.log_error(f"❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_tests()