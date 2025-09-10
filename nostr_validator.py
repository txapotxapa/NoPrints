#!/usr/bin/env python3
"""
Nostr protocol validation and detection module
"""

import re
import hashlib
import base64

class NostrValidator:
    def __init__(self):
        # Nostr key patterns
        self.patterns = {
            # Nostr public keys (npub - bech32 encoded)
            'npub': re.compile(r'^npub1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{58}$'),
            
            # Nostr private keys (nsec - bech32 encoded)
            'nsec': re.compile(r'^nsec1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{58}$'),
            
            # Nostr note IDs (note - bech32 encoded)
            'note': re.compile(r'^note1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{58}$'),
            
            # Nostr event IDs (nevent - bech32 encoded with additional data)
            'nevent': re.compile(r'^nevent1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{100,200}$'),
            
            # Nostr profile references (nprofile - bech32 encoded with relay info)
            'nprofile': re.compile(r'^nprofile1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{100,300}$'),
            
            # Nostr relay URLs (nrelay - bech32 encoded relay URL)
            'nrelay': re.compile(r'^nrelay1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{50,100}$'),
            
            # Nostr addresses (naddr - bech32 encoded addresses)
            'naddr': re.compile(r'^naddr1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{100,200}$'),
            
            # Raw hex public keys (64 characters)
            'hex_pubkey': re.compile(r'^[0-9a-fA-F]{64}$'),
            
            # Raw hex private keys (64 characters) - same pattern but context matters
            'hex_privkey': re.compile(r'^[0-9a-fA-F]{64}$'),
            
            # Nostr relay WebSocket URLs
            'relay_ws': re.compile(r'^wss?://[a-zA-Z0-9.-]+(?::[0-9]+)?(?:/[^\s]*)?$'),
            
            # NIP-05 identifiers (like email format)
            'nip05': re.compile(r'^[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,}$', re.IGNORECASE),
            
            # Lightning addresses in Nostr context
            'lightning_nip57': re.compile(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', re.IGNORECASE),
            
            # Nostr Zap requests/receipts
            'zap_request': re.compile(r'\"kind\":\s*9734'),
            'zap_receipt': re.compile(r'\"kind\":\s*9735'),
        }
        
        # Bech32 alphabet for Nostr
        self.bech32_alphabet = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l'
        
        # Common Nostr relay hosts
        self.known_relays = [
            'relay.damus.io',
            'relay.snort.social', 
            'nos.lol',
            'relay.nostr.band',
            'nostr-pub.wellorder.net',
            'relay.current.fyi',
            'brb.io',
            'relay.nostr.info',
            'offchain.pub',
            'relay.nostrgraph.net'
        ]
        
        # Nostr event kinds (for context detection)
        self.event_kinds = {
            0: 'profile_metadata',
            1: 'text_note',
            2: 'recommend_relay',
            3: 'contact_list',
            4: 'encrypted_dm',
            5: 'event_deletion',
            6: 'repost',
            7: 'reaction',
            9734: 'zap_request',
            9735: 'zap_receipt',
            10002: 'relay_list',
            30023: 'long_form_content'
        }
    
    def detect_nostr_content(self, text):
        """
        Detect Nostr-related content in text
        Returns: dict with detected items and their types
        """
        results = {
            'public_keys': [],
            'private_keys': [],
            'notes': [],
            'events': [],
            'relays': [],
            'nip05_ids': [],
            'zaps': [],
            'raw_events': [],
            'risk_level': 'low'
        }
        
        if not text:
            return results
        
        # Split text into tokens for analysis
        tokens = text.split()
        lines = text.split('\n')
        
        for token in tokens:
            token = token.strip('.,;:!?"\'()[]{}')
            
            # Check Nostr bech32 encoded keys and IDs
            if self.patterns['nsec'].match(token):
                results['private_keys'].append({
                    'value': token,
                    'type': 'nsec',
                    'encoding': 'bech32'
                })
                results['risk_level'] = 'critical'
                
            elif self.patterns['npub'].match(token):
                results['public_keys'].append({
                    'value': token,
                    'type': 'npub', 
                    'encoding': 'bech32'
                })
                results['risk_level'] = max_risk(results['risk_level'], 'medium')
                
            elif self.patterns['note'].match(token):
                results['notes'].append({
                    'value': token,
                    'type': 'note',
                    'encoding': 'bech32'
                })
                results['risk_level'] = max_risk(results['risk_level'], 'low')
                
            elif self.patterns['nevent'].match(token):
                results['events'].append({
                    'value': token,
                    'type': 'nevent',
                    'encoding': 'bech32'
                })
                results['risk_level'] = max_risk(results['risk_level'], 'low')
                
            elif self.patterns['nprofile'].match(token):
                results['public_keys'].append({
                    'value': token,
                    'type': 'nprofile',
                    'encoding': 'bech32'
                })
                results['risk_level'] = max_risk(results['risk_level'], 'medium')
                
            elif self.patterns['nrelay'].match(token):
                results['relays'].append({
                    'value': token,
                    'type': 'nrelay',
                    'encoding': 'bech32'
                })
                
            elif self.patterns['naddr'].match(token):
                results['events'].append({
                    'value': token,
                    'type': 'naddr',
                    'encoding': 'bech32'
                })
                
            # Check relay WebSocket URLs
            elif self.patterns['relay_ws'].match(token):
                results['relays'].append({
                    'value': token,
                    'type': 'websocket_url'
                })
                
            # Check NIP-05 identifiers
            elif self.patterns['nip05'].match(token):
                # Distinguish from regular email by checking known domains or context
                if any(relay in token for relay in self.known_relays) or 'nostr' in text.lower():
                    results['nip05_ids'].append({
                        'value': token,
                        'type': 'nip05'
                    })
        
        # Check for raw hex keys (need context to distinguish pub vs priv)
        hex_tokens = [t for t in tokens if self.patterns['hex_pubkey'].match(t)]
        
        for hex_token in hex_tokens:
            # Try to determine if it's a private key based on context
            context = text.lower()
            
            if any(indicator in context for indicator in ['private', 'secret', 'nsec', 'priv']):
                results['private_keys'].append({
                    'value': hex_token,
                    'type': 'hex_private',
                    'encoding': 'hex'
                })
                results['risk_level'] = 'critical'
            elif any(indicator in context for indicator in ['public', 'npub', 'pubkey']):
                results['public_keys'].append({
                    'value': hex_token,
                    'type': 'hex_public',
                    'encoding': 'hex'
                })
                results['risk_level'] = max_risk(results['risk_level'], 'medium')
        
        # Check for Nostr event JSON
        if '"kind":' in text and '"pubkey":' in text:
            results['raw_events'].append({
                'type': 'json_event',
                'content_preview': text[:100] + '...' if len(text) > 100 else text
            })
            
            # Check for sensitive event types
            if self.patterns['zap_request'].search(text):
                results['zaps'].append({
                    'type': 'zap_request',
                    'kind': 9734
                })
                results['risk_level'] = max_risk(results['risk_level'], 'medium')
                
            elif self.patterns['zap_receipt'].search(text):
                results['zaps'].append({
                    'type': 'zap_receipt', 
                    'kind': 9735
                })
                
            # Check if it contains private key data
            if '"tags":' in text and any(sensitive in text for sensitive in ['"s"', 'nsec']):
                results['risk_level'] = 'critical'
        
        return results
    
    def validate_nostr_key(self, key):
        """
        Validate Nostr key with bech32 checksum verification
        Returns: (is_valid, key_type, encoding)
        """
        # Check bech32 encoded keys
        for key_type, pattern in self.patterns.items():
            if key_type in ['npub', 'nsec', 'note', 'nevent', 'nprofile', 'nrelay', 'naddr']:
                if pattern.match(key):
                    # Basic bech32 validation
                    is_valid = self._validate_bech32(key)
                    return is_valid, key_type, 'bech32'
        
        # Check hex keys (basic length and character validation)
        if self.patterns['hex_pubkey'].match(key):
            return True, 'hex_key', 'hex'
        
        return False, None, None
    
    def _validate_bech32(self, data):
        """Basic bech32 validation for Nostr keys"""
        try:
            if len(data) < 8:
                return False
            
            # Find the separator
            separator_pos = data.rfind('1')
            if separator_pos == -1:
                return False
            
            # Check if all characters after separator are in bech32 alphabet
            data_part = data[separator_pos + 1:]
            return all(c in self.bech32_alphabet for c in data_part)
        except:
            return False
    
    def get_display_format(self, value, value_type):
        """Get display format for Nostr data"""
        if value_type in ['nsec', 'hex_private']:
            # Never show private keys
            return '***NOSTR PRIVATE KEY HIDDEN***'
        elif value_type in ['npub', 'nprofile']:
            # Show abbreviated public key
            if len(value) > 16:
                return f"{value[:8]}...{value[-6:]}"
        elif value_type in ['note', 'nevent', 'naddr']:
            # Show abbreviated note/event ID
            if len(value) > 16:
                return f"{value[:8]}...{value[-6:]}"
        elif value_type == 'websocket_url':
            # Show domain only for relay URLs
            try:
                from urllib.parse import urlparse
                parsed = urlparse(value)
                return f"wss://{parsed.netloc}"
            except:
                return value[:30] + '...' if len(value) > 30 else value
        
        return value
    
    def get_risk_score(self, content_type):
        """Get risk score for different Nostr content types"""
        risk_scores = {
            'nsec': 100,           # Private key - CRITICAL
            'hex_private': 100,    # Private key - CRITICAL  
            'npub': 20,           # Public key - LOW
            'hex_public': 20,     # Public key - LOW
            'nprofile': 25,       # Profile with relay info - LOW
            'note': 10,           # Note ID - VERY LOW
            'nevent': 15,         # Event reference - VERY LOW
            'naddr': 15,          # Address reference - VERY LOW
            'relay_ws': 5,        # Relay URL - MINIMAL
            'nip05': 10,          # NIP-05 ID - VERY LOW
            'zap_request': 30,    # Zap request - LOW-MEDIUM
            'zap_receipt': 15,    # Zap receipt - VERY LOW
            'json_event': 25      # Raw event - LOW
        }
        return risk_scores.get(content_type, 0)
    
    def get_nostr_icon(self, content_type):
        """Get appropriate icon for Nostr content type"""
        icons = {
            'nsec': '🔑',         # Private key
            'hex_private': '🔑',  # Private key
            'npub': '👤',         # Public key/profile
            'hex_public': '👤',   # Public key/profile  
            'nprofile': '👤',     # Profile
            'note': '📝',         # Note
            'nevent': '📅',       # Event
            'naddr': '🏷️',        # Address
            'relay_ws': '🔗',     # Relay
            'nip05': '🆔',        # Identity
            'zap_request': '⚡',  # Lightning zap
            'zap_receipt': '⚡',  # Lightning zap
            'json_event': '📋'    # Raw event
        }
        return icons.get(content_type, '🟣')  # Purple circle for generic Nostr

def max_risk(current, new):
    """Return the higher risk level"""
    risk_levels = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
    current_level = risk_levels.get(current, 0)
    new_level = risk_levels.get(new, 0)
    
    for level, value in risk_levels.items():
        if value == max(current_level, new_level):
            return level
    return current