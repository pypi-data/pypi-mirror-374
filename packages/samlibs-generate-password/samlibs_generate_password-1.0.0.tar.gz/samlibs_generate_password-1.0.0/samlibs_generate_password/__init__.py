"""
samlibs-generate-password: A lightweight, fast, and optimized password generator library

This library provides a simple and efficient way to generate secure passwords
with customizable options including character sets and exclusion lists.

Example:
    Basic usage:
        from samlibs_generate_password import generate_password
        
        password = generate_password()
        print(password)  # e.g., "K9$mN7#qR2@x"
    
    Advanced usage:
        password = generate_password(
            length=16,
            uppercase=True,
            lowercase=True,
            numbers=True,
            special=False,
            exclude=['0', 'O', 'l', '1']
        )
"""

from .generator import (
    generate_password,
    generate_password_dict,
    password_generator,
    __version__,
    __author__,
    __email__
)

# Make the main function available at package level
__all__ = [
    'generate_password',
    'generate_password_dict', 
    'password_generator',
    '__version__',
    '__author__',
    '__email__'
]

# Package metadata
__title__ = 'samlibs-generate-password'
__description__ = 'A lightweight, fast, and optimized password generator library'
__url__ = 'https://github.com/themrsami/samlibs-generate-password'
__license__ = 'MIT'