#!/usr/bin/env python3
"""
NoPrints - Advanced clipboard manager with Bitcoin and Nostr security
"""

import rumps
import threading
import time
import re
import unicodedata
import subprocess
from datetime import datetime
from AppKit import (NSPasteboard, NSStringPboardType, NSPasteboardTypeString,
                    NSWorkspace, NSEvent, NSEventMaskKeyDown)
from Foundation import NSUserDefaults
from pynput import keyboard

# Import our modules
from clipboard_history import ClipboardHistory
from security_detector import SecurityDetector
from bitcoin_validator import BitcoinValidator
from smart_paste import SmartPaste
from history_window import HistoryWindow
from logo_handler import get_menu_bar_icons

class NoPrints(rumps.App):
    def __init__(self):
        super(NoPrints, self).__init__("🔒", quit_button=None)
        
        # Set icon - load menu bar icons  
        self.menu_icons = get_menu_bar_icons()
        self.template = None
        
        # Initialize components
        self.enabled = True
        self.pasteboard = NSPasteboard.generalPasteboard()
        self.last_change_count = 0
        self.last_content = None
        
        # Initialize modules
        self.history = ClipboardHistory(max_items=50)
        self.security = SecurityDetector()
        self.bitcoin = BitcoinValidator()
        self.smart_paste = SmartPaste()
        
        # Statistics
        self.cleaned_count = 0
        self.bitcoin_detected_count = 0
        self.passwords_detected_count = 0
        
        # Load preferences
        self.defaults = NSUserDefaults.standardUserDefaults()
        self.enabled = self.defaults.boolForKey_("ClipboardProtectionEnabled")
        if self.enabled is None:
            self.enabled = True
        
        # Hidden unicode characters (from original functionality)
        self.hidden_chars = [
            '\u200b', '\u200c', '\u200d', '\u200e', '\u200f',
            '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
            '\u2060', '\u2061', '\u2062', '\u2063', '\u2064',
            '\u2066', '\u2067', '\u2068', '\u2069',
            '\ufeff', '\ufffc', '\ufffd', '\u0000'
        ] + [chr(i) for i in range(0x01, 0x20)] + ['\u007f']
        
        self.hidden_pattern = re.compile('[' + ''.join(self.hidden_chars) + ']')
        
        # Setup menu
        self.setup_menu()
        
        # Start monitoring
        self.monitoring_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
        self.monitoring_thread.start()
        
        # Start expiration checker
        self.expiration_thread = threading.Thread(target=self.check_expirations, daemon=True)
        self.expiration_thread.start()
        
        # Setup global hotkeys
        self.setup_hotkeys()
        
        # Update icon
        self.update_icon()
    
    def setup_menu(self):
        """Build the menu bar dropdown"""
        # Main toggle
        self.toggle_item = rumps.MenuItem(
            f"{'✓ ' if self.enabled else '   '}Clipboard Protection",
            callback=self.toggle_protection
        )
        
        # Recent items section
        self.recent_menu = rumps.MenuItem("Recent Items")
        
        # Advanced features submenu (Bitcoin & Nostr)
        self.advanced_menu = rumps.MenuItem("Advanced")
        
        # Bitcoin items (in advanced)
        self.bitcoin_menu = rumps.MenuItem("₿ Bitcoin Items")
        
        # Nostr items (in advanced)
        self.nostr_menu = rumps.MenuItem("🟣 Nostr Items")
        
        # Security status (in advanced)
        self.security_status = rumps.MenuItem("🔒 Security Status")
        
        # Settings submenu
        settings_menu = rumps.MenuItem("Settings")
        
        self.auto_expire_sensitive = rumps.MenuItem(
            f"{'✓ ' if self.defaults.boolForKey_('AutoExpireSensitive') else '   '}Auto-expire Sensitive Data",
            callback=self.toggle_auto_expire_sensitive
        )
        
        self.show_notifications = rumps.MenuItem(
            f"{'✓ ' if self.defaults.boolForKey_('ShowNotifications') else '   '}Show Notifications",
            callback=self.toggle_notifications
        )
        
        self.blur_sensitive = rumps.MenuItem(
            f"{'✓ ' if self.defaults.boolForKey_('BlurSensitive') else '   '}Blur Sensitive Data",
            callback=self.toggle_blur
        )
        
        settings_menu.add(self.auto_expire_sensitive)
        settings_menu.add(self.show_notifications)
        settings_menu.add(self.blur_sensitive)
        
        # Actions
        show_history = rumps.MenuItem(
            "Show History (Cmd+Shift+V)",
            callback=self.show_history_window
        )
        
        clear_sensitive = rumps.MenuItem(
            "Clear Sensitive Data",
            callback=self.clear_sensitive_data
        )
        
        clear_all = rumps.MenuItem(
            "🗑️ Clear All (Clipboard + History)",
            callback=self.clear_all_data
        )
        
        # Statistics
        self.stats_item = rumps.MenuItem(
            f"📊 Stats: {self.cleaned_count} cleaned",
            callback=None
        )
        
        # Help & About
        help_item = rumps.MenuItem("Help", callback=self.show_help)
        about_item = rumps.MenuItem("About", callback=self.show_about)
        
        # Quit
        quit_item = rumps.MenuItem("Quit", callback=self.quit_app)
        
        # Build Advanced submenu
        self.advanced_menu.add(self.bitcoin_menu)
        self.advanced_menu.add(self.nostr_menu)
        self.advanced_menu.add(rumps.separator)
        self.advanced_menu.add(self.security_status)
        self.advanced_menu.add(rumps.separator)
        self.advanced_menu.add(self.stats_item)
        
        # Build main menu - cleaner structure
        self.menu = [
            self.toggle_item,
            rumps.separator,
            self.recent_menu,
            rumps.separator,
            show_history,
            clear_sensitive,
            clear_all,
            rumps.separator,
            settings_menu,
            self.advanced_menu,
            rumps.separator,
            help_item,
            about_item,
            rumps.separator,
            quit_item
        ]
        
        # Now update menu contents after menu is built
        self.update_recent_menu()
        self.update_bitcoin_menu()
        self.update_nostr_menu()
        self.update_security_status()
    
    def setup_hotkeys(self):
        """Setup global keyboard shortcuts"""
        def on_hotkey():
            # Show history window on Cmd+Shift+V
            self.show_history_window(None)
        
        # This would require additional setup for global hotkeys
        # For now, menu shortcuts work when app is focused
        pass
    
    def update_icon(self):
        """Update menu bar icon based on state"""
        if not self.enabled:
            new_icon = self.menu_icons['disabled']
        else:
            # Check for sensitive content in recent history
            recent = self.history.get_recent(count=5, include_sensitive=True)
            has_bitcoin = any(i.get('icon') == '₿' for i in recent)
            has_nostr = any(i.get('icon') in ['👤', '📝', '🟣'] for i in recent)
            has_sensitive = any(i.get('is_sensitive') for i in recent)
            
            if has_bitcoin and has_nostr:
                new_icon = self.menu_icons['both']
            elif has_bitcoin:
                new_icon = self.menu_icons['bitcoin']
            elif has_nostr:
                new_icon = self.menu_icons['nostr']
            elif has_sensitive:
                new_icon = self.menu_icons['sensitive']
            else:
                new_icon = self.menu_icons['normal']
        
        # Update icon - handle both file paths and emoji
        try:
            if new_icon and new_icon.endswith('.png'):
                # File-based icon (template)
                self.icon = new_icon
                self.template = True  # Enable template mode for proper macOS theming
                self.title = ""  # Clear title when using icon
            else:
                # Emoji-based icon  
                self.title = new_icon
                self.icon = None  # Clear icon when using title
                self.template = False
        except Exception as e:
            # Fallback to emoji
            self.title = '🔒'
            self.icon = None
            self.template = False
    
    def update_recent_menu(self):
        """Update recent items submenu"""
        try:
            self.recent_menu.clear()
        except AttributeError:
            # Menu not initialized yet
            pass
        
        recent_items = self.history.get_recent(count=10, include_sensitive=False)
        
        if not recent_items:
            self.recent_menu.add(rumps.MenuItem("(empty)", callback=None))
        else:
            for idx, item in enumerate(recent_items, 1):
                icon = item.get('icon', '📋')
                display = item.get('display_text', item['text'][:30])
                is_sensitive = item.get('is_sensitive', False)
                
                # Add number shortcut hint
                if idx <= 9:
                    menu_text = f"[{idx}] {icon} {display}"
                else:
                    menu_text = f"{icon} {display}"
                
                # For sensitive items, create submenu with reveal option
                if is_sensitive and display != item['text'][:30]:
                    parent_item = rumps.MenuItem(menu_text)
                    
                    # Main paste action
                    paste_item = rumps.MenuItem(
                        "📋 Paste",
                        callback=lambda _, i=item: self.paste_from_history(i)
                    )
                    parent_item.add(paste_item)
                    
                    # Reveal full content option
                    full_text = item['text'][:50] + ('...' if len(item['text']) > 50 else '')
                    reveal_item = rumps.MenuItem(
                        f"👁 Show: {full_text}",
                        callback=lambda _, i=item: self.paste_from_history(i)
                    )
                    parent_item.add(reveal_item)
                    
                    self.recent_menu.add(parent_item)
                else:
                    # Regular menu item for non-sensitive content
                    menu_item = rumps.MenuItem(
                        menu_text,
                        callback=lambda _, i=item: self.paste_from_history(i)
                    )
                    self.recent_menu.add(menu_item)
    
    def update_bitcoin_menu(self):
        """Update Bitcoin items submenu"""
        try:
            self.bitcoin_menu.clear()
        except AttributeError:
            # Menu not initialized yet
            pass
        
        bitcoin_items = self.history.get_bitcoin_items()
        
        if not bitcoin_items:
            self.bitcoin_menu.add(rumps.MenuItem("(no Bitcoin data)", callback=None))
        else:
            # Group by type
            addresses = []
            lightning = []
            sensitive = []
            
            for item in bitcoin_items:
                bitcoin_data = item['metadata'].get('security_analysis', {}).get('bitcoin', {})
                
                if bitcoin_data.get('private_keys') or bitcoin_data.get('seed_phrases'):
                    sensitive.append(item)
                elif bitcoin_data.get('lightning'):
                    lightning.append(item)
                elif bitcoin_data.get('addresses'):
                    addresses.append(item)
            
            # Add grouped items
            if addresses:
                self.bitcoin_menu.add(rumps.MenuItem(f"— Addresses ({len(addresses)}) —", callback=None))
                for item in addresses[:5]:
                    addr = item['metadata']['security_analysis']['bitcoin']['addresses'][0]
                    addr_value = addr['value']
                    addr_type = addr['type']
                    display = f"₿ {addr_type}: {addr_value[:6]}...{addr_value[-4:]}"
                    
                    # Create submenu for Bitcoin address with reveal option
                    parent_item = rumps.MenuItem(display)
                    
                    # Main paste action
                    paste_item = rumps.MenuItem(
                        "📋 Paste Address",
                        callback=lambda _, i=item: self.paste_from_history(i)
                    )
                    parent_item.add(paste_item)
                    
                    # Reveal full address option
                    reveal_item = rumps.MenuItem(
                        f"👁 Full: {addr_value}",
                        callback=lambda _, i=item: self.paste_from_history(i)
                    )
                    parent_item.add(reveal_item)
                    
                    self.bitcoin_menu.add(parent_item)
            
            if lightning:
                self.bitcoin_menu.add(rumps.separator)
                self.bitcoin_menu.add(rumps.MenuItem(f"— Lightning ({len(lightning)}) —", callback=None))
                for item in lightning[:3]:
                    menu_item = rumps.MenuItem(
                        f"⚡ Invoice",
                        callback=lambda _, i=item: self.paste_from_history(i)
                    )
                    self.bitcoin_menu.add(menu_item)
            
            if sensitive:
                self.bitcoin_menu.add(rumps.separator)
                self.bitcoin_menu.add(rumps.MenuItem(f"— ⚠️ Sensitive ({len(sensitive)}) —", callback=None))
                self.bitcoin_menu.add(rumps.MenuItem("(hidden for security)", callback=None))
    
    def update_nostr_menu(self):
        """Update Nostr items submenu"""
        try:
            self.nostr_menu.clear()
        except AttributeError:
            # Menu not initialized yet
            pass
        
        nostr_items = self.get_nostr_items()
        
        if not nostr_items:
            self.nostr_menu.add(rumps.MenuItem("(no Nostr data)", callback=None))
        else:
            # Group by type
            public_keys = []
            private_keys = []
            notes = []
            events = []
            relays = []
            
            for item in nostr_items:
                nostr_data = item['metadata'].get('security_analysis', {}).get('nostr', {})
                
                if nostr_data.get('private_keys'):
                    private_keys.append(item)
                elif nostr_data.get('public_keys'):
                    public_keys.append(item)
                elif nostr_data.get('notes'):
                    notes.append(item)
                elif nostr_data.get('events'):
                    events.append(item)
                elif nostr_data.get('relays'):
                    relays.append(item)
            
            # Add grouped items
            if public_keys:
                self.nostr_menu.add(rumps.MenuItem(f"— Public Keys ({len(public_keys)}) —", callback=None))
                for item in public_keys[:5]:
                    key_info = item['metadata']['security_analysis']['nostr']['public_keys'][0]
                    key_type = key_info['type']
                    key_value = key_info['value']
                    display = f"👤 {key_type}: {key_value[:12]}..."
                    
                    # Create submenu for Nostr key with reveal option
                    parent_item = rumps.MenuItem(display)
                    
                    # Main paste action
                    paste_item = rumps.MenuItem(
                        "📋 Paste Key",
                        callback=lambda _, i=item: self.paste_from_history(i)
                    )
                    parent_item.add(paste_item)
                    
                    # Reveal full key option
                    reveal_item = rumps.MenuItem(
                        f"👁 Full: {key_value}",
                        callback=lambda _, i=item: self.paste_from_history(i)
                    )
                    parent_item.add(reveal_item)
                    
                    self.nostr_menu.add(parent_item)
            
            if notes:
                if public_keys:
                    self.nostr_menu.add(rumps.separator)
                self.nostr_menu.add(rumps.MenuItem(f"— Notes ({len(notes)}) —", callback=None))
                for item in notes[:3]:
                    menu_item = rumps.MenuItem(
                        f"📝 Note",
                        callback=lambda _, i=item: self.paste_from_history(i)
                    )
                    self.nostr_menu.add(menu_item)
            
            if events:
                if public_keys or notes:
                    self.nostr_menu.add(rumps.separator)
                self.nostr_menu.add(rumps.MenuItem(f"— Events ({len(events)}) —", callback=None))
                for item in events[:3]:
                    menu_item = rumps.MenuItem(
                        f"📅 Event",
                        callback=lambda _, i=item: self.paste_from_history(i)
                    )
                    self.nostr_menu.add(menu_item)
            
            if relays:
                if any([public_keys, notes, events]):
                    self.nostr_menu.add(rumps.separator)
                self.nostr_menu.add(rumps.MenuItem(f"— Relays ({len(relays)}) —", callback=None))
                for item in relays[:3]:
                    menu_item = rumps.MenuItem(
                        f"🔗 Relay",
                        callback=lambda _, i=item: self.paste_from_history(i)
                    )
                    self.nostr_menu.add(menu_item)
            
            if private_keys:
                self.nostr_menu.add(rumps.separator)
                self.nostr_menu.add(rumps.MenuItem(f"— ⚠️ Private Keys ({len(private_keys)}) —", callback=None))
                self.nostr_menu.add(rumps.MenuItem("(hidden for security)", callback=None))
    
    def get_nostr_items(self):
        """Get all Nostr-related items"""
        nostr_items = []
        
        for item in self.history.history:
            if self._is_expired(item):
                continue
            
            metadata = item.get('metadata', {})
            security = metadata.get('security_analysis', {})
            
            if security.get('nostr') and any(security['nostr'].values()):
                nostr_items.append(item)
        
        return nostr_items
    
    def _is_expired(self, item):
        """Check if history item is expired"""
        expire_at = item.get('expire_at')
        if expire_at:
            import time
            return time.time() >= expire_at
        return False
    
    def update_security_status(self):
        """Update security status menu"""
        try:
            self.security_status.clear()
        except AttributeError:
            # Menu not initialized yet
            pass
        
        stats = self.history.get_statistics()
        
        # Count Nostr items
        nostr_count = len(self.get_nostr_items())
        
        # Status items
        status_items = [
            f"Total items: {stats['total_items']}",
            f"Sensitive items: {stats['sensitive_items']}",
            f"Bitcoin items: {stats['bitcoin_items']}",
            f"Nostr items: {nostr_count}",
            f"Expiring soon: {stats['expiring_soon']}",
            f"Pinned items: {stats['pinned_items']}"
        ]
        
        for status in status_items:
            self.security_status.add(rumps.MenuItem(status, callback=None))
    
    def toggle_protection(self, sender):
        """Toggle clipboard protection on/off"""
        self.enabled = not self.enabled
        sender.title = f"{'✓ ' if self.enabled else '   '}Clipboard Protection"
        self.defaults.setBool_forKey_(self.enabled, "ClipboardProtectionEnabled")
        self.update_icon()
        
        if self.defaults.boolForKey_("ShowNotifications"):
            status = "enabled" if self.enabled else "disabled"
            rumps.notification(
                "Clipboard Protection",
                "",
                f"Protection {status}",
                sound=False
            )
    
    def toggle_auto_expire_sensitive(self, sender):
        """Toggle auto-expiration for all sensitive data"""
        current = self.defaults.boolForKey_("AutoExpireSensitive")
        new_state = not current
        self.defaults.setBool_forKey_(new_state, "AutoExpireSensitive")
        # Also set the legacy keys for compatibility
        self.defaults.setBool_forKey_(new_state, "AutoExpireBitcoin")
        self.defaults.setBool_forKey_(new_state, "AutoExpirePasswords")
        sender.title = f"{'✓ ' if new_state else '   '}Auto-expire Sensitive Data"
    
    def toggle_notifications(self, sender):
        """Toggle notifications"""
        current = self.defaults.boolForKey_("ShowNotifications")
        new_state = not current
        self.defaults.setBool_forKey_(new_state, "ShowNotifications")
        sender.title = f"{'✓ ' if new_state else '   '}Show Notifications"
    
    def toggle_blur(self, sender):
        """Toggle sensitive data blurring"""
        current = self.defaults.boolForKey_("BlurSensitive")
        new_state = not current
        self.defaults.setBool_forKey_(new_state, "BlurSensitive")
        sender.title = f"{'✓ ' if new_state else '   '}Blur Sensitive Data"
    
    def show_history_window(self, sender):
        """Show the history picker window"""
        def on_select(item):
            # Paste the selected item
            self.set_clipboard_content(item['text'])
        
        window = HistoryWindow(self.history, on_select)
        window.show()
    
    def clear_sensitive_data(self, sender):
        """Clear all sensitive clipboard data"""
        self.history.clear_sensitive()
        self.update_recent_menu()
        self.update_bitcoin_menu()
        self.update_security_status()
        
        if self.defaults.boolForKey_("ShowNotifications"):
            rumps.notification(
                "Security",
                "",
                "Sensitive data cleared",
                sound=False
            )
    
    def clear_all_data(self, sender):
        """Clear system clipboard, all history, and reset stats"""
        # Clear system clipboard
        self.set_clipboard_content("")
        
        # Clear all clipboard history
        self.history.clear_all()
        
        # Reset all statistics
        self.cleaned_count = 0
        self.bitcoin_detected_count = 0
        self.passwords_detected_count = 0
        if hasattr(self, 'nostr_detected_count'):
            self.nostr_detected_count = 0
        
        # Update all UI components
        self.update_recent_menu()
        self.update_bitcoin_menu()
        self.update_nostr_menu()
        self.update_security_status()
        self.update_icon()
        
        # Update stats display
        self.stats_item.title = "📊 Stats: 0 cleaned, 0 Bitcoin, 0 Nostr"
        
        if self.defaults.boolForKey_("ShowNotifications"):
            rumps.notification(
                "NoPrints",
                "",
                "🗑️ All data cleared: clipboard, history & stats reset",
                sound=False
            )
    
    def paste_from_history(self, item):
        """Paste item from history"""
        self.set_clipboard_content(item['text'])
        
        # Apply smart paste if needed
        target_app = self.smart_paste.get_active_app()
        formatted_text, format_type = self.smart_paste.format_for_paste(
            item['text'],
            target_app
        )
        
        if formatted_text != item['text']:
            self.set_clipboard_content(formatted_text)
    
    def show_help(self, sender):
        """Show help dialog"""
        rumps.alert(
            "NoPrints Help",
            "NoPrints eliminates hidden unicode characters and protects sensitive data.\n\n"
            "Keyboard Shortcuts:\n"
            "• Cmd+V: Normal paste\n"
            "• Cmd+Shift+V: Show history\n"
            "• 1-9: Quick paste from recent\n\n"
            "Features:\n"
            "• Removes hidden Unicode characters\n"
            "• Protects Bitcoin addresses & keys\n"
            "• Protects Nostr keys & events\n"
            "• Auto-expires sensitive data\n"
            "• Smart paste for different apps\n"
            "• Encrypted history storage\n\n"
            "Security:\n"
            "• Bitcoin data expires in 30s\n"
            "• Nostr private keys expire in 10s\n"
            "• Passwords expire in 60s\n"
            "• Private keys hidden immediately",
            "OK"
        )
    
    def show_about(self, sender):
        """Show about dialog"""
        rumps.alert(
            "NoPrints",
            "Version 3.1\n\n"
            "Advanced clipboard management with:\n"
            "• Bitcoin security features\n"
            "• Nostr protocol protection\n"
            "• Hidden Unicode removal\n"
            "• Smart paste technology\n"
            "• Encrypted history\n\n"
            "© 2025 - NoPrints for macOS",
            "OK"
        )
    
    def quit_app(self, sender):
        """Quit application"""
        rumps.quit_application()
    
    def clean_text(self, text):
        """Remove hidden unicode characters"""
        if not text:
            return text
        
        text = unicodedata.normalize('NFC', text)
        text = self.hidden_pattern.sub('', text)
        
        # Additional cleaning
        text = re.sub(r'\s+', ' ', text)
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        text = '\n'.join(lines)
        
        return text
    
    def get_clipboard_content(self):
        """Get clipboard content if changed"""
        if self.pasteboard.changeCount() == self.last_change_count:
            return None
        
        self.last_change_count = self.pasteboard.changeCount()
        
        content = self.pasteboard.stringForType_(NSStringPboardType)
        if not content:
            content = self.pasteboard.stringForType_(NSPasteboardTypeString)
        
        return content
    
    def set_clipboard_content(self, content):
        """Set clipboard content"""
        self.pasteboard.clearContents()
        self.pasteboard.setString_forType_(content, NSStringPboardType)
        self.last_change_count = self.pasteboard.changeCount()
    
    def monitor_clipboard(self):
        """Main clipboard monitoring loop"""
        while True:
            try:
                if self.enabled:
                    content = self.get_clipboard_content()
                    
                    if content and content != self.last_content:
                        # Clean hidden unicode
                        cleaned = self.clean_text(content)
                        
                        if cleaned != content:
                            self.set_clipboard_content(cleaned)
                            self.cleaned_count += 1
                            content = cleaned
                        
                        # Get active app
                        active_app = self.smart_paste.get_active_app()
                        
                        # Analyze security
                        security_analysis = self.security.analyze_content(
                            content,
                            source_app=active_app.get('name')
                        )
                        
                        # Add to history
                        self.history.add_item(content, {
                            'security_analysis': security_analysis,
                            'source_app': active_app.get('name'),
                            'timestamp': time.time()
                        })
                        
                        # Update counts
                        if security_analysis['bitcoin']:
                            self.bitcoin_detected_count += 1
                        if security_analysis['passwords']:
                            self.passwords_detected_count += 1
                        
                        # Show notifications
                        if self.defaults.boolForKey_("ShowNotifications"):
                            if security_analysis['risk_level'] == 'critical':
                                rumps.notification(
                                    "⚠️ Critical Security Alert",
                                    "",
                                    security_analysis['warnings'][0] if security_analysis['warnings'] else "Sensitive data detected",
                                    sound=True
                                )
                            elif security_analysis['risk_level'] == 'high':
                                rumps.notification(
                                    "Security Notice",
                                    "",
                                    f"Sensitive data will expire in {security_analysis.get('expire_seconds', 60)}s",
                                    sound=False
                                )
                        
                        # Count Nostr detections
                        if security_analysis['nostr']:
                            self.nostr_detected_count = getattr(self, 'nostr_detected_count', 0) + 1
                        
                        # Update UI
                        self.update_recent_menu()
                        self.update_bitcoin_menu()
                        self.update_nostr_menu()
                        self.update_security_status()
                        self.update_icon()
                        self.stats_item.title = f"📊 Stats: {self.cleaned_count} cleaned, {self.bitcoin_detected_count} Bitcoin, {getattr(self, 'nostr_detected_count', 0)} Nostr"
                        
                        self.last_content = cleaned
                
            except Exception as e:
                print(f"Monitor error: {e}")
            
            time.sleep(0.1)
    
    def check_expirations(self):
        """Check for expired items"""
        while True:
            try:
                expired = self.history.clear_expired()
                if expired > 0:
                    self.update_recent_menu()
                    self.update_bitcoin_menu()
                    self.update_security_status()
                    self.update_icon()
            except Exception as e:
                print(f"Expiration check error: {e}")
            
            time.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    app = NoPrints()
    app.run()