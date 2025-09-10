#!/usr/bin/env python3
"""
Logo handling utilities for NoPrints
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw

def create_menu_bar_icon_from_svg():
    """
    Create a menu bar compatible icon from the SVG
    Since rumps requires emoji or image data, we'll create a PNG from SVG concept
    """
    
    # For now, we'll use the text-based approach but could enhance with proper SVG conversion
    # The SVG shows a fingerprint, so we'll create a simplified version
    
    # Create a small icon that matches the SVG design
    size = 16
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw fingerprint-like ridges based on the SVG paths
    # Outer ridges (opacity 0.8)
    color_outer = (51, 51, 51, int(255 * 0.8))  # #333 with 0.8 opacity
    
    # Draw curved lines to represent fingerprint ridges
    # These approximate the SVG paths
    
    # Outer ridge 1 (right side)
    draw.arc([4, 2, 12, 10], start=-90, end=90, fill=color_outer, width=1)
    
    # Outer ridge 2 (left side)  
    draw.arc([4, 6, 12, 14], start=90, end=270, fill=color_outer, width=1)
    
    # Middle ridges (opacity 0.6)
    color_middle = (51, 51, 51, int(255 * 0.6))
    draw.arc([5, 3, 11, 9], start=-90, end=90, fill=color_middle, width=1)
    draw.arc([5, 7, 11, 13], start=90, end=270, fill=color_middle, width=1)
    
    # Inner ridges (opacity 0.5)
    color_inner = (51, 51, 51, int(255 * 0.5))
    draw.arc([6, 4, 10, 8], start=-90, end=90, fill=color_inner, width=1)
    draw.arc([6, 8, 10, 12], start=90, end=270, fill=color_inner, width=1)
    
    # Save the icon
    icon_path = Path(__file__).parent / 'menubar_icon.png'
    img.save(icon_path)
    
    return str(icon_path)

def get_menu_bar_icons():
    """
    Get different menu bar icons for different states
    Uses custom fingerprint template icon when available
    """
    from pathlib import Path
    
    # Check if we can create a template icon from SVG
    svg_path = Path(__file__).parent / 'no-prints-template.svg'
    template_path = Path(__file__).parent / 'menubar_template_icon.png'
    
    custom_icon = None
    if svg_path.exists():
        try:
            # Try to create template icon
            from svg_to_template import create_template_icon
            if create_template_icon(str(svg_path), str(template_path)):
                custom_icon = str(template_path)
        except Exception as e:
            print(f"Could not create template icon: {e}")
    
    icons = {
        'normal': custom_icon if custom_icon else '🔒',  # Custom fingerprint or emoji fallback
        'bitcoin': '₿',  # Bitcoin detected
        'nostr': '🟣',   # Nostr detected  
        'both': '⚡',     # Both Bitcoin and Nostr
        'sensitive': '⚠️', # High-risk content
        'disabled': '🔓'   # Protection disabled
    }
    
    return icons

def create_template_icon_from_svg(svg_path):
    """
    Create a menu bar template icon from SVG
    This would ideally convert SVG to a template image,
    but for now returns the emoji as rumps needs special handling
    """
    # For macOS menu bar, rumps works best with:
    # 1. Emoji (what we're using)
    # 2. Template images (requires special setup)
    # 3. Regular images
    
    # Return the fingerprint emoji for now, but this could be enhanced
    # to create actual template images
    return "🔒"

def create_app_icon_from_svg():
    """
    Create app bundle icon from the logo SVG
    This creates a proper macOS app icon
    """
    
    # Create a 512x512 icon based on the SVG design
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background circle (macOS app style)
    margin = 50
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill='#2E3440', outline='#4C566A', width=8)
    
    # Scale up the fingerprint design from the SVG
    center_x, center_y = size // 2, size // 2
    scale = 12  # Scale factor for the fingerprint
    
    # Draw fingerprint ridges scaled up
    # Outer ridges
    color = '#ECEFF4'
    width = 6
    
    # Right side ridges
    draw.arc([center_x - 4*scale, center_y - 6*scale, 
              center_x + 4*scale, center_y + 2*scale], 
             start=-90, end=90, fill=color, width=width)
    
    # Left side ridges  
    draw.arc([center_x - 4*scale, center_y - 2*scale,
              center_x + 4*scale, center_y + 6*scale],
             start=90, end=270, fill=color, width=width)
    
    # Middle ridges
    draw.arc([center_x - 3*scale, center_y - 5*scale,
              center_x + 3*scale, center_y + 1*scale],
             start=-90, end=90, fill=color, width=width-1)
             
    draw.arc([center_x - 3*scale, center_y - 1*scale,
              center_x + 3*scale, center_y + 5*scale],
             start=90, end=270, fill=color, width=width-1)
    
    # Inner ridges
    draw.arc([center_x - 2*scale, center_y - 4*scale,
              center_x + 2*scale, center_y],
             start=-90, end=90, fill=color, width=width-2)
             
    draw.arc([center_x - 2*scale, center_y,
              center_x + 2*scale, center_y + 4*scale],
             start=90, end=270, fill=color, width=width-2)
    
    return img

if __name__ == "__main__":
    # Test the icon creation
    icon_path = create_menu_bar_icon_from_svg()
    print(f"Menu bar icon created: {icon_path}")
    
    app_icon = create_app_icon_from_svg()
    app_icon.save('test_app_icon.png')
    print("App icon created: test_app_icon.png")