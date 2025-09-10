# NoPrints - Quick Start Guide

🎉 **Installation Complete!** 

NoPrints is ready to run. Here are your options:

## 🚀 Starting NoPrints

### Option 1: App Bundle (Recommended)
```bash
open NoPrints.app
```

### Option 2: Terminal Launcher
```bash
./launch_noprints.command
```

### Option 3: Direct Python
```bash
python3 NoPrints.py
```

## ⚡ Auto-Start at Login

### Enable Auto-Start
```bash
launchctl load ~/Library/LaunchAgents/com.local.noprints.plist
```

### Disable Auto-Start
```bash
launchctl unload ~/Library/LaunchAgents/com.local.noprints.plist
```

## 🔒 First Run Permissions

NoPrints will request:
1. **Accessibility Access** - System Preferences > Security & Privacy > Accessibility
2. **Keychain Access** - For encrypted storage keys

## 📱 Usage

Look for the **🔒** icon in your menu bar:
- **🔒** - Normal protection active
- **₿** - Bitcoin content detected  
- **🟣** - Nostr content detected
- **⚡** - Both Bitcoin + Nostr detected
- **⚠️** - Sensitive data detected
- **🔓** - Protection disabled

## ⌨️ Keyboard Shortcuts

- **⌘V** - Normal paste (most recent)
- **⌘⇧V** - Show history picker window  
- **1-9** - Quick paste from recent items (in menu)

## 🛡️ Security Features

| Data Type | Expiry | Protection |
|-----------|--------|------------|
| Bitcoin private keys | 10s | Hidden |
| Nostr private keys (nsec) | 10s | Hidden |
| Bitcoin addresses | 30s | Blurred |
| Nostr public keys | 60s | Abbreviated |
| Passwords | 60s | Auto-expire |
| Normal text | None | Unicode cleaned |

## 🎯 Ready to Use!

Your clipboard is now protected with:
- ✅ Hidden Unicode character removal
- ✅ Bitcoin security detection
- ✅ Nostr protocol protection  
- ✅ Encrypted history storage
- ✅ Smart paste technology
- ✅ Auto-expiration of sensitive data

Enjoy secure clipboard management! 🛡️