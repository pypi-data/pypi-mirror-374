def find_max_list(lst):
    """
    Find the maximum value in a list.

    Args:
        lst (list): A list of numerical values.

    Returns:
        int or float: The maximum value in the list.

    Examples:
        >>> find_max_list([1, 2, 3, 4, 5])
        5
        >>> find_max_list([-1, -2, -3, -4, -5])
        -1
    """
    max_val = lst[0]
    for val in lst:
        if val > max_val:
            max_val = val
    return max_val

def find_min_list(lst):
    """
    Find the minimum value in a list.

    Args:
        lst (list): A list of numerical values.

    Returns:
        int or float: The minimum value in the list.

    Examples:
        >>> find_min_list([1, 2, 3, 4, 5])
        1
        >>> find_min_list([-1, -2, -3, -4, -5])
        -5
    """
    min_val = lst[0]
    for val in lst:
        if val < min_val:
            min_val = val
    return min_val

def sort_list(lst, reverse=False):
    """
    Sort a list in ascending or descending order.

    Args:
        lst (list): A list of numerical values.
        reverse (bool): If True, sort the list in descending order. Default is False.

    Returns:
        list: The sorted list.

    Examples:
        >>> sort_list([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])
        [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]
        >>> sort_list([9, 8, 7, 6, 5, 4, 3, 2, 1])
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> sort_list([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], reverse=True)
        [9, 6, 5, 5, 5, 4, 3, 3, 2, 1, 1]
    """
    return sorted(lst, reverse=reverse)

def remove_duplicates_list(lst):
    """
    Remove duplicates from a list.

    Args:
        lst (list): A list of values.

    Returns:
        list: A list with duplicates removed.

    Examples:
        >>> remove_duplicates_list([1, 2, 3, 2, 1, 4, 5, 4, 6])
        [1, 2, 3, 4, 5, 6]
        >>> remove_duplicates_list([1, 2, 3, 4, 5, 6])
        [1, 2, 3, 4, 5, 6]
    """
    return list(set(lst))

def merge_dicts(dict1, dict2):
    """
    Merge two dictionaries.

    Args:
        dict1 (dict): The first dictionary.
        dict2 (dict): The second dictionary.

    Returns:
        dict: The merged dictionary.

    Examples:
        >>> merge_dicts({"a": 1, "b": 2}, {"b": 3, "c": 4})
        {'a': 1, 'b': 3, 'c': 4}
        >>> merge_dicts({"a": 1, "b": 2}, {"c": 3, "d": 4})
        {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    """
    return {**dict1, **dict2}

def invert_dict(d):
    """
    Invert a dictionary.

    Args:
        d (dict): The dictionary to invert.

    Returns:
        dict: The inverted dictionary.

    Examples:
        >>> invert_dict({"a": 1, "b": 2, "c": 3})
        {1: 'a', 2: 'b', 3: 'c'}
        >>> invert_dict({"a": 1, "b": 1, "c": 1})
        {1: 'c'}
    """
    return {v: k for k, v in d.items()}

def get_dict_keys(d):
    """
    Get the keys of a dictionary.

    Args:
        d (dict): The dictionary.

    Returns:
        list: A list of keys.

    Examples:
        >>> get_dict_keys({"a": 1, "b": 2, "c": 3})
        ['a', 'b', 'c']
        >>> get_dict_keys({"a": 1, "b": 1, "c": 1})
        ['a', 'b', 'c']
    """
    return list(d.keys())

def get_dict_values(d):
    """
    Get the values of a dictionary.

    Args:
        d (dict): The dictionary.

    Returns:
        list: A list of values.

    Examples:
        >>> get_dict_values({"a": 1, "b": 2, "c": 3})
        [1, 2, 3]
        >>> get_dict_values({"a": 1, "b": 1, "c": 1})
        [1, 1, 1]
    """
    return list(d.values())

def check_key_dict(d, key):
    """
    Check if a key exists in a dictionary.

    Args:
        d (dict): The dictionary.
        key (str): The key to check.

    Returns:
        bool: True if the key exists, False otherwise.

    Examples:
        >>> check_key_dict({"a": 1, "b": 2, "c": 3}, "b")
        True
        >>> check_key_dict({"a": 1, "b": 2, "c": 3}, "d")
        False
    """
    return key in d