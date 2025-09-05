"""
samlibs-generate-password: A lightweight, fast, and optimized password generator library
"""

import secrets
import string
from typing import Union, List, Dict, Any


def generate_password(
    length: int = 12,
    quantity: int = 1,
    lowercase: bool = True,
    uppercase: bool = True,
    numbers: bool = True,
    special: bool = True,
    exclude: List[str] = None
) -> Union[str, List[str]]:
    """
    Generate secure random passwords with customizable options
    
    Args:
        length (int): Length of each password (default: 12)
        quantity (int): Number of passwords to generate (default: 1)
        lowercase (bool): Include lowercase letters (default: True)
        uppercase (bool): Include uppercase letters (default: True)
        numbers (bool): Include numbers (default: True)
        special (bool): Include special characters (default: True)
        exclude (List[str]): List of characters to exclude (default: None)
    
    Returns:
        Union[str, List[str]]: Generated password(s) - string if quantity is 1, list if quantity > 1
    
    Raises:
        ValueError: If invalid parameters are provided
    """
    # Handle None exclude parameter
    if exclude is None:
        exclude = []
    
    # Validate inputs
    if length < 1:
        raise ValueError('Password length must be at least 1')
    if quantity < 1:
        raise ValueError('Quantity must be at least 1')
    if not isinstance(exclude, list):
        raise ValueError('Exclude must be a list')
    
    # Character sets - optimized for performance
    char_sets = {
        'lowercase': string.ascii_lowercase,
        'uppercase': string.ascii_uppercase,
        'numbers': string.digits,
        'special': '!@#$%^&*()_+-=[]{}|;:,.<>?'
    }
    
    # Build character pool
    chars = ''
    if lowercase:
        chars += char_sets['lowercase']
    if uppercase:
        chars += char_sets['uppercase']
    if numbers:
        chars += char_sets['numbers']
    if special:
        chars += char_sets['special']
    
    # Check if any character set is enabled
    if not chars:
        raise ValueError('At least one character set must be enabled')
    
    # Remove excluded characters efficiently using set operations
    if exclude:
        exclude_set = set(exclude)
        chars = ''.join(char for char in chars if char not in exclude_set)
    
    # Check if there are enough characters after exclusion
    if not chars:
        raise ValueError('No characters available after exclusion')
    
    # Generate password(s)
    passwords = []
    chars_length = len(chars)
    
    for _ in range(quantity):
        # Use secrets module for cryptographically secure random generation
        password = ''.join(secrets.choice(chars) for _ in range(length))
        passwords.append(password)
    
    # Return single password or list based on quantity
    return passwords[0] if quantity == 1 else passwords


# Alternative function that accepts a dictionary (like Node.js version)
def generate_password_dict(options: Dict[str, Any] = None) -> Union[str, List[str]]:
    """
    Generate secure random passwords using a dictionary of options (Node.js style API)
    
    Args:
        options (Dict[str, Any]): Configuration dictionary with same keys as function parameters
    
    Returns:
        Union[str, List[str]]: Generated password(s)
    """
    if options is None:
        options = {}
    
    return generate_password(
        length=options.get('length', 12),
        quantity=options.get('quantity', 1),
        lowercase=options.get('lowercase', True),
        uppercase=options.get('uppercase', True),
        numbers=options.get('numbers', True),
        special=options.get('special', True),
        exclude=options.get('exclude', [])
    )


# For backwards compatibility and convenience
def password_generator(options: Dict[str, Any] = None) -> Union[str, List[str]]:
    """Alias for generate_password_dict for convenience"""
    return generate_password_dict(options)


# Version information
__version__ = "1.0.0"
__author__ = "themrsami"
__email__ = "usamanazir13@gmail.com"