"""
File handling for document upload and search using xAI Files API
"""

import os
from typing import Optional, List
from openai import OpenAI


class FileHandler:
    """Handle file uploads and document search using xAI Files API"""
    
    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY")
        if not self.api_key:
            raise ValueError("XAI_API_KEY not found in environment variables")
        
        # xAI Files API uses OpenAI-compatible client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )
        self.uploaded_files: List[str] = []  # Store file IDs
    
    def upload_file(self, file_path: str, purpose: str = "assistants") -> Optional[str]:
        """
        Upload a file to xAI Files API
        
        Args:
            file_path: Path to the file to upload
            purpose: Purpose of the file (default: "assistants")
        
        Returns:
            File ID if successful, None otherwise
        """
        try:
            with open(file_path, "rb") as file:
                response = self.client.files.create(
                    file=file,
                    purpose=purpose
                )
                file_id = response.id
                self.uploaded_files.append(file_id)
                return file_id
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return None
    
    def upload_file_content(self, content: bytes, filename: str, purpose: str = "assistants") -> Optional[str]:
        """
        Upload file content directly
        
        Args:
            content: File content as bytes
            filename: Name of the file
            purpose: Purpose of the file
        
        Returns:
            File ID if successful, None otherwise
        """
        try:
            # Create a temporary file-like object
            from io import BytesIO
            file_obj = BytesIO(content)
            file_obj.name = filename
            
            response = self.client.files.create(
                file=file_obj,
                purpose=purpose
            )
            file_id = response.id
            self.uploaded_files.append(file_id)
            return file_id
        except Exception as e:
            print(f"Error uploading file content: {str(e)}")
            return None
    
    def get_file_content(self, file_id: str) -> Optional[str]:
        """
        Retrieve content from an uploaded file
        
        Args:
            file_id: ID of the file
        
        Returns:
            File content as string, None if error
        """
        try:
            response = self.client.files.content(file_id)
            return response.read().decode('utf-8')
        except Exception as e:
            print(f"Error retrieving file content: {str(e)}")
            return None
    
    def list_files(self) -> List[dict]:
        """List all uploaded files"""
        try:
            response = self.client.files.list()
            return [{"id": f.id, "filename": f.filename, "purpose": f.purpose} for f in response.data]
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """Delete an uploaded file"""
        try:
            self.client.files.delete(file_id)
            if file_id in self.uploaded_files:
                self.uploaded_files.remove(file_id)
            return True
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

