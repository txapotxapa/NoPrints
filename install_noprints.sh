#!/bin/bash

echo "================================================"
echo "NoPrints Installation"
echo "================================================"
echo "Installing NoPrints - advanced clipboard manager with:"
echo "• Clipboard history (50 items)"
echo "• Bitcoin + Nostr security detection"
echo "• Password protection"
echo "• Smart paste technology"
echo "• Hidden unicode removal"
echo "• Encrypted storage"
echo "================================================"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This tool is designed for macOS only"
    exit 1
fi

echo "🔍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.7 or later"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

echo ""
echo "📦 Installing Python dependencies..."

# Create requirements list
cat > requirements_temp.txt << 'EOF'
rumps>=0.3.0
pyobjc-framework-Cocoa
keyring
cryptography>=3.0
pynput
Pillow
EOF

# Install packages
pip3 install -r requirements_temp.txt --user || {
    echo "⚠️  Warning: Some packages may require system installation"
    echo "Try: brew install python-tk (if using Homebrew)"
    echo "Or install packages individually:"
    echo "pip3 install rumps pyobjc-framework-Cocoa keyring cryptography pynput Pillow"
}

rm requirements_temp.txt

echo ""
echo "🔧 Setting up application structure..."

# Make Python files executable
chmod +x *.py

# Create app bundle directory
mkdir -p NoPrints.app/Contents/MacOS
mkdir -p NoPrints.app/Contents/Resources
mkdir -p NoPrints.app/Contents/Frameworks

# Create Info.plist for proper macOS app
cat > NoPrints.app/Contents/Info.plist << 'EOF'
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
    <string>CBMP</string>
    <key>CFBundleExecutable</key>
    <string>NoPrints</string>
    <key>LSUIElement</key>
    <true/>
    <key>LSBackgroundOnly</key>
    <false/>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
    <key>NSAppleEventsUsageDescription</key>
    <string>NoPrints needs access to monitor clipboard changes and provide smart paste functionality.</string>
    <key>NSSystemAdministrationUsageDescription</key>
    <string>Used to detect active applications for smart paste formatting.</string>
</dict>
</plist>
EOF

# Create launcher script
cat > NoPrints.app/Contents/MacOS/NoPrints << 'EOF'
#!/bin/bash
# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$DIR/../../../"

# Change to the base directory
cd "$BASE_DIR"

# Set Python path
export PYTHONPATH="$BASE_DIR:$PYTHONPATH"

# Launch the application
/usr/bin/python3 NoPrints.py
EOF

chmod +x NoPrints.app/Contents/MacOS/NoPrints

# Create a simple launcher script for terminal
cat > launch_noprints.command << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 NoPrints.py
EOF

chmod +x launch_noprints.command

echo ""
echo "🔐 Setting up security permissions..."

# Create application support directory
mkdir -p ~/Library/Application\ Support/NoPrints

# Set up keychain access (macOS will prompt for permission)
echo "ℹ️  First run will request keychain access for encrypted storage"

echo ""
echo "🎛️  Setting up launch agent (auto-start)..."

# Create launch agent
mkdir -p ~/Library/LaunchAgents

cat > ~/Library/LaunchAgents/com.local.noprints.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.local.noprints</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$(pwd)/NoPrints.app/Contents/MacOS/NoPrints</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$(echo ~)/Library/Logs/NoPrints.log</string>
    
    <key>StandardErrorPath</key>
    <string>$(echo ~)/Library/Logs/NoPrints_error.log</string>
    
    <key>ProcessType</key>
    <string>Interactive</string>
    
    <key>LimitLoadToSessionType</key>
    <string>Aqua</string>
</dict>
</plist>
EOF

echo ""
echo "✅ Installation Complete!"
echo ""
echo "================================================"
echo "🚀 How to Start:"
echo "================================================"
echo ""
echo "Option 1 - Double-click the app:"
echo "  📁 NoPrints.app"
echo ""
echo "Option 2 - Terminal launch:"
echo "  📄 ./launch_noprints.command"
echo ""
echo "Option 3 - Direct Python:"
echo "  🐍 python3 NoPrints.py"
echo ""
echo "================================================"
echo "⚡ Auto-Start Setup:"
echo "================================================"
echo ""
echo "To start automatically at login:"
echo "  launchctl load ~/Library/LaunchAgents/com.local.noprints.plist"
echo ""
echo "To stop auto-start:"
echo "  launchctl unload ~/Library/LaunchAgents/com.local.noprints.plist"
echo ""
echo "================================================"
echo "🔒 Features Overview:"
echo "================================================"
echo ""
echo "Menu Bar Features:"
echo "  🔒 Toggle protection on/off"
echo "  📋 Recent 10 clipboard items"
echo "  ₿ Bitcoin items (addresses, invoices)"
echo "  🟣 Nostr items (keys, events, relays)"
echo "  🔐 Security status & settings"
echo "  📊 Usage statistics"
echo ""
echo "Keyboard Shortcuts:"
echo "  ⌘V - Normal paste"
echo "  ⌘⇧V - Show history window"
echo "  1-9 - Quick paste from recent items"
echo ""
echo "Security Features:"
echo "  ⚡ Bitcoin addresses expire in 30s"
echo "  🔑 Private keys hidden immediately"
echo "  🔒 Passwords expire in 60s"
echo "  💳 Credit cards auto-detected"
echo "  🌱 Seed phrases protected"
echo ""
echo "Smart Features:"
echo "  🧠 Context-aware paste formatting"
echo "  🧹 Hidden Unicode removal"
echo "  💾 Encrypted history storage"
echo "  🔍 Searchable clipboard history"
echo "  📌 Pin important items"
echo ""
echo "================================================"
echo "🎉 Ready to Use!"
echo "================================================"
echo ""
echo "Look for the 🔒 icon in your menu bar after starting."
echo "First launch will request permissions for:"
echo "• Accessibility (for global hotkeys)"
echo "• Keychain access (for encryption)"
echo ""
echo "Enjoy secure clipboard management! 🛡️"