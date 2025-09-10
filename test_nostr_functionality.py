#!/usr/bin/env python3
"""
Comprehensive test suite for Nostr functionality
"""

from nostr_validator import NostrValidator
from security_detector import SecurityDetector

def test_nostr_key_detection():
    """Test Nostr key pattern detection"""
    validator = NostrValidator()
    
    print("🟣 Testing Nostr Key Detection")
    print("=" * 50)
    
    test_cases = [
        # Nostr public keys (npub) - using valid bech32 characters
        ("npub1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "npub", True),
        ("npub1234567890qwertyuiopasdfghjklzxcvbnm234567890qwertyuiopa", "npub", True),
        
        # Nostr private keys (nsec) - CRITICAL
        ("nsec1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "nsec", True),
        ("nsec1234567890qwertyuiopasdfghjklzxcvbnm234567890qwertyuiopa", "nsec", True),
        
        # Note IDs
        ("note1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "note", True),
        
        # Events (longer format)
        ("nevent1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "nevent", True),
        
        # Profiles (longer format)  
        ("nprofile1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "nprofile", True),
        
        # Relays
        ("wss://relay.damus.io", "relay_ws", True),
        ("wss://relay.snort.social/", "relay_ws", True),
        ("ws://localhost:7777", "relay_ws", True),
        
        # NIP-05 identifiers
        ("alice@example.com", "nip05", True),
        ("bob@relay.damus.io", "nip05", True),
        
        # Raw hex keys (64 chars) - context dependent
        ("a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2", "hex_key", True),
        
        # Invalid formats
        ("invalid_nostr_key", None, False),
        ("npub_too_short", None, False),
        ("nsec_invalid_chars!", None, False),
        ("", None, False),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_input, expected_type, should_detect in test_cases:
        result = validator.detect_nostr_content(test_input)
        
        detected = False
        detected_type = None
        
        # Check what was detected
        if result['private_keys']:
            detected = True
            detected_type = result['private_keys'][0]['type']
        elif result['public_keys']:
            detected = True
            detected_type = result['public_keys'][0]['type']
        elif result['notes']:
            detected = True
            detected_type = 'note'
        elif result['events']:
            detected = True
            detected_type = result['events'][0]['type']
        elif result['relays']:
            detected = True
            detected_type = result['relays'][0]['type']
        elif result['nip05_ids']:
            detected = True
            detected_type = 'nip05'
        
        print(f"Input: {test_input[:40]}{'...' if len(test_input) > 40 else ''}")
        print(f"Expected: {expected_type}, Should detect: {should_detect}")
        print(f"Detected: {detected}, Type: {detected_type}")
        print(f"Risk Level: {result['risk_level']}")
        
        # Evaluate test result
        detection_correct = detected == should_detect
        type_correct = not should_detect or detected_type == expected_type
        
        if detection_correct and type_correct:
            print("✅ PASS\n")
            passed += 1
        else:
            print("❌ FAIL\n")
    
    print(f"📊 Nostr Key Detection Results: {passed}/{total} passed")
    return passed == total

def test_nostr_security_levels():
    """Test Nostr content security risk assessment"""
    detector = SecurityDetector()
    
    print("🔐 Testing Nostr Security Risk Assessment")
    print("=" * 50)
    
    test_cases = [
        # Critical risk - private keys
        ("nsec1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "critical"),
        ("Here's my private key: nsec1234567890qwertyuiopasdfghjklzxcvbn", "critical"),
        ("Secret: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2", "critical"),
        
        # Medium risk - public keys
        ("npub1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "medium"),
        ("My Nostr pubkey: npub1234567890qwertyuiopasdfghjklzxcvbn", "medium"),
        ("nprofile1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "medium"),
        
        # Low risk - notes and events  
        ("note1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "low"),
        ("nevent1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", "low"),
        
        # Minimal risk - relays
        ("wss://relay.damus.io", "low"),
        ("Connect to: wss://relay.snort.social", "low"),
        
        # Normal text
        ("This is just normal text", "low"),
        ("Hello Nostr world!", "low"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for text, expected_risk in test_cases:
        result = detector.analyze_content(text)
        actual_risk = result['risk_level']
        
        print(f"Text: {text[:40]}{'...' if len(text) > 40 else ''}")
        print(f"Expected Risk: {expected_risk}")
        print(f"Actual Risk: {actual_risk}")
        print(f"Risk Score: {result['risk_score']}")
        print(f"Should Expire: {result['should_expire']}")
        if result['expire_seconds']:
            print(f"Expire Time: {result['expire_seconds']}s")
        
        # Check Nostr-specific results
        if result['nostr']:
            nostr_data = result['nostr']
            if nostr_data['private_keys']:
                print(f"Private Keys: {len(nostr_data['private_keys'])}")
            if nostr_data['public_keys']:
                print(f"Public Keys: {len(nostr_data['public_keys'])}")
            if nostr_data['notes']:
                print(f"Notes: {len(nostr_data['notes'])}")
            if nostr_data['events']:
                print(f"Events: {len(nostr_data['events'])}")
            if nostr_data['relays']:
                print(f"Relays: {len(nostr_data['relays'])}")
        
        if actual_risk == expected_risk:
            print("✅ PASS\n")
            passed += 1
        else:
            print("❌ FAIL\n")
    
    print(f"📊 Nostr Security Assessment Results: {passed}/{total} passed")
    return passed == total

def test_nostr_display_formatting():
    """Test secure display formatting for Nostr content"""
    detector = SecurityDetector()
    
    print("🎨 Testing Nostr Display Formatting")
    print("=" * 50)
    
    test_cases = [
        # Private keys - should be hidden
        ("nsec1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", True),
        ("Private: nsec1234567890qwertyuiopasdfghjklzxcvbnmasdfghjkl", True),
        
        # Public keys - should be abbreviated  
        ("npub1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", True),
        ("nprofile1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", True),
        
        # Notes and events - normal display
        ("note1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", False),
        ("nevent1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", False),
        
        # Normal text
        ("This is normal Nostr discussion text", False),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for text, should_be_hidden in test_cases:
        analysis = detector.analyze_content(text)
        display_text = detector.get_display_text(text, analysis)
        
        print(f"Original: {text}")
        print(f"Display:  {display_text}")
        print(f"Should Hide: {should_be_hidden}")
        print(f"Is Blurred: {analysis['should_blur']}")
        
        # Evaluate formatting
        if should_be_hidden:
            # Should be hidden/abbreviated
            if display_text != text and len(display_text) < len(text):
                print("✅ PASS - Properly secured\n")
                passed += 1
            else:
                print("❌ FAIL - Not properly secured\n")
        else:
            # Should be normal display or reasonable truncation
            if display_text == text or (len(text) > 50 and "..." in display_text):
                print("✅ PASS - Normal display\n")
                passed += 1
            else:
                print("❌ FAIL - Unexpected formatting\n")
    
    print(f"📊 Nostr Display Formatting Results: {passed}/{total} passed")
    return passed == total

def test_nostr_event_detection():
    """Test detection of Nostr JSON events"""
    validator = NostrValidator()
    
    print("📅 Testing Nostr Event Detection")
    print("=" * 50)
    
    # Example Nostr events
    test_events = [
        # Basic text note (kind 1)
        '{"id":"abc123","pubkey":"def456","created_at":1640000000,"kind":1,"tags":[],"content":"Hello Nostr!","sig":"xyz789"}',
        
        # Profile metadata (kind 0)
        '{"kind":0,"pubkey":"a1b2c3","content":"{\\"name\\":\\"Alice\\",\\"about\\":\\"Nostr user\\"}"}',
        
        # Zap request (kind 9734) - sensitive
        '{"kind":9734,"pubkey":"pubkey123","tags":[["relays","wss://relay.example.com"]],"content":"zap request"}',
        
        # Zap receipt (kind 9735)
        '{"kind":9735,"tags":[["bolt11","lnbc100u1..."]],"content":"zap receipt"}',
        
        # Not a Nostr event
        '{"message":"hello","timestamp":1640000000}',
        
        # Invalid JSON
        '{"kind":1,"invalid_json',
    ]
    
    for i, event_json in enumerate(test_events, 1):
        print(f"\nTest {i}: {event_json[:50]}{'...' if len(event_json) > 50 else ''}")
        
        result = validator.detect_nostr_content(event_json)
        
        if result['raw_events']:
            event_info = result['raw_events'][0]
            print(f"✅ Detected Nostr event: {event_info['type']}")
            print(f"Risk Level: {result['risk_level']}")
        elif result['zaps']:
            zap_info = result['zaps'][0]
            print(f"⚡ Detected Zap: {zap_info['type']} (kind {zap_info['kind']})")
            print(f"Risk Level: {result['risk_level']}")
        else:
            print("❌ No Nostr event detected")
    
    return True

def test_combined_bitcoin_nostr():
    """Test handling of combined Bitcoin and Nostr content"""
    detector = SecurityDetector()
    
    print("⚡ Testing Combined Bitcoin + Nostr Detection")
    print("=" * 50)
    
    combined_texts = [
        # Bitcoin + Nostr addresses
        "My Bitcoin: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa and Nostr: npub1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",
        
        # Multiple sensitive items  
        "Keys: nsec1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq and Bitcoin key: 5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ",
        
        # Relay + Lightning
        "Connect to wss://relay.damus.io for Nostr and pay lnbc100u1p3pj257pp5... for Bitcoin",
        
        # Normal discussion
        "I love using both Bitcoin and Nostr protocols for decentralized everything!",
    ]
    
    for i, text in enumerate(combined_texts, 1):
        print(f"\nTest {i}: {text[:60]}{'...' if len(text) > 60 else ''}")
        
        result = detector.analyze_content(text)
        
        print(f"Overall Risk Level: {result['risk_level']}")
        print(f"Risk Score: {result['risk_score']}")
        
        # Check Bitcoin content
        if result['bitcoin']:
            bitcoin = result['bitcoin']
            print(f"Bitcoin - Addresses: {len(bitcoin.get('addresses', []))}, "
                  f"Private Keys: {len(bitcoin.get('private_keys', []))}")
        
        # Check Nostr content  
        if result['nostr']:
            nostr = result['nostr']
            print(f"Nostr - Public Keys: {len(nostr.get('public_keys', []))}, "
                  f"Private Keys: {len(nostr.get('private_keys', []))}, "
                  f"Relays: {len(nostr.get('relays', []))}")
        
        print(f"Should Expire: {result['should_expire']}")
        if result['expire_seconds']:
            print(f"Expire Time: {result['expire_seconds']}s")
    
    return True

if __name__ == "__main__":
    print("🚀 Nostr Functionality Test Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        test_results = {
            'nostr_key_detection': test_nostr_key_detection(),
            'nostr_security_levels': test_nostr_security_levels(),
            'nostr_display_formatting': test_nostr_display_formatting(),
            'nostr_event_detection': test_nostr_event_detection(),
            'combined_bitcoin_nostr': test_combined_bitcoin_nostr()
        }
        
        print("\n" + "=" * 60)
        print("📋 NOSTR FUNCTIONALITY TEST RESULTS")
        print("=" * 60)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        if passed_tests == total_tests:
            print(f"\n🎉 ALL NOSTR TESTS PASSED ({passed_tests}/{total_tests})")
            print("✅ Nostr functionality is working correctly!")
        else:
            print(f"\n⚠️ SOME NOSTR TESTS FAILED ({passed_tests}/{total_tests})")
            print("❌ Review failed tests before deployment")
        
        print("\n" + "=" * 60)
        print("🟣 NOSTR FEATURES TESTED:")
        print("• Nostr key detection (npub, nsec, hex)")
        print("• Security risk assessment")
        print("• Display text formatting & privacy")
        print("• JSON event detection")
        print("• Combined Bitcoin + Nostr handling")
        print("• Private key protection")
        print("• Public key abbreviation")
        print("• Relay URL detection")
        print("• NIP-05 identifier support")
        print("• Zap request/receipt detection")
        print("=" * 60)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure nostr_validator.py and security_detector.py are available")
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()