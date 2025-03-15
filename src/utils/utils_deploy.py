import os
import zipfile
import rarfile
from pathlib import Path
from typing import Optional, Dict
import json
import zipfile


def download_extract_file(s3_client, event_dict: Dict, local_download_path: str, extract_path: str) -> Optional[str]:
    try:
        # Extract S3 bucket and object key from the event
        print("Received event:", json.dumps(event_dict, indent=2))
        
        print(f"Downloading from S3")
        # download_file_from_s3(s3_client=s3_client, event_dict = event_dict, local_path = local_download_path)

        print("Download complete. Extracting...")
        extract_compressed_file(local_download_path, extract_path)

        print(f"Extraction complete. Files extracted to: {extract_path}")

        return {
            "statusCode": 200,
            "body": f"ZIP file extracted to {extract_path}"
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": f"Failed to process file: {str(e)}"
        }

def download_file_from_s3(s3_client, event_dict: Dict, local_path: str) -> bool:
        # Extract S3 bucket and object key from the event
        s3_bucket = event_dict["detail"]["bucket"]["name"]
        s3_object_key = event_dict["detail"]["object"]["key"]
        
        s3_client.download_file(s3_bucket, s3_object_key, local_path)


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
    extract_path.mkdir(parents=True, exist_ok=True)

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
            raise ValueError("Unsupported file type")
        
        # Return path to extracted directory
        return str(extract_path)
    
    except Exception as e:
        print(f"Error extracting file: {str(e)}")  
        return None