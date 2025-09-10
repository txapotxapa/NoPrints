#!/usr/bin/env python3
"""
Bitcoin address validation and detection module
"""

import re
import hashlib

class BitcoinValidator:
    def __init__(self):
        # Bitcoin address patterns
        self.patterns = {
            'legacy': re.compile(r'^[1][a-km-zA-HJ-NP-Z1-9]{25,34}$'),
            'segwit_p2sh': re.compile(r'^[3][a-km-zA-HJ-NP-Z1-9]{25,34}$'),
            'bech32': re.compile(r'^bc1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{6,87}$'),
            'taproot': re.compile(r'^bc1p[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{58}$'),
            'testnet_legacy': re.compile(r'^[mn2][a-km-zA-HJ-NP-Z1-9]{25,34}$'),
            'testnet_bech32': re.compile(r'^tb1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{6,87}$'),
            'lightning_invoice': re.compile(r'^ln(bc|tb)[0-9a-z]+$', re.IGNORECASE),
            'lightning_address': re.compile(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', re.IGNORECASE),
            'private_key_wif': re.compile(r'^[5KL][1-9A-HJ-NP-Za-km-z]{50,51}$'),
            'private_key_hex': re.compile(r'^[0-9a-fA-F]{64}$'),
            'xpub': re.compile(r'^xpub[1-9A-HJ-NP-Za-km-z]{107}$'),
            'xprv': re.compile(r'^xprv[1-9A-HJ-NP-Za-km-z]{107}$'),
            'transaction_id': re.compile(r'^[0-9a-fA-F]{64}$'),
        }
        
        # BIP39 seed phrase words (abbreviated list - full list has 2048 words)
        self.bip39_words = set([
            'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract',
            'absurd', 'abuse', 'access', 'accident', 'account', 'accuse', 'achieve', 'acid',
            'acoustic', 'acquire', 'across', 'act', 'action', 'actor', 'actress', 'actual',
            'adapt', 'add', 'addict', 'address', 'adjust', 'admit', 'adult', 'advance',
            'advice', 'aerobic', 'affair', 'afford', 'afraid', 'again', 'age', 'agent',
            'agree', 'ahead', 'aim', 'air', 'airport', 'aisle', 'alarm', 'album',
            # ... abbreviated for brevity, would include all 2048 words in production
        ])
        
        # Base58 alphabet for Bitcoin
        self.base58_alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    
    def detect_bitcoin_content(self, text):
        """
        Detect Bitcoin-related content in text
        Returns: dict with detected items and their types
        """
        results = {
            'addresses': [],
            'lightning': [],
            'private_keys': [],
            'extended_keys': [],
            'transaction_ids': [],
            'seed_phrases': [],
            'risk_level': 'low'
        }
        
        if not text:
            return results
        
        # Split text into tokens for analysis
        tokens = text.split()
        
        for token in tokens:
            token = token.strip('.,;:!?"\'')
            
            # Check Bitcoin addresses - order matters for correct detection
            if self.patterns['taproot'].match(token):
                results['addresses'].append({
                    'value': token,
                    'type': 'taproot',
                    'network': 'mainnet'
                })
            elif self.patterns['bech32'].match(token):
                results['addresses'].append({
                    'value': token,
                    'type': 'bech32',
                    'network': 'mainnet'
                })
            elif self.patterns['testnet_bech32'].match(token):
                results['addresses'].append({
                    'value': token,
                    'type': 'bech32',
                    'network': 'testnet'
                })
            elif self.patterns['segwit_p2sh'].match(token):
                results['addresses'].append({
                    'value': token,
                    'type': 'segwit_p2sh',
                    'network': 'mainnet'
                })
            elif self.patterns['legacy'].match(token):
                results['addresses'].append({
                    'value': token,
                    'type': 'legacy',
                    'network': 'mainnet'
                })
            elif self.patterns['testnet_legacy'].match(token):
                results['addresses'].append({
                    'value': token,
                    'type': 'legacy',
                    'network': 'testnet'
                })
            
            # Check Lightning
            elif self.patterns['lightning_invoice'].match(token):
                results['lightning'].append({
                    'value': token,
                    'type': 'invoice'
                })
            elif self.patterns['lightning_address'].match(token):
                results['lightning'].append({
                    'value': token,
                    'type': 'address'
                })
            
            # Check private keys (HIGH RISK)
            elif self.patterns['private_key_wif'].match(token):
                results['private_keys'].append({
                    'value': token,
                    'type': 'wif'
                })
                results['risk_level'] = 'critical'
            
            # Check extended keys (HIGH RISK)
            elif self.patterns['xprv'].match(token):
                results['extended_keys'].append({
                    'value': token,
                    'type': 'xprv'
                })
                results['risk_level'] = 'critical'
            elif self.patterns['xpub'].match(token):
                results['extended_keys'].append({
                    'value': token,
                    'type': 'xpub'
                })
                results['risk_level'] = 'high'
        
        # Check for seed phrases (12 or 24 words)
        words = [w.lower().strip('.,;:!?"\'') for w in tokens]
        if self._is_seed_phrase(words):
            results['seed_phrases'].append({
                'value': ' '.join(words),
                'word_count': len(words)
            })
            results['risk_level'] = 'critical'
        
        # Check for hex private keys (64 hex chars)
        for token in tokens:
            if len(token) == 64 and self.patterns['private_key_hex'].match(token):
                # Could be private key or transaction ID
                # Transaction IDs are less sensitive
                if any(addr['value'] in text for addr in results['addresses']):
                    results['transaction_ids'].append({
                        'value': token,
                        'type': 'txid'
                    })
                else:
                    results['private_keys'].append({
                        'value': token,
                        'type': 'hex'
                    })
                    results['risk_level'] = 'critical'
        
        # Update risk level based on content
        if results['addresses'] and results['risk_level'] == 'low':
            results['risk_level'] = 'medium'
        
        return results
    
    def _is_seed_phrase(self, words):
        """Check if words form a potential seed phrase"""
        if len(words) not in [12, 24]:
            return False
        
        # Check if most words are BIP39 words
        # In production, would check against full BIP39 wordlist
        bip39_count = sum(1 for w in words if len(w) >= 3 and w.isalpha())
        return bip39_count >= 10  # At least 10 valid words
    
    def validate_address(self, address):
        """
        Validate Bitcoin address with checksum verification
        Returns: (is_valid, address_type, network)
        """
        # Basic pattern matching first
        for pattern_name, pattern in self.patterns.items():
            if 'legacy' in pattern_name or 'bech32' in pattern_name or 'taproot' in pattern_name:
                if pattern.match(address):
                    network = 'testnet' if 'testnet' in pattern_name else 'mainnet'
                    addr_type = pattern_name.replace('testnet_', '').replace('segwit_', '')
                    
                    # For bech32 addresses, perform bech32 checksum validation
                    if 'bech32' in pattern_name or 'taproot' in pattern_name:
                        is_valid = self._validate_bech32(address)
                    else:
                        # For legacy addresses, perform base58 checksum validation
                        is_valid = self._validate_base58_checksum(address)
                    
                    return is_valid, addr_type, network
        
        return False, None, None
    
    def _validate_base58_checksum(self, address):
        """Validate base58 Bitcoin address checksum"""
        try:
            # Decode base58
            decoded = self._decode_base58(address)
            if decoded is None:
                return False
            
            # Last 4 bytes are checksum
            checksum = decoded[-4:]
            payload = decoded[:-4]
            
            # Calculate expected checksum
            hash_result = hashlib.sha256(hashlib.sha256(payload).digest()).digest()
            expected_checksum = hash_result[:4]
            
            return checksum == expected_checksum
        except:
            return False
    
    def _decode_base58(self, s):
        """Decode base58 string to bytes"""
        try:
            decoded = 0
            for char in s:
                decoded = decoded * 58 + self.base58_alphabet.index(char)
            
            # Convert to bytes
            hex_str = hex(decoded)[2:]
            if len(hex_str) % 2:
                hex_str = '0' + hex_str
            
            return bytes.fromhex(hex_str)
        except:
            return None
    
    def _validate_bech32(self, address):
        """Basic bech32 validation"""
        # Simplified bech32 validation
        # In production, would use full bech32 checksum algorithm
        if address.startswith('bc1') or address.startswith('tb1'):
            # Check character set
            valid_chars = set('qpzry9x8gf2tvdw0s3jn54khce6mua7l')
            addr_chars = set(address[3:].lower())
            return addr_chars.issubset(valid_chars)
        return False
    
    def get_display_format(self, value, value_type):
        """Get display format for sensitive data"""
        if value_type in ['private_key', 'xprv', 'seed_phrase']:
            # Never show private keys
            return '***PRIVATE KEY HIDDEN***'
        elif value_type in ['address', 'xpub']:
            # Show first and last 4 characters
            if len(value) > 12:
                return f"{value[:6]}...{value[-4:]}"
        elif value_type == 'lightning_invoice':
            # Show first part of invoice
            if len(value) > 20:
                return f"{value[:15]}..."
        
        return value
    
    def get_risk_score(self, content_type):
        """Get risk score for different Bitcoin content types"""
        risk_scores = {
            'private_key': 100,
            'seed_phrase': 100,
            'xprv': 95,
            'xpub': 60,
            'address': 30,
            'lightning_invoice': 25,
            'lightning_address': 20,
            'transaction_id': 10
        }
        return risk_scores.get(content_type, 0)