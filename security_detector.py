#!/usr/bin/env python3
"""
Security detection module for sensitive data in clipboard
"""

import re
from bitcoin_validator import BitcoinValidator
from nostr_validator import NostrValidator

class SecurityDetector:
    def __init__(self):
        self.bitcoin_validator = BitcoinValidator()
        self.nostr_validator = NostrValidator()
        
        # Sensitive data patterns
        self.patterns = {
            'password': [
                re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'),
                re.compile(r'(?:password|passwd|pwd|pass)[\s:=]+\S+', re.IGNORECASE),
            ],
            'credit_card': [
                re.compile(r'\b(?:\d[ -]*?){13,16}\b'),  # Basic credit card pattern
                re.compile(r'\b[3-6]\d{3}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{3,4}\b'),
            ],
            'ssn': [
                re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),  # US SSN
                re.compile(r'\b\d{9}\b'),  # SSN without dashes
            ],
            'api_key': [
                re.compile(r'(?:api[_-]?key|apikey|api_token)[\s:=]+[\w-]{20,}', re.IGNORECASE),
                re.compile(r'sk_live_[a-zA-Z0-9]{24,}'),  # Stripe
                re.compile(r'pk_live_[a-zA-Z0-9]{24,}'),  # Stripe public
                re.compile(r'[a-f0-9]{32}'),  # Generic 32-char hex (API keys)
            ],
            'jwt': [
                re.compile(r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'),
            ],
            'ssh_key': [
                re.compile(r'-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----'),
                re.compile(r'ssh-(?:rsa|dss|ed25519) [A-Za-z0-9+/]+'),
            ],
            'aws_key': [
                re.compile(r'AKIA[0-9A-Z]{16}'),  # AWS Access Key
                re.compile(r'[a-zA-Z0-9/+=]{40}'),  # AWS Secret Key pattern
            ],
        }
        
        # Excluded applications (won't store clipboard from these)
        self.excluded_apps = [
            '1Password',
            'Bitwarden',
            'LastPass',
            'KeePassXC',
            'Sparrow',
            'Electrum',
            'Bitcoin Core',
            'BlueWallet',
            'Wasabi Wallet',
            'Damus',
            'Primal',
            'Amethyst',
            'Iris',
            'Snort',
            'Nostrudel',
            'Terminal',
            'iTerm',
        ]
    
    def analyze_content(self, text, source_app=None):
        """
        Analyze clipboard content for sensitive data
        Returns: dict with detected items, risk level, and recommendations
        """
        results = {
            'bitcoin': {},
            'nostr': {},
            'passwords': [],
            'credit_cards': [],
            'api_keys': [],
            'other_sensitive': [],
            'risk_level': 'low',
            'risk_score': 0,
            'should_expire': False,
            'expire_seconds': None,
            'should_blur': False,
            'warnings': []
        }
        
        if not text:
            return results
        
        # Check if from excluded app
        if source_app and any(app in source_app for app in self.excluded_apps):
            results['warnings'].append(f'Content from excluded app: {source_app}')
            results['should_expire'] = True
            results['expire_seconds'] = 30
        
        # Check for Bitcoin content
        bitcoin_results = self.bitcoin_validator.detect_bitcoin_content(text)
        results['bitcoin'] = bitcoin_results
        
        # Check for Nostr content
        nostr_results = self.nostr_validator.detect_nostr_content(text)
        results['nostr'] = nostr_results
        
        # Handle Bitcoin-specific risks
        if bitcoin_results['private_keys'] or bitcoin_results['seed_phrases']:
            results['risk_level'] = 'critical'
            results['risk_score'] = 100
            results['should_expire'] = True
            results['expire_seconds'] = 10  # Very short expiry for private keys
            results['should_blur'] = True
            results['warnings'].append('⚠️ CRITICAL: Private key or seed phrase detected!')
        elif bitcoin_results['extended_keys']:
            if any(k['type'] == 'xprv' for k in bitcoin_results['extended_keys']):
                results['risk_level'] = 'critical'
                results['risk_score'] = 95
                results['should_expire'] = True
                results['expire_seconds'] = 15
                results['should_blur'] = True
                results['warnings'].append('⚠️ Extended private key detected!')
            else:
                results['risk_level'] = 'high'
                results['risk_score'] = 60
                results['should_expire'] = True
                results['expire_seconds'] = 30
        elif bitcoin_results['addresses']:
            results['risk_level'] = 'medium'
            results['risk_score'] = 30
            results['should_expire'] = True
            results['expire_seconds'] = 30
            results['should_blur'] = True
        elif bitcoin_results['lightning']:
            results['risk_level'] = 'medium'
            results['risk_score'] = 25
            results['should_expire'] = True
            results['expire_seconds'] = 60
        
        # Handle Nostr-specific risks
        if nostr_results['private_keys']:
            results['risk_level'] = 'critical'
            results['risk_score'] = 100
            results['should_expire'] = True
            results['expire_seconds'] = min(results['expire_seconds'] or 10, 10)
            results['should_blur'] = True
            results['warnings'].append('⚠️ CRITICAL: Nostr private key detected!')
        elif nostr_results['public_keys']:
            results['risk_level'] = max(results['risk_level'], 'medium', key=self._risk_priority)
            results['risk_score'] = max(results['risk_score'], 25)
            results['should_expire'] = True
            results['expire_seconds'] = min(results['expire_seconds'] or 60, 60)
            results['should_blur'] = True
        elif nostr_results['raw_events'] and any('kind' in str(event) for event in nostr_results['raw_events']):
            results['risk_level'] = max(results['risk_level'], 'medium', key=self._risk_priority)
            results['risk_score'] = max(results['risk_score'], 30)
            results['should_expire'] = True
            results['expire_seconds'] = min(results['expire_seconds'] or 120, 120)
        
        # Check for passwords
        for pattern in self.patterns['password']:
            if pattern.search(text):
                results['passwords'].append({
                    'type': 'password',
                    'pattern_matched': True
                })
                results['risk_level'] = max(results['risk_level'], 'high', key=self._risk_priority)
                results['risk_score'] = max(results['risk_score'], 80)
                results['should_expire'] = True
                results['expire_seconds'] = min(results['expire_seconds'] or 60, 60)
                results['should_blur'] = True
                results['warnings'].append('Password detected')
                break
        
        # Check for credit cards
        for pattern in self.patterns['credit_card']:
            matches = pattern.findall(text)
            for match in matches:
                # Basic Luhn check for credit card
                digits = re.sub(r'\D', '', match)
                if len(digits) >= 13 and len(digits) <= 19:
                    if self._luhn_check(digits):
                        results['credit_cards'].append({
                            'type': 'credit_card',
                            'masked': f"****-****-****-{digits[-4:]}"
                        })
                        results['risk_level'] = max(results['risk_level'], 'high', key=self._risk_priority)
                        results['risk_score'] = max(results['risk_score'], 85)
                        results['should_expire'] = True
                        results['expire_seconds'] = min(results['expire_seconds'] or 30, 30)
                        results['should_blur'] = True
                        results['warnings'].append('Credit card detected')
        
        # Check for API keys
        for pattern in self.patterns['api_key']:
            if pattern.search(text):
                results['api_keys'].append({
                    'type': 'api_key',
                    'pattern_matched': True
                })
                results['risk_level'] = max(results['risk_level'], 'high', key=self._risk_priority)
                results['risk_score'] = max(results['risk_score'], 75)
                results['should_expire'] = True
                results['expire_seconds'] = min(results['expire_seconds'] or 120, 120)
                results['warnings'].append('API key detected')
                break
        
        # Check for JWT tokens
        for pattern in self.patterns['jwt']:
            if pattern.search(text):
                results['other_sensitive'].append({
                    'type': 'jwt_token'
                })
                results['risk_level'] = max(results['risk_level'], 'medium', key=self._risk_priority)
                results['risk_score'] = max(results['risk_score'], 50)
                results['should_expire'] = True
                results['expire_seconds'] = min(results['expire_seconds'] or 300, 300)
                results['warnings'].append('JWT token detected')
        
        # Check for SSH keys
        for pattern in self.patterns['ssh_key']:
            if pattern.search(text):
                results['other_sensitive'].append({
                    'type': 'ssh_key'
                })
                results['risk_level'] = 'critical'
                results['risk_score'] = 100
                results['should_expire'] = True
                results['expire_seconds'] = 10
                results['should_blur'] = True
                results['warnings'].append('⚠️ SSH private key detected!')
                break
        
        return results
    
    def _risk_priority(self, level):
        """Return priority for risk level comparison"""
        priorities = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
        return priorities.get(level, 0)
    
    def _luhn_check(self, card_number):
        """Validate credit card number using Luhn algorithm"""
        try:
            digits = [int(d) for d in card_number]
            checksum = 0
            
            # Double every second digit from right
            for i in range(len(digits) - 2, -1, -2):
                doubled = digits[i] * 2
                if doubled > 9:
                    doubled = doubled - 9
                digits[i] = doubled
            
            checksum = sum(digits)
            return checksum % 10 == 0
        except:
            return False
    
    def get_security_icon(self, content_type):
        """Get appropriate icon for content type"""
        icons = {
            'bitcoin_address': '₿',
            'lightning': '⚡',
            'private_key': '🔑',
            'seed_phrase': '🌱',
            'nostr_private': '🔑',
            'nostr_public': '👤',
            'nostr_note': '📝',
            'nostr_event': '📅',
            'nostr_relay': '🔗',
            'nostr_zap': '⚡',
            'password': '🔒',
            'credit_card': '💳',
            'api_key': '🔐',
            'ssh_key': '🔑',
            'jwt_token': '🎫',
            'sensitive': '⚠️',
            'safe': '✓'
        }
        return icons.get(content_type, '📋')
    
    def get_display_text(self, text, content_analysis):
        """Get safe display version of sensitive text"""
        if content_analysis['should_blur']:
            # For very sensitive content, show limited info
            if content_analysis['nostr'].get('private_keys'):
                return "🔑 Nostr Private Key (hidden)"
            elif content_analysis['bitcoin'].get('private_keys'):
                return "🔑 Bitcoin Private Key (hidden)"
            elif content_analysis['bitcoin'].get('seed_phrases'):
                return "🌱 Seed Phrase (hidden)"
            elif content_analysis['passwords']:
                return "🔒 Password (hidden)"
            elif content_analysis['credit_cards']:
                cc = content_analysis['credit_cards'][0]
                return f"💳 Card ending in {cc['masked'][-4:]}"
            elif content_analysis['nostr'].get('public_keys'):
                key = content_analysis['nostr']['public_keys'][0]['value']
                key_type = content_analysis['nostr']['public_keys'][0]['type']
                if key_type == 'npub':
                    return f"👤 npub1...{key[-6:]}"
                elif key_type == 'nprofile':
                    return f"👤 nprofile1...{key[-6:]}"
                else:
                    return f"👤 {key[:8]}...{key[-6:]}"
            elif content_analysis['bitcoin'].get('addresses'):
                addr = content_analysis['bitcoin']['addresses'][0]['value']
                return f"₿ {addr[:6]}...{addr[-4:]}"
            else:
                # Generic blur - show first and last few chars
                if len(text) > 12:
                    return f"{text[:4]}...{text[-4:]}"
                else:
                    return "***hidden***"
        
        # For non-sensitive content, show preview
        if len(text) > 50:
            return text[:47] + "..."
        return text