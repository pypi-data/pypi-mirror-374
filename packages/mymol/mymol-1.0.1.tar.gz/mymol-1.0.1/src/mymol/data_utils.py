import json
import pickle

def hello(string: str) -> str:
    return f"Hello {string}!"

def convert_dict_to_json(data_dict):
    """
    Convert a dictionary to a JSON string.
    Args:
        data_dict (dict): The dictionary to convert to JSON format.
    Returns:
        str: The JSON string representation of the dictionary.

    Example:
        >>> data_dict = {"name": "Alice", "age": 25}
        >>> convert_dict_to_json(data_dict)
        '{"name": "Alice", "age": 25}'
    """
    return json.dumps(data_dict)

def load_json(json_str):
    """
    Load a JSON string and return the corresponding Python object.
    Args:
        json_str (str): A string containing JSON data.
    Returns:
        object: The Python object represented by the JSON string.
    Raises:
        json.JSONDecodeError: If the JSON string is not properly formatted.
    Example:
        >>> json_str = '{"name": "John", "age": 30}'
        >>> load_json(json_str)
        {'name': 'John', 'age': 30}
    """

    return json.loads(json_str)

def save_json(json_str, filename):
    """
    Save a JSON string to a file.

    Args:
        json_str (str): The JSON string to be saved.
        filename (str): The name of the file where the JSON string will be saved.

    Examples:
        >>> save_json('{"key": "value"}', 'data.json')
    """
    try:
        with open(filename, 'w') as file:
            file.write(json_str)
    except IOError as e:
        print(f"An error occurred while writing to the file {filename}: {e}")

def read_csv(filename):
    """
    Read a CSV file and return its contents as a list of dictionaries.
    Args:
        filename (str): The name of the CSV file to read.
    Returns:
        list: A list of dictionaries representing the rows in the CSV file.
    Example:
        >>> read_csv('data.csv')
        [{'name': 'Alice', 'age': '25'}, {'name': 'Bob', 'age': '30'}]
    """
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except IOError as e:
        print(f"An error occurred while reading the file {filename}: {e}")
        return []

    if not lines:
        return []

    header = lines[0].strip().split(',')
    data = []
    for line in lines[1:]:
        values = line.strip().split(',')
        row = dict(zip(header, values))
        data.append(row)

    return data

def write_csv(data, filename):
    """
    Write a list of dictionaries to a CSV file.
    Args:
        data (list): A list of dictionaries to write to the CSV file.
        filename (str): The name of the CSV file to write.
    Example:
        >>> data = [{'name': 'Alice', 'age': '25'}, {'name': 'Bob', 'age': '30'}]
        >>> write_csv(data, 'data.csv')
    """
    if not data:
        return

    header = ','.join(data[0].keys())
    rows = [','.join(row.values()) for row in data]

    try:
        with open(filename, 'w') as file:
            file.write(f"{header}\n")
            for row in rows:
                file.write(f"{row}\n")
    except IOError as e:
        print(f"An error occurred while writing to the file {filename}: {e}")

def serialize_object(obj, filename):
    """
    Serialize an object using pickle and save it to a file.
    Args:
        obj (object): The object to serialize.
        filename (str): The name of the file where the serialized object will be saved.
    Example:
        >>> data = {'name': 'Alice', 'age': 25}
        >>> serialize_object_with_pickle(data, 'data.pkl')
    """
    try:
        with open(filename, 'wb') as file:
            pickle.dump(obj, file)
    except IOError as e:
        print(f"An error occurred while writing to the file {filename}: {e}")

def deserialize_object(filename):
    """
    Deserialize an object from a file using pickle.
    Args:
        filename (str): The name of the file containing the serialized object.
    Returns:
        object: The deserialized object.
    Example:
        >>> deserialize_object_with_pickle('data.pkl')
        {'name': 'Alice', 'age': 25}
    """
    try:
        with open(filename, 'rb') as file:
            obj = pickle.load(file)
            return obj
    except IOError as e:
        print(f"An error occurred while reading the file {filename}: {e}")
        return None
    
def convert_xml_to_dict(xml_str):
    """
    Convert an XML string to a dictionary.
    Args:
        xml_str (str): A string containing XML data.
    Returns:
        dict: A dictionary representing the XML data.
    Example:
        >>> xml_str = '<data><name>Alice</name><age>25</age></data>'
        >>> convert_xml_to_dict(xml_str)
        {'data': {'name': 'Alice', 'age': '25'}}
    """
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        print("The xml.etree.ElementTree module is not available.")
        return {}

    root = ET.fromstring(xml_str)
    return convert_xml_to_dict(root)

def save_yaml_file(data, filename):
    """
    Save a dictionary to a YAML file.
    Args:
        data (dict): The dictionary to save to the YAML file.
        filename (str): The name of the file where the dictionary will be saved.
    Example:
        >>> data = {'name': 'Alice', 'age': 25}
        >>> save_yaml_file(data, 'data.yaml')
    """
    try:
        import yaml
    except ImportError:
        print("The PyYAML module is not available.")
        return

    with open(filename, 'w') as file:
        yaml.dump(data, file)

def load_yaml_file(filename):
    """
    Load a dictionary from a YAML file.
    Args:
        filename (str): The name of the YAML file to load.
    Returns:
        dict: The dictionary loaded from the YAML file.
    Example:
        >>> load_yaml_file('data.yaml')
        {'name': 'Alice', 'age': 25}
    """
    try:
        import yaml
    except ImportError:
        print("The PyYAML module is not available.")
        return {}

    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
        return data