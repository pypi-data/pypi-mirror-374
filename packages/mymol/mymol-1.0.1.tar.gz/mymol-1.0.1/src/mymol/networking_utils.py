import requests
import os
import socket
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def ping_url(url):
    """
    Check if a URL is reachable by sending a GET request.

    Args:
        url (str): The URL to ping.

    Returns:
        bool: True if the URL is reachable (status code 200), False otherwise.

    Examples:
        >>> ping_url("https://www.example.com")
        True
        >>> ping_url("https://www.nonexistentwebsite.com")
        False
    """
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
    
def get_public_ip():
    """
    Get the public IP address of the machine.

    Returns:
        str: The public IP address of the machine.

    Examples:
        >>> get_public_ip()
        '192.0.2.1'
    """
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        return response.json()['ip']
    except requests.exceptions.RequestException:
        return None
    
def download_file(url, filename):
    """
    Download a file from a URL and save it to the local filesystem in the Downloads  folder.

    Args:
        url (str): The URL of the file to download.
        filename (str): The name of the file to save the contents to.

    Returns:
        bool: True if the file was downloaded successfully, False otherwise.

    Examples:
        >>> download_file("https://www.example.com/file.txt", "file.txt")
        True
        >>> download_file("https://www.nonexistentwebsite.com/file.txt", "file.txt")
        False
    """
    downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)
    
    file_path = os.path.join(downloads_folder, filename)
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, 'wb') as file:
            file.write(response.content)
        return True
    except requests.exceptions.RequestException:
        return False
    
def check_internet_connection():
    """
    Check if the machine has an active internet connection.

    Returns:
        bool: True if the machine has an active internet connection, False otherwise.

    Examples:
        >>> check_internet_connection()
        True
    """
    return ping_url('https://www.google.com')

def fetch_json_from_API(url):
    """
    Fetch JSON data from an API endpoint.

    Args:
        url (str): The URL of the API endpoint.

    Returns:
        dict: The JSON data returned by the API.

    Examples:
        >>> fetch_json_from_API("https://jsonplaceholder.typicode.com/posts/1")
        {'userId': 1, 'id': 1, 'title': 'sunt aut facere repellat provident occaecati excepturi optio reprehenderit', 'body': 'quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto'}
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None
    
def get_hostname():
    """
    Get the hostname of the machine.

    Returns:
        str: The hostname of the machine.

    Examples:
        >>> get_hostname()
        'mymachine'
    """
    return os.uname().nodename

def get_local_ip():
    """
    Get the local IP address of the machine.

    Returns:
        str: The local IP address of the machine.

    Examples:
        >>> get_local_ip()
        '192.168.1.2'
    """
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

def resolve_hostname(hostname):
    """
    Resolve the IP address of a hostname.

    Args:
        hostname (str): The hostname to resolve.

    Returns:
        str: The IP address of the hostname.

    Examples:
        >>> resolve_hostname('www.example.com')
        '93.184.216.34'
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.error:
        return None
    
def get_open_ports(hostname):
    """
    Get a list of open ports on a hostname.

    Args:
        hostname (str): The hostname to scan for open ports.

    Returns:
        list: A list of open ports on the hostname.

    Examples:
        >>> get_open_ports('www.example.com')
        [80, 443]
    """
    open_ports = []
    for port in range(1, 1025):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((hostname, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports

def send_email(sender, recipient, subject, body, smtp_server, smtp_port, smtp_user, smtp_password):
    """
    Send an email from one address to another.

    Args:
        sender (str): The email address of the sender.
        recipient (str): The email address of the recipient.
        subject (str): The subject of the email.
        body (str): The body of the email.
        smtp_server (str): The SMTP server address.
        smtp_port (int): The SMTP server port.
        smtp_user (str): The SMTP server username.
        smtp_password (str): The SMTP server password.

    Returns:
        bool: True if the email was sent successfully, False otherwise.

    Examples:
        >>> send_email('sender@example.com', 'recipient@example.com', 'Subject', 'Email body', 'smtp.example.com', 587, 'smtp_user', 'smtp_password')
        True
    """

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender, recipient, msg.as_string())
        return True
    except smtplib.SMTPException:
        return False