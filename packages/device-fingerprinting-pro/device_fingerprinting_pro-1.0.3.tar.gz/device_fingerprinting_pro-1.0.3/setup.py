"""
Setup configuration for DeviceFingerprint Library
"""

from setuptools import setup

# Read README for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except:
        return "Professional-grade hardware-based device identification for Python applications"

setup(
    name="device-fingerprinting-pro",
    version="1.0.3",
    author="Johnson Ajiboye",
    author_email="johnson@devicefingerprint.dev",
    description="Professional-grade hardware-based device identification for Python applications",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Johnsonajibi/DeviceFingerprinting",
    py_modules=["devicefingerprint"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Hardware",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
        ],
    },
    keywords=[
        "device fingerprinting",
        "hardware identification", 
        "security",
        "authentication",
        "device binding",
        "quantum resistant",
        "hardware security",
        "device detection",
        "system identification",
        "anti-fraud"
    ],
    project_urls={
        "Bug Reports": "https://github.com/Johnsonajibi/DeviceFingerprinting/issues",
        "Source": "https://github.com/Johnsonajibi/DeviceFingerprinting",
        "Documentation": "https://github.com/Johnsonajibi/DeviceFingerprinting#readme",
        "Release Notes": "https://github.com/Johnsonajibi/DeviceFingerprinting/blob/main/RELEASE_NOTES.md",
    },
)
