"""
Oxidize: High-performance data processing tools for Python, built with Rust.

This is an umbrella package that provides information about oxidize packages
for high-performance data processing tools.

Tools from oxidize:
- oxidize-xml: Streaming XML to JSON conversion
- oxidize-postal: Address parsing and normalization
- More tools coming soon...

For specific functionality, install the individual tools:
    pip install oxidize-xml
    pip install oxidize-postal
"""

__version__ = "0.7.0"
__author__ = "Eric Aleman"

def list_tools():
    """List available tools from oxidize."""
    tools = {
        "oxidize-xml": {
            "description": "Streaming XML to JSON conversion",
            "github": "https://github.com/yourusername/oxidize-xml",
            "install": "pip install oxidize-xml"
        },
        "oxidize-postal": {
            "description": "Address parsing and normalization with international support",
            "github": "https://github.com/yourusername/oxidize-postal", 
            "install": "pip install oxidize-postal"
        }
    }
    
    print("Oxidize Ecosystem Tools:")
    print("=" * 50)
    for name, info in tools.items():
        print(f"\n{name}:")
        print(f"  Description: {info['description']}")
        print(f"  Install: {info['install']}")
        print(f"  GitHub: {info['github']}")
    
    return tools

def get_version():
    """Get the version of the oxidize umbrella package."""
    return __version__
