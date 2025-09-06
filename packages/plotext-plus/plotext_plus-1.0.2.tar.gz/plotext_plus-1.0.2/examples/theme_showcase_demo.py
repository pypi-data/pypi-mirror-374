#!/usr/bin/env python3
"""
Plotext Theme Showcase - Comprehensive demonstration of all available themes
Shows how different themes affect the same data visualization for easy comparison
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import plotext_plus as plt
# Use the clean public API
from plotext_plus import themes, utilities as ut
import random
import time
import math

def create_sample_data():
    """Create standardized sample data for theme comparison"""
    x = list(range(15))
    
    # Different types of data series
    growth_series = [i**1.3 + random.uniform(-2, 2) for i in x]
    linear_series = [i*3 + random.uniform(-4, 4) for i in x] 
    sine_series = [20 + 10*math.sin(i/2) + random.uniform(-2, 2) for i in x]
    decline_series = [50 - i*2.5 + random.uniform(-3, 3) for i in x]
    
    return x, growth_series, linear_series, sine_series, decline_series

def demo_theme_comparison():
    """Show the same chart with different themes for direct comparison"""
    plt.log_success("🎨 Starting Comprehensive Theme Showcase")
    plt.log_info("Each theme will display the same data for easy visual comparison\n")
    
    # Get sample data
    x, y1, y2, y3, y4 = create_sample_data()
    
    # Get available themes
    try:
        theme_info = themes.get_theme_info()
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
            
            # Use terminal-aware sizing that accounts for banner borders
            plot_width = plt.terminal_width() or 75
            plt.plotsize(plot_width, 20)
            
            # Enable banner mode with theme name
            banner_title = f"🎨 {theme_name.replace('_', ' ').title()} Theme"
            plt.banner_mode(True, banner_title)
            
            # Plot multiple data series to show color variety
            plt.plot(x, y1, label='Growth Trend', marker='braille')
            plt.plot(x, y2, label='Linear Progress', marker='braille')
            plt.plot(x, y3, label='Oscillation', marker='braille')
            plt.scatter(x[::2], y4[::2], label='Data Points', marker='●')
            
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

def demo_theme_categories():
    """Show themes grouped by category"""
    plt.log_info("📂 Themes by Category\n")
    
    try:
        # Use public themes API
        theme_info = themes.get_theme_info()
        
        # Group themes by style
        categories = {}
        for theme_name, info in theme_info.items():
            style = info.get('style', 'other')
            if style not in categories:
                categories[style] = []
            categories[style].append(theme_name)
        
        # Show each category
        for category, theme_list in categories.items():
            plt.log_info(f"🏷️  {category.upper()} ({len(theme_list)} themes)")
            for theme in theme_list:
                info = theme_info[theme]
                plt.log_info(f"   • {theme}: {info['description']}")
            print()
            
    except ImportError:
        plt.log_warning("Theme categorization not available")

def demo_chart_classes_with_themes():
    """Show how different chart classes look with various themes"""
    plt.log_info("🔗 Chart Classes + Themes Demo\n")
    
    # Sample data
    x = list(range(8))
    y = [i*i for i in x]
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [random.randint(10, 50) for _ in categories]
    
    demo_themes = ['chuk_dark', 'professional', 'dracula', 'solarized_light']
    
    for theme_name in demo_themes:
        plt.log_info(f"🎨 Demonstrating {theme_name} with specialized charts")
        
        # Apply theme
        plt.theme(theme_name)
        
        # ScatterChart
        scatter_chart = plt.ScatterChart(
            x, y, color='auto', 
            use_banners=True, 
            banner_title=f"📊 Scatter - {theme_name.title()}"
        )
        scatter_chart.title("ScatterChart Example").show()
        
        time.sleep(1)
        
        # BarChart
        bar_chart = plt.BarChart(
            categories, values, color='auto',
            use_banners=True,
            banner_title=f"📊 Bar - {theme_name.title()}"
        )
        bar_chart.title("BarChart Example").show()
        
        time.sleep(1)
        
        # LineChart
        line_chart = plt.LineChart(
            x, [i*1.5 for i in x], color='auto',
            use_banners=True,
            banner_title=f"📊 Line - {theme_name.title()}"
        )
        line_chart.title("LineChart Example").show()
        
        time.sleep(1.5)
    
    plt.theme('chuk_default')
    plt.log_success("✓ Chart classes + themes demo complete")

def interactive_theme_browser():
    """Interactive theme browser"""
    plt.log_info("🔍 Interactive Theme Browser")
    plt.log_info("Browse themes interactively (press Enter between themes)\n")
    
    try:
        # Use public themes API
        theme_info = themes.get_theme_info()
        available_themes = list(theme_info.keys())
    except ImportError:
        available_themes = ['chuk_default', 'chuk_dark', 'chuk_light', 'professional', 'dracula']
    
    # Sample data
    x, y1, y2, y3, y4 = create_sample_data()
    
    for theme_name in available_themes:
        try:
            plt.clear_figure()
            plt.theme(theme_name)
            # Use banner-aware sizing for interactive browser
            plot_width = plt.terminal_width() or 70
            plt.plotsize(plot_width, 18)
            plt.banner_mode(True, f"🎨 {theme_name.replace('_', ' ').title()}")
            
            # Create varied visualization
            plt.plot(x, y1, label='Series 1')
            plt.plot(x, y2, label='Series 2')
            plt.scatter(x[::3], y3[::3], label='Points')
            
            plt.title(f"Interactive Browser: {theme_name}")
            plt.xlabel("X Axis")
            plt.ylabel("Y Axis") 
            plt.show()
            
            if 'theme_info' in locals():
                info = theme_info.get(theme_name, {})
                plt.log_info(f"📝 {info.get('description', 'No description')}")
                plt.log_info(f"🎯 Style: {info.get('style', 'unknown')}")
                plt.log_info(f"🎨 Primary colors: {', '.join(info.get('primary_colors', []))}")
            
            user_input = input(f"\nPress Enter for next theme, 'q' to quit: ")
            if user_input.lower() == 'q':
                break
                
        except Exception as e:
            plt.log_warning(f"Error with theme {theme_name}: {e}")
            continue
    
    plt.theme('chuk_default')
    plt.banner_mode(False)

def main():
    """Main demo menu"""
    plt.log_success("🎨 Plotext Theme Library Showcase")
    plt.log_info("Comprehensive demonstration of chuk-term compatible themes\n")
    
    while True:
        print("\n" + "="*60)
        plt.log_info("🎮 Theme Showcase Menu")
        print("1. 🔄 Complete Theme Comparison (auto)")
        print("2. 📂 Theme Categories Overview")
        print("3. 🔗 Chart Classes + Themes")
        print("4. 🔍 Interactive Theme Browser")
        print("5. 🎯 Quick Theme Test")
        print("0. Exit")
        
        try:
            choice = input("\nSelect option (0-5): ").strip()
            
            if choice == '0':
                plt.log_success("👋 Thanks for exploring Plotext themes!")
                break
            elif choice == '1':
                demo_theme_comparison()
            elif choice == '2':
                demo_theme_categories()
            elif choice == '3':
                demo_chart_classes_with_themes()
            elif choice == '4':
                interactive_theme_browser()
            elif choice == '5':
                # Quick test with a few themes
                plt.log_info("🎯 Quick theme test with 3 popular themes")
                for theme in ['chuk_dark', 'dracula', 'professional']:
                    plt.clear_figure()
                    plt.theme(theme)
                    # Use banner-aware sizing for quick test
                    plot_width = plt.terminal_width() or 60
                    plt.plotsize(plot_width, 12)
                    plt.banner_mode(True, f"Test: {theme}")
                    plt.plot([1,2,3,4], [1,4,2,3])
                    plt.title(f"Quick Test: {theme}")
                    plt.show()
                    time.sleep(1)
                plt.theme('chuk_default')
                plt.banner_mode(False)
            else:
                plt.log_warning("⚠️ Invalid choice. Please select 0-5.")
                
        except KeyboardInterrupt:
            plt.log_info("\n👋 Demo interrupted by user")
            break
        except Exception as e:
            plt.log_error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()