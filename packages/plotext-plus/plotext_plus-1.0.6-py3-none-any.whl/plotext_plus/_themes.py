#!/usr/bin/env python3
"""
Plotext Theme Library - Compatible with chuk-term themes
Provides color schemes and styling that match chuk-term's visual themes.
"""

from plotext_plus._dict import no_color, color_sequence

# Color definitions used across themes
rgb_colors = {
    # Chuk-term compatible colors
    'bright_green': (0, 255, 0),
    'bright_red': (255, 0, 0),
    'bright_yellow': (255, 255, 0),
    'bright_cyan': (0, 255, 255),
    'bright_white': (255, 255, 255),
    'bright_blue': (0, 100, 255),
    'bright_magenta': (255, 0, 255),
    
    'dark_green': (0, 128, 0),
    'dark_red': (128, 0, 0),
    'dark_goldenrod': (184, 134, 11),
    'dark_cyan': (0, 139, 139),
    'dark_blue': (0, 0, 139),
    'dark_magenta': (139, 0, 139),
    
    # Dracula theme colors
    'dracula_background': (40, 42, 54),
    'dracula_foreground': (248, 248, 242),
    'dracula_cyan': (139, 233, 253),
    'dracula_green': (80, 250, 123),
    'dracula_orange': (255, 184, 108),
    'dracula_pink': (255, 121, 198),
    'dracula_purple': (189, 147, 249),
    
    # Solarized colors
    'sol_base03': (0, 43, 54),      # darkest
    'sol_base02': (7, 54, 66),
    'sol_base01': (88, 110, 117),   # dark gray
    'sol_base00': (101, 123, 131),  # light gray
    'sol_base0': (131, 148, 150),   # main text (dark)
    'sol_base1': (147, 161, 161),   # secondary text
    'sol_base2': (238, 232, 213),   # background highlights
    'sol_base3': (253, 246, 227),   # lightest
    'sol_red': (220, 50, 47),
    'sol_green': (133, 153, 0),
    'sol_yellow': (181, 137, 0),
    'sol_blue': (38, 139, 210),
    'sol_magenta': (211, 54, 130),
    'sol_cyan': (42, 161, 152),
    
    # Terminal colors
    'term_black': (0, 0, 0),
    'term_white': (255, 255, 255),
    'term_gray': (128, 128, 128),
}

def create_chuk_term_themes():
    """
    Create a theme dictionary compatible with chuk-term themes.
    Each theme follows plotext format: [canvas_color, axes_color, ticks_color, ticks_style, color_sequence]
    """
    themes = {}
    
    # === DEFAULT THEME ===
    # Matches chuk-term default theme (cyan primary, blue secondary)
    sequence = [rgb_colors['bright_cyan'], rgb_colors['bright_blue'], rgb_colors['bright_magenta'], 
               rgb_colors['bright_green'], rgb_colors['bright_yellow'], rgb_colors['bright_red']]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['chuk_default'] = ['white', rgb_colors['bright_cyan'], rgb_colors['dark_cyan'], 'bold', sequence]
    
    # === DARK THEME ===
    # Matches chuk-term dark theme (bright colors on dark background)
    sequence = [rgb_colors['bright_cyan'], rgb_colors['bright_green'], rgb_colors['bright_yellow'],
               rgb_colors['bright_magenta'], rgb_colors['bright_blue'], rgb_colors['bright_red']]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['chuk_dark'] = ['black', rgb_colors['bright_cyan'], rgb_colors['bright_white'], 'bold', sequence]
    
    # === LIGHT THEME ===
    # Matches chuk-term light theme (dark colors on light background)
    sequence = [rgb_colors['dark_cyan'], rgb_colors['dark_green'], rgb_colors['dark_goldenrod'],
               rgb_colors['dark_magenta'], rgb_colors['dark_blue'], rgb_colors['dark_red']]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['chuk_light'] = ['white', rgb_colors['dark_cyan'], 'black', no_color, sequence]
    
    # === MINIMAL THEME ===
    # Matches chuk-term minimal theme (no colors, just structure)
    sequence = ['white', 'white', 'white', 'white', 'white']
    sequence += [el for el in color_sequence if el not in sequence]
    themes['chuk_minimal'] = [no_color, 'white', 'white', no_color, sequence]
    
    # === TERMINAL THEME ===
    # Matches chuk-term terminal theme (basic ANSI colors)
    sequence = ['cyan', 'blue', 'magenta', 'green', 'yellow', 'red']
    sequence += [el for el in color_sequence if el not in sequence]
    themes['chuk_terminal'] = ['black', 'white', 'white', 'bold', sequence]
    
    # === ENHANCED THEMES ===
    
    # Professional/Corporate theme
    sequence = [rgb_colors['dark_blue'], rgb_colors['dark_cyan'], rgb_colors['dark_green'],
               (100, 100, 100), (150, 150, 150), (200, 100, 50)]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['professional'] = ['white', rgb_colors['dark_blue'], 'black', no_color, sequence]
    
    # Scientific theme (inspired by matplotlib defaults)
    sequence = [(31, 119, 180), (255, 127, 14), (44, 160, 44), (214, 39, 40),
               (148, 103, 189), (140, 86, 75), (227, 119, 194), (127, 127, 127)]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['scientific'] = ['white', (70, 70, 70), (50, 50, 50), no_color, sequence]
    
    # Gaming/Neon theme
    sequence = [(0, 255, 255), (255, 0, 255), (0, 255, 0), (255, 255, 0),
               (255, 0, 0), (0, 100, 255), (255, 100, 0)]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['neon'] = ['black', (0, 255, 255), (255, 255, 255), 'bold', sequence]
    
    # Pastel theme (soft, muted colors)
    sequence = [(173, 216, 230), (255, 182, 193), (221, 160, 221), (144, 238, 144),
               (255, 218, 185), (230, 230, 250), (255, 240, 245)]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['pastel'] = ['white', (150, 150, 200), (100, 100, 100), no_color, sequence]
    
    # High contrast theme (for accessibility)
    sequence = ['black', 'white', rgb_colors['bright_yellow'], rgb_colors['bright_cyan'],
               rgb_colors['bright_magenta'], rgb_colors['bright_green']]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['high_contrast'] = ['white', 'black', 'black', 'bold', sequence]
    
    # === POPULAR THEMES ===
    
    # Dracula theme - popular dark theme with purples and pinks
    sequence = [rgb_colors['dracula_cyan'], rgb_colors['dracula_green'], rgb_colors['dracula_orange'],
               rgb_colors['dracula_pink'], rgb_colors['dracula_purple']]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['dracula'] = [rgb_colors['dracula_background'], rgb_colors['dracula_foreground'], 
                        rgb_colors['dracula_cyan'], 'bold', sequence]
    
    # Solarized Dark
    sequence = [rgb_colors['sol_cyan'], rgb_colors['sol_green'], rgb_colors['sol_yellow'],
               rgb_colors['sol_blue'], rgb_colors['sol_magenta'], rgb_colors['sol_red']]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['solarized_dark'] = [rgb_colors['sol_base03'], rgb_colors['sol_base0'], 
                               rgb_colors['sol_base1'], no_color, sequence]
    
    # Solarized Light
    sequence = [rgb_colors['sol_cyan'], rgb_colors['sol_green'], rgb_colors['sol_yellow'],
               rgb_colors['sol_blue'], rgb_colors['sol_magenta'], rgb_colors['sol_red']]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['solarized_light'] = [rgb_colors['sol_base3'], rgb_colors['sol_base01'], 
                                rgb_colors['sol_base00'], no_color, sequence]
    
    # Matrix theme (enhanced version)
    sequence = [(0, 255, 65), (0, 200, 50), (0, 150, 35), (0, 100, 20)]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['matrix_enhanced'] = ['black', (0, 255, 65), (0, 255, 65), 'bold', sequence]
    
    # Cyberpunk theme
    sequence = [(255, 20, 147), (0, 255, 255), (255, 215, 0), (124, 252, 0),
               (255, 69, 0), (138, 43, 226)]
    sequence += [el for el in color_sequence if el not in sequence]
    themes['cyberpunk'] = ['black', (255, 20, 147), (0, 255, 255), 'bold', sequence]
    
    return themes

def get_theme_info():
    """
    Get information about all available themes.
    
    Returns:
        dict: Theme information with descriptions and color palettes
    """
    return {
        # Chuk-term compatible themes
        'chuk_default': {
            'name': 'Chuk Default',
            'description': 'Default chuk-term theme with cyan and blue accents',
            'primary_colors': ['cyan', 'blue', 'magenta'],
            'background': 'white',
            'style': 'modern'
        },
        'chuk_dark': {
            'name': 'Chuk Dark',
            'description': 'Dark theme with bright accent colors',
            'primary_colors': ['bright_cyan', 'bright_green', 'bright_yellow'],
            'background': 'black', 
            'style': 'modern'
        },
        'chuk_light': {
            'name': 'Chuk Light',
            'description': 'Light theme with muted colors for light terminals',
            'primary_colors': ['dark_cyan', 'dark_green', 'dark_blue'],
            'background': 'white',
            'style': 'modern'
        },
        'chuk_minimal': {
            'name': 'Chuk Minimal',
            'description': 'Minimal theme with no colors, focus on structure',
            'primary_colors': ['white'],
            'background': 'none',
            'style': 'minimal'
        },
        'chuk_terminal': {
            'name': 'Chuk Terminal',
            'description': 'Basic terminal theme using ANSI colors',
            'primary_colors': ['cyan', 'blue', 'magenta'],
            'background': 'black',
            'style': 'terminal'
        },
        
        # Enhanced themes
        'professional': {
            'name': 'Professional',
            'description': 'Corporate-friendly theme with muted blues',
            'primary_colors': ['dark_blue', 'dark_cyan', 'gray'],
            'background': 'white',
            'style': 'corporate'
        },
        'scientific': {
            'name': 'Scientific',
            'description': 'Scientific theme inspired by matplotlib',
            'primary_colors': ['blue', 'orange', 'green'],
            'background': 'white',
            'style': 'academic'
        },
        'neon': {
            'name': 'Neon',
            'description': 'Gaming-inspired theme with bright neon colors',
            'primary_colors': ['neon_cyan', 'neon_magenta', 'neon_green'],
            'background': 'black',
            'style': 'gaming'
        },
        'pastel': {
            'name': 'Pastel',
            'description': 'Soft, muted colors for gentle visualization',
            'primary_colors': ['light_blue', 'light_pink', 'light_green'],
            'background': 'white',
            'style': 'soft'
        },
        'high_contrast': {
            'name': 'High Contrast',
            'description': 'High contrast theme for accessibility',
            'primary_colors': ['black', 'white', 'yellow'],
            'background': 'white',
            'style': 'accessible'
        },
        
        # Popular themes
        'dracula': {
            'name': 'Dracula',
            'description': 'Popular dark theme with purple and pink accents',
            'primary_colors': ['dracula_cyan', 'dracula_pink', 'dracula_purple'],
            'background': 'dracula_dark',
            'style': 'popular'
        },
        'solarized_dark': {
            'name': 'Solarized Dark',
            'description': 'Popular dark theme with carefully chosen colors',
            'primary_colors': ['sol_cyan', 'sol_green', 'sol_blue'],
            'background': 'solarized_dark',
            'style': 'popular'
        },
        'solarized_light': {
            'name': 'Solarized Light',
            'description': 'Light version of the popular Solarized theme',
            'primary_colors': ['sol_cyan', 'sol_green', 'sol_blue'],
            'background': 'solarized_light',
            'style': 'popular'
        },
        'matrix_enhanced': {
            'name': 'Matrix Enhanced',
            'description': 'Enhanced matrix theme with green on black',
            'primary_colors': ['matrix_green'],
            'background': 'black',
            'style': 'classic'
        },
        'cyberpunk': {
            'name': 'Cyberpunk',
            'description': 'Futuristic theme with pink and cyan',
            'primary_colors': ['hot_pink', 'cyan', 'gold'],
            'background': 'black',
            'style': 'futuristic'
        }
    }

def apply_chuk_theme_to_chart(chart, theme_name='chuk_default'):
    """
    Apply a chuk-term compatible theme to a plotext chart.
    
    Args:
        chart: Plotext chart instance
        theme_name (str): Name of theme to apply
    
    Returns:
        chart: Chart with theme applied
    """
    themes = create_chuk_term_themes()
    
    if theme_name not in themes:
        theme_name = 'chuk_default'
    
    # Apply theme using plotext's theme system
    chart.theme(theme_name)
    return chart

def get_chuk_theme_for_banner_mode(theme_name='chuk_default'):
    """
    Get appropriate banner styling based on theme.
    
    Args:
        theme_name (str): Theme name
    
    Returns:
        dict: Banner styling configuration
    """
    theme_info = get_theme_info()
    info = theme_info.get(theme_name, theme_info['chuk_default'])
    
    # Map theme styles to banner configurations
    style_mappings = {
        'modern': {'style': 'rounded', 'padding': (0, 1)},
        'minimal': {'style': 'none', 'padding': (0, 0)},
        'terminal': {'style': 'ascii', 'padding': (0, 1)},
        'corporate': {'style': 'heavy', 'padding': (0, 2)},
        'academic': {'style': 'double', 'padding': (0, 1)},
        'gaming': {'style': 'rounded', 'padding': (0, 2)},
        'soft': {'style': 'rounded', 'padding': (0, 2)},
        'accessible': {'style': 'heavy', 'padding': (0, 1)},
        'popular': {'style': 'rounded', 'padding': (0, 1)},
        'classic': {'style': 'ascii', 'padding': (0, 1)},
        'futuristic': {'style': 'rounded', 'padding': (0, 2)}
    }
    
    return style_mappings.get(info['style'], style_mappings['modern'])

# Export the theme functions for easy access
__all__ = [
    'create_chuk_term_themes',
    'get_theme_info', 
    'apply_chuk_theme_to_chart',
    'get_chuk_theme_for_banner_mode',
    'rgb_colors'
]