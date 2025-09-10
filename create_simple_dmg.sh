#!/bin/bash

echo "================================================"
echo "NoPrints DMG Creator (Simplified)"
echo "================================================"

# Set variables
APP_NAME="NoPrints"
VERSION="3.1"
DMG_NAME="NoPrints-v3.1"
BUILD_DIR="build"
DMG_DIR="dmg_temp"
FINAL_DMG="${DMG_NAME}.dmg"

# Clean up
echo "🧹 Cleaning up..."
rm -rf "$BUILD_DIR" "$DMG_DIR" "$FINAL_DMG" "${DMG_NAME}_temp.dmg"

# Create directories
echo "📁 Creating directories..."
mkdir -p "$BUILD_DIR" "$DMG_DIR"

# Copy the working app bundle
echo "📦 Copying NoPrints.app..."
cp -R NoPrints.app "$BUILD_DIR/"

# Update the app bundle with proper icon
echo "🎨 Creating proper app icon..."
python3 -c "
import sys
sys.path.append('.')
from logo_handler import create_app_icon_from_svg
from PIL import Image

print('Creating app icon...')
img = create_app_icon_from_svg()

# Save different sizes
sizes = [16, 32, 64, 128, 256, 512]
for s in sizes:
    resized = img.resize((s, s), Image.Resampling.LANCZOS)
    resized.save(f'$BUILD_DIR/NoPrints.app/Contents/Resources/NoPrints_{s}.png')

print('✅ Icon files created')
"

# Create iconset and convert to icns
echo "🔄 Creating icns file..."
mkdir -p "$BUILD_DIR/NoPrints.iconset"
cp "$BUILD_DIR/NoPrints.app/Contents/Resources/NoPrints_16.png" "$BUILD_DIR/NoPrints.iconset/icon_16x16.png"
cp "$BUILD_DIR/NoPrints.app/Contents/Resources/NoPrints_32.png" "$BUILD_DIR/NoPrints.iconset/icon_16x16@2x.png"
cp "$BUILD_DIR/NoPrints.app/Contents/Resources/NoPrints_32.png" "$BUILD_DIR/NoPrints.iconset/icon_32x32.png"
cp "$BUILD_DIR/NoPrints.app/Contents/Resources/NoPrints_64.png" "$BUILD_DIR/NoPrints.iconset/icon_32x32@2x.png"
cp "$BUILD_DIR/NoPrints.app/Contents/Resources/NoPrints_128.png" "$BUILD_DIR/NoPrints.iconset/icon_128x128.png"
cp "$BUILD_DIR/NoPrints.app/Contents/Resources/NoPrints_256.png" "$BUILD_DIR/NoPrints.iconset/icon_128x128@2x.png"
cp "$BUILD_DIR/NoPrints.app/Contents/Resources/NoPrints_256.png" "$BUILD_DIR/NoPrints.iconset/icon_256x256.png"
cp "$BUILD_DIR/NoPrints.app/Contents/Resources/NoPrints_512.png" "$BUILD_DIR/NoPrints.iconset/icon_256x256@2x.png"
cp "$BUILD_DIR/NoPrints.app/Contents/Resources/NoPrints_512.png" "$BUILD_DIR/NoPrints.iconset/icon_512x512.png"

iconutil -c icns "$BUILD_DIR/NoPrints.iconset" -o "$BUILD_DIR/NoPrints.app/Contents/Resources/NoPrints.icns"

# Copy documentation and installer
echo "📚 Adding documentation..."
cp README.md "$BUILD_DIR/"
cp QUICK_START.md "$BUILD_DIR/"
cp install_noprints.sh "$BUILD_DIR/"
chmod +x "$BUILD_DIR/install_noprints.sh"

# Prepare DMG contents
echo "💿 Preparing DMG contents..."
cp -R "$BUILD_DIR/NoPrints.app" "$DMG_DIR/"
cp "$BUILD_DIR/README.md" "$DMG_DIR/"
cp "$BUILD_DIR/QUICK_START.md" "$DMG_DIR/"
cp "$BUILD_DIR/install_noprints.sh" "$DMG_DIR/"

# Create Applications symlink
ln -sf /Applications "$DMG_DIR/Applications"

# Create a simple DMG without complex AppleScript
echo "💿 Creating DMG..."
hdiutil create -srcfolder "$DMG_DIR" -format UDZO -imagekey zlib-level=9 -volname "$DMG_NAME" "$FINAL_DMG"

# Clean up
echo "🧹 Cleaning up..."
rm -rf "$BUILD_DIR" "$DMG_DIR" "NoPrints.iconset"

# Get file size
if [ -f "$FINAL_DMG" ]; then
    DMG_SIZE=$(du -h "$FINAL_DMG" | cut -f1)
    
    echo ""
    echo "================================================"
    echo "✅ DMG Creation Complete!"
    echo "================================================"
    echo ""
    echo "📦 File: $FINAL_DMG"
    echo "💾 Size: $DMG_SIZE"
    echo ""
    echo "📋 Contents:"
    echo "  • NoPrints.app with proper logo icon"
    echo "  • install_noprints.sh (dependency installer)"
    echo "  • README.md (full documentation)"
    echo "  • QUICK_START.md (getting started guide)"
    echo "  • Applications folder symlink"
    echo ""
    echo "🎨 Logo Features:"
    echo "  • Professional fingerprint-themed app icon"
    echo "  • High-resolution ICNS file"
    echo "  • Visible in Finder and DMG"
    echo ""
    echo "🚀 Ready for Distribution!"
    echo "================================================"
else
    echo "❌ DMG creation failed"
    exit 1
fi