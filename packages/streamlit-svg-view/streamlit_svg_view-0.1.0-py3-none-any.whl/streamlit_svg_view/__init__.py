import os
import streamlit.components.v1 as components

__version__ = "0.1.0"

# Create a _RELEASE constant. We'll set this to False while we're developing
# the component, and True when we're ready to package and distribute it.
_RELEASE = True

# Declare a Streamlit component. `declare_component` returns a function
# that is used to create instances of the component. We're naming this
# function `svg_view`, since that's the name of our component.
if not _RELEASE:
    _component_func = components.declare_component(
        "svg_view",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        "svg_view", path=build_dir
    )


def svg_view(svg_content, width=None, height=None, play_color=None, pause_color=None, restart_color=None, key=None):
    """Create an SVG viewer component with animation controls.
    
    Parameters
    ----------
    svg_content : str
        The SVG content as a string
    width : int or None
        Component width in pixels
    height : int or None  
        Component height in pixels
    play_color : str or None
        Color for the play button (CSS color format, e.g., 'rgba(52,199,89,0.8)' or '#34c759')
    pause_color : str or None
        Color for the pause button (CSS color format, e.g., 'rgba(255,149,0,0.8)' or '#ff9500')
    restart_color : str or None
        Color for the restart button (CSS color format, e.g., 'rgba(88,86,214,0.8)' or '#5856d6')
    key : str or None
        An optional key that uniquely identifies this component
        
    Returns
    -------
    dict
        Dictionary containing the current animation state and any user interactions
    """
    component_value = _component_func(
        svg_content=svg_content,
        width=width,
        height=height,
        play_color=play_color,
        pause_color=pause_color,
        restart_color=restart_color,
        key=key,
        default={"is_playing": True, "action": None}
    )
    
    return component_value


# Add some test functions here to work with the frontend component during development
if not _RELEASE:
    import streamlit as st
    
    def main():
        st.write("## SVG Animation Control Component")
        
        # Sample animated SVG
        sample_svg = '''
        <svg width="200" height="200" viewBox="0 0 200 200">
            <circle cx="100" cy="100" r="50" fill="blue">
                <animate attributeName="r" values="50;80;50" dur="2s" repeatCount="indefinite"/>
                <animate attributeName="fill" values="blue;red;blue" dur="2s" repeatCount="indefinite"/>
            </circle>
        </svg>
        '''
        
        result = svg_view(sample_svg, width=300, height=300)
        st.write("Component returned:", result)


if __name__ == "__main__":
    main()