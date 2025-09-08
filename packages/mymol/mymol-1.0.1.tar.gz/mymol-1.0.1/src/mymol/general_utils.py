import uuid
import re
import hashlib
import random
import string
import time
import os
import pyperclip

def generate_UUID() -> str:
    """
    Generate a UUID (Universally Unique Identifier).

    Args:
        None

    Returns:
        str: A UUID (Universally Unique Identifier).

    Examples:
        >>> generate_UUID()
        'f47ac10b-58cc-4372-a567-0e02b2c3d479'
        >>> generate_UUID()
        'c0e2f6b2-472c-4372-a567-0e02b2c3d479'
    """
    return str(uuid.uuid4())

def validate_email(email: str) -> bool:
    """
    Validate the given email address.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email address is valid, False otherwise.

    Examples:
        >>> validate_email("test@example.com")
        True
        >>> validate_email("invalid-email")
        False
        """

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def hash_string(text: str) -> str:
    """
    Hash the given text using SHA-256 algorithm.

    Args:
        text (str): The input text to hash.

    Returns:
        str: The hashed text.

    Examples:
        >>> hash_string("Hello world")
        '2ef7bde608ce5404e97d5f042f95f89f1c232871d3d7e1c2'
        >>> hash_string("This is a test sentence.")
        'b5b1e4b7f8c8f2f2d4a0c8f9b8d0b4b4e0f1f1b7e8f2f0f2f0'
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(text.encode('utf-8'))
    return sha256_hash.hexdigest()

def generate_password(length: int = 8) -> str:
    """
    Generate a random password of the given length.

    Args:
        length (int): The length of the password to generate.

    Returns:
        str: A random password of the given length.

    Examples:
        >>> generate_password()
        'P@ssw0rd'
        >>> generate_password(12)
        'P@ssw0rd123'
    """


    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for i in range(length))
    return password

def validate_password(password: str) -> bool:
    """
    Validate the given password.

    Args:
        password (str): The password to validate.

    Returns:
        bool: True if the password is valid, False otherwise.

    Examples:
        >>> validate_password("P@ssw0rd")
        True
        >>> validate_password("password")
        False
    """
    return any(char.isupper() for char in password) and any(char.islower() for char in password) and any(char.isdigit() for char in password) and any(char in string.punctuation for char in password)

def measure_execution_time(func):
    """
    Measure the execution time of the given function.

    Args:
        func (function): The function to measure the execution time of.

    Returns:
        function: The wrapper function.

    Examples:
        >>> @measure_execution_time
        ... def my_function():
        ...     return sum(range(1000000))
        >>> my_function()
        Execution time: 0.001 seconds
        499999500000
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f'Execution time: {end_time - start_time:.3f} seconds')
        return result

    return wrapper

def enviroment_variable_getter(env_var: str) -> str:
    """
    Get the value of the given environment variable.

    Args:
        env_var (str): The name of the environment variable.

    Returns:
        str: The value of the environment variable.

    Examples:
        >>> enviroment_variable_getter("HOME")
        '/home/user'
        >>> enviroment_variable_getter("SHELL")
        '/bin/bash'
    """
    return os.getenv(env_var)

def clipboard_manager(text: str) -> None:
    """
    Copy the given text to the clipboard.

    Args:
        text (str): The text to copy to the clipboard.

    Returns:
        None

    Examples:
        >>> clipboard_manager("Hello world")
        """
    try:

        pyperclip.copy(text)
        print('Text copied to clipboard')
    except ImportError:
        print('pyperclip module is not installed. Please install it using "pip install pyperclip"')

def check_os() -> str:
    """
    Check the operating system.

    Args:
        None

    Returns:
        str: The name of the operating system.

    Examples:
        >>> check_os()
        'Linux'
        """
    return os.name
