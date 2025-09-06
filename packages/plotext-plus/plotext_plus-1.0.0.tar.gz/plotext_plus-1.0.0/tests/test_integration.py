#!/usr/bin/env python3

# Test script to verify the chuk-term integration works properly

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotext_plus as plt

def test_basic_plot():
    """Test basic plotting functionality"""
    print("Testing basic plot...")
    
    # Create simple test data
    x = list(range(10))
    y = [i**2 for i in x]
    
    # Test traditional mode (should work as before)
    plt.scatter(x, y)
    plt.title("Basic Scatter Plot - Traditional Mode")
    plt.show()
    
    print("\n" + "="*50 + "\n")

def test_banner_mode():
    """Test banner mode with chuk-term"""
    print("Testing banner mode...")
    
    # Enable banner mode
    plt.banner_mode(True, "Enhanced Scatter Plot")
    
    # Create the same plot
    x = list(range(10))
    y = [i**2 for i in x]
    
    plt.scatter(x, y)
    plt.title("Basic Scatter Plot - Banner Mode")
    plt.show()
    
    # Test chuk-term output functions
    plt.output_success("Chart rendered successfully!")
    plt.output_info("Banner mode is now active")
    
    print("\n" + "="*50 + "\n")

def test_output_functions():
    """Test the new chuk-term output functions"""
    print("Testing chuk-term output functions...")
    
    plt.output_info("This is an info message")
    plt.output_success("This is a success message")
    plt.output_warning("This is a warning message")
    plt.output_error("This is an error message")

if __name__ == "__main__":
    try:
        test_basic_plot()
        test_banner_mode()
        test_output_functions()
        
        plt.output_success("All tests completed successfully!")
        
    except Exception as e:
        plt.output_error(f"Test failed: {str(e)}")
        raise