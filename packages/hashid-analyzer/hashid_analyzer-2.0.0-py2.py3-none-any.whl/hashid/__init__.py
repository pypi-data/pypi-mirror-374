"""
HashID - Comprehensive Hash and Token Analyzer

A professional tool for identifying and analyzing hash formats, tokens, and encoded data.
Designed for penetration testers, red team operators, security researchers, and developers.

Author: XPAlchemnist
Version: 2.0.0
License: MIT
"""

from .core.analyzer import HashTokenAnalyzer

__version__ = "2.0.0"
__author__ = "XPAlchemnist"
__email__ = "xpalchemnist@gmail.com"
__license__ = "MIT"
__description__ = "Comprehensive hash and token analyzer with persistent mode for security professionals"

# Main classes and functions for public API
__all__ = [
    'HashTokenAnalyzer',
    '__version__',
    '__author__',
    '__license__',
    '__description__'
]


def analyze(target_input: str, verbose: bool = True) -> 'HashTokenAnalyzer':
    """
    Quick analysis function for programmatic use.
    
    Args:
        target_input (str): Hash, token, or encoded data to analyze
        verbose (bool): Enable verbose output (default: True)
        
    Returns:
        HashTokenAnalyzer: Analyzer instance with results
        
    Example:
        >>> import hashid
        >>> result = hashid.analyze("5d41402abc4b2a76b9719d911017c592")
        >>> print(result.results['detected_formats'])
    """
    analyzer = HashTokenAnalyzer(target_input, verbose=verbose)
    analyzer.comprehensive_analysis()
    return analyzer


def quick_analyze(target_input: str, verbose: bool = False) -> 'HashTokenAnalyzer':
    """
    Quick analysis function without intensive operations.
    
    Args:
        target_input (str): Hash, token, or encoded data to analyze
        verbose (bool): Enable verbose output (default: False)
        
    Returns:
        HashTokenAnalyzer: Analyzer instance with basic results
        
    Example:
        >>> import hashid
        >>> result = hashid.quick_analyze("5d41402abc4b2a76b9719d911017c592")
        >>> print(result.results['detected_formats'])
    """
    analyzer = HashTokenAnalyzer(target_input, verbose=verbose)
    analyzer.identify_hash_formats()
    analyzer._calculate_entropy()
    return analyzer