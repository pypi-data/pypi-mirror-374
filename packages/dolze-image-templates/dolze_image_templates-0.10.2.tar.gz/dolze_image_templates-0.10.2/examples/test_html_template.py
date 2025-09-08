"""
Test script for HTML template rendering.

This script demonstrates how to use the HTML component to render HTML/CSS content in templates.
It supports rendering multiple HTML templates with different configurations.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.append(str(Path(__file__).parent.parent))

from dolze_image_templates import (
    get_template_registry,
    configure,
    get_font_manager,
)

# Initialize font manager to scan for fonts
font_manager = get_font_manager()
print("Font manager initialized. Available fonts:", font_manager.list_fonts())

# Configure the library
configure(
    templates_dir=os.path.join(
        os.path.dirname(__file__), "..", "dolze_image_templates", "available_templates"
    ),
    output_dir=os.path.join(os.path.dirname(__file__), "output"),
)


def render_html_template(template_name, template_data):
    """Render an HTML template with the provided data.

    Args:
        template_name (str): Name to use for the output file
        template_data (dict): Template data with custom HTML and CSS

    Returns:
        The rendered image
    """
    # Get the template registry
    registry = get_template_registry()

    # Render the template with the data
    output_path = os.path.join("output", f"{template_name}.png")
    rendered_image = registry.render_template(
        template_name,  # Use the actual template name
        template_data,
        output_path=output_path,
    )

    print(f"Template saved to {os.path.abspath(output_path)}")
    return rendered_image


def get_html_card_template_data():
    return {
        "title": "How to Grow Your Brand on Social Media 1",
        "tip1": "Determine a consistent upload schedule.",
        "tip2": "Understand your target demographic.",
        "tip3": "Keep track of social media analytics.",
        "tip4": "Encourage interaction with your posts.",
        "tip5": "Engage directly with your audience online.",
        "button_text": "Follow @reallygreatsite for more tips",
        "button_url": "#",
    }


def get_social_media_tips_template_data():
    """Get sample data for the social media tips template."""
    return {
        "title": "How to Grow Your Brand on Social Media",
        "tip1": "Determine a consistent upload schedule.",
        "tip2": "Understand your target demographic.",
        "tip3": "Keep track of social media analytics.",
        "tip4": "Encourage interaction with your posts.",
        "tip5": "Engage directly with your audience online.",
        "button_text": "Follow @reallygreatsite for more tips",
        "button_url": "#",
        "custom_css": "",
        "custom_html": ""
    }


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Define the templates to render
        templates = [
            {"name": "html_card_template", "data": get_html_card_template_data()},
            {"name": "social_media_tips_template", "data": get_social_media_tips_template_data()}
        ]

        # Render each template
        for template in templates:
            render_html_template(template["name"], template["data"])

        print("\nAll HTML templates generated successfully!")
    except Exception as e:
        print(f"\nError generating HTML templates: {str(e)}")
        import traceback

        traceback.print_exc()
