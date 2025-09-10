#!/usr/bin/env python3
"""
Clipboard history management with encryption and expiration
"""

import json
import time
import hashlib
import base64
from datetime import datetime, timedelta
from collections import deque
import keyring
from cryptography.fernet import Fernet

class ClipboardHistory:
    def __init__(self, max_items=50):
        self.max_items = max_items
        self.history = deque(maxlen=max_items)
        self.sensitive_items = {}  # Track expiration times
        self.pinned_items = []
        self.encryption_key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Load saved history
        self.load_history()
    
    def _get_or_create_key(self):
        """Get or create encryption key in macOS Keychain"""
        service_name = "NoPrints"
        account_name = "encryption_key"
        
        # Try to get existing key
        stored_key = keyring.get_password(service_name, account_name)
        
        if stored_key:
            return base64.urlsafe_b64decode(stored_key.encode())
        else:
            # Generate new key
            key = Fernet.generate_key()
            # Store in keychain
            keyring.set_password(service_name, account_name, 
                               base64.urlsafe_b64encode(key).decode())
            return key
    
    def add_item(self, text, metadata=None):
        """
        Add item to history with metadata
        
        metadata can include:
        - security_analysis: from SecurityDetector
        - source_app: application it came from
        - timestamp: when copied
        - expire_at: when to auto-remove
        - is_sensitive: boolean
        """
        if not text:
            return
        
        # Check if item already exists (avoid duplicates)
        for item in self.history:
            if item['text'] == text:
                # Move to front (most recent)
                self.history.remove(item)
                item['timestamp'] = time.time()
                item['access_count'] = item.get('access_count', 0) + 1
                self.history.appendleft(item)
                return
        
        # Create new history item
        item = {
            'id': self._generate_id(text),
            'text': text,
            'timestamp': time.time(),
            'access_count': 1,
            'metadata': metadata or {},
            'display_text': None,
            'icon': '📋'
        }
        
        # Process metadata
        if metadata:
            security = metadata.get('security_analysis', {})
            
            # Set display text based on security
            if security.get('should_blur'):
                item['display_text'] = self._get_blurred_text(text, security)
            else:
                item['display_text'] = text[:100] + '...' if len(text) > 100 else text
            
            # Set icon based on content type
            if security.get('bitcoin'):
                bitcoin_data = security['bitcoin']
                if bitcoin_data.get('private_keys'):
                    item['icon'] = '🔑'
                elif bitcoin_data.get('seed_phrases'):
                    item['icon'] = '🌱'
                elif bitcoin_data.get('addresses'):
                    item['icon'] = '₿'
                elif bitcoin_data.get('lightning'):
                    item['icon'] = '⚡'
            elif security.get('passwords'):
                item['icon'] = '🔒'
            elif security.get('credit_cards'):
                item['icon'] = '💳'
            elif security.get('api_keys'):
                item['icon'] = '🔐'
            
            # Set expiration
            if security.get('should_expire'):
                expire_seconds = security.get('expire_seconds', 60)
                item['expire_at'] = time.time() + expire_seconds
                self.sensitive_items[item['id']] = item['expire_at']
            
            # Mark as sensitive
            item['is_sensitive'] = security.get('risk_level') in ['high', 'critical']
        
        # Add to history
        self.history.appendleft(item)
        
        # Save to disk (encrypted)
        self.save_history()
        
        return item
    
    def get_item(self, item_id):
        """Get specific item by ID"""
        for item in self.history:
            if item['id'] == item_id:
                item['access_count'] = item.get('access_count', 0) + 1
                return item
        return None
    
    def get_recent(self, count=10, include_sensitive=False):
        """Get recent items"""
        items = []
        for item in self.history:
            # Skip expired items
            if self._is_expired(item):
                continue
            
            # Skip sensitive if requested
            if not include_sensitive and item.get('is_sensitive'):
                continue
            
            items.append(item)
            
            if len(items) >= count:
                break
        
        return items
    
    def search(self, query, include_sensitive=False):
        """Search history"""
        query = query.lower()
        results = []
        
        for item in self.history:
            # Skip expired
            if self._is_expired(item):
                continue
            
            # Skip sensitive if requested
            if not include_sensitive and item.get('is_sensitive'):
                continue
            
            # Search in text
            if query in item['text'].lower():
                results.append(item)
            # Search in metadata
            elif any(query in str(v).lower() for v in item.get('metadata', {}).values()):
                results.append(item)
        
        return results
    
    def get_bitcoin_items(self):
        """Get all Bitcoin-related items"""
        bitcoin_items = []
        
        for item in self.history:
            if self._is_expired(item):
                continue
            
            metadata = item.get('metadata', {})
            security = metadata.get('security_analysis', {})
            
            if security.get('bitcoin'):
                bitcoin_items.append(item)
        
        return bitcoin_items
    
    def clear_sensitive(self):
        """Clear all sensitive items immediately"""
        # Create new history without sensitive items
        new_history = deque(maxlen=self.max_items)
        
        for item in self.history:
            if not item.get('is_sensitive'):
                new_history.append(item)
        
        self.history = new_history
        self.sensitive_items.clear()
        self.save_history()
    
    def clear_expired(self):
        """Remove expired items"""
        current_time = time.time()
        expired_ids = []
        
        # Find expired items
        for item_id, expire_time in list(self.sensitive_items.items()):
            if expire_time <= current_time:
                expired_ids.append(item_id)
                del self.sensitive_items[item_id]
        
        # Remove from history
        if expired_ids:
            new_history = deque(maxlen=self.max_items)
            for item in self.history:
                if item['id'] not in expired_ids:
                    new_history.append(item)
            self.history = new_history
            self.save_history()
        
        return len(expired_ids)
    
    def pin_item(self, item_id):
        """Pin an item to keep it from being removed"""
        if item_id not in self.pinned_items:
            self.pinned_items.append(item_id)
            # Remove from expiration tracking
            if item_id in self.sensitive_items:
                del self.sensitive_items[item_id]
    
    def unpin_item(self, item_id):
        """Unpin an item"""
        if item_id in self.pinned_items:
            self.pinned_items.remove(item_id)
    
    def delete_item(self, item_id):
        """Delete specific item"""
        for item in list(self.history):
            if item['id'] == item_id:
                self.history.remove(item)
                if item_id in self.sensitive_items:
                    del self.sensitive_items[item_id]
                if item_id in self.pinned_items:
                    self.pinned_items.remove(item_id)
                self.save_history()
                return True
        return False
    
    def save_history(self):
        """Save history to encrypted file"""
        try:
            # Prepare data for saving
            save_data = {
                'history': list(self.history)[:20],  # Save only last 20 for persistence
                'pinned': self.pinned_items,
                'sensitive_expiry': self.sensitive_items
            }
            
            # Convert to JSON
            json_data = json.dumps(save_data)
            
            # Encrypt
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            
            # Save to file
            history_file = self._get_history_file()
            with open(history_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_history(self):
        """Load history from encrypted file"""
        try:
            history_file = self._get_history_file()
            
            if not history_file.exists():
                return
            
            # Read encrypted data
            with open(history_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            json_data = self.cipher_suite.decrypt(encrypted_data).decode()
            
            # Parse JSON
            save_data = json.loads(json_data)
            
            # Restore history
            self.history = deque(save_data.get('history', []), maxlen=self.max_items)
            self.pinned_items = save_data.get('pinned', [])
            self.sensitive_items = save_data.get('sensitive_expiry', {})
            
            # Clean expired items on load
            self.clear_expired()
            
        except Exception as e:
            print(f"Error loading history: {e}")
            # Start with empty history on error
            self.history = deque(maxlen=self.max_items)
    
    def _generate_id(self, text):
        """Generate unique ID for clipboard item"""
        timestamp = str(time.time())
        hash_input = f"{text}{timestamp}".encode()
        return hashlib.sha256(hash_input).hexdigest()[:12]
    
    def _is_expired(self, item):
        """Check if item is expired"""
        expire_at = item.get('expire_at')
        if expire_at:
            return time.time() >= expire_at
        return False
    
    def _get_blurred_text(self, text, security_analysis):
        """Get blurred version of sensitive text"""
        bitcoin = security_analysis.get('bitcoin', {})
        
        if bitcoin.get('private_keys'):
            return "🔑 Private Key (hidden)"
        elif bitcoin.get('seed_phrases'):
            phrase = bitcoin['seed_phrases'][0]
            word_count = phrase.get('word_count', 12)
            return f"🌱 Seed Phrase ({word_count} words)"
        elif bitcoin.get('addresses'):
            addr = bitcoin['addresses'][0]['value']
            addr_type = bitcoin['addresses'][0].get('type', 'bitcoin')
            return f"₿ {addr_type}: {addr[:6]}...{addr[-4:]}"
        elif security_analysis.get('passwords'):
            return "🔒 Password (hidden)"
        elif security_analysis.get('credit_cards'):
            return "💳 Credit Card (hidden)"
        else:
            # Generic blur
            if len(text) > 12:
                return f"{text[:4]}...{text[-4:]}"
            return "***hidden***"
    
    def _get_history_file(self):
        """Get path to history file"""
        from pathlib import Path
        app_data = Path.home() / 'Library' / 'Application Support' / 'NoPrints'
        app_data.mkdir(parents=True, exist_ok=True)
        return app_data / 'history.enc'
    
    def get_statistics(self):
        """Get history statistics"""
        stats = {
            'total_items': len(self.history),
            'sensitive_items': sum(1 for i in self.history if i.get('is_sensitive')),
            'bitcoin_items': len(self.get_bitcoin_items()),
            'pinned_items': len(self.pinned_items),
            'expiring_soon': sum(1 for i in self.sensitive_items.values() 
                               if i - time.time() < 30)
        }
        return stats