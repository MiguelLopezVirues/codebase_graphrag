import zipfile
import rarfile
import os
from pathlib import Path
import streamlit as st

def unzip_project():

    """
    Unzips a ZIP or RAR file uploaded through Streamlit's file uploader.
    The function extracts the contents to a specified location.
    """
    # Get the uploaded file from session state
    uploaded_file = st.session_state.codebase_project
    
    if uploaded_file is not None:
        extract_path = Path("./extracted_files")
        
        extract_path.mkdir(parents=True, exist_ok=True)
        
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        try:
            # Write the uploaded file to a temporary location
            temp_path = Path(f"./temp_{uploaded_file.name}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Extract based on file type
            if file_extension == ".zip":
                with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                st.success(f"ZIP file successfully extracted to {extract_path}")
            
            elif file_extension == ".rar":
                with rarfile.RarFile(temp_path, 'r') as rar_ref:
                    rar_ref.extractall(extract_path)
                st.success(f"RAR file successfully extracted to {extract_path}")
            
            else:
                st.error("Unsupported file format. Please upload a ZIP or RAR file.")

            # Clean up the temporary file
            os.remove(temp_path)

            # Get path to extracted file
            st.session_state.extracted_path = str(next(Path(extract_path).iterdir(), None))
            
            return extract_path
            
        except Exception as e:
            st.error(f"Error extracting file: {str(e)}")