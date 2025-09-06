"""
Test suite for DeviceFingerprint Library
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devicefingerprint import (
    DeviceFingerprintGenerator,
    AdvancedDeviceFingerprinter,
    FingerprintMethod,
    FingerprintResult,
    generate_device_fingerprint,
    bind_token_to_device,
    verify_device_binding
)


class TestDeviceFingerprintGenerator(unittest.TestCase):
    """Test basic device fingerprint generator"""
    
    def setUp(self):
        self.generator = DeviceFingerprintGenerator()
    
    def test_generate_fingerprint(self):
        """Test basic fingerprint generation"""
        fingerprint = self.generator.generate_device_fingerprint()
        
        # Check format and length
        self.assertIsInstance(fingerprint, str)
        self.assertTrue(fingerprint.startswith('device_'))
        self.assertEqual(len(fingerprint), 39)  # 'device_' + 32 chars
    
    def test_fingerprint_consistency(self):
        """Test that fingerprint is consistent across calls"""
        fp1 = self.generator.generate_device_fingerprint()
        fp2 = self.generator.generate_device_fingerprint()
        
        self.assertEqual(fp1, fp2)
    
    def test_static_method(self):
        """Test static method access"""
        fp1 = DeviceFingerprintGenerator.generate_device_fingerprint()
        fp2 = self.generator.generate_device_fingerprint()
        
        self.assertEqual(fp1, fp2)


class TestAdvancedDeviceFingerprinter(unittest.TestCase):
    """Test advanced device fingerprinter"""
    
    def setUp(self):
        self.fingerprinter = AdvancedDeviceFingerprinter()
    
    def test_basic_method(self):
        """Test basic fingerprinting method"""
        result = self.fingerprinter.generate_fingerprint(FingerprintMethod.BASIC)
        
        self.assertIsInstance(result, FingerprintResult)
        self.assertEqual(result.method, FingerprintMethod.BASIC)
        self.assertEqual(len(result.fingerprint), 32)
        self.assertGreaterEqual(result.confidence, 0.0)
        self.assertLessEqual(result.confidence, 1.0)
        self.assertIsInstance(result.components, list)
        self.assertIsInstance(result.warnings, list)
    
    def test_advanced_method(self):
        """Test advanced fingerprinting method"""
        result = self.fingerprinter.generate_fingerprint(FingerprintMethod.ADVANCED)
        
        self.assertIsInstance(result, FingerprintResult)
        self.assertEqual(result.method, FingerprintMethod.ADVANCED)
        self.assertEqual(len(result.fingerprint), 32)
        self.assertGreaterEqual(result.confidence, 0.7)  # Should be higher than basic
    
    def test_quantum_resistant_method(self):
        """Test quantum-resistant fingerprinting method"""
        result = self.fingerprinter.generate_fingerprint(FingerprintMethod.QUANTUM_RESISTANT)
        
        self.assertIsInstance(result, FingerprintResult)
        self.assertEqual(result.method, FingerprintMethod.QUANTUM_RESISTANT)
        self.assertEqual(len(result.fingerprint), 32)
        self.assertGreaterEqual(result.confidence, 0.9)  # Should be highest
    
    def test_default_method(self):
        """Test default method is quantum resistant"""
        result = self.fingerprinter.generate_fingerprint()
        
        self.assertEqual(result.method, FingerprintMethod.QUANTUM_RESISTANT)
    
    def test_fingerprint_stability(self):
        """Test fingerprint stability verification"""
        result = self.fingerprinter.generate_fingerprint(FingerprintMethod.QUANTUM_RESISTANT)
        
        is_stable, confidence = self.fingerprinter.verify_fingerprint_stability(
            result.fingerprint, FingerprintMethod.QUANTUM_RESISTANT
        )
        
        self.assertTrue(is_stable)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_fingerprint_components(self):
        """Test that fingerprint includes hardware components"""
        result = self.fingerprinter.generate_fingerprint(FingerprintMethod.ADVANCED)
        
        # Should have multiple components
        self.assertGreater(len(result.components), 2)
        
        # Should include system info
        system_info_found = any('Windows' in str(comp) or 'Linux' in str(comp) or 'Darwin' in str(comp) 
                               for comp in result.components)
        self.assertTrue(system_info_found, "Should include system information")


class TestLegacyFunctions(unittest.TestCase):
    """Test legacy compatibility functions"""
    
    def test_generate_device_fingerprint(self):
        """Test legacy generate_device_fingerprint function"""
        fingerprint = generate_device_fingerprint()
        
        self.assertIsInstance(fingerprint, str)
        self.assertEqual(len(fingerprint), 32)
    
    def test_consistency_with_advanced(self):
        """Test legacy function consistency with advanced method"""
        legacy_fp = generate_device_fingerprint()
        
        advanced = AdvancedDeviceFingerprinter()
        advanced_result = advanced.generate_fingerprint(FingerprintMethod.QUANTUM_RESISTANT)
        
        self.assertEqual(legacy_fp, advanced_result.fingerprint)


class TestTokenBinding(unittest.TestCase):
    """Test token binding functionality"""
    
    def test_bind_token_to_device(self):
        """Test token binding to device"""
        original_token = {
            'user_id': 'test_user',
            'permissions': ['read', 'write'],
            'data': 'secret_data'
        }
        
        bound_token = bind_token_to_device(original_token)
        
        # Should have original data
        self.assertEqual(bound_token['user_id'], 'test_user')
        self.assertEqual(bound_token['permissions'], ['read', 'write'])
        self.assertEqual(bound_token['data'], 'secret_data')
        
        # Should have binding data
        self.assertIn('device_fingerprint', bound_token)
        self.assertIn('binding_timestamp', bound_token)
        self.assertIn('binding_version', bound_token)
        
        # Check fingerprint format
        self.assertIsInstance(bound_token['device_fingerprint'], str)
        self.assertEqual(len(bound_token['device_fingerprint']), 32)
        
        # Check version
        self.assertEqual(bound_token['binding_version'], 'quantum-device-bound-v1')
    
    def test_verify_device_binding_success(self):
        """Test successful device binding verification"""
        original_token = {'user': 'test', 'data': 'secret'}
        bound_token = bind_token_to_device(original_token)
        
        # Should verify successfully on same device
        self.assertTrue(verify_device_binding(bound_token))
    
    def test_verify_device_binding_no_binding(self):
        """Test verification of token without binding"""
        token_without_binding = {'user': 'test', 'data': 'secret'}
        
        # Should allow tokens without binding (backward compatibility)
        self.assertTrue(verify_device_binding(token_without_binding))
    
    def test_verify_device_binding_wrong_fingerprint(self):
        """Test verification with wrong fingerprint"""
        token_with_wrong_fp = {
            'user': 'test',
            'data': 'secret',
            'device_fingerprint': 'wrong_fingerprint_12345678901234567890'
        }
        
        # Should fail verification
        self.assertFalse(verify_device_binding(token_with_wrong_fp))
    
    def test_bind_empty_token(self):
        """Test binding empty token"""
        empty_token = {}
        bound_token = bind_token_to_device(empty_token)
        
        # Should still add binding data
        self.assertIn('device_fingerprint', bound_token)
        self.assertIn('binding_timestamp', bound_token)
        self.assertIn('binding_version', bound_token)


if __name__ == '__main__':
    unittest.main()
