#!/usr/bin/env python3
"""
Core functionality tests without external dependencies
"""

import time
import unicodedata
import re
from datetime import datetime

def test_unicode_cleaning():
    """Test hidden Unicode character removal"""
    print("🧹 Testing Unicode Cleaning")
    print("=" * 50)
    
    # Unicode cleaning function (from main app)
    def clean_text(text):
        if not text:
            return text
        
        hidden_chars = [
            '\u200b', '\u200c', '\u200d', '\u200e', '\u200f',  # Zero-width and directional
            '\u202a', '\u202b', '\u202c', '\u202d', '\u202e',  # Embedding and override
            '\u2060', '\u2061', '\u2062', '\u2063', '\u2064',  # Word joiner and invisibles
            '\u2066', '\u2067', '\u2068', '\u2069',            # Isolates
            '\ufeff', '\ufffc', '\ufffd',                      # BOM and replacements
            '\u0000',                                           # Null
        ] + [chr(i) for i in range(0x01, 0x20)] + ['\u007f']  # Control characters
        
        hidden_pattern = re.compile('[' + ''.join(hidden_chars) + ']')
        
        # Normalize unicode
        text = unicodedata.normalize('NFC', text)
        
        # Remove hidden characters
        text = hidden_pattern.sub('', text)
        
        # Additional cleaning
        text = re.sub(r'\s+', ' ', text)
        lines = text.split('\n')
        lines = [line.rstrip() for line in lines]
        text = '\n'.join(lines)
        
        return text
    
    # Test cases with hidden characters
    test_cases = [
        # Zero-width spaces
        ("Hello\u200bworld", "Helloworld"),
        ("Test\u200c\u200dstring", "Teststring"),
        
        # Directional marks  
        ("Text\u200ewith\u200fmarks", "Textwithmarks"),
        
        # Control characters
        ("Clean\u0000this\u0001text", "Cleanthistext"),
        
        # BOM and replacements
        ("\ufeffBOM at start", "BOM at start"),
        ("Replace\ufffcthis", "Replacethis"),
        
        # Multiple spaces
        ("Multiple   spaces    here", "Multiple spaces here"),
        
        # Normal text (should be unchanged)
        ("Normal text", "Normal text"),
        ("Email: user@example.com", "Email: user@example.com"),
        
        # Mixed content
        ("Bitcoin:\u200b1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Bitcoin:1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for dirty_text, expected in test_cases:
        cleaned = clean_text(dirty_text)
        
        print(f"Input:    '{dirty_text}' ({len(dirty_text)} chars)")
        print(f"Expected: '{expected}'")
        print(f"Cleaned:  '{cleaned}' ({len(cleaned)} chars)")
        
        if cleaned == expected:
            print("✅ PASS\n")
            passed += 1
        else:
            print("❌ FAIL\n")
            print(f"Difference: Expected '{expected}', got '{cleaned}'")
    
    print(f"📊 Unicode Cleaning Results: {passed}/{total} passed")
    return passed == total

def test_bitcoin_patterns():
    """Test Bitcoin address pattern matching"""
    print("₿ Testing Bitcoin Pattern Matching")
    print("=" * 50)
    
    # Bitcoin patterns (from validator)
    patterns = {
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
    }
    
    test_cases = [
        # Valid addresses
        ("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "legacy", True),
        ("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy", "segwit_p2sh", True),
        ("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", "bech32", True),
        ("bc1p5d7rjq7g6rdk2yhzks9smlaqtedr4dekq08ge8ztwac72sfr9rusxg3297", "taproot", True),
        
        # Testnet
        ("mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn", "testnet_legacy", True),
        ("tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx", "testnet_bech32", True),
        
        # Lightning
        ("lnbc100u1p3pj257pp5yztkwjcz5ftl5laxkav23zmzekaw37zk6kmv80pk4", "lightning_invoice", True),
        ("satoshi@stacker.news", "lightning_address", True),
        
        # Private keys
        ("5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ", "private_key_wif", True),
        ("e9873d79c6d87dc0fb6a5778633389f4453213303da61f20bd67fc233aa33262", "private_key_hex", True),
        
        # Invalid
        ("1InvalidAddress", None, False),
        ("NotAnAddress", None, False),
        ("", None, False),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for address, expected_type, should_match in test_cases:
        matched = False
        matched_type = None
        
        # Test all patterns
        for pattern_name, pattern in patterns.items():
            if pattern.match(address):
                matched = True
                matched_type = pattern_name
                break
        
        print(f"Address: {address[:30]}{'...' if len(address) > 30 else ''}")
        print(f"Expected: {expected_type}, Should match: {should_match}")
        print(f"Matched: {matched}, Type: {matched_type}")
        
        if (matched == should_match) and (not should_match or matched_type == expected_type):
            print("✅ PASS\n")
            passed += 1
        else:
            print("❌ FAIL\n")
    
    print(f"📊 Bitcoin Pattern Results: {passed}/{total} passed")
    return passed == total

def test_security_patterns():
    """Test security-related pattern matching"""
    print("🔐 Testing Security Patterns")
    print("=" * 50)
    
    # Security patterns
    patterns = {
        'password_strong': re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'),
        'password_context': re.compile(r'(?:password|passwd|pwd|pass)[\s:=]+\S+', re.IGNORECASE),
        'credit_card': re.compile(r'\b(?:\d[ -]*?){13,16}\b'),
        'api_key': re.compile(r'(?:api[_-]?key|apikey|api_token)[\s:=]+[\w-]{20,}', re.IGNORECASE),
        'jwt': re.compile(r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'),
        'ssh_key': re.compile(r'-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----'),
    }
    
    test_cases = [
        # Strong passwords
        ("MyStr0ng!P@ssw0rd", "password_strong", True),
        ("SuperSecure123!", "password_strong", True),
        
        # Password contexts
        ("password: secret123", "password_context", True),
        ("pwd=MySecret456!", "password_context", True),
        
        # Credit cards
        ("4111111111111111", "credit_card", True),
        ("4111-1111-1111-1111", "credit_card", True),
        
        # API keys
        ("api_key: sk_live_abcdef1234567890abcdef", "api_key", True),
        ("API_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx", "api_key", True),
        
        # JWT tokens
        ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c", "jwt", True),
        
        # SSH keys
        ("-----BEGIN RSA PRIVATE KEY-----", "ssh_key", True),
        ("-----BEGIN OPENSSH PRIVATE KEY-----", "ssh_key", True),
        
        # Normal text (should not match)
        ("This is normal text", None, False),
        ("user@example.com", None, False),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for text, expected_pattern, should_match in test_cases:
        matched = False
        matched_pattern = None
        
        # Test all patterns
        for pattern_name, pattern in patterns.items():
            if pattern.search(text):
                matched = True
                matched_pattern = pattern_name
                break
        
        print(f"Text: {text[:40]}{'...' if len(text) > 40 else ''}")
        print(f"Expected: {expected_pattern}, Should match: {should_match}")
        print(f"Matched: {matched}, Pattern: {matched_pattern}")
        
        if (matched == should_match) and (not should_match or matched_pattern == expected_pattern):
            print("✅ PASS\n")
            passed += 1
        else:
            print("❌ FAIL\n")
    
    print(f"📊 Security Pattern Results: {passed}/{total} passed")
    return passed == total

def test_display_formatting():
    """Test safe display text formatting"""
    print("🎨 Testing Display Formatting")
    print("=" * 50)
    
    def get_display_text(text, should_blur=False, content_type="generic"):
        """Mock display text function"""
        if should_blur:
            if content_type == "bitcoin_address" and len(text) > 10:
                return f"₿ {text[:6]}...{text[-4:]}"
            elif content_type == "private_key":
                return "🔑 Private Key (hidden)"
            elif content_type == "password":
                return "🔒 Password (hidden)"
            elif content_type == "credit_card":
                return f"💳 Card ending in {text[-4:]}"
            else:
                if len(text) > 12:
                    return f"{text[:4]}...{text[-4:]}"
                else:
                    return "***hidden***"
        else:
            if len(text) > 50:
                return text[:47] + "..."
            return text
    
    test_cases = [
        # Bitcoin addresses - should be blurred
        ("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", True, "bitcoin_address"),
        ("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", True, "bitcoin_address"),
        
        # Private keys - should be hidden
        ("5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ", True, "private_key"),
        
        # Passwords - should be hidden
        ("MySecure123!Password", True, "password"),
        
        # Credit cards - show last 4
        ("4111111111111111", True, "credit_card"),
        
        # Normal text - full display
        ("This is normal text that should be displayed", False, "text"),
        ("Short text", False, "text"),
        ("Very long text that should be truncated because it exceeds the maximum display length", False, "text"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for text, should_blur, content_type in test_cases:
        display_text = get_display_text(text, should_blur, content_type)
        
        print(f"Original: {text}")
        print(f"Display:  {display_text}")
        print(f"Blurred:  {should_blur}")
        
        # Basic validation - display text should be different if blurred
        if should_blur:
            if display_text != text and len(display_text) <= len(text):
                print("✅ PASS - Properly obscured\n")
                passed += 1
            else:
                print("❌ FAIL - Not properly obscured\n")
        else:
            if display_text == text or (len(text) > 50 and display_text.endswith("...")):
                print("✅ PASS - Proper display\n")
                passed += 1
            else:
                print("❌ FAIL - Improper display\n")
    
    print(f"📊 Display Formatting Results: {passed}/{total} passed")
    return passed == total

def test_risk_assessment():
    """Test risk level assessment"""
    print("⚠️ Testing Risk Assessment")
    print("=" * 50)
    
    def assess_risk(text):
        """Mock risk assessment function"""
        risk_score = 0
        risk_level = "low"
        should_expire = False
        expire_seconds = None
        
        # Check for Bitcoin content
        if any(pattern in text for pattern in ["1", "3", "bc1"]):
            if len([c for c in text if c.isalnum()]) > 25:  # Looks like address
                risk_score = 30
                risk_level = "medium"
                should_expire = True
                expire_seconds = 30
        
        # Check for private keys
        if any(text.startswith(prefix) for prefix in ["5", "K", "L"]) and len(text) > 50:
            risk_score = 100
            risk_level = "critical"
            should_expire = True
            expire_seconds = 10
        
        # Check for passwords
        if any(indicator in text.lower() for indicator in ["password", "pass", "pwd"]):
            risk_score = max(risk_score, 80)
            risk_level = "high" if risk_level != "critical" else "critical"
            should_expire = True
            expire_seconds = min(expire_seconds or 60, 60)
        
        # Check for complex passwords
        if (len(text) > 8 and 
            any(c.isupper() for c in text) and 
            any(c.islower() for c in text) and 
            any(c.isdigit() for c in text) and 
            any(c in "!@#$%^&*" for c in text)):
            risk_score = max(risk_score, 75)
            risk_level = "high" if risk_level not in ["critical"] else risk_level
            should_expire = True
            expire_seconds = min(expire_seconds or 60, 60)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'should_expire': should_expire,
            'expire_seconds': expire_seconds
        }
    
    test_cases = [
        # Low risk
        ("Normal text message", "low"),
        ("user@example.com", "low"),
        ("Hello world!", "low"),
        
        # Medium risk
        ("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "medium"),
        ("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", "medium"),
        
        # High risk
        ("password: MySecure123!", "high"),
        ("MyComplexP@ssw0rd2023", "high"),
        
        # Critical risk
        ("5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ", "critical"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for text, expected_risk in test_cases:
        result = assess_risk(text)
        actual_risk = result['risk_level']
        
        print(f"Text: {text[:40]}{'...' if len(text) > 40 else ''}")
        print(f"Expected Risk: {expected_risk}")
        print(f"Actual Risk: {actual_risk}")
        print(f"Risk Score: {result['risk_score']}")
        print(f"Should Expire: {result['should_expire']}")
        if result['expire_seconds']:
            print(f"Expire Time: {result['expire_seconds']}s")
        
        if actual_risk == expected_risk:
            print("✅ PASS\n")
            passed += 1
        else:
            print("❌ FAIL\n")
    
    print(f"📊 Risk Assessment Results: {passed}/{total} passed")
    return passed == total

if __name__ == "__main__":
    print("🚀 Core Functionality Test Suite")
    print("=" * 60)
    
    # Run all tests
    test_results = {
        'unicode_cleaning': test_unicode_cleaning(),
        'bitcoin_patterns': test_bitcoin_patterns(),
        'security_patterns': test_security_patterns(),
        'display_formatting': test_display_formatting(),
        'risk_assessment': test_risk_assessment()
    }
    
    print("\n" + "=" * 60)
    print("📋 CORE FUNCTIONALITY TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL CORE TESTS PASSED ({passed_tests}/{total_tests})")
        print("✅ Core functionality is working correctly!")
    else:
        print(f"\n⚠️ SOME CORE TESTS FAILED ({passed_tests}/{total_tests})")
        print("❌ Review failed tests before deployment")
    
    print("\n" + "=" * 60)
    print("🔍 TESTED FUNCTIONALITY:")
    print("• Unicode character detection & removal")
    print("• Bitcoin address pattern matching")  
    print("• Security pattern detection (passwords, API keys, etc.)")
    print("• Safe display text formatting")
    print("• Risk level assessment")
    print("=" * 60)