import os

def read_file(file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The contents of the file.

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If there's an issue reading the file.

    Example:
        >>> content = read_file('example.txt')
        >>> print(content)
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file: {e}")
    
def write_file(file_path: str, content: str):
    """
    Write content to a file.

    Args:
        file_path (str): The path to the file.
        content (str): The content to write to the file.

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If there's an issue writing to the file.

    Example:
        >>> write_file('example.txt', 'Hello, World!')
    """
    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while writing to the file: {e}")
    
def append_file(file_path: str, content: str):
    """
    Append content to a file.

    Args:
        file_path (str): The path to the file.
        content (str): The content to append to the file.

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If there's an issue appending to the file.

    Example:
        >>> append_file('example.txt', 'Hello, World!')
    """
    try:
        with open(file_path, 'a') as file:
            file.write(content)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while appending to the file: {e}")
    
def delete_file(file_path: str):
    """
    Delete a file.

    Args:
        file_path (str): The path to the file.

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If there's an issue deleting the file.

    Example:
        >>> delete_file('example.txt')
    """
    try:
        os.remove(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while deleting the file: {e}")
    
def list_files(directory: str) -> list:
    """
    List all files in a directory.

    Args:
        directory (str): The path to the directory.

    Returns:
        list: A list of files in the directory.

    Raises:
        FileNotFoundError: If the directory is not found.
        Exception: If there's an issue listing the files.

    Example:
        >>> files = list_files('/path/to/directory')
        >>> print(files)
    """
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except FileNotFoundError:
        raise FileNotFoundError(f"The directory '{directory}' was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while listing files in the directory: {e}")
    
def check_file_exists(file_path: str) -> bool:
    """
    Check if a file exists.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file exists, False otherwise.

    Example:
        >>> file_exists = check_file_exists('example.txt')
        >>> print(file_exists)
    """
    return os.path.exists(file_path)

def copy_file(source_path: str, destination_path: str):
    """
    Copy a file from the source path to the destination path.

    Args:
        source_path (str): The path to the source file.
        destination_path (str): The path to the destination file.

    Raises:
        FileNotFoundError: If the source file is not found.
        Exception: If there's an issue copying the file.
    
    Example:
        >>> copy_file('source.txt', 'destination.txt')
    """
    try:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"The source file '{source_path}' was not found.")
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with open(source_path, 'r') as source_file:
            with open(destination_path, 'w') as dest_file:
                dest_file.write(source_file.read())
    except Exception as e:
        raise Exception(f"An error occurred while copying the file: {e}")
    
def move_file(source_path: str, destination_path: str):
    """
    Move a file from the source path to the destination path.

    Args:
        source_path (str): The path to the source file.
        destination_path (str): The path to the destination file.

    Raises:
        FileNotFoundError: If the source file is not found.
        Exception: If there's an issue moving the file.

    Example:
        >>> move_file('source.txt', 'destination.txt')
    """
    try:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"The source file '{source_path}' was not found.")
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        os.rename(source_path, destination_path)
    except Exception as e:
        raise Exception(f"An error occurred while moving the file: {e}")
    
def rename_file(file_path: str, new_name: str):
    """
    Rename a file.

    Args:
        file_path (str): The path to the file.
        new_name (str): The new name for the file.

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If there's an issue renaming the file.

    Example:
        >>> rename_file('example.txt', 'new_example.txt')
    """
    try:
        os.rename(file_path, os.path.join(os.path.dirname(file_path), new_name))
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while renaming the file: {e}")
    
def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.

    Args:
        file_path (str): The path to the file.

    Returns:
        int: The size of the file in bytes.

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If there's an issue getting the file size.

    Example:
        >>> size = get_file_size('example.txt')
        >>> print(size)
    """
    try:
        return os.path.getsize(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while getting the file size: {e}")  
    
def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The extension of the file.

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If there's an issue getting the file extension.

    Example:
        >>> get_file_extension('/path/to/file.txt')
        '.txt'
    """
    try:
        return os.path.splitext(file_path)[1]
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while getting the file extension: {e}")
    
