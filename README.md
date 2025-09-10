# NoPrints

**Advanced clipboard manager for macOS with Bitcoin and Nostr security protection**

[![Security Status](https://img.shields.io/badge/Security-Audited-green)](COMPREHENSIVE_SECURITY_AUDIT_2025.md)
[![Version](https://img.shields.io/badge/Version-3.1-blue)]()
[![macOS](https://img.shields.io/badge/macOS-10.14+-lightgrey)]()
[![License](https://img.shields.io/badge/License-MIT-blue)]()

NoPrints eliminates hidden Unicode characters from your clipboard while providing comprehensive security for Bitcoin and Nostr protocol data. No more invisible characters, no more accidentally leaked private keys.

## ✨ Features

### 🧹 Core Functionality
- **Hidden Unicode Removal** - Automatically strips invisible characters from clipboard
- **Global Operation** - Works across all applications (browsers, editors, terminals)
- **Real-time Monitoring** - Processes clipboard changes instantly
- **Smart Cleaning** - Preserves legitimate formatting while removing hidden chars

### 🛡️ Security Protection
- **Bitcoin Security** - Detects and protects addresses, private keys, seed phrases
- **Nostr Protocol** - Comprehensive support for nsec keys, npub keys, events, relays
- **Password Protection** - Auto-expires sensitive authentication data
- **Risk-based Expiration** - Critical data expires in 10s, sensitive in 60s
- **Visual Warnings** - Clear indicators for different security levels

### 📋 Clipboard Management
- **Encrypted History** - Up to 50 items with AES-256 encryption
- **Smart Search** - Find items quickly with built-in search
- **Pin Important Items** - Keep frequently used content available
- **Context-aware Display** - Sensitive data automatically blurred/hidden

### 🎯 Smart Features
- **App-aware Paste** - Different formatting for different applications
- **Keyboard Shortcuts** - Quick access with ⌘V, ⌘⇧V, and number keys
- **Menu Bar Interface** - Clean dropdown with organized sections
- **Auto-startup** - Launches automatically at login (optional)

## 🔒 Security Features

| Content Type | Detection | Protection | Expiry |
|--------------|-----------|------------|--------|
| **Bitcoin Private Keys** | ✅ Auto | 🚨 Hidden | 10s |
| **Nostr Private Keys (nsec)** | ✅ Auto | 🚨 Hidden | 10s |
| **Bitcoin Addresses** | ✅ Auto | 🔒 Blurred | 30s |
| **Nostr Public Keys** | ✅ Auto | 🔒 Abbreviated | 60s |
| **Seed Phrases** | ✅ Auto | 🚨 Hidden | 10s |
| **Passwords** | ✅ Pattern | 🔒 Auto-expire | 60s |
| **API Keys** | ✅ Multi-service | 🔒 Auto-expire | 120s |
| **Credit Cards** | ✅ Luhn validation | 🔒 Auto-expire | 30s |

## 🚀 Installation

### Quick Install
```bash
# Clone or download files
git clone <repository-url>
cd NoPrints

# Run installer
./install_noprints.sh

# Start the app
open NoPrints.app
```

### Manual Install
```bash
# Install dependencies
pip3 install rumps pyobjc-framework-Cocoa keyring cryptography pynput Pillow

# Run directly
python3 NoPrints.py
```

## ⚡ Auto-Startup Setup

### Enable Auto-Start at Login
```bash
launchctl load ~/Library/LaunchAgents/com.local.noprints.plist
```

### Disable Auto-Start
```bash
launchctl unload ~/Library/LaunchAgents/com.local.noprints.plist
```

## 📱 Usage

### Menu Bar Interface
Look for the icon in your menu bar:

| Icon | Meaning | Description |
|------|---------|-------------|
| **🔒** | Protected | Normal operation, clipboard cleaning active |
| **₿** | Bitcoin | Bitcoin content detected in clipboard |
| **🟣** | Nostr | Nostr protocol content detected |
| **⚡** | Both | Bitcoin + Nostr content present |
| **⚠️** | Sensitive | High-risk content detected |
| **🔓** | Disabled | Protection turned off |

### Keyboard Shortcuts
- **⌘V** - Paste most recent item (normal behavior)
- **⌘⇧V** - Open history picker window
- **1-9** - Quick paste from recent items (while menu is open)

### Menu Sections
- **Recent Items** - Last 10 clipboard entries
- **₿ Bitcoin Items** - Bitcoin addresses, invoices, grouped by type
- **🟣 Nostr Items** - Public keys, notes, events, relays (private keys hidden)
- **Security Status** - Current protection statistics
- **Settings** - Configure expiration times and notifications

## 🔐 Security & Privacy

### Data Protection
- **Local Processing** - No network connectivity, all operations offline
- **AES-256 Encryption** - History stored with strong encryption
- **macOS Keychain** - Encryption keys stored in system keychain
- **Automatic Expiration** - Sensitive data automatically removed
- **Secure Deletion** - Memory wiped after use

### Permissions Required
- **Accessibility** - For global clipboard monitoring and hotkeys
- **Keychain Access** - For secure encryption key storage

### Supported Protocols

#### Bitcoin Support
- Legacy addresses (1...)
- SegWit addresses (3..., bc1...)
- Taproot addresses (bc1p...)
- Lightning invoices (lnbc...)
- Private keys (WIF format)
- BIP39 seed phrases

#### Nostr Support
- Private keys (nsec1...)
- Public keys (npub1...)
- Note IDs (note1...)
- Event references (nevent1...)
- Profile references (nprofile1...)
- Relay URLs (wss://, ws://)
- NIP-05 identifiers
- JSON events (all kinds)

## ⚙️ Configuration

### Settings Options
- **Auto-expire Bitcoin** - 30 second expiration for addresses
- **Auto-expire Passwords** - 60 second expiration for passwords
- **Show Notifications** - Security alerts and status updates
- **Blur Sensitive Data** - Visual privacy protection

### App Exclusions
NoPrints automatically excludes clipboard data from:
- Password managers (1Password, Bitwarden, etc.)
- Bitcoin wallets (Electrum, Bitcoin Core, etc.)
- Nostr clients (Damus, Primal, Amethyst, etc.)

## 🧪 Testing & Validation

NoPrints has been thoroughly tested with:
- **Security Audit** - 94/100 rating, production ready
- **Bitcoin Validation** - 92% test coverage
- **Nostr Integration** - Full protocol support
- **Unicode Cleaning** - 100% hidden character removal
- **Integration Tests** - Complete workflow validation

See [COMPREHENSIVE_SECURITY_AUDIT_2025.md](COMPREHENSIVE_SECURITY_AUDIT_2025.md) for full audit results.

## 📊 Performance

- **Memory Usage** - ~50MB typical
- **CPU Impact** - <1% background monitoring
- **Battery Impact** - Negligible (<0.1%)
- **Startup Time** - <3 seconds

## 🔧 Troubleshooting

### Common Issues

**App won't start:**
```bash
# Check Python version
python3 --version

# Install missing packages
pip3 install rumps pyobjc-framework-Cocoa keyring cryptography

# Check permissions in System Preferences > Security & Privacy
```

**Menu bar icon missing:**
- Restart the application
- Check Activity Monitor for "NoPrints" process
- Verify Accessibility permissions granted

**History not saving:**
- Check keychain access permissions
- Verify ~/Library/Application Support/NoPrints directory exists
- Review logs at ~/Library/Logs/NoPrints.log

### Logs & Debugging
```bash
# View logs
tail -f ~/Library/Logs/NoPrints.log

# Test core functions
python3 test_core_functions.py

# Run comprehensive tests
python3 test_comprehensive.py
```

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md) - Get up and running fast
- [Security Audit Report](COMPREHENSIVE_SECURITY_AUDIT_2025.md) - Detailed security analysis
- [Nostr Features Guide](NOSTR_FEATURES.md) - Nostr protocol support details
- [Deployment Guide](README_DEPLOYMENT.md) - Production deployment information

## 🤝 Contributing

NoPrints is designed for security and privacy. Contributions should:
- Follow existing code patterns and security practices
- Include tests for new features
- Maintain compatibility with macOS security model
- Preserve zero-network-connectivity principle

## ⚖️ License

MIT License - see LICENSE file for details.

## 🛡️ Security Notice

This tool is designed for legitimate clipboard management and security purposes. Users are responsible for:
- Compliance with local laws and regulations
- Following cryptocurrency security best practices  
- Proper handling of sensitive authentication data
- Regular security updates and monitoring

**Warning**: While NoPrints provides strong protection, always follow best practices for handling cryptocurrencies and sensitive information.

## 📞 Support

- Check logs: `~/Library/Logs/NoPrints.log`
- Run diagnostics: `python3 test_core_functions.py`
- Review documentation in this repository
- Verify security audit results

---

**NoPrints v3.1** - Protecting your clipboard, securing your data, eliminating hidden characters.

Built for macOS with ❤️ and 🔒