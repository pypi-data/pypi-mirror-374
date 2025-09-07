#!/usr/bin/env python3
"""
Interactive Plotext Demo with Chuk-Term Banners and Themes
This demo showcases the enhanced visual features and allows users to explore
different banner styles, themes, and chart types interactively.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotext_plus as plt
# Use the clean public API instead of private modules
from plotext_plus import utilities as ut
import math
import random
import time

def get_optimal_chart_height():
    """Calculate optimal chart height based on current terminal dimensions"""
    from plotext_plus import _utility as ut
    
    terminal_width, terminal_height = ut.terminal_size()
    
    # Calculate all the extra lines that appear before/after charts
    welcome_message_lines = 2   # Success + info message  
    separator_lines = 2         # Separator line + blank line
    banner_border_lines = 4     # Banner top border + title line + bottom border + spacing
    menu_info_lines = 2         # Info symbol + menu title
    menu_options = 12           # 11 options + exit
    menu_prompt_lines = 2       # Prompt + input line
    
    total_overhead_lines = (welcome_message_lines + separator_lines + banner_border_lines +
                           menu_info_lines + menu_options + menu_prompt_lines)
    
    # Calculate available height for charts (the actual chart content area)
    available_height = terminal_height - total_overhead_lines
    optimal_chart_height = max(available_height, 3)  # At least 3 for minimal chart
    
    return optimal_chart_height

def get_optimal_grid_height():
    """Calculate optimal height for 2x2 grid layout"""
    from plotext_plus import _utility as ut
    
    terminal_width, terminal_height = ut.terminal_size()
    
    # For grid layout, we only need space for a compact menu at bottom
    menu_lines = 4  # Compact menu display for grid (title + option + prompt + buffer)
    available_height = terminal_height - menu_lines
    
    return max(available_height, 15)

def get_full_terminal_height():
    """Get the full terminal height for 'Run all demos' mode"""
    from plotext_plus import _utility as ut
    
    terminal_width, terminal_height = ut.terminal_size()
    
    # Use terminal height minus 3 lines, with minimum of 5
    return max(terminal_height - 3, 5)

def welcome_screen():
    """Display welcome screen with banner"""
    plt.log_success("🎉 Welcome to Plotext Interactive Demo!")
    plt.log_info("This demo showcases the new chuk-term integration features")
    print("\n" + "="*60)
    
    # Create a welcome chart
    x = list(range(15))
    y = [5 + 3*math.sin(i/2) + random.uniform(-0.5, 0.5) for i in x]
    
    chart = plt.Chart(use_banners=True, banner_title="🎨 Welcome to Enhanced Plotext")
    chart._config['height'] = get_optimal_chart_height()
    chart.line(x, y, color='cyan', label='Demo Signal')
    chart.title("Interactive Demo - Enhanced Terminal Plotting")
    chart.xlabel("Time Steps")
    chart.ylabel("Amplitude")
    chart.show()
    
    print("="*60 + "\n")

def demo_banner_styles(use_full_height=False):
    """Demonstrate different banner styles and themes"""
    plt.log_info("🎭 Demonstrating Banner Styles and Themes...")
    
    # Scientific theme
    x = list(range(20))
    pressure = [1013 + 50*math.sin(i/3) + random.randint(-10, 10) for i in x]
    
    chart1 = plt.Chart(use_banners=True, banner_title="🔬 Scientific Data Analysis")
    chart1._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
    chart1.scatter(x, pressure, color='blue', label='Pressure Readings')
    chart1.title("Atmospheric Pressure Monitoring")
    chart1.xlabel("Time (hours)")
    chart1.ylabel("Pressure (hPa)")
    chart1.show()
    
    plt.log_success("✓ Scientific theme demonstrated")
    time.sleep(2)
    
    # Business theme
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue = [120, 135, 158, 142, 167, 181]
    growth = [(rev/120 - 1)*100 for rev in revenue]
    
    chart2 = plt.Chart(use_banners=True, banner_title="💼 Business Intelligence Dashboard")
    chart2._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
    chart2.bar(list(range(len(months))), revenue, color='green')
    chart2.line(list(range(len(months))), [r/2 for r in revenue], color='orange', label='Trend')
    chart2.title("Monthly Revenue & Growth Analysis")
    chart2.show()
    
    plt.log_success("✓ Business theme demonstrated")
    time.sleep(2)
    
    # Gaming/Fun theme
    levels = ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5']
    scores = [850, 1200, 975, 1450, 1600]
    
    chart3 = plt.Chart(use_banners=True, banner_title="🎮 Gaming Statistics")
    chart3._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
    chart3.bar(list(range(len(levels))), scores, color='magenta')
    chart3.title("Player Performance by Level")
    chart3.show()
    
    plt.log_success("✓ Gaming theme demonstrated")
    time.sleep(2)

def demo_interactive_charts(use_full_height=False):
    """Create interactive-style charts with real-time feel"""
    plt.log_info("📊 Creating Interactive-Style Charts...")
    
    # Simulate real-time data
    plt.log_info("📡 Simulating real-time data stream...")
    
    for i in range(3):
        # Generate new data each iteration
        time_points = list(range(25))
        values = [10 + 5*math.sin(t/4) + 2*math.cos(t/2) + random.uniform(-1, 1) for t in time_points]
        
        chart = plt.Chart(use_banners=True, banner_title=f"📈 Real-time Monitor (Update {i+1}/3)")
        chart._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
        chart.line(time_points, values, color='cyan', label='Live Signal')
        chart.scatter([time_points[-1]], [values[-1]], color='red', label='Current')
        chart.title(f"Live Data Stream - Update {i+1}")
        chart.xlabel("Time")
        chart.ylabel("Signal Value")
        chart.show()
        
        plt.log_info(f"📊 Data point {i+1}: {values[-1]:.2f}")
        if i < 2:  # Don't sleep after the last iteration
            time.sleep(1.5)
    
    plt.log_success("✓ Real-time simulation complete")

def demo_four_panel_dashboard(use_full_height=False):
    """Create a 2x2 grid dashboard with four panels displayed side-by-side"""
    plt.log_info("📊 Creating Four-Panel Dashboard (2x2 grid layout)...")
    
    # Use plotext_plus for subplot functionality
    core_plt = plt
    
    # Clear any existing plot data to avoid conflicts
    core_plt.clear_figure()
    
    # Create 2x2 subplot grid
    core_plt.subplots(2, 2)
    # Calculate dynamic dimensions based on current terminal
    from plotext_plus import _utility as ut
    terminal_width, terminal_height = ut.terminal_size()
    grid_height = get_full_terminal_height() if use_full_height else get_optimal_grid_height()
    
    # Use banner-adjusted width for subplots when banners are enabled
    # ut.terminal_width() returns the appropriate width (reduced if banners are active)
    plot_width = ut.terminal_width() or terminal_width
    core_plt.plot_size(plot_width, grid_height)  # Use adjusted width for proper banner alignment
    
    # Panel 1: Top-left (1,1) - System Resources
    core_plt.subplot(1, 1)
    cpu_data = [45, 52, 48, 61, 58, 63, 55]
    mem_data = [67, 71, 74, 72, 75, 73, 70]
    core_plt.plot(list(range(7)), cpu_data, color='red', label='CPU')
    core_plt.plot(list(range(7)), mem_data, color='blue', label='MEM')
    core_plt.title("⚡ System Resources")
    
    # Panel 2: Top-right (1,2) - Network I/O
    core_plt.subplot(1, 2)
    net_down = [1.2, 2.1, 1.8, 3.2, 2.9, 1.5, 2.3]
    net_up = [0.8, 1.1, 0.9, 1.8, 1.5, 0.7, 1.2]
    core_plt.plot(list(range(7)), net_down, color='green', label='↓ Down')
    core_plt.plot(list(range(7)), net_up, color='orange', label='↑ Up')
    core_plt.title("🌐 Network I/O")
    
    # Panel 3: Bottom-left (2,1) - Error Types
    core_plt.subplot(2, 1)
    errors = [15, 8, 12, 5]
    error_labels = ['404', '500', 'Timeout', 'DNS']
    core_plt.bar(list(range(4)), errors, color='red')
    core_plt.title("🚨 Error Types")
    
    # Panel 4: Bottom-right (2,2) - Performance
    core_plt.subplot(2, 2)
    perf_times = list(range(10))
    response_times = [120, 135, 98, 156, 143, 89, 134, 112, 128, 145]
    core_plt.scatter(perf_times, response_times, color='cyan', label='Response')
    # Add simple trend line
    avg_resp = sum(response_times) / len(response_times)
    core_plt.plot([0, len(perf_times)-1], [avg_resp, avg_resp], color='yellow', label='Avg')
    core_plt.title("⏱️  Performance")
    
    # Display the complete 2x2 grid
    core_plt.show()
    
    plt.log_success("✓ Four-panel dashboard complete - 2x2 grid layout")

def demo_multi_chart_dashboard(use_full_height=False):
    """Create a multi-chart dashboard layout"""
    plt.log_info("🖥️  Creating Multi-Chart Dashboard...")
    
    # Chart 1: System Performance
    cpu_usage = [45, 52, 48, 61, 58, 63, 55, 49, 44, 41]
    memory_usage = [67, 69, 71, 74, 72, 75, 73, 70, 68, 66]
    
    chart1 = plt.Chart(use_banners=True, banner_title="⚡ System Performance Metrics")
    chart1._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
    chart1.line(list(range(10)), cpu_usage, color='red', label='CPU %')
    chart1.line(list(range(10)), memory_usage, color='blue', label='Memory %')
    chart1.title("System Resource Utilization")
    chart1.xlabel("Time (minutes)")
    chart1.ylabel("Usage %")
    chart1.show()
    
    # Chart 2: Network Traffic
    download = [1.2, 2.1, 1.8, 3.2, 2.9, 1.5, 2.3, 1.9, 2.7, 3.1]
    upload = [0.8, 1.1, 0.9, 1.8, 1.5, 0.7, 1.2, 1.0, 1.6, 1.9]
    
    chart2 = plt.Chart(use_banners=True, banner_title="🌐 Network Traffic Analysis")
    chart2._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
    chart2.line(list(range(10)), download, color='green', label='Download')
    chart2.line(list(range(10)), upload, color='orange', label='Upload')
    chart2.title("Network Bandwidth Usage (MB/s)")
    chart2.xlabel("Time (minutes)")
    chart2.ylabel("Speed (MB/s)")
    chart2.show()
    
    # Chart 3: Error Distribution
    error_types = ['HTTP 404', 'HTTP 500', 'Timeout', 'DNS', 'SSL']
    error_counts = [15, 8, 12, 5, 3]
    
    chart3 = plt.Chart(use_banners=True, banner_title="🚨 Error Analysis Dashboard")
    chart3._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
    chart3.bar(list(range(len(error_types))), error_counts, color='red')
    chart3.title("Error Distribution by Type")
    chart3.show()
    
    plt.log_success("✓ Multi-chart dashboard complete")

def demo_mathematical_visualizations(use_full_height=False):
    """Show mathematical function plotting capabilities"""
    plt.log_info("📐 Mathematical Function Visualizations...")
    
    # Trigonometric functions
    x = [i/10 for i in range(-50, 51)]
    sin_vals = [math.sin(val) for val in x]
    cos_vals = [math.cos(val) for val in x]
    tan_vals = [math.tan(val) if abs(math.tan(val)) < 5 else None for val in x]
    # Filter out None values for tan
    tan_x = [x[i] for i in range(len(tan_vals)) if tan_vals[i] is not None]
    tan_clean = [val for val in tan_vals if val is not None]
    
    chart1 = plt.Chart(use_banners=True, banner_title="📊 Trigonometric Functions")
    chart1._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
    chart1.line(x, sin_vals, color='red', label='sin(x)')
    chart1.line(x, cos_vals, color='blue', label='cos(x)')
    chart1.title("Mathematical Function Visualization")
    chart1.xlabel("x")
    chart1.ylabel("f(x)")
    chart1.show()
    
    # Exponential and logarithmic
    x_pos = [i/10 for i in range(1, 31)]
    exp_vals = [math.exp(val/5) for val in x_pos]
    log_vals = [math.log(val) for val in x_pos]
    
    chart2 = plt.Chart(use_banners=True, banner_title="📈 Exponential & Logarithmic")
    chart2._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
    chart2.line(x_pos, exp_vals, color='green', label='exp(x/5)')
    chart2.line(x_pos, log_vals, color='purple', label='ln(x)')
    chart2.title("Growth and Decay Functions")
    chart2.xlabel("x")
    chart2.ylabel("f(x)")
    chart2.show()
    
    plt.log_success("✓ Mathematical visualizations complete")

def demo_data_analysis_workflow(use_full_height=False):
    """Simulate a complete data analysis workflow"""
    plt.log_info("🔍 Data Analysis Workflow Demonstration...")
    
    # Step 1: Raw data exploration
    from chuk_term import ui
    ui.clear_screen()
    plt.log_info("📥 Step 1/3: Loading and exploring raw data...")
    raw_data = [random.gauss(100, 15) for _ in range(50)]
    
    chart1 = plt.Chart(use_banners=True, banner_title="📊 Raw Data Exploration")
    chart1._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
    chart1.scatter(list(range(len(raw_data))), raw_data, color='gray', label='Raw Data')
    chart1.title("Step 1: Raw Data Points")
    chart1.xlabel("Sample Index")
    chart1.ylabel("Value")
    chart1.show()
    
    plt.log_info("✓ Raw data loaded: 50 samples")
    time.sleep(1)
    
    # Step 2: Data processing
    ui.clear_screen()
    plt.log_info("⚙️ Step 2/3: Processing and smoothing data...")
    # Simple moving average
    window = 5
    smoothed_data = []
    for i in range(len(raw_data)):
        start = max(0, i - window//2)
        end = min(len(raw_data), i + window//2 + 1)
        smoothed_data.append(sum(raw_data[start:end]) / (end - start))
    
    chart2 = plt.Chart(use_banners=True, banner_title="🔧 Data Processing Pipeline")
    chart2._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
    chart2.scatter(list(range(len(raw_data))), raw_data, color='lightblue', label='Raw')
    chart2.line(list(range(len(smoothed_data))), smoothed_data, color='red', label='Smoothed')
    chart2.title("Step 2: Data Smoothing & Filtering")
    chart2.xlabel("Sample Index")
    chart2.ylabel("Value")
    chart2.show()
    
    plt.log_info("✓ Data processing complete")
    time.sleep(1)
    
    # Step 3: Statistical analysis
    ui.clear_screen()
    plt.log_info("📈 Step 3/3: Statistical analysis...")
    mean_val = sum(smoothed_data) / len(smoothed_data)
    std_val = (sum((x - mean_val)**2 for x in smoothed_data) / len(smoothed_data))**0.5
    
    # Create histogram-like data
    bins = 10
    min_val, max_val = min(smoothed_data), max(smoothed_data)
    bin_width = (max_val - min_val) / bins
    hist_counts = [0] * bins
    
    for value in smoothed_data:
        bin_idx = min(int((value - min_val) / bin_width), bins - 1)
        hist_counts[bin_idx] += 1
    
    bin_centers = [min_val + (i + 0.5) * bin_width for i in range(bins)]
    
    chart3 = plt.Chart(use_banners=True, banner_title="📊 Statistical Analysis")
    chart3._config['height'] = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
    chart3.bar(list(range(len(hist_counts))), hist_counts, color='green')
    chart3.title(f"Step 3: Distribution (μ={mean_val:.1f}, σ={std_val:.1f})")
    chart3.show()
    
    plt.log_success("✓ Statistical analysis complete")
    plt.log_info(f"📊 Mean: {mean_val:.2f}, Std Dev: {std_val:.2f}")

def demo_theme_showcase(use_full_height=False):
    """Complete Theme Comparison - Comprehensive demonstration of all available themes"""
    plt.log_success("🎨 Starting Comprehensive Theme Showcase")
    plt.log_info("Each theme will display the same data for easy visual comparison\n")
    
    # Create standardized sample data for theme comparison
    x = list(range(15))
    growth_series = [i**1.3 + random.uniform(-2, 2) for i in x]
    linear_series = [i*3 + random.uniform(-4, 4) for i in x] 
    sine_series = [20 + 10*math.sin(i/2) + random.uniform(-2, 2) for i in x]
    decline_series = [50 - i*2.5 + random.uniform(-3, 3) for i in x]
    
    # Get available themes
    try:
        from plotext._themes import get_theme_info
        theme_info = get_theme_info()
        themes_to_show = list(theme_info.keys())
    except ImportError:
        # Fallback themes
        themes_to_show = [
            'chuk_default', 'chuk_dark', 'chuk_light', 'chuk_minimal', 'chuk_terminal',
            'professional', 'scientific', 'neon', 'pastel', 'high_contrast',
            'dracula', 'solarized_dark', 'solarized_light', 'matrix_enhanced', 'cyberpunk'
        ]
    
    plt.log_info(f"📊 Available themes: {len(themes_to_show)}")
    plt.log_info("⏱️  Each theme will display for 2 seconds\n")
    
    for i, theme_name in enumerate(themes_to_show, 1):
        try:
            # Clear terminal before each theme display
            from chuk_term import ui
            ui.clear_screen()
            
            # Get theme description
            if 'theme_info' in locals():
                info = theme_info.get(theme_name, {})
                description = info.get('description', f'{theme_name} theme')
                style_category = info.get('style', 'custom')
            else:
                description = f'{theme_name.replace("_", " ").title()} theme'
                style_category = 'custom'
            
            # Show progress
            plt.log_info(f"[{i:2d}/{len(themes_to_show)}] 🎨 {theme_name.replace('_', ' ').title()}")
            plt.log_info(f"      📝 {description}")
            plt.log_info(f"      🏷️  Category: {style_category}")
            
            # Configure chart (clear first, then apply theme)
            plt.clear_figure()
            
            # Apply the theme after clearing
            plt.theme(theme_name)
            
            # Enable banner mode with theme name
            banner_title = f"🎨 {theme_name.replace('_', ' ').title()} Theme"
            plt.banner_mode(True, banner_title)
            
            # Use terminal-aware sizing that accounts for banner borders (AFTER banner mode is active)
            plot_width = ut.terminal_width() or 75
            chart_height = get_full_terminal_height() if use_full_height else get_optimal_chart_height()
            plt.plotsize(plot_width, chart_height)
            
            # Plot multiple data series to show color variety
            plt.plot(x, growth_series, label='Growth Trend', marker='braille')
            plt.plot(x, linear_series, label='Linear Progress', marker='braille')
            plt.plot(x, sine_series, label='Oscillation', marker='braille')
            plt.scatter(x[::2], decline_series[::2], label='Data Points', marker='●')
            
            # Add chart elements
            plt.title(f"Theme Demonstration: {theme_name.replace('_', ' ').title()}")
            plt.xlabel("Time Period")
            plt.ylabel("Measurement Values")
            
            # Display the chart
            plt.show()
            
            # Show theme category info
            category_icons = {
                'modern': '🔮', 'minimal': '⚪', 'terminal': '💻', 'corporate': '💼',
                'academic': '🎓', 'gaming': '🎮', 'soft': '🌸', 'accessible': '♿',
                'popular': '⭐', 'classic': '👴', 'futuristic': '🚀'
            }
            icon = category_icons.get(style_category, '🎨')
            plt.log_info(f"      {icon} Style: {style_category}")
            
            # Pause for viewing
            time.sleep(2)
            print()  # Add spacing
            
        except Exception as e:
            plt.log_error(f"❌ Error displaying theme '{theme_name}': {str(e)}")
            continue
    
    # Reset to default
    plt.theme('chuk_default')
    plt.banner_mode(False)
    
    plt.log_success("🎉 Theme showcase completed!")
    plt.log_info("✨ All themes displayed the same data for easy comparison")

def demo_image_plotting(use_full_height=False):
    """Demonstrate image plotting capabilities"""
    plt.log_info("🖼️ Image Plotting Demo...")
    
    # Check if PIL is available
    try:
        import PIL
    except ImportError:
        plt.banner_mode(True, "⚠️ PIL Required")
        plt.log_warning("PIL (Pillow) not available for image plotting")
        plt.log_info("💡 Install with: pip install pillow")
        plt.log_info("🔗 Then run this demo to see image functionality")
        plt.banner_mode(False)
        return
    
    import tempfile
    
    # Download and display test image
    temp_path = os.path.join(tempfile.gettempdir(), 'demo_cat.jpg')
    
    try:
        plt.log_info("📥 Downloading test image...")
        plt.download(plt.test_image_url, temp_path, log=False)
        
        # Basic image plot
        plt.banner_mode(True, "🐱 Basic Image Display")
        plt.clear_figure()
        plt.plotsize(70, 20)
        plt.image_plot(temp_path)
        plt.title("Test Image - Color")
        plt.show()
        
        time.sleep(2)
        
        # Grayscale version
        plt.banner_mode(True, "⚫ Grayscale Image")
        plt.clear_figure()
        plt.plotsize(70, 20)
        plt.image_plot(temp_path, grayscale=True)
        plt.title("Test Image - Grayscale")
        plt.show()
        
        time.sleep(2)
        
        # Fast mode
        plt.banner_mode(True, "⚡ Fast Rendering Mode")
        plt.clear_figure()
        plt.plotsize(60, 18)
        plt.image_plot(temp_path, fast=True)
        plt.title("Test Image - Fast Mode")
        plt.show()
        
        time.sleep(2)
        
        # Custom marker style
        plt.banner_mode(True, "🎨 Custom Marker Style")
        plt.clear_figure()
        plt.plotsize(50, 16)
        plt.image_plot(temp_path, marker="CuteCat", style='inverted')
        plt.title("Test Image - Custom Marker")
        plt.show()
        
        plt.banner_mode(False)  # Reset banner mode
        plt.log_success("✓ Image plotting demo complete")
        
    except Exception as e:
        plt.log_error(f"Image demo failed: {str(e)}")
        plt.banner_mode(False)
    finally:
        # Clean up
        if os.path.exists(temp_path):
            plt.delete_file(temp_path, log=False)

def demo_video_functionality(use_full_height=False):
    """Demonstrate video functionality with proper dependency checking"""
    plt.log_info("🎬 Video Functionality Demo...")
    
    # Check if OpenCV is available
    try:
        import cv2
        opencv_available = True
    except ImportError:
        opencv_available = False
    
    # Use local video file from data folder
    data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
    video_path = os.path.join(data_folder, 'chart.mp4')
    
    try:
        if not opencv_available:
            plt.banner_mode(True, "⚠️ OpenCV Required")
            plt.log_warning("OpenCV (cv2) not available for video playback")
            plt.log_info("💡 Install with: pip install opencv-python")
            plt.log_info("🔗 Then run this demo to see video functionality")
            plt.log_info("📋 Video features include:")
            plt.log_info("   • Local video file playback")
            plt.log_info("   • YouTube streaming support")
            plt.log_info("   • Terminal-based video rendering")
            plt.log_info("   • Audio synchronization")
            plt.banner_mode(False)
            return
            
        plt.log_info("📁 Using local video file from data folder...")
        if not os.path.exists(video_path):
            raise Exception(f"Local video file not found: {video_path}")
        
        # No need to download - using local file
        
        if os.path.exists(video_path) and os.path.getsize(video_path) > 0:
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            plt.banner_mode(True, "🎥 Video Information")
            plt.log_success(f"✓ Local video file found!")
            plt.log_info(f"📋 File size: {file_size:.2f} MB")
            plt.log_info(f"📁 Video path: data/chart.mp4")
            plt.log_info("🎮 Video playback functionality available via:")
            plt.log_info("   plt.play_video(path)")
            plt.log_info("   plt.play_video(path, from_youtube=True)")
            
            # Create a simple chart to demonstrate video metadata
            plt.clear_figure()
            # Use smaller size (terminal width - 10 for margins)
            plot_width = max(ut.terminal_width() - 10, 50)
            plt.plotsize(plot_width, 12)
            
            # Sample video stats visualization
            frames = list(range(0, 100, 10))
            quality = [random.randint(720, 1080) for _ in frames]
            
            plt.scatter(frames, quality, color='red', label='Quality')
            plt.title("Sample Video Quality Metrics")
            plt.xlabel("Frame Number")
            plt.ylabel("Resolution (p)")
            plt.show()
            
            plt.banner_mode(False)
            
            # Actually play the video with proper sizing
            plt.log_info("🎬 Starting video playback...")
            
            # Set video display size similar to other demos
            # Use terminal width aware sizing with appropriate height
            video_width = max(ut.terminal_width() - 6, 50)  # Account for banners
            video_height = max(int(video_width * 0.4), 16)  # 40% aspect ratio, minimum 16 rows
            plt.plotsize(video_width, video_height)
            
            plt.play_video(video_path)
            plt.log_success("✓ Video playback complete!")
            plt.log_success("✓ Video functionality demo complete")
        else:
            raise Exception("Local video file not found or is empty")
        
    except Exception as e:
        plt.log_error(f"Video demo failed: {str(e)}")
        plt.banner_mode(False)
    finally:
        # No cleanup needed - using local file from data folder
        pass

def demo_multimedia_showcase(use_full_height=False):
    """Combined multimedia demonstration"""
    plt.log_info("🎭 Multimedia Showcase Demo...")
    
    # Check if PIL is available for image functionality
    pil_available = True
    try:
        import PIL
    except ImportError:
        pil_available = False
    
    # Check if OpenCV is available for video functionality
    opencv_available = True
    try:
        import cv2
    except ImportError:
        opencv_available = False
    
    import tempfile
    
    # Image path
    image_path = os.path.join(tempfile.gettempdir(), 'showcase_image.jpg')
    
    try:
        # Multimedia showcase banner
        plt.banner_mode(True, "🎪 Multimedia Capabilities")
        
        # Show capabilities info
        plt.log_info("🖼️ Image Plotting Features:")
        if pil_available:
            plt.log_success("   ✓ Color and grayscale rendering")
            plt.log_success("   ✓ Custom markers and styles")  
            plt.log_success("   ✓ Fast rendering mode")
            plt.log_success("   ✓ Automatic size adaptation")
        else:
            plt.log_warning("   ⚠️ Requires PIL/Pillow (pip install pillow)")
        
        plt.log_info("\n🎬 Video Features:")
        if opencv_available:
            plt.log_success("   ✓ Local video playback")
            plt.log_success("   ✓ YouTube streaming support")
            plt.log_success("   ✓ Audio synchronization")
            plt.log_success("   ✓ Terminal size adaptation")
        else:
            plt.log_warning("   ⚠️ Requires OpenCV (pip install opencv-python)")
        
        if pil_available:
            # Download and display test image
            plt.download(plt.test_image_url, image_path, log=False)
            
            # Display sample image in showcase
            plt.clear_figure()
            plt.plotsize(65, 18)
            plt.image_plot(image_path, grayscale=True)
            plt.title("Multimedia Showcase - Sample Image")
            plt.show()
        else:
            plt.log_info("🖼️ Image demo skipped - PIL not available")
        
        plt.banner_mode(False)
        plt.log_success("✓ Multimedia showcase complete")
        
    except Exception as e:
        plt.log_error(f"Multimedia showcase failed: {str(e)}")
        plt.banner_mode(False)
    finally:
        # Clean up
        if os.path.exists(image_path):
            plt.delete_file(image_path, log=False)

def interactive_menu():
    """Main interactive menu"""
    while True:
        plt.log_info("\n🎮 Interactive Demo Menu")
        print("\nChoose a demonstration:")
        print("1. 🎭 Banner Styles & Themes")
        print("2. 📊 Interactive-Style Charts")
        print("3. 🖥️  Multi-Chart Dashboard")
        print("4. 📊 Four-Panel Dashboard (fits terminal)")
        print("5. 📐 Mathematical Visualizations")
        print("6. 🔍 Data Analysis Workflow")
        print("7. 🎨 Theme Showcase")
        print("8. 🖼️ Image Plotting Demo")
        print("9. 🎬 Video Functionality Demo")
        print("10. 🎭 Multimedia Showcase")
        print("11. 🎯 Run All Demos")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice (0-11): ").strip()
            
            if choice == '0':
                plt.log_success("👋 Thanks for exploring Plotext!")
                break
            elif choice == '1':
                demo_banner_styles()
            elif choice == '2':
                demo_interactive_charts()
            elif choice == '3':
                demo_multi_chart_dashboard()
            elif choice == '4':
                demo_four_panel_dashboard()
            elif choice == '5':
                demo_mathematical_visualizations()
            elif choice == '6':
                demo_data_analysis_workflow(use_full_height=True)
            elif choice == '7':
                demo_theme_showcase()
            elif choice == '8':
                demo_image_plotting()
            elif choice == '9':
                demo_video_functionality()
            elif choice == '10':
                demo_multimedia_showcase()
            elif choice == '11':
                import time
                from chuk_term import ui
                
                plt.log_info("🚀 Running all demonstrations...")
                plt.log_info("⏱️  Each demo will display for a few seconds before continuing...")
                time.sleep(2)  # Initial pause
                
                # Run all demos with screen clearing before each one, using full terminal height
                ui.clear_screen()
                plt.log_info("🎭 Starting Demo 1/10: Banner Styles & Themes")
                demo_banner_styles(use_full_height=True)
                time.sleep(3)
                
                ui.clear_screen()
                plt.log_info("📊 Starting Demo 2/10: Interactive-Style Charts")
                demo_interactive_charts(use_full_height=True)
                time.sleep(3)
                
                ui.clear_screen()
                plt.log_info("🖥️  Starting Demo 3/10: Multi-Chart Dashboard")
                demo_multi_chart_dashboard(use_full_height=True)
                time.sleep(3)
                
                ui.clear_screen()
                plt.log_info("📊 Starting Demo 4/10: Four-Panel Dashboard")
                demo_four_panel_dashboard(use_full_height=True)
                time.sleep(3)
                
                ui.clear_screen()
                plt.log_info("📐 Starting Demo 5/10: Mathematical Visualizations")
                demo_mathematical_visualizations(use_full_height=True)
                time.sleep(3)
                
                ui.clear_screen()
                plt.log_info("🔍 Starting Demo 6/10: Data Analysis Workflow")
                demo_data_analysis_workflow(use_full_height=True)
                time.sleep(3)
                
                ui.clear_screen()
                plt.log_info("🎨 Starting Demo 7/10: Theme Showcase")
                demo_theme_showcase(use_full_height=True)
                time.sleep(2)
                
                ui.clear_screen()
                plt.log_info("🖼️ Starting Demo 8/10: Image Plotting")
                demo_image_plotting(use_full_height=True)
                time.sleep(2)
                
                ui.clear_screen()
                plt.log_info("🎬 Starting Demo 9/10: Video Functionality")
                demo_video_functionality(use_full_height=True)
                time.sleep(2)
                
                ui.clear_screen()
                plt.log_info("🎭 Starting Demo 10/10: Multimedia Showcase")
                demo_multimedia_showcase(use_full_height=True)
                time.sleep(2)
                
                ui.clear_screen()
                plt.log_success("🎉 All demonstrations complete!")
                plt.log_info("📋 Press Enter to return to the main menu...")
                input()
            else:
                plt.log_warning("⚠️ Invalid choice. Please select 0-11.")
                
        except KeyboardInterrupt:
            plt.log_info("\n👋 Demo interrupted by user")
            break
        except Exception as e:
            plt.log_error(f"❌ Error: {str(e)}")

def main():
    """Main demo function"""
    try:
        # Display welcome
        welcome_screen()
        
        # Run interactive menu
        interactive_menu()
        
    except Exception as e:
        plt.log_error(f"💥 Demo failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()