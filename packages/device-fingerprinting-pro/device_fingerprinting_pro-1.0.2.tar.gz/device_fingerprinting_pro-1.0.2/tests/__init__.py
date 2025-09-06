"""
Test runner for device fingerprinting library
"""

import unittest
import os
import sys

if __name__ == '__main__':
    # Add parent directory to path
    test_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(test_dir)
    sys.path.insert(0, parent_dir)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = test_dir
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
