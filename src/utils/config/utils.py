import logging
import os
import zipfile
import rarfile
from pathlib import Path
from typing import Optional

def get_log_level(level_str):
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    return levels.get(level_str.upper(), logging.ERROR)


def extract_compressed_file(file_path: str, extract_to: str) -> Optional[str]:
    """
    Extracts a ZIP or RAR file to the specified directory.
    
    Args:
        file_path (str): Path to the uploaded file.
        extract_to (str): Directory where the file should be extracted.
    
    Returns:
        Optional[str]: Path to the extracted folder or None if extraction fails.
    """
    extract_path = Path(extract_to)
    os.makedirs(extract_path, exist_ok=True)

    file_extension = Path(file_path).suffix.lower()
    
    try:
        # Extract based on file type
        if file_extension == ".zip":
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
        
        elif file_extension == ".rar":
            with rarfile.RarFile(file_path, 'r') as rar_ref:
                rar_ref.extractall(extract_path)
        
        else:
            return None  # Unsupported file type
        
        # Return path to extracted directory
        return str(extract_path)
    
    except Exception as e:
        print(f"Error extracting file: {str(e)}")  # Log errors
        return None
