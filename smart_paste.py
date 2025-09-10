#!/usr/bin/env python3
"""
Smart paste module for context-aware clipboard pasting
"""

import subprocess
from AppKit import NSWorkspace, NSRunningApplication

class SmartPaste:
    def __init__(self):
        # App categories for smart formatting
        self.app_categories = {
            'terminal': [
                'Terminal', 'iTerm2', 'iTerm', 'Hyper', 'Alacritty',
                'kitty', 'WezTerm', 'Console'
            ],
            'ide': [
                'Visual Studio Code', 'Code', 'Xcode', 'IntelliJ IDEA',
                'PyCharm', 'WebStorm', 'Sublime Text', 'Atom', 'Nova',
                'TextMate', 'BBEdit', 'Cursor', 'Zed'
            ],
            'browser': [
                'Safari', 'Google Chrome', 'Chrome', 'Firefox', 'Brave Browser',
                'Microsoft Edge', 'Opera', 'Vivaldi', 'Arc'
            ],
            'word_processor': [
                'Microsoft Word', 'Pages', 'Google Docs', 'LibreOffice Writer',
                'TextEdit', 'Scrivener', 'Ulysses', 'Bear', 'Notion',
                'Obsidian', 'Craft'
            ],
            'spreadsheet': [
                'Microsoft Excel', 'Numbers', 'Google Sheets', 'LibreOffice Calc'
            ],
            'email': [
                'Mail', 'Outlook', 'Thunderbird', 'Spark', 'Airmail',
                'Canary Mail', 'Gmail'
            ],
            'messaging': [
                'Messages', 'Slack', 'Discord', 'Telegram', 'WhatsApp',
                'Signal', 'Microsoft Teams', 'Zoom'
            ],
            'bitcoin_wallet': [
                'Sparrow', 'Electrum', 'Bitcoin Core', 'Wasabi Wallet',
                'BlueWallet', 'Specter', 'Bitcoin-Qt', 'Blockstream Green'
            ],
            'password_manager': [
                '1Password', 'Bitwarden', 'LastPass', 'KeePassXC',
                'Dashlane', 'Enpass', 'NordPass'
            ]
        }
        
        # Format preferences by app category
        self.format_preferences = {
            'terminal': 'plain_text',
            'ide': 'preserve_code',
            'browser': 'smart_format',
            'word_processor': 'rich_text',
            'spreadsheet': 'tabular',
            'email': 'email_format',
            'messaging': 'plain_text',
            'bitcoin_wallet': 'exact_copy',
            'password_manager': 'exact_copy'
        }
    
    def get_active_app(self):
        """Get the currently active application"""
        try:
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.activeApplication()
            
            if active_app:
                app_name = active_app.get('NSApplicationName', '')
                bundle_id = active_app.get('NSApplicationBundleIdentifier', '')
                
                return {
                    'name': app_name,
                    'bundle_id': bundle_id,
                    'category': self._categorize_app(app_name)
                }
        except Exception as e:
            print(f"Error getting active app: {e}")
        
        return {
            'name': 'Unknown',
            'bundle_id': '',
            'category': 'unknown'
        }
    
    def _categorize_app(self, app_name):
        """Categorize app based on its name"""
        for category, apps in self.app_categories.items():
            if any(app.lower() in app_name.lower() for app in apps):
                return category
        return 'unknown'
    
    def format_for_paste(self, text, target_app=None):
        """
        Format text based on target application
        
        Returns: (formatted_text, format_type)
        """
        if not target_app:
            target_app = self.get_active_app()
        
        app_category = target_app.get('category', 'unknown')
        format_type = self.format_preferences.get(app_category, 'smart_format')
        
        # Apply formatting based on type
        if format_type == 'plain_text':
            return self._to_plain_text(text), 'plain'
        elif format_type == 'preserve_code':
            return self._preserve_code_format(text), 'code'
        elif format_type == 'rich_text':
            return text, 'rich'  # Keep as-is
        elif format_type == 'tabular':
            return self._format_tabular(text), 'table'
        elif format_type == 'email_format':
            return self._format_for_email(text), 'email'
        elif format_type == 'exact_copy':
            return text, 'exact'  # No modification at all
        else:
            return self._smart_format(text), 'smart'
    
    def _to_plain_text(self, text):
        """Convert to plain text, removing all formatting"""
        # Remove hidden unicode characters
        import unicodedata
        
        # Normalize unicode
        text = unicodedata.normalize('NFC', text)
        
        # Remove common hidden characters
        hidden_chars = [
            '\u200b', '\u200c', '\u200d', '\u200e', '\u200f',
            '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',
            '\u2060', '\u2061', '\u2062', '\u2063', '\u2064',
            '\ufeff'
        ]
        
        for char in hidden_chars:
            text = text.replace(char, '')
        
        # Normalize whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _preserve_code_format(self, text):
        """Preserve code formatting, keep indentation"""
        # Remove trailing whitespace from lines but preserve indentation
        lines = text.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        return '\n'.join(cleaned_lines)
    
    def _format_tabular(self, text):
        """Format text for spreadsheet paste"""
        # Detect if text has tab-separated values
        if '\t' in text:
            return text  # Already formatted
        
        # Check if comma-separated
        if ',' in text and '\n' in text:
            # Convert CSV to TSV for spreadsheet paste
            lines = text.split('\n')
            formatted_lines = []
            for line in lines:
                # Simple CSV parsing (doesn't handle quoted commas)
                formatted_lines.append(line.replace(',', '\t'))
            return '\n'.join(formatted_lines)
        
        return text
    
    def _format_for_email(self, text):
        """Format text for email clients"""
        # Clean up excessive line breaks
        import re
        
        # Replace multiple newlines with double newline (paragraph break)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Ensure proper sentence spacing
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1  \2', text)
        
        return text
    
    def _smart_format(self, text):
        """Apply smart formatting based on content detection"""
        # Detect content type and format accordingly
        
        # Check if it's code
        code_indicators = ['function', 'def ', 'class ', 'import ', 'const ', 'var ', 'let ']
        if any(indicator in text for indicator in code_indicators):
            return self._preserve_code_format(text)
        
        # Check if it's structured data (JSON, XML, etc.)
        if text.strip().startswith('{') or text.strip().startswith('['):
            return self._preserve_code_format(text)  # Likely JSON
        
        # Check if it's a URL
        if text.startswith('http://') or text.startswith('https://'):
            return text.strip()  # Clean URL
        
        # Check if it's an email
        if '@' in text and '.' in text and ' ' not in text:
            return text.strip().lower()  # Clean email
        
        # Default: clean plain text
        return self._to_plain_text(text)
    
    def should_paste_as_plain(self, target_app=None):
        """Determine if paste should be plain text"""
        if not target_app:
            target_app = self.get_active_app()
        
        app_category = target_app.get('category', 'unknown')
        
        # These categories should always get plain text
        plain_text_categories = ['terminal', 'messaging', 'bitcoin_wallet']
        
        return app_category in plain_text_categories
    
    def get_paste_shortcuts(self, target_app=None):
        """Get recommended paste shortcuts for current app"""
        if not target_app:
            target_app = self.get_active_app()
        
        app_category = target_app.get('category', 'unknown')
        app_name = target_app.get('name', 'Unknown')
        
        shortcuts = {
            'normal': 'Cmd+V',
            'plain': 'Cmd+Shift+V',
            'history': 'Cmd+Shift+H',
            'special': None
        }
        
        # App-specific shortcuts
        if app_category == 'terminal':
            shortcuts['special'] = 'Right-click to paste'
        elif app_category == 'ide':
            shortcuts['special'] = 'Cmd+Shift+V for history'
        elif 'Excel' in app_name or 'Numbers' in app_name:
            shortcuts['special'] = 'Cmd+Opt+V for paste special'
        
        return shortcuts
    
    def analyze_paste_context(self, clipboard_text, target_app=None):
        """
        Analyze the paste context and provide recommendations
        
        Returns dict with:
        - recommended_format: how to format the text
        - warnings: any warnings about the paste
        - suggestions: helpful suggestions
        """
        if not target_app:
            target_app = self.get_active_app()
        
        result = {
            'recommended_format': 'auto',
            'warnings': [],
            'suggestions': []
        }
        
        app_category = target_app.get('category', 'unknown')
        app_name = target_app.get('name', 'Unknown')
        
        # Check for Bitcoin content going to non-wallet app
        from bitcoin_validator import BitcoinValidator
        validator = BitcoinValidator()
        bitcoin_content = validator.detect_bitcoin_content(clipboard_text)
        
        if bitcoin_content['addresses'] or bitcoin_content['private_keys']:
            if app_category not in ['bitcoin_wallet', 'password_manager']:
                result['warnings'].append(f"⚠️ Bitcoin data detected - pasting to {app_name}")
                result['suggestions'].append("Consider using a Bitcoin wallet app")
        
        # Check for password going to public app
        if app_category in ['browser', 'messaging', 'email']:
            # Simple password detection
            if len(clipboard_text) > 8 and any(c.isdigit() for c in clipboard_text) \
               and any(c.isupper() for c in clipboard_text) and any(c.islower() for c in clipboard_text):
                result['warnings'].append("⚠️ Possible password - pasting to public app")
        
        # Formatting recommendations
        if app_category == 'terminal':
            result['recommended_format'] = 'plain_text'
            result['suggestions'].append("Will paste as plain text")
        elif app_category == 'spreadsheet' and '\n' in clipboard_text:
            result['recommended_format'] = 'tabular'
            result['suggestions'].append("Will format as table data")
        elif app_category == 'bitcoin_wallet':
            result['recommended_format'] = 'exact'
            result['suggestions'].append("Exact copy - no modifications")
        
        return result