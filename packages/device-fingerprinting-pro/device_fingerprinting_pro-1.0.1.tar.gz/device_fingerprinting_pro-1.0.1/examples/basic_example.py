"""
Basic DeviceFingerprint Example
==============================

Hey there! This example shows you how easy it is to use our DeviceFingerprint library.
We'll create a unique ID for your computer in just a few lines of code. Pretty cool, right?
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devicefingerprint import DeviceFingerprintGenerator

def main():
    print("=== Let's Create Your Device's Unique ID! ===\n")
    
    # First, let's set up our fingerprint maker
    generator = DeviceFingerprintGenerator()
    
    # Now let's create your computer's unique fingerprint!
    print("Working on your device fingerprint... (this is pretty fast!)")
    fingerprint = generator.generate_device_fingerprint()
    
    print(f"Ta-da! Your device fingerprint: {fingerprint}")
    print(f"That's {len(fingerprint)} characters of pure uniqueness!")
    print(f"Starts with 'device_': {fingerprint.startswith('device_')}")
    
    # Test consistency
    print("\nTesting consistency...")
    fingerprint2 = generator.generate_device_fingerprint()
    print(f"Second fingerprint: {fingerprint2}")
    print(f"Fingerprints match: {fingerprint == fingerprint2}")
    
    # Static method usage
    print("\nUsing static method...")
    static_fingerprint = DeviceFingerprintGenerator.generate_device_fingerprint()
    print(f"Static method result: {static_fingerprint}")
    print(f"Matches instance method: {fingerprint == static_fingerprint}")

if __name__ == '__main__':
    main()
