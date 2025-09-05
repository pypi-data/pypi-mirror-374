import os
import csv
from datetime import datetime
import qrcode
import numpy as np
import matplotlib.pyplot as plt

def generate_timestamp():
    """
    Produces a timestamp in the form YYYY_MM-DD_hh_mm

    Returns:
        timestamp : str

    """
    return datetime.now().strftime("%Y_%m_%d_%H_%M")

def folder_create(path) -> None:
    """
    Creates the folder (including all intermediate directories) if it doesn't exist.

    Parameters:
        path (str): Directory path to create.

    Returns:
        None

    Raises:
        OSError: If the directory cannot be created due to permissions or invalid path.
    """
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        raise OSError(f"Could not create directory '{path}': {e}")

def folder_create_structure(base_path, structure: dict) -> None:
    """
    Recursively creates nested folder structures from a dictionary.

    Parameters:
        base_path (str): Base directory under which folders will be created.
        structure (dict): Nested dictionary representing folder structure.
            Keys are folder names, values are subfolder dicts or None.

    Returns:
        None

    Example:
        structure = {
            'A': {'1': None, '2': None},
            'B': {'1': None},
            'C': {'1': None, '2': None, '3': None}
        }
        folder_create_structure('root_folder', structure)
    """
    for folder, subfolders in structure.items():
        current_path = os.path.join(base_path, folder)
        folder_create(current_path)
        if isinstance(subfolders, dict):
            folder_create_structure(current_path, subfolders)

def file_check(filename, path=None):
    """
    Check if a file exists at a specified location.

    Parameters:
        filename (str): The name of the file to check (e.g., 'data.csv' or 'report.txt').
        path (str, optional): The directory path where the file should be located.
            If None, defaults to the directory of the current script.

    Returns:
        bool: True if the file exists at the resolved location, False otherwise.
    """
    directory = path or os.getcwd()
    folder_create(directory)  # ensure the directory exists
    file_path = os.path.join(directory, filename)
    return os.path.isfile(file_path)

def csv_create(filename, header, path=None):
    """
    Create a CSV file with the given filename and header row, if it doesn't already exist.

    Parameters:
        filename (str): The name of the CSV file to create (e.g., 'data.csv').
        header (list): A list of column names to write as the header row.
        path (str, optional): The directory path where the file should be created.
            If None, defaults to the directory of the current script.

    Returns:
        str: The full path to the CSV file.
    """
    
    directory = path or os.getcwd()
    folder_create(directory)  # ensure the directory exists
    
    file_path = os.path.join(directory, filename)

    if file_check(filename, path):
        print(f"[Info] CSV file already exists: {file_path}")
        return file_path

    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)

    print(f"[Success] CSV file created: {file_path}")
    return file_path

def csv_append_row(filename, row, path=None):
    """
    Append a single row of data to an existing CSV file.

    Parameters:
        filename (str): The name of the CSV file where the row should be appended.
        row (list): A list of values representing a single row to add to the file.
            The order and number of values should match the existing CSV header.
        path (str, optional): The directory path where the file is located.
            If None, defaults to the directory of the current script.

    Returns:
        None

    Notes:
        - If the file does not exist, this function will raise a FileNotFoundError.
        - Data is appended at the end of the file without modifying existing contents.
        - It is the caller’s responsibility to ensure the row structure matches the CSV.
    """
    directory = path or os.getcwd()
    file_path = os.path.join(directory, filename)

    with open(file_path, mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def csv_append_data(filename, data, path=None):
    """
    Append multiple rows of data to an existing CSV file.

    Parameters:
        filename (str): The name of the CSV file where the data should be appended.
        data (list of list): A list of rows, where each row is a list of values.
            Each row should match the column structure of the existing CSV file.
        path (str, optional): The directory path where the file is located.
            If None, defaults to the directory of the current script.

    Returns:
        None

    Notes:
        - If the file does not exist, this function will raise a FileNotFoundError.
        - All rows in 'data' are appended in the order they appear in the list.
        - It is the caller’s responsibility to ensure each row has the correct format.
    """
    directory = path or os.getcwd()
    file_path = os.path.join(directory, filename)

    with open(file_path, mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def csv_open(filename, path=None):
    """
    Open and read the contents of a CSV file, returning all rows as a list.

    Parameters:
        filename (str): The name of the CSV file to open and read.
        path (str, optional): The directory path where the file is located.
            If None, defaults to the directory of the current script.

    Returns:
        list: A list of rows from the CSV file, where each row is a list of string values.

    Notes:
        - If the file does not exist, this function will raise a FileNotFoundError.
        - The entire contents of the CSV are loaded into memory.
        - Prints the contents to the terminal row by row.
    """
    directory = path or os.getcwd()
    file_path = os.path.join(directory, filename)

    with open(file_path, mode="r", newline='') as file:
        reader = csv.reader(file)
        contents = list(reader)

    print(f"Opened '{file_path}':")

    return contents

def markdown_write(text, filename, path=None) -> None:
    """
    Write the given markdown content to a file (overwrites if exists).

    Accepts either a string or a list of strings/tuples to format and write.

    Parameters:
        text (str | list): Markdown content to write.
            - If a string, writes it directly.
            - If a list of (name, description) tuples, formats as markdown.
            - If a list of strings, writes each string followed by a newline.
        filename (str): Name of the markdown file (e.g., 'README.md').
        path (str, optional): Directory path where the file will be saved.
            If None, uses the current directory.

    Returns:
        None
    """

    directory = path or os.getcwd()
    folder_create(directory)  # ensure folder exists
    output_path = os.path.join(directory, filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        if isinstance(text, str):
            f.write(text)
        elif isinstance(text, list):
            for item in text:
                if isinstance(item, tuple) and len(item) == 2:
                    name, doc = item
                    f.write(f"## `{name}`\n\n{doc.strip()}\n\n")
                elif isinstance(item, str):
                    f.write(f"{item}\n")
                else:
                    raise ValueError("Unsupported item type in list passed to markdown_write.")
        else:
            raise TypeError("markdown_write expects a string or a list.")

def markdown_append(text, filename, path=None) -> None:
    """
    Append the given markdown text to a file (creates file if it doesn't exist).
    
    Accepts either a string or a list of strings/tuples to format and write.
    
    Parameters:
        text (str | list): Markdown content to append.
            - If a string, writes it directly.
            - If a list of (name, description) tuples, formats as markdown.
            - If a list of strings, writes each string followed by a newline.
        filename (str): Name of the markdown file (e.g., 'README.md').
        path (str, optional): Directory path where the file will be saved.
            If None, uses the current directory.

    Returns:
        None
    """

    directory = path or os.getcwd()
    folder_create(directory)  # ensure folder exists
    output_path = os.path.join(directory, filename)

    with open(output_path, 'a', encoding='utf-8') as f:
        if isinstance(text, str):
            f.write(text)
        elif isinstance(text, list):
            for item in text:
                if isinstance(item, tuple) and len(item) == 2:
                    name, doc = item
                    f.write(f"## `{name}`\n\n{doc.strip()}\n\n")
                elif isinstance(item, str):
                    f.write(f"{item}\n")
                else:
                    raise ValueError("Unsupported item type in list passed to markdown_append.")
        else:
            raise TypeError("markdown_append expects a string or a list.")

def QR_generate(
    data,
    filename="qrcode.png",
    path=".",
    box_size=10,
    border=4,
    colorSquare="black",
    colorBackground="white",
    plotQR=False
):
    """
    Generates a QR code image, saves it to a specified directory, displays a coordinate plot, 
    and returns the binary matrix representing the QR code.

    Creates the folder (including all intermediate directories) if it doesn't exist.

    Parameters:
        data (str): The text or URL to encode in the QR code.
        filename (str): The name of the output PNG file.
        path (str): Directory path to save the QR code image.
        box_size (int): The size of each box in the QR code.
        border (int): The thickness of the border around the QR code.
        colorSquare (str): The color of the QR code squares (default: "black").
        colorBackground (str): The background color of the QR code (default: "white").
        plotQR (bool): If true, will plot the resulting QR code

    Returns:
        np.ndarray: 2D NumPy array where 1 represents a colored square and 0 represents background.

    Raises:
        OSError: If the directory cannot be created due to permissions or invalid path.
    """


    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    
    qr.add_data(data)
    qr.make(fit=True)

    # Create and save QR code image with custom colors
    img = qr.make_image(fill_color=colorSquare, back_color=colorBackground)
    
    # Ensure directory exists
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, filename)
    img.save(full_path)
    print(f"QR Code saved as '{full_path}'")

    # Convert QR code to NumPy array (1 for colorSquare, 0 for colorBackground)
    qr_matrix = np.array(qr.modules).astype(int)

    # Extract black box coordinates for plotting
    coordinates = [(x, y) for y, row in enumerate(qr_matrix) for x, value in enumerate(row) if value == 1]
    
    # Plot QR Code
    if plotQR:
        plt.figure(figsize=(6, 6))
        plt.imshow(qr_matrix, cmap='gray_r', interpolation='none')  # Always black on white
        plt.axis("off")
        plt.title(data)
        plt.show()




if __name__ == "__main__":
    csv_append_data("www.google.com")
