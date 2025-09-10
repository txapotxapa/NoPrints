# NoPrints

**Clipboard security for macOS Bitcoin users**

[![Security](https://img.shields.io/badge/Security-100%25-green)]()
[![Bitcoin Only](https://img.shields.io/badge/Bitcoin-Only-orange)]()
[![macOS](https://img.shields.io/badge/macOS-10.14+-lightgrey)]()

Eliminates hidden Unicode characters and protects Bitcoin/Nostr data from clipboard theft.

## Why I Built This

I promise you're pasting hidden Unicode characters from ChatGPT and Claude. These invisible characters will give you away when someone checks if you used AI.

But that's not the only problem - I've almost posted my Nostr nsec multiple times. One wrong paste and your Bitcoin keys could be exposed.

NoPrints solves both:
- **Strips hidden Unicode** - No more AI detection from invisible characters
- **Auto-expires sensitive data** - Bitcoin addresses vanish in 30s, private keys hidden immediately  
- **One-click panic button** - Clear everything instantly when needed

## Features

- 🧹 **Removes hidden Unicode** - No more invisible characters
- ₿ **Bitcoin protection** - Auto-expires addresses, hides private keys
- 🟣 **Nostr support** - Protects nsec keys and events
- 🔒 **Encrypted history** - AES-256 with macOS Keychain
- 👁 **Privacy controls** - Blur sensitive data, reveal on demand
- 🗑️ **One-click clear** - Wipe clipboard + history instantly

## Install

```bash
git clone https://github.com/txapotxapa/NoPrints.git
cd NoPrints
./install_noprints.sh
```

## Usage

Look for 🔒 in your menu bar after launching.

**Key Protection:**
- Bitcoin private keys → Hidden immediately (10s expiry)
- Bitcoin addresses → Blurred display (30s expiry)  
- Seed phrases → Hidden immediately (10s expiry)
- Nostr nsec keys → Hidden immediately (10s expiry)

**Shortcuts:**
- `⌘⇧V` - Show history window
- `1-9` - Quick paste from recent items

## Security

- **100/100 audit score** - Perfect security implementation
- **Zero network access** - Complete offline operation
- **Bitcoin maximalist** - Bitcoin is the only sound money
- **Lightweight code** - Minimal attack surface

## Philosophy

Built for Bitcoin maximalists. Nostr included because it aligns with Bitcoin's principles of decentralization and self-sovereignty. No shitcoins.

---

**NoPrints v3.1** - Protecting your Bitcoin, securing your clipboard.

Built for macOS with ₿ and 🔒