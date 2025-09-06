#!/usr/bin/env python3

"""
Test suite for image and video plotting functions in Plotext
Tests image_plot, play_video, and related functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotext_plus as plt
import tempfile
import time

def check_pil_available():
    """Check if PIL is available for image processing"""
    try:
        import PIL
        return True
    except ImportError:
        plt.log_warning("⚠️ PIL (Pillow) not available - skipping image functionality")
        plt.log_info("💡 Install with: pip install pillow")
        return False

def test_image_plot_basic():
    """Test basic image plotting functionality"""
    plt.log_info("Testing basic image plot...")
    
    if not check_pil_available():
        return
    
    # Use temporary file for test image
    temp_path = os.path.join(tempfile.gettempdir(), 'test_cat.jpg')
    
    try:
        # Download test image
        plt.download(plt.test_image_url, temp_path, log=False)
        
        # Test basic image plot
        plt.clear_figure()
        plt.plotsize(60, 20)  # Set reasonable size for test
        plt.image_plot(temp_path)
        plt.title("Test Image - Basic")
        plt.show()
        
        plt.log_success("Basic image plot test passed!")
        
    except Exception as e:
        plt.log_error(f"Basic image plot test failed: {str(e)}")
        raise
    finally:
        # Clean up
        if os.path.exists(temp_path):
            plt.delete_file(temp_path, log=False)
    
    print("\n" + "="*60 + "\n")

def test_image_plot_grayscale():
    """Test grayscale image plotting"""
    plt.log_info("Testing grayscale image plot...")
    
    if not check_pil_available():
        return
    
    temp_path = os.path.join(tempfile.gettempdir(), 'test_cat_gray.jpg')
    
    try:
        # Download test image
        plt.download(plt.test_image_url, temp_path, log=False)
        
        # Test grayscale image plot
        plt.clear_figure()
        plt.plotsize(60, 20)
        plt.image_plot(temp_path, grayscale=True)
        plt.title("Test Image - Grayscale")
        plt.show()
        
        plt.log_success("Grayscale image plot test passed!")
        
    except Exception as e:
        plt.log_error(f"Grayscale image plot test failed: {str(e)}")
        raise
    finally:
        # Clean up
        if os.path.exists(temp_path):
            plt.delete_file(temp_path, log=False)
    
    print("\n" + "="*60 + "\n")

def test_video_functionality():
    """Test video functionality (download only, not actual playback)"""
    plt.log_info("Testing video functionality...")
    
    temp_path = os.path.join(tempfile.gettempdir(), 'test_moonwalk.mp4')
    
    try:
        # Download test video
        plt.download(plt.test_video_url, temp_path, log=False)
        
        # Check if video file was downloaded successfully
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            plt.log_success("Video download test passed!")
            plt.log_info("Note: Actual video playback test skipped (would play video)")
        else:
            raise Exception("Video file was not downloaded properly")
        
    except Exception as e:
        plt.log_error(f"Video functionality test failed: {str(e)}")
        raise
    finally:
        # Clean up
        if os.path.exists(temp_path):
            plt.delete_file(temp_path, log=False)
    
    print("\n" + "="*60 + "\n")

def test_multimedia_demo_functions():
    """Test that multimedia demo functions can be called without errors"""
    plt.log_info("Testing multimedia demo function imports...")
    
    # Import the demo functions from interactive_demo
    import sys
    demo_path = os.path.join(os.path.dirname(__file__), '..', 'examples')
    sys.path.insert(0, demo_path)
    
    try:
        # This just tests that the functions can be imported
        from interactive_demo import demo_image_plotting, demo_video_functionality, demo_multimedia_showcase
        plt.log_success("Multimedia demo functions imported successfully!")
        
    except Exception as e:
        plt.log_error(f"Demo function import test failed: {str(e)}")
        raise
    
    print("\n" + "="*60 + "\n")

def run_all_image_video_tests():
    """Run all image and video tests"""
    plt.log_info("🎬 Starting comprehensive Image & Video tests...\n")
    
    try:
        test_image_plot_basic()
        test_image_plot_grayscale()
        test_video_functionality()
        test_multimedia_demo_functions()
        
        plt.log_success("🎉 All image and video tests completed!")
        plt.log_info("✨ Image and video functionality is available!")
        
        # Show summary
        pil_available = check_pil_available()
        if pil_available:
            plt.log_info("📷 Image plotting: Available")
        else:
            plt.log_warning("📷 Image plotting: Requires PIL/Pillow")
        plt.log_info("🎬 Video downloading: Available")
        plt.log_info("🎮 Video playback: Available (not tested)")
        
    except Exception as e:
        plt.log_error(f"❌ Image/Video test failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_image_video_tests()