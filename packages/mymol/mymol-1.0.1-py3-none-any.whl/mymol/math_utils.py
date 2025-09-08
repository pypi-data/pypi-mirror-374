import random

def calculate_factorial(n: int) -> int:
    """
    Calculate the factorial of a given number.

    Args:
        n (int): The number to calculate the factorial for.

    Returns:
        int: The factorial of the given number.

    Raises:
        ValueError: If the input is a negative integer.
    """
    if n == 0:
        return 1
    else:
        return n * calculate_factorial(n-1)
    
def find_gcd(a: int, b: int) -> int:
    """
    Calculate the Greatest Common Divisor (GCD) of two numbers using the Euclidean algorithm.
    Args:
        a (int): The first number.
        b (int): The second number.
    Returns:
        int: The GCD of the two given numbers.
    Raises:
        ValueError: If either of the inputs is not an integer.
    """
    
    if b == 0:
        return a
    else:
        return find_gcd(b, a % b)

def check_prime(n: int) -> bool:
    """
    Check if a number is a prime number.
    Args:
        n (int): The number to check.
    Returns:
        bool: True if the number is prime, False otherwise.
    Raises:
        ValueError: If the input is a negative integer.
    """
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate_fibonacci(n: int) -> list:
    """
    Generate the Fibonacci sequence up to the nth term.
    Args:
        n (int): The number of terms in the sequence.
    Returns:
        list: The Fibonacci sequence up to the nth term.
    Raises:
        ValueError: If the input is a negative integer.
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    else:
        fib_sequence = [0, 1]
        for i in range(2, n):
            fib_sequence.append(fib_sequence[i - 1] + fib_sequence[i - 2])
        return fib_sequence
    
def round_number(number: float, places: int) -> float:
    """
    Round a number to a specified number of decimal places.
    Args:
        number (float): The number to round.
        places (int): The number of decimal places to round to.
    Returns:
        float: The rounded number.
    Raises:
        ValueError: If the input number is not a float.
    """
    return round(number, places)

def sum_digits(n: int) -> int:
    """
    Calculate the sum of the digits of a number.
    Args:
        n (int): The number to calculate the sum of digits for.
    Returns:
        int: The sum of the digits of the number.
    Raises:
        ValueError: If the input is a negative integer.
    """
    return sum(int(digit) for digit in str(n))

def find_power(base: int, exponent: int) -> int:
    """
    Calculate the power of a number.
    Args:
        base (int): The base number.
        exponent (int): The exponent.
    Returns:
        int: The result of the base raised to the exponent.
    Raises:
        ValueError: If either of the inputs is not an integer.
    """
    return base ** exponent

def is_armstrong_number(n: int) -> bool:
    """
    Check if a number is an Armstrong number.
    Args:
        n (int): The number to check.
    Returns:
        bool: True if the number is an Armstrong number, False otherwise.
    Raises:
        ValueError: If the input is a negative integer.
    """
    return n == sum(int(digit) ** len(str(n)) for digit in str(n))

def convert_int_to_binary(n: int) -> str:
    """
    Convert an integer to a binary string.
    Args:
        n (int): The integer to convert.
    Returns:
        str: The binary representation of the integer.
    Raises:
        ValueError: If the input is a negative integer.
    """
    return bin(n)[2:]

def convert_int_to_hexadecimal(n: int) -> str:
    """
    Convert an integer to a hexadecimal string.
    Args:
        n (int): The integer to convert.
    Returns:
        str: The hexadecimal representation of the integer.
    Raises:
        ValueError: If the input is a negative integer.
    """
    return hex(n)[2:]

def convert_int_to_octal(n: int) -> str:
    """
    Convert an integer to an octal string.
    Args:
        n (int): The integer to convert.
    Returns:
        str: The octal representation of the integer.
    Raises:
        ValueError: If the input is a negative integer.
    """
    return oct(n)[2:]

def convert_binary_to_int(binary: str) -> int:
    """
    Convert a binary string to an integer.
    Args:
        binary (str): The binary string to convert.
    Returns:
        int: The integer representation of the binary string.
    Raises:
        ValueError: If the input is not a valid binary string.
    """
    return int(binary, 2)   

def convert_hexadecimal_to_int(hexadecimal: str) -> int:
    """
    Convert a hexadecimal string to an integer.
    Args:
        hexadecimal (str): The hexadecimal string to convert.
    Returns:
        int: The integer representation of the hexadecimal string.
    Raises:
        ValueError: If the input is not a valid hexadecimal string.
    """
    return int(hexadecimal, 16)

def convert_octal_to_int(octal: str) -> int:
    """
    Convert an octal string to an integer.
    Args:
        octal (str): The octal string to convert.
    Returns:
        int: The integer representation of the octal string.
    Raises:
        ValueError: If the input is not a valid octal string.
    """
    return int(octal, 8)

def random_number(start: int, end: int) -> int:
    """
    Generate a random number within a specified range.
    Args:
        start (int): The start of the range.
        end (int): The end of the range.
    Returns:
        int: A random number within the specified range.
    Raises:
        ValueError: If either of the inputs is not an integer.
    """
    return random.randint(start, end)

def find_median(numbers: list) -> float:
    """
    Calculate the median of a list of numbers.
    Args:
        numbers (list): The list of numbers.
    Returns:
        float: The median of the list of numbers.
    Raises:
        ValueError: If the input is not a list of numbers.
    """
    numbers.sort()
    n = len(numbers)
    if n % 2 == 0:
        return (numbers[n // 2 - 1] + numbers[n // 2]) / 2
    else:
        return numbers[n // 2]
    
