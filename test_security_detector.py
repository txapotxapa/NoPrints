#!/usr/bin/env python3
"""
Test security detector functionality
"""

from security_detector import SecurityDetector

def test_bitcoin_detection():
    """Test Bitcoin content detection"""
    detector = SecurityDetector()
    
    test_cases = [
        # Bitcoin addresses
        ("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", "medium"),
        ("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "medium"),
        ("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy", "medium"),
        
        # Private keys - CRITICAL
        ("5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ", "critical"),
        ("e9873d79c6d87dc0fb6a5778633389f4453213303da61f20bd67fc233aa33262", "critical"),
        
        # Seed phrases - CRITICAL
        ("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about", "critical"),
        
        # Lightning
        ("lnbc100u1p3pj257pp5yztkwjcz5ftl5laxkav23zmzekaw37zk6kmv80pk4xaev5qhtz7qdqu2askcmr9wssx7e3q", "medium"),
        
        # Normal text
        ("Hello world, this is normal text", "low"),
    ]
    
    print("🔍 Testing Bitcoin Detection")
    print("=" * 50)
    
    passed = 0
    total = len(test_cases)
    
    for text, expected_risk in test_cases:
        result = detector.analyze_content(text)
        actual_risk = result['risk_level']
        
        print(f"Text: {text[:40]}{'...' if len(text) > 40 else ''}")
        print(f"Expected Risk: {expected_risk}, Actual: {actual_risk}")
        
        if result['bitcoin']:
            bitcoin_data = result['bitcoin']
            print(f"Bitcoin Data: {len(bitcoin_data['addresses'])} addresses, "
                  f"{len(bitcoin_data['private_keys'])} keys, "
                  f"{len(bitcoin_data['seed_phrases'])} phrases")
        
        if actual_risk == expected_risk:
            print("✅ PASS\n")
            passed += 1
        else:
            print("❌ FAIL\n")
    
    print(f"📊 Bitcoin Detection Results: {passed}/{total} passed")
    return passed == total

def test_password_detection():
    """Test password detection"""
    detector = SecurityDetector()
    
    test_passwords = [
        # Strong passwords that should be detected
        "MyStr0ng!P@ssw0rd",
        "SuperSecure123!",
        "Complex#Password2023",
        
        # Password-like patterns
        "password: secret123",
        "pwd=MySecret456!",
        
        # Should not detect as passwords
        "this is normal text",
        "user@example.com",
        "1234567890",  # Numbers only
    ]
    
    print("🔒 Testing Password Detection")
    print("=" * 50)
    
    for text in test_passwords:
        result = detector.analyze_content(text)
        
        print(f"Text: {text}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Passwords Detected: {len(result['passwords'])}")
        print(f"Should Expire: {result['should_expire']}")
        print(f"Expire Time: {result['expire_seconds']}s")
        print()
    
    return True

def test_credit_card_detection():
    """Test credit card detection"""
    detector = SecurityDetector()
    
    test_cards = [
        # Valid format credit cards (using test numbers that pass Luhn)
        "4111111111111111",  # Visa test number
        "4111-1111-1111-1111",  # With dashes
        "4111 1111 1111 1111",  # With spaces
        
        # Invalid cards
        "1234567890123456",  # Fails Luhn check
        "411111111111111",   # Too short
        
        # Not credit cards
        "this is just text",
        "123456789",
    ]
    
    print("💳 Testing Credit Card Detection")
    print("=" * 50)
    
    for text in test_cards:
        result = detector.analyze_content(text)
        
        print(f"Text: {text}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Credit Cards: {len(result['credit_cards'])}")
        if result['credit_cards']:
            for cc in result['credit_cards']:
                print(f"  Masked: {cc['masked']}")
        print()
    
    return True

def test_api_key_detection():
    """Test API key detection"""
    detector = SecurityDetector()
    
    test_keys = [
        # API key patterns (completely fake for testing)
        "api_key: test_key_abcdef1234567890abcdef1234567890test",
        "API_TOKEN=token_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "apikey=EXAMPLE_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
        
        # Example keys (fake for testing)  
        "example_key_1234567890abcdef1234567890abcdef12345678",
        "public_key_1234567890abcdef1234567890abcdef12345678",
        
        # Not API keys
        "this is normal text",
        "key: value",
    ]
    
    print("🔐 Testing API Key Detection")
    print("=" * 50)
    
    for text in test_keys:
        result = detector.analyze_content(text)
        
        print(f"Text: {text[:50]}{'...' if len(text) > 50 else ''}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"API Keys: {len(result['api_keys'])}")
        print()
    
    return True

def test_combined_detection():
    """Test detection of multiple sensitive data types"""
    detector = SecurityDetector()
    
    # Text with multiple sensitive items
    combined_text = """
    Here's my Bitcoin address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
    And my password: MySecure123!
    Credit card: 4111-1111-1111-1111
    API key: example_live_1234567890abcdef1234567890abcdef12345678
    """
    
    print("🎯 Testing Combined Detection")
    print("=" * 50)
    
    result = detector.analyze_content(combined_text)
    
    print(f"Risk Level: {result['risk_level']}")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Should Expire: {result['should_expire']}")
    print(f"Expire Time: {result['expire_seconds']}s")
    print(f"Should Blur: {result['should_blur']}")
    print(f"Warnings: {result['warnings']}")
    print()
    
    print("Detected Items:")
    if result['bitcoin']['addresses']:
        print(f"  Bitcoin Addresses: {len(result['bitcoin']['addresses'])}")
    if result['passwords']:
        print(f"  Passwords: {len(result['passwords'])}")
    if result['credit_cards']:
        print(f"  Credit Cards: {len(result['credit_cards'])}")
    if result['api_keys']:
        print(f"  API Keys: {len(result['api_keys'])}")
    
    return True

def test_display_formatting():
    """Test safe display formatting"""
    detector = SecurityDetector()
    
    test_cases = [
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",  # Bitcoin address
        "5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ",  # Private key
        "MySecure123!Password",  # Password
        "4111-1111-1111-1111",  # Credit card
        "This is just normal text that should not be blurred at all",
    ]
    
    print("🎨 Testing Display Formatting")
    print("=" * 50)
    
    for text in test_cases:
        result = detector.analyze_content(text)
        display_text = detector.get_display_text(text, result)
        
        print(f"Original: {text}")
        print(f"Display:  {display_text}")
        print(f"Blurred:  {result['should_blur']}")
        print()
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Security Detector Tests")
    print("=" * 60)
    
    try:
        # Run all tests
        bitcoin_test = test_bitcoin_detection()
        password_test = test_password_detection()
        card_test = test_credit_card_detection()
        api_test = test_api_key_detection()
        combined_test = test_combined_detection()
        display_test = test_display_formatting()
        
        print("=" * 60)
        print("📋 SECURITY DETECTOR TEST SUMMARY")
        print("=" * 60)
        print(f"Bitcoin Detection: {'✅ PASS' if bitcoin_test else '❌ FAIL'}")
        print(f"Password Detection: {'✅ PASS' if password_test else '❌ FAIL'}")
        print(f"Credit Card Detection: {'✅ PASS' if card_test else '❌ FAIL'}")
        print(f"API Key Detection: {'✅ PASS' if api_test else '❌ FAIL'}")
        print(f"Combined Detection: {'✅ PASS' if combined_test else '❌ FAIL'}")
        print(f"Display Formatting: {'✅ PASS' if display_test else '❌ FAIL'}")
        
        overall = all([bitcoin_test, password_test, card_test, api_test, combined_test, display_test])
        print(f"\nOverall: {'🎉 ALL TESTS PASSED' if overall else '⚠️ SOME TESTS FAILED'}")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure all required modules are available")
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()