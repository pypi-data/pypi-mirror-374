import re

def reverse_string(string: str) -> str:
    """
    Reverse a string.

    Args:
        string (str): The input string.

    Returns:
        str: The reversed string.
        
    Example:
        >>> reverse_string("hello")
        "olleh"
    """
    return string[::-1]

def is_palindrome(string: str) -> bool:
    """
    Check if a string is a palindrome.

    Args:
        string (str): The input string.

    Returns:
        bool: True if the string is a palindrome, False otherwise.
        
    Example:
        >>> is_palindrome("racecar")
        True
        >>> is_palindrome("hello")
        False
    """
    return string == reverse_string(string)

def cap_string(string: str) -> str:
    """
    Capitalize the first letter of a string.

    Args:
        string (str): The input string.

    Returns:
        str: The capitalized string.
        
    Example:
        >>> cap_string("hello")
        "Hello"
    """
    return string.capitalize()

def cap_words(string: str) -> str:
    """
    Capitalize the first letter of each word in a string.

    Args:
        string (str): The input string.

    Returns:
        str: The capitalized string.
        
    Example:
        >>> cap_words("hello world")
        "Hello World"
    """
    return ' '.join(word.capitalize() for word in string.split())

def cap_whole_string(string: str) -> str:
    """
    Capitalize the entire string.

    Args:
        string (str): The input string.

    Returns:
        str: The capitalized string.
        
    Example:
        >>> cap_whole_string("hello")
        "HELLO"
    """
    return string.upper()

def count_vowels(string: str) -> int:
    """
    Count the number of vowels in a string.

    Args:
        string (str): The input string.

    Returns:
        int: The number of vowels in the string.
        
    Example:
        >>> count_vowels("hello")
        2
    """
    return len([char for char in string if char.lower() in 'aeiou'])

def replace_substring(string: str, old: str, new: str) -> str:
    """
    Replace all occurrences of a substring in a string.

    Args:
        string (str): The input string.
        old (str): The substring to replace.
        new (str): The new substring.

    Returns:
        str: The modified string.
        
    Example:
        >>> replace_substring("hello world", "world", "there")
        "hello there"
    """
    return string.replace(old, new)

def split_CamelCase(string: str) -> str:
    """
    Split a CamelCase string into separate words.

    Args:
        string (str): The input string.

    Returns:
        str: The split string.
        
    Example:
        >>> split_CamelCase("CamelCaseString")
        "Camel Case String"
    """
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', string)

def generate_acronym(string: str) -> str:
    """
    Generate an acronym from a string.

    Args:
        string (str): The input string.

    Returns:
        str: The acronym.
        
    Example:
        >>> generate_acronym("Portable Network Graphics")
        "PNG"
    """
    return ''.join(word[0].upper() for word in string.split())

def check_anagram(string1: str, string2: str) -> bool:
    """
    Check if two strings are anagrams of each other.

    Args:
        string1 (str): The first input string.
        string2 (str): The second input string.

    Returns:
        bool: True if the strings are anagrams, False otherwise.
        
    Example:
        >>> check_anagram("listen", "silent")
        True
        >>> check_anagram("hello", "world")
        False
    """
    return sorted(string1) == sorted(string2)

def remove_whitespace(string: str) -> str:
    """
    Remove all whitespace characters from a string.

    Args:
        string (str): The input string.

    Returns:
        str: The string without whitespace.
        
    Example:
        >>> remove_whitespace("hello world")
        "helloworld"
    """
    return ''.join(string.split())

def remove_punctuation(string: str) -> str:
    """
    Remove all punctuation characters from a string.

    Args:
        string (str): The input string.

    Returns:
        str: The string without punctuation.
        
    Example:
        >>> remove_punctuation("hello, world!")
        "helloworld"
    """
    return ''.join(char for char in string if char.isalnum())

def snake_case(string: str) -> str:

    """
    Convert a string to snake_case.

    Args:
        string (str): The input string.

    Returns:
        str: The string in snake_case.

    Example:
        >>> snake_case("HelloWorld")
        'hello_world'
    """
    if not isinstance(string, str):
        raise ValueError("Input must be a string")
    
    # Replace spaces with underscores and insert underscores before uppercase letters
    string = re.sub(r'\s+', '_', string)  # Replace spaces with underscores
    string = re.sub(r'(?<!^)(?=[A-Z])', '_', string)  # Insert underscores before uppercase letters
    return string.lower()  # Convert the result to lowercase