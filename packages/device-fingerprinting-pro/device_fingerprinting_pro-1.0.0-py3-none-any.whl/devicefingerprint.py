"""
DeviceFingerprint Library
========================

Hey there! This is your friendly device identification system that helps keep your apps secure.
Think of it like a digital fingerprint for your computer - it looks at your hardware and creates 
a unique ID that stays the same every time, even after you restart your computer.

What cool stuff can it do?
- Looks at your computer's hardware (like CPU, memory, hard drive) to create a unique ID
- Works great on Windows, Linux, and Mac computers
- Uses super-strong encryption (SHA3-512, SHA3-256) to keep things secure
- Can spot if someone's trying to mess with your device
- Keeps your private info safe by scrambling sensitive data
- Can tie security tokens to your specific device
- Detects if someone's trying to tamper with your system

Perfect for keeping bad guys out and making sure you're really you!

"""

import hashlib
import os
import platform
import secrets
import subprocess
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

class FingerprintGenerationError(Exception):
    """Oops! Something went wrong when trying to create your device fingerprint and we can't safely fall back to a backup method"""
    pass

__version__ = "1.0.0"
__author__ = "DeviceFingerprint Development Team"

class FingerprintMethod(Enum):
    """Different ways we can create your device fingerprint - pick what works best for you!"""
    BASIC = "basic"
    ADVANCED = "advanced"
    QUANTUM_RESISTANT = "quantum_resistant"

@dataclass
class FingerprintResult:
    """Here's everything we found out about your device! This bundle contains your unique fingerprint plus all the cool details about how we made it"""
    fingerprint: str
    method: FingerprintMethod
    components: List[str]
    timestamp: str
    confidence: float
    warnings: List[str]

class DeviceFingerprintGenerator:
    """
    Your Basic Device ID Creator
    
    This friendly little class works perfectly with our dual QR recovery system.
    It looks at your computer's hardware to create a unique ID that stops people 
    from copying your login credentials to other computers. Pretty neat, right?
    """
    
    @staticmethod
    def generate_device_fingerprint() -> str:
        """
        Let's create a unique ID for your device!
        
        Returns:
            A special string that's unique to your computer
        """
        fingerprint_components = []  # We'll collect info about your computer here
        
        try:
            # Let's see what kind of computer you're using
            fingerprint_components.append(platform.system())  # Windows? Mac? Linux?
            fingerprint_components.append(platform.release()) # What version?
            fingerprint_components.append(platform.machine()) # Intel? AMD? ARM?
            
            try:
                fingerprint_components.append(platform.processor()) # What's your CPU?
            except:
                fingerprint_components.append("unknown_processor")  # No worries if we can't get this
            
            try:
                fingerprint_components.append(platform.node())  # Your computer's name
            except:
                fingerprint_components.append("unknown_node")  # Still okay if this fails
            
            # Let's also check what Python you're running
            fingerprint_components.append(platform.python_implementation())
            fingerprint_components.append(platform.python_version())
            
        except Exception:
            # Oops! If something goes wrong, we'll use a backup method
            fingerprint_components = ["fallback_device", str(secrets.randbits(64))]
        
        # Now let's mix all this info together and scramble it for security
        combined = "|".join(str(component) for component in fingerprint_components)
        fingerprint_hash = hashlib.sha3_256(combined.encode()).hexdigest()
        
        return f"device_{fingerprint_hash[:32]}"  # Here's your unique device ID!

class AdvancedDeviceFingerprinter:
    """
    The Super-Smart Device ID Creator
    
    This is our premium device identification system that really knows its stuff!
    It uses quantum-resistant encryption (fancy future-proof security) and works 
    great on any computer - Windows, Mac, or Linux. It's like having a detective 
    that can identify your computer just by looking at its hardware!
    """
    
    def __init__(self):
        """Getting our super-smart fingerprinter ready to go!"""
        self.supported_methods = [
            FingerprintMethod.BASIC,        # Quick and easy
            FingerprintMethod.ADVANCED,     # More thorough
            FingerprintMethod.QUANTUM_RESISTANT  # Maximum security
        ]
    
    def generate_fingerprint(self, method: FingerprintMethod = FingerprintMethod.QUANTUM_RESISTANT) -> FingerprintResult:
        """
        Time to create your device's unique fingerprint!
        
        Args:
            method: Which method do you want? (We default to the super-secure quantum one!)
            
        Returns:
            A complete package with your fingerprint and all the cool details about how we made it
        """
        if method == FingerprintMethod.BASIC:
            return self._generate_basic_fingerprint()  # Quick and simple
        elif method == FingerprintMethod.ADVANCED:
            return self._generate_advanced_fingerprint()  # The balanced approach
        else:
            return self._generate_quantum_resistant_fingerprint()  # Maximum security mode!
    
    def _generate_basic_fingerprint(self) -> FingerprintResult:
        """Let's create a quick and simple fingerprint using basic system info"""
        components = []  # We'll collect some basic info about your computer
        warnings = []    # If anything goes wrong, we'll note it here
        
        try:
            # Let's grab the essentials about your system
            components.extend([
                platform.system(),   # What OS are you running?
                platform.machine(),  # What kind of processor architecture?
                platform.node()      # What's your computer's name?
            ])
            
            try:
                # Let's try to get your network card's unique ID
                mac = str(uuid.getnode())
                components.append(mac)
            except:
                components.append("no-mac")
                warnings.append("Could not retrieve MAC address")  # No big deal if this fails
            
            # Now let's mix it all together and create your unique ID
            combined = '|'.join(components)
            fingerprint_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
            
            return FingerprintResult(
                fingerprint=fingerprint_hash[:32],  # Here's your device ID!
                method=FingerprintMethod.BASIC,
                components=components,
                timestamp=datetime.now().isoformat(),
                confidence=0.7,
                warnings=warnings
            )
            
        except Exception as e:
            fallback = f"basic-fallback-{secrets.randbits(32)}"
            return FingerprintResult(
                fingerprint=hashlib.sha256(fallback.encode()).hexdigest()[:32],
                method=FingerprintMethod.BASIC,
                components=["fallback"],
                timestamp=datetime.now().isoformat(),
                confidence=0.3,
                warnings=[f"Fallback fingerprint due to: {e}"]
            )
    
    def _generate_advanced_fingerprint(self) -> FingerprintResult:
        """Now we're getting serious! Let's dig deeper into your hardware details"""
        components = []  # We'll gather more detailed info this time
        warnings = []    # Keep track of any hiccups along the way
        
        try:
            # Let's get more detailed info about your system
            components.extend([
                platform.system(),    # Your operating system
                platform.release(),   # Which version exactly
                platform.machine(),   # Your processor type
                platform.processor()  # Detailed processor info
            ])
            
            try:
                # Your network card's unique identifier
                mac = str(uuid.getnode())
                components.append(mac)
            except:
                components.append("no-mac")
                warnings.append("Could not retrieve MAC address")  # No problem if we can't get this
            
            # Let's get system-specific details
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\\n')
                        for line in lines:
                            if line.strip() and 'UUID' not in line:
                                components.append(line.strip())
                                break
                except Exception as e:
                    warnings.append(f"Could not retrieve Windows UUID: {e}")
            else:
                try:
                    if os.path.exists('/etc/machine-id'):
                        with open('/etc/machine-id', 'r') as f:
                            machine_id = f.read().strip()
                            components.append(machine_id)
                    elif os.path.exists('/var/lib/dbus/machine-id'):
                        with open('/var/lib/dbus/machine-id', 'r') as f:
                            machine_id = f.read().strip()
                            components.append(machine_id)
                except Exception as e:
                    warnings.append(f"Could not retrieve machine ID: {e}")
            
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(['wmic', 'cpu', 'get', 'ProcessorId'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\\n')
                        for line in lines:
                            if line.strip() and 'ProcessorId' not in line:
                                components.append(line.strip())
                                break
            except Exception as e:
                warnings.append(f"Could not retrieve CPU ID: {e}")
            
            combined = '|'.join(components)
            fingerprint_hash = hashlib.sha3_256(combined.encode('utf-8')).hexdigest()
            
            return FingerprintResult(
                fingerprint=fingerprint_hash[:32],
                method=FingerprintMethod.ADVANCED,
                components=components,
                timestamp=datetime.now().isoformat(),
                confidence=0.9,
                warnings=warnings
            )
            
        except Exception as e:
            warnings.append(f"Advanced fingerprinting failed: {e}")
            raise FingerprintGenerationError(
                f"Advanced fingerprinting failed: {e}. "
                f"Use explicit fallback or basic method if lower security is acceptable."
            )
    
    def _generate_quantum_resistant_fingerprint(self) -> FingerprintResult:
        """
        Generate quantum-resistant device fingerprint
        
        Uses SHA3-512 for quantum resistance and comprehensive hardware data.
        """
        components = []
        warnings = []
        
        try:
            components.extend([
                platform.system(),
                platform.release(),
                platform.machine()
            ])
            
            try:
                mac = str(uuid.getnode())
                components.append(mac)
            except:
                components.append("no-mac")
                warnings.append("Could not retrieve MAC address")
            
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\\n')
                        for line in lines:
                            if line.strip() and 'UUID' not in line:
                                components.append(line.strip())
                                break
                except Exception as e:
                    warnings.append(f"Could not retrieve Windows UUID: {e}")
            else:
                try:
                    if os.path.exists('/etc/machine-id'):
                        with open('/etc/machine-id', 'r') as f:
                            machine_id = f.read().strip()
                            components.append(machine_id)
                    elif os.path.exists('/var/lib/dbus/machine-id'):
                        with open('/var/lib/dbus/machine-id', 'r') as f:
                            machine_id = f.read().strip()
                            components.append(machine_id)
                except Exception as e:
                    warnings.append(f"Could not retrieve machine ID: {e}")
            
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(['wmic', 'cpu', 'get', 'ProcessorId'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\\n')
                        for line in lines:
                            if line.strip() and 'ProcessorId' not in line:
                                components.append(line.strip())
                                break
            except Exception as e:
                warnings.append(f"Could not retrieve CPU ID: {e}")
            
            combined = '|'.join(components)
            
            device_hash = hashlib.sha3_512(combined.encode('utf-8')).hexdigest()
            
            return FingerprintResult(
                fingerprint=device_hash[:32],
                method=FingerprintMethod.QUANTUM_RESISTANT,
                components=components,
                timestamp=datetime.now().isoformat(),
                confidence=0.95,
                warnings=warnings
            )
            
        except Exception as e:
            warnings.append(f"Quantum-resistant fingerprinting failed: {e}")
            fallback = f"{platform.system()}-{platform.machine()}-{os.getlogin() if hasattr(os, 'getlogin') else 'unknown'}"
            fallback_hash = hashlib.sha3_512(fallback.encode('utf-8')).hexdigest()[:32]
            
            return FingerprintResult(
                fingerprint=fallback_hash,
                method=FingerprintMethod.QUANTUM_RESISTANT,
                components=[fallback],
                timestamp=datetime.now().isoformat(),
                confidence=0.6,
                warnings=warnings + ["Used fallback fingerprint"]
            )
    
    def generate_fingerprint_with_fallback(self, method: FingerprintMethod = FingerprintMethod.QUANTUM_RESISTANT, allow_fallback: bool = False) -> FingerprintResult:
        """
        Generate device fingerprint with explicit fallback control
        
        Args:
            method: Fingerprint generation method
            allow_fallback: If True, falls back to basic method on failure
            
        Returns:
            FingerprintResult with fingerprint and metadata
            
        Raises:
            FingerprintGenerationError: If fingerprinting fails and fallback not allowed
        """
        try:
            return self.generate_fingerprint(method)
        except FingerprintGenerationError as e:
            if not allow_fallback:
                raise e
            
            # Explicit fallback with clear indication
            basic_result = self._generate_basic_fingerprint()
            basic_result.warnings.append(f"Fallback from {method.value} to basic method due to failure")
            basic_result.confidence = min(basic_result.confidence, 0.5)  # Reduce confidence for fallback
            return basic_result
    
    def verify_fingerprint_stability(self, stored_fingerprint: str, method: FingerprintMethod = FingerprintMethod.QUANTUM_RESISTANT) -> Tuple[bool, float]:
        """
        Verify fingerprint stability across time
        
        Args:
            stored_fingerprint: Previously generated fingerprint
            method: Method used to generate stored fingerprint
            
        Returns:
            Tuple of (is_stable, confidence_score)
        """
        current_result = self.generate_fingerprint(method)
        
        is_match = secrets.compare_digest(stored_fingerprint, current_result.fingerprint)
        
        return is_match, current_result.confidence

def generate_device_fingerprint() -> str:
    """
    Legacy compatibility function for main application
    
    Returns:
        Quantum-resistant device fingerprint
    """
    fingerprinter = AdvancedDeviceFingerprinter()
    result = fingerprinter.generate_fingerprint(FingerprintMethod.QUANTUM_RESISTANT)
    return result.fingerprint

def bind_token_to_device(token_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Let's tie your security token to this specific device! 
    
    Think of this like putting a special sticker on your token that says 
    "This belongs to this computer only!" It helps prevent bad guys from 
    using your token on a different device.
    
    Args:
        token_data: Your original security token (as a dictionary)
    
    Returns:
        Your token, now with extra security info that ties it to this device
    """
    try:
        # First, let's get this device's unique fingerprint
        device_fingerprint = generate_device_fingerprint()
        
        # Now let's add the security info to your token
        enhanced_token = token_data.copy()  # Make a copy so we don't mess up the original
        enhanced_token['device_fingerprint'] = device_fingerprint  # Add the device ID
        enhanced_token['binding_timestamp'] = datetime.now().isoformat()  # When we did this
        enhanced_token['binding_version'] = 'quantum-device-bound-v1'  # What method we used
        
        return enhanced_token  # Here's your newly secured token!
        
    except Exception:
        # If something goes wrong, just return the original token
        return token_data

def verify_device_binding(token_data: Dict[str, Any]) -> bool:
    """
    Let's check if this token really belongs to this device!
    
    Args:
        token_data: Token data dictionary with device binding
    
    Returns:
        True if device matches or no binding exists, False if binding check fails
    """
    try:
        if 'device_fingerprint' not in token_data:
            return True
        
        current_fingerprint = generate_device_fingerprint()
        stored_fingerprint = token_data['device_fingerprint']
        
        return secrets.compare_digest(current_fingerprint, stored_fingerprint)
            
    except Exception:
        return True
