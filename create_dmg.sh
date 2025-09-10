#!/bin/bash

echo "================================================"
echo "NoPrints DMG Creator"
echo "================================================"
echo "Creating distributable DMG for NoPrints v3.1"
echo "================================================"

# Set variables
APP_NAME="NoPrints"
VERSION="3.1"
DMG_NAME="NoPrints-v3.1"
BUILD_DIR="build"
DMG_DIR="dmg_temp"
FINAL_DMG="${DMG_NAME}.dmg"

# Clean up any previous builds
echo "🧹 Cleaning up previous builds..."
rm -rf "$BUILD_DIR"
rm -rf "$DMG_DIR"
rm -f "$FINAL_DMG"
rm -f "${DMG_NAME}_temp.dmg"

# Create build directory
echo "📁 Creating build directory..."
mkdir -p "$BUILD_DIR"
mkdir -p "$DMG_DIR"

# Create proper app bundle
echo "📦 Creating app bundle..."
mkdir -p "$BUILD_DIR/${APP_NAME}.app/Contents/MacOS"
mkdir -p "$BUILD_DIR/${APP_NAME}.app/Contents/Resources"
mkdir -p "$BUILD_DIR/${APP_NAME}.app/Contents/Frameworks"

# Copy all Python files and logo assets
echo "📂 Copying application files..."
cp *.py "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/"
cp *.svg "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/" 2>/dev/null || true

# Create Info.plist
echo "📄 Creating Info.plist..."
cat > "$BUILD_DIR/${APP_NAME}.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>NoPrints</string>
    <key>CFBundleDisplayName</key>
    <string>NoPrints</string>
    <key>CFBundleIdentifier</key>
    <string>com.local.noprints</string>
    <key>CFBundleVersion</key>
    <string>3.1</string>
    <key>CFBundleShortVersionString</key>
    <string>3.1</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>NOPR</string>
    <key>CFBundleExecutable</key>
    <string>NoPrints</string>
    <key>CFBundleIconFile</key>
    <string>NoPrints.icns</string>
    <key>LSUIElement</key>
    <true/>
    <key>LSBackgroundOnly</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSAppleEventsUsageDescription</key>
    <string>NoPrints needs access to monitor clipboard changes and provide smart paste functionality.</string>
    <key>NSSystemAdministrationUsageDescription</key>
    <string>Used to detect active applications for smart paste formatting.</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHumanReadableCopyright</key>
    <string>© 2025 NoPrints. Advanced clipboard security for macOS.</string>
</dict>
</plist>
EOF

# Create launcher script
echo "🚀 Creating launcher script..."
cat > "$BUILD_DIR/${APP_NAME}.app/Contents/MacOS/NoPrints" << 'EOF'
#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES_DIR="$DIR/../Resources"

# Change to the resources directory
cd "$RESOURCES_DIR"

# Set Python path
export PYTHONPATH="$RESOURCES_DIR:$PYTHONPATH"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "Python 3 is required but not found. Please install Python 3.7 or later from python.org" buttons {"OK"} default button "OK" with icon caution'
    exit 1
fi

# Check for required packages
python3 -c "import rumps, keyring, cryptography" 2>/dev/null || {
    osascript -e 'display dialog "Required Python packages are missing. Please run the installer script first." buttons {"OK"} default button "OK" with icon caution'
    exit 1
}

# Launch the application
exec python3 NoPrints.py
EOF

chmod +x "$BUILD_DIR/${APP_NAME}.app/Contents/MacOS/NoPrints"

# Create application icon using logo handler
echo "🎨 Creating application icon..."
python3 -c "
import os
import sys
sys.path.append('.')
from logo_handler import create_app_icon_from_svg
from PIL import Image

# Create the main app icon
img = create_app_icon_from_svg()

# Save as PNG first
img.save('$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints.png')

# Create sizes for icns
sizes = [16, 32, 64, 128, 256, 512]
for s in sizes:
    resized = img.resize((s, s), Image.Resampling.LANCZOS)
    resized.save(f'$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints_{s}.png')

print('✅ Icon files created using NoPrints logo design')
"

# Convert PNG to icns using macOS tools
echo "🔄 Converting to icns format..."
mkdir -p "$BUILD_DIR/NoPrints.iconset"
cp "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints_16.png" "$BUILD_DIR/NoPrints.iconset/icon_16x16.png"
cp "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints_32.png" "$BUILD_DIR/NoPrints.iconset/icon_16x16@2x.png"
cp "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints_32.png" "$BUILD_DIR/NoPrints.iconset/icon_32x32.png"
cp "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints_64.png" "$BUILD_DIR/NoPrints.iconset/icon_32x32@2x.png"
cp "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints_128.png" "$BUILD_DIR/NoPrints.iconset/icon_128x128.png"
cp "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints_256.png" "$BUILD_DIR/NoPrints.iconset/icon_128x128@2x.png"
cp "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints_256.png" "$BUILD_DIR/NoPrints.iconset/icon_256x256.png"
cp "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints_512.png" "$BUILD_DIR/NoPrints.iconset/icon_256x256@2x.png"
cp "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints_512.png" "$BUILD_DIR/NoPrints.iconset/icon_512x512.png"

iconutil -c icns "$BUILD_DIR/NoPrints.iconset" -o "$BUILD_DIR/${APP_NAME}.app/Contents/Resources/NoPrints.icns"

# Copy documentation
echo "📚 Copying documentation..."
cp README.md "$BUILD_DIR/"
cp QUICK_START.md "$BUILD_DIR/"
cp COMPREHENSIVE_SECURITY_AUDIT_2025.md "$BUILD_DIR/"
cp NOSTR_FEATURES.md "$BUILD_DIR/"

# Copy installer script
cp install_noprints.sh "$BUILD_DIR/"
chmod +x "$BUILD_DIR/install_noprints.sh"

# Prepare DMG contents
echo "💿 Preparing DMG contents..."
cp -R "$BUILD_DIR/${APP_NAME}.app" "$DMG_DIR/"
cp "$BUILD_DIR/README.md" "$DMG_DIR/"
cp "$BUILD_DIR/QUICK_START.md" "$DMG_DIR/"
cp "$BUILD_DIR/install_noprints.sh" "$DMG_DIR/"

# Create Applications symlink
ln -sf /Applications "$DMG_DIR/Applications"

# Create DMG background image
echo "🎨 Creating DMG background..."
python3 -c "
from PIL import Image, ImageDraw, ImageFont
import os

# Create background image
width, height = 800, 400
img = Image.new('RGB', (width, height), '#F5F5F7')
draw = ImageDraw.Draw(img)

# Title
try:
    font_large = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 48)
    font_medium = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 24)
    font_small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 16)
except:
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default() 
    font_small = ImageFont.load_default()

# Main title
draw.text((50, 50), 'NoPrints v3.1', fill='#1D1D1F', font=font_large)
draw.text((50, 110), 'Advanced Clipboard Security for macOS', fill='#6E6E73', font=font_medium)

# Features
features = [
    '🧹 Eliminates hidden Unicode characters',
    '₿ Bitcoin address and key protection', 
    '🟣 Nostr protocol security',
    '🔒 Encrypted clipboard history',
    '⚡ Smart paste technology'
]

y_pos = 160
for feature in features:
    draw.text((70, y_pos), feature, fill='#424245', font=font_small)
    y_pos += 25

# Instructions
draw.text((450, 160), 'Installation:', fill='#1D1D1F', font=font_medium)
draw.text((450, 190), '1. Drag NoPrints to Applications', fill='#424245', font=font_small)
draw.text((450, 210), '2. Run install_noprints.sh for dependencies', fill='#424245', font=font_small)
draw.text((450, 230), '3. Grant Accessibility permissions', fill='#424245', font=font_small)
draw.text((450, 250), '4. Look for 🔒 icon in menu bar', fill='#424245', font=font_small)

# Security badge
draw.rectangle([450, 290, 750, 340], fill='#007AFF', outline=None)
draw.text((460, 305), '✅ Security Audited - 94/100 Rating', fill='white', font=font_medium)

img.save('$DMG_DIR/.background.png')
print('✅ DMG background created')
"

# Create temp DMG
echo "💿 Creating temporary DMG..."
hdiutil create -srcfolder "$DMG_DIR" -format UDRW -fs HFS+ -fsargs "-c c=64,a=16,e=16" -volname "$DMG_NAME" "${DMG_NAME}_temp.dmg"

# Mount temp DMG
echo "🔧 Mounting and configuring DMG..."
hdiutil attach "${DMG_NAME}_temp.dmg" -readwrite -mountpoint "/Volumes/$DMG_NAME"

# Configure DMG appearance using AppleScript
osascript << EOF
tell application "Finder"
    tell disk "$DMG_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 900, 500}
        set background picture of icon view options of container window to file ".background.png"
        set arrangement of icon view options of container window to not arranged
        set icon size of icon view options of container window to 128
        delay 1
        set position of item "NoPrints.app" of container window to {150, 200}
        set position of item "Applications" of container window to {350, 200}
        set position of item "README.md" of container window to {550, 300}
        set position of item "install_noprints.sh" of container window to {650, 300}
        close
        open
        update without registering applications
        delay 2
        close
    end tell
end tell
EOF

# Eject the DMG
echo "⏏️ Ejecting temporary DMG..."
hdiutil detach "/Volumes/$DMG_NAME"

# Convert to final compressed DMG
echo "🗜️ Creating final compressed DMG..."
hdiutil convert "${DMG_NAME}_temp.dmg" -format UDZO -imagekey zlib-level=9 -o "$FINAL_DMG"

# Clean up
echo "🧹 Cleaning up temporary files..."
rm -rf "$BUILD_DIR"
rm -rf "$DMG_DIR"
rm -f "${DMG_NAME}_temp.dmg"

# Get file size
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
echo "  • NoPrints.app (drag to Applications)"
echo "  • install_noprints.sh (dependency installer)"
echo "  • README.md (full documentation)"
echo "  • QUICK_START.md (getting started guide)"
echo ""
echo "🚀 Distribution Ready!"
echo "================================================"
echo ""
echo "Users can now:"
echo "1. Download and open $FINAL_DMG"
echo "2. Drag NoPrints.app to Applications folder"  
echo "3. Run install_noprints.sh to install Python dependencies"
echo "4. Launch NoPrints from Applications folder"
echo ""
echo "🔒 The app will request Accessibility and Keychain permissions"
echo "⚡ Auto-startup can be enabled via the installer"
echo ""
echo "Enjoy secure clipboard management! 🛡️"