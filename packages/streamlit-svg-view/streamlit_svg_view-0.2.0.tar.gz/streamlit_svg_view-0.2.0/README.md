# Streamlit SVG View

A Streamlit custom component for displaying SVG animations with interactive play, pause, and restart controls.

## Features

- Interactive Controls - Play, pause, and restart SVG animations with hover overlay controls
- Customizable Colors - Set custom colors for control buttons to match your app's theme  
- Responsive Design - Works seamlessly across different screen sizes
- Cross-browser Compatible - Supports all modern browsers with graceful fallbacks
- Lightweight - Minimal dependencies and optimized performance
- Easy Integration - Simple API that works with any animated SVG

## Installation

```bash
pip install streamlit-svg-view
```

## Quick Start

```python
import streamlit as st
from streamlit_svg_view import svg_view

# Your animated SVG content
svg_content = '''
<svg width="200" height="200" viewBox="0 0 200 200">
    <circle cx="100" cy="100" r="50" fill="blue">
        <animate attributeName="r" values="50;80;50" dur="2s" repeatCount="indefinite"/>
        <animate attributeName="fill" values="blue;red;blue" dur="2s" repeatCount="indefinite"/>
    </circle>
</svg>
'''

# Display with controls
result = svg_view(svg_content, width=250, height=250)
st.write("Animation state:", result)
```

## API Reference

### svg_view(svg_content, width=None, height=None, play_color=None, pause_color=None, restart_color=None, key=None)

#### Parameters

- **svg_content** (str): The SVG content as a string
- **width** (int, optional): Component width in pixels (default: 400)
- **height** (int, optional): Component height in pixels (default: 300)
- **play_color** (str, optional): Color for the play button (CSS format)
- **pause_color** (str, optional): Color for the pause button (CSS format)
- **restart_color** (str, optional): Color for the restart button (CSS format)
- **key** (str, optional): Unique key for the component instance

#### Returns

**dict**: Component state containing:
- is_playing (bool): Whether animations are currently playing
- action (str): Last user action ('play', 'pause', 'restart', or 'state_change')

## Examples

### Basic Usage

```python
import streamlit as st
from streamlit_svg_view import svg_view

# Simple pulsing circle
svg = '''
<svg width="100" height="100" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="20" fill="blue">
        <animate attributeName="r" values="20;30;20" dur="1s" repeatCount="indefinite"/>
    </circle>
</svg>
'''

svg_view(svg)
```

### Custom Colors

```python
# Match your app's color scheme
svg_view(
    svg_content,
    play_color="#ff6b6b",      # Coral red
    pause_color="#4ecdc4",     # Turquoise  
    restart_color="#45b7d1",   # Sky blue
    width=300,
    height=200
)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.