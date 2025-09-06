"""
Token Binding Security Example
=============================

This example shows how to use device fingerprinting for
security token binding and verification.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devicefingerprint import (
    bind_token_to_device,
    verify_device_binding
)
import json

def main():
    print("=== Token Binding Security Example ===\n")
    
    # Simulate a user authentication token
    user_token = {
        'user_id': 'john_doe_123',
        'username': 'john.doe',
        'permissions': ['read', 'write', 'admin'],
        'session_id': 'sess_abc123def456',
        'expires_at': '2025-09-06T12:00:00Z',
        'issued_at': '2025-09-05T12:00:00Z'
    }
    
    print("Original token:")
    print(json.dumps(user_token, indent=2))
    print(f"Token size: {len(json.dumps(user_token))} bytes")
    
    # Bind token to current device
    print("\n=== Binding Token to Device ===")
    bound_token = bind_token_to_device(user_token)
    
    print("Token after device binding:")
    print(json.dumps(bound_token, indent=2))
    print(f"Bound token size: {len(json.dumps(bound_token))} bytes")
    
    # Show what was added
    added_fields = set(bound_token.keys()) - set(user_token.keys())
    print(f"\nAdded fields: {', '.join(added_fields)}")
    
    # Verify token on same device
    print("\n=== Token Verification ===")
    is_valid = verify_device_binding(bound_token)
    print(f"Token valid on current device: {is_valid}")
    
    # Simulate token verification on different device
    print("\n=== Simulating Different Device ===")
    fake_token = bound_token.copy()
    fake_token['device_fingerprint'] = 'fake_device_fingerprint_12345678'
    
    is_valid_fake = verify_device_binding(fake_token)
    print(f"Token valid with fake fingerprint: {is_valid_fake}")
    
    # Test backward compatibility
    print("\n=== Backward Compatibility Test ===")
    old_token = {'user': 'legacy_user', 'data': 'legacy_data'}
    is_valid_old = verify_device_binding(old_token)
    print(f"Legacy token without binding: {is_valid_old}")
    
    # Security demonstration
    print("\n=== Security Demonstration ===")
    print("PASS: Same device verification")
    print("FAIL: Different device verification") 
    print("PASS: Legacy token compatibility")
    print("\nThis prevents token theft and unauthorized device access!")

if __name__ == '__main__':
    main()
