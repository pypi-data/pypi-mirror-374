# Themes and Styling

- [Overview](#overview)
- [Chuk-Term Compatible Themes](#chuk-term-compatible-themes)
- [Theme Categories](#theme-categories)
- [Using Themes](#using-themes)
- [Theme Showcase](#theme-showcase)
- [Custom Themes](#custom-themes)
- [Banner Integration](#banner-integration)

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide)

## Overview

Plotext now includes a comprehensive theme library that provides chuk-term compatible color schemes and styling options. Themes control the visual appearance of charts including colors, backgrounds, and styling elements.

### Theme Structure

Each plotext theme consists of:
- **Canvas color** - Background color of the chart area
- **Axes color** - Color of axes lines and labels
- **Ticks color** - Color of axis tick marks and numbers
- **Ticks style** - Style of ticks (bold, normal, etc.)
- **Color sequence** - Array of colors used for data series

### Key Benefits

- **Consistent styling** - Themes provide consistent visual appearance
- **Chuk-term integration** - Themes match chuk-term's visual themes
- **Easy switching** - Change the entire chart appearance with one command
- **Accessibility** - High contrast and accessible themes available
- **Professional** - Themes suitable for corporate and academic use

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Themes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/themes.md#themes-and-styling)

## Chuk-Term Compatible Themes

The following themes are designed to match chuk-term's visual themes:

### Core Chuk-Term Themes

- **`chuk_default`** - Default chuk-term theme with cyan and blue accents
- **`chuk_dark`** - Dark theme with bright accent colors on black background
- **`chuk_light`** - Light theme with muted colors for light terminals
- **`chuk_minimal`** - Minimal theme with no colors, focus on structure
- **`chuk_terminal`** - Basic terminal theme using standard ANSI colors

### Example

```python
import plotext_plus as plt

# Apply chuk-term dark theme
plt.theme('chuk_dark')

# Create chart - will use dark theme colors
plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.title("Dark Theme Example")
plt.show()
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Themes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/themes.md#themes-and-styling)

## Theme Categories

Themes are organized into categories based on their intended use:

### Modern Themes
Professional themes for contemporary applications:
- `chuk_default` - Modern cyan and blue styling
- `chuk_dark` - Dark mode with bright accents
- `chuk_light` - Light mode with muted colors

### Corporate Themes
Business and professional use:
- `professional` - Corporate-friendly blues and grays
- `scientific` - Academic theme inspired by matplotlib
- `high_contrast` - Accessible high contrast theme

### Popular Community Themes  
Well-known color schemes:
- `dracula` - Popular dark theme with purple and pink accents
- `solarized_dark` - Dark version of the popular Solarized theme
- `solarized_light` - Light version of Solarized theme

### Creative Themes
Artistic and expressive themes:
- `neon` - Gaming-inspired bright neon colors
- `cyberpunk` - Futuristic pink and cyan theme
- `pastel` - Soft, muted colors for gentle visualization

### Accessibility Themes
Designed for accessibility and readability:
- `high_contrast` - Maximum contrast for visibility
- `chuk_minimal` - Simple, clean appearance

### Classic Themes
Traditional and retro styling:
- `matrix_enhanced` - Enhanced Matrix theme with green on black
- `chuk_terminal` - Classic terminal styling

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Themes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/themes.md#themes-and-styling)

## Using Themes

### Basic Theme Application

```python
import plotext_plus as plt

# Apply a theme before creating charts
plt.theme('dracula')

# All subsequent charts will use the Dracula theme
plt.plot(x, y)
plt.title("Chart with Dracula Theme")
plt.show()
```

### With Chart Classes

```python
import plotext_plus as plt

# Apply theme to specialized chart classes
chart = plt.ScatterChart(x, y, use_banners=True, banner_title="Analysis")
chart.theme('scientific')  # Use scientific theme
chart.title("Scientific Analysis").show()
```

### Theme Switching

```python
import plotext_plus as plt

# Show same data with different themes
data_x = [1, 2, 3, 4, 5]
data_y = [1, 4, 9, 16, 25]

themes_to_try = ['chuk_default', 'chuk_dark', 'professional', 'dracula']

for theme_name in themes_to_try:
    plt.theme(theme_name)
    plt.clear_figure()
    plt.plot(data_x, data_y)
    plt.title(f"Theme: {theme_name}")
    plt.show()
```

### Banner Mode Integration

```python
import plotext_plus as plt

# Themes work seamlessly with banner mode
plt.theme('cyberpunk')
plt.banner_mode(True, "🚀 Futuristic Analysis")

plt.plot(x, y)
plt.title("Cyberpunk Styled Chart")
plt.show()

plt.banner_mode(False)  # Disable banner mode
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Themes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/themes.md#themes-and-styling)

## Theme Showcase

### Interactive Theme Browser

Use the interactive theme showcase to explore all available themes:

```bash
python examples/theme_showcase_demo.py
```

This demo provides:
- Complete theme comparison with the same data
- Theme categories overview
- Interactive theme browser
- Chart classes with different themes

### Programmatic Theme Information

```python
# Get information about available themes
from plotext._themes import get_theme_info

theme_info = get_theme_info()
for name, info in theme_info.items():
    print(f"{name}: {info['description']}")
    print(f"  Style: {info['style']}")
    print(f"  Colors: {', '.join(info['primary_colors'])}")
    print()
```

### Theme Comparison Example

```python
import plotext_plus as plt

def compare_themes(data_x, data_y, theme_list):
    """Compare multiple themes with the same data"""
    for theme_name in theme_list:
        plt.theme(theme_name)
        plt.clear_figure()
        plt.banner_mode(True, f"Theme: {theme_name}")
        
        plt.plot(data_x, data_y, label='Data Series')
        plt.title(f"Comparison: {theme_name}")
        plt.xlabel("X Values")
        plt.ylabel("Y Values") 
        plt.show()
        
        input("Press Enter for next theme...")

# Usage
x = list(range(10))
y = [i**2 for i in x]
themes = ['chuk_dark', 'professional', 'dracula', 'solarized_light']
compare_themes(x, y, themes)
```

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Themes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/themes.md#themes-and-styling)

## Custom Themes

### Creating Custom Themes

You can create custom themes by defining the theme components:

```python
import plotext_plus as plt

# Define a custom theme
# Format: [canvas_color, axes_color, ticks_color, ticks_style, color_sequence]
custom_colors = [(255, 100, 150), (100, 255, 150), (150, 100, 255)]  # RGB tuples
custom_theme = ['black', (200, 200, 200), 'white', 'bold', custom_colors]

# Apply custom theme (requires modifying plotext._dict.themes)
# This is an advanced feature for future enhancement
```

### Modifying Existing Themes

```python
import plotext_plus as plt

# Start with an existing theme and modify specific aspects
plt.theme('chuk_dark')

# You can override specific colors after setting the theme
# (This requires using lower-level plotext functions)
plt.canvas_color('black')
plt.axes_color('cyan')
```

### Theme Development Tips

- **Test accessibility** - Ensure themes work for users with different visual needs
- **Consider context** - Choose appropriate themes for the intended audience
- **Maintain contrast** - Ensure sufficient contrast between elements
- **Test on different terminals** - Themes may appear differently across terminals

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Themes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/themes.md#themes-and-styling)

## Banner Integration

### Automatic Banner Styling

Themes automatically integrate with chuk-term banner mode:

```python
import plotext_plus as plt

# Different themes provide different banner styling
themes_and_styles = {
    'chuk_default': 'Modern rounded banners',
    'chuk_minimal': 'No banner decoration', 
    'professional': 'Heavy border banners',
    'cyberpunk': 'Futuristic styling'
}

for theme_name, description in themes_and_styles.items():
    plt.theme(theme_name)
    plt.banner_mode(True, f"Theme: {theme_name}")
    
    plt.plot([1, 2, 3], [1, 4, 2])
    plt.title(description)
    plt.show()
```

### Theme-Aware Banner Configuration

The theme system provides banner styling recommendations:

```python
from plotext._themes import get_chuk_theme_for_banner_mode

# Get banner configuration for a theme
banner_config = get_chuk_theme_for_banner_mode('cyberpunk')
print(banner_config)
# Output: {'style': 'rounded', 'padding': (0, 2)}
```

### Best Practices

- **Match banner to theme** - Use banner styles that complement the theme
- **Consider readability** - Ensure banner text remains readable with theme colors
- **Test combinations** - Verify theme/banner combinations work well together
- **Consistent styling** - Use consistent banner styling within an application

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Themes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/themes.md#themes-and-styling)

## Advanced Theme Usage

### Theme in Chart Classes

```python
import plotext_plus as plt

# Different chart types with coordinated theming
plt.theme('scientific')

# Scatter plot
scatter = plt.ScatterChart(x1, y1, use_banners=True, banner_title="📊 Observations")
scatter.title("Experimental Data").show()

# Bar chart with same theme
bar = plt.BarChart(labels, values, use_banners=True, banner_title="📈 Results")
bar.title("Summary Statistics").show()
```

### Dynamic Theme Selection

```python
import plotext_plus as plt

def auto_select_theme(data_type, context):
    """Automatically select appropriate theme based on context"""
    if context == 'presentation':
        return 'professional'
    elif context == 'research':
        return 'scientific' 
    elif data_type == 'financial':
        return 'chuk_dark'
    else:
        return 'chuk_default'

# Usage
theme = auto_select_theme('financial', 'presentation')
plt.theme(theme)
```

### Performance Considerations

- **Theme switching** - Minimal performance impact
- **Color calculations** - Themes are pre-computed for efficiency
- **Banner integration** - Automatic styling with no performance cost
- **Memory usage** - Themes add minimal memory overhead

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Themes](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/themes.md#themes-and-styling)