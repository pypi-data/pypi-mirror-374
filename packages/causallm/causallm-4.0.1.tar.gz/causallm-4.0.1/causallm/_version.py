"""
Version information for CausalLLM.

This module provides a single source of truth for version information.
"""

__version__ = "4.0.1"
__version_info__ = tuple(int(x) for x in __version__.split('.'))

# Additional version metadata
VERSION_MAJOR = __version_info__[0]
VERSION_MINOR = __version_info__[1] 
VERSION_PATCH = __version_info__[2]

# Build metadata
BUILD_DATE = "2024-09-07"
BUILD_TYPE = "release"  # "release", "beta", "alpha", "dev"

def get_version_string(include_build=False):
    """
    Get formatted version string.
    
    Args:
        include_build: Whether to include build metadata
        
    Returns:
        Formatted version string
    """
    base_version = __version__
    
    if include_build:
        return f"{base_version} ({BUILD_TYPE}, {BUILD_DATE})"
    
    return base_version

def get_version_info():
    """
    Get detailed version information.
    
    Returns:
        Dictionary with version details
    """
    return {
        "version": __version__,
        "version_info": __version_info__,
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR, 
        "patch": VERSION_PATCH,
        "build_date": BUILD_DATE,
        "build_type": BUILD_TYPE,
        "version_string": get_version_string(include_build=True)
    }