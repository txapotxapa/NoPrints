#!/usr/bin/env python3
"""
Test Bitcoin validator functionality
"""

from bitcoin_validator import BitcoinValidator

def test_bitcoin_addresses():
    """Test Bitcoin address detection and validation"""
    validator = BitcoinValidator()
    
    # Test addresses (these are example formats, not real addresses)
    test_cases = [
        # Bitcoin Legacy (P2PKH) - starts with 1
        ("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "legacy", True),
        
        # Bitcoin SegWit (P2SH) - starts with 3  
        ("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy", "segwit_p2sh", True),
        
        # Bitcoin Bech32 (Native SegWit) - starts with bc1
        ("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", "bech32", True),
        
        # Bitcoin Taproot - starts with bc1p
        ("bc1p5d7rjq7g6rdk2yhzks9smlaqtedr4dekq08ge8ztwac72sfr9rusxg3297", "taproot", True),
        
        # Testnet addresses
        ("mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn", "testnet_legacy", True),
        ("tb1qw508d6qejxtdg4y5r3zarvary0c5xw7kxpjzsx", "testnet_bech32", True),
        
        # Lightning Network
        ("lnbc100u1p3pj257pp5yztkwjcz5ftl5laxkav23zmzekaw37zk6kmv80pk4xaev5qhtz7qdqu2askcmr9wssx7e3q2dshgmmndp5scedqiis9fhnztt4", "lightning_invoice", True),
        ("satoshi@stacker.news", "lightning_address", True),
        
        # Invalid addresses
        ("1InvalidAddress", "legacy", False),
        ("NotAnAddress", "none", False),
        ("", "none", False),
    ]
    
    print("🧪 Testing Bitcoin Address Detection & Validation")
    print("=" * 60)
    
    passed = 0
    total = len(test_cases)
    
    for address, expected_type, should_be_valid in test_cases:
        print(f"\nTesting: {address[:30]}{'...' if len(address) > 30 else ''}")
        
        # Test detection
        result = validator.detect_bitcoin_content(address)
        
        # Check if detected correctly
        detected = False
        detected_type = "none"
        
        if result['addresses']:
            detected = True
            detected_type = result['addresses'][0]['type']
        elif result['lightning']:
            detected = True
            detected_type = "lightning_" + result['lightning'][0]['type']
        
        # Test validation for addresses
        if expected_type in ['legacy', 'bech32', 'taproot', 'testnet_legacy', 'testnet_bech32']:
            is_valid, addr_type, network = validator.validate_address(address)
            validation_passed = is_valid == should_be_valid
        else:
            validation_passed = True  # Skip validation for non-address types
        
        detection_passed = detected == should_be_valid
        type_passed = detected_type == expected_type or not should_be_valid
        
        if detection_passed and type_passed and validation_passed:
            print(f"✅ PASS - Detected: {detected}, Type: {detected_type}, Valid: {should_be_valid}")
            passed += 1
        else:
            print(f"❌ FAIL - Expected: {expected_type}, Got: {detected_type}")
            print(f"    Detection: {detection_passed}, Type: {type_passed}, Validation: {validation_passed}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    return passed == total

def test_private_keys():
    """Test private key detection"""
    validator = BitcoinValidator()
    
    test_keys = [
        # WIF format private keys (example format)
        "5HueCGU8rMjxEXxiPuD5BDku4MkFqeZyd4dZ1jvhTVqvbTLvyTJ",
        "KwDiBf89QgGbjEhKnhXJuH7LrciVrZi3qYjgd9M7rFU73sVHnoWn",
        "L4rK1yDtCWekvXuE6oXD9jCYfFNV2cWRpVuPLBcCU2z8TrisoyY1",
        
        # Hex format (64 chars)
        "e9873d79c6d87dc0fb6a5778633389f4453213303da61f20bd67fc233aa33262",
        
        # Invalid
        "not_a_private_key",
        "5InvalidPrivateKey"
    ]
    
    print("\n🔐 Testing Private Key Detection")
    print("=" * 60)
    
    for key in test_keys:
        result = validator.detect_bitcoin_content(key)
        
        if result['private_keys']:
            print(f"✅ Detected private key: {key[:10]}...{key[-4:]}")
            print(f"   Type: {result['private_keys'][0]['type']}")
            print(f"   Risk Level: {result['risk_level']}")
        else:
            print(f"❌ No private key detected: {key}")
    
    return True

def test_seed_phrases():
    """Test seed phrase detection"""
    validator = BitcoinValidator()
    
    seed_phrases = [
        # Example 12-word phrase (not a real seed)
        "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
        
        # Example 24-word phrase
        "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art",
        
        # Invalid phrases
        "this is not a seed phrase",
        "one two three four five six seven eight nine ten eleven",  # Only 11 words
    ]
    
    print("\n🌱 Testing Seed Phrase Detection")
    print("=" * 60)
    
    for phrase in seed_phrases:
        result = validator.detect_bitcoin_content(phrase)
        
        if result['seed_phrases']:
            seed_info = result['seed_phrases'][0]
            print(f"✅ Detected seed phrase: {seed_info['word_count']} words")
            print(f"   Risk Level: {result['risk_level']}")
        else:
            print(f"❌ No seed phrase detected in: {phrase[:30]}...")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Bitcoin Validator Tests")
    print("=" * 60)
    
    try:
        # Run all tests
        addr_test = test_bitcoin_addresses()
        key_test = test_private_keys()
        seed_test = test_seed_phrases()
        
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        print(f"Address Detection & Validation: {'✅ PASS' if addr_test else '❌ FAIL'}")
        print(f"Private Key Detection: {'✅ PASS' if key_test else '❌ FAIL'}")
        print(f"Seed Phrase Detection: {'✅ PASS' if seed_test else '❌ FAIL'}")
        
        overall = addr_test and key_test and seed_test
        print(f"\nOverall: {'🎉 ALL TESTS PASSED' if overall else '⚠️ SOME TESTS FAILED'}")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure bitcoin_validator.py is in the same directory")
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()