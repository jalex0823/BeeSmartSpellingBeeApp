"""
Meshy API Integration Module
Handles communication with Meshy API for 3D model conversion and processing
"""

import os
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeshyAPIClient:
    """Client for interacting with Meshy API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.meshy.ai"):
        """
        Initialize Meshy API client
        
        Args:
            api_key: Meshy API key
            base_url: Base URL for Meshy API
        """
        self.api_key = api_key or os.getenv("MESHY_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
    
    def validate_api_key(self) -> bool:
        """
        Validate the API key by making a test request
        
        Returns:
            bool: True if API key is valid, False otherwise
        """
        if not self.api_key:
            logger.error("No API key provided")
            return False
        
        try:
            response = self.session.get(f"{self.base_url}/v1/models")
            return response.status_code in [200, 401]  # 401 means auth failed but endpoint exists
        except Exception as e:
            logger.error(f"API validation failed: {e}")
            return False
    
    def upload_3d_model(self, file_path: Path, model_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Upload a 3D model file to Meshy API
        
        Args:
            file_path: Path to the 3D model file
            model_name: Optional name for the model
            
        Returns:
            Dict containing upload response or None if failed
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        if not model_name:
            model_name = file_path.stem
        
        try:
            # Prepare file upload
            with open(file_path, 'rb') as file:
                files = {
                    'file': (file_path.name, file, 'application/octet-stream')
                }
                
                data = {
                    'name': model_name,
                    'format': file_path.suffix.lower().lstrip('.')
                }
                
                # Remove Content-Type header for file upload
                headers = self.session.headers.copy()
                if 'Content-Type' in headers:
                    del headers['Content-Type']
                
                response = self.session.post(
                    f"{self.base_url}/v1/models/upload",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully uploaded: {model_name}")
                    return result
                else:
                    logger.error(f"Upload failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return None
    
    def convert_model(self, model_id: str, target_format: str = "glb") -> Optional[Dict[str, Any]]:
        """
        Convert a 3D model to a target format
        
        Args:
            model_id: ID of the uploaded model
            target_format: Target format (glb, fbx, obj, etc.)
            
        Returns:
            Dict containing conversion job info or None if failed
        """
        try:
            data = {
                "model_id": model_id,
                "target_format": target_format,
                "optimization": "web"  # Optimize for web use
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/models/convert",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Conversion job started: {result.get('job_id', 'Unknown')}")
                return result
            else:
                logger.error(f"Conversion failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return None
    
    def get_conversion_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a conversion job
        
        Args:
            job_id: ID of the conversion job
            
        Returns:
            Dict containing job status or None if failed
        """
        try:
            response = self.session.get(f"{self.base_url}/v1/jobs/{job_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Status check failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return None
    
    def download_converted_model(self, job_id: str, output_path: Path) -> bool:
        """
        Download the converted model
        
        Args:
            job_id: ID of the completed conversion job
            output_path: Path where to save the downloaded file
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/v1/jobs/{job_id}/download")
            
            if response.status_code == 200:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Downloaded converted model: {output_path}")
                return True
            else:
                logger.error(f"Download failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False
    
    def wait_for_conversion(self, job_id: str, timeout: int = 300, poll_interval: int = 10) -> Optional[Dict[str, Any]]:
        """
        Wait for a conversion job to complete
        
        Args:
            job_id: ID of the conversion job
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
            
        Returns:
            Dict containing final job status or None if failed/timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_conversion_status(job_id)
            
            if not status:
                logger.error("Failed to get conversion status")
                return None
            
            job_status = status.get('status', '').lower()
            
            if job_status == 'completed':
                logger.info(f"Conversion completed: {job_id}")
                return status
            elif job_status in ['failed', 'error']:
                logger.error(f"Conversion failed: {status.get('error', 'Unknown error')}")
                return None
            elif job_status in ['pending', 'processing', 'running']:
                logger.info(f"Conversion in progress: {job_status}")
                time.sleep(poll_interval)
            else:
                logger.warning(f"Unknown status: {job_status}")
                time.sleep(poll_interval)
        
        logger.error(f"Conversion timeout after {timeout} seconds")
        return None
    
    def create_thumbnail(self, model_id: str, camera_angle: str = "isometric") -> Optional[Dict[str, Any]]:
        """
        Create a thumbnail/preview image of the 3D model
        
        Args:
            model_id: ID of the model
            camera_angle: Camera angle for the preview
            
        Returns:
            Dict containing thumbnail job info or None if failed
        """
        try:
            data = {
                "model_id": model_id,
                "camera_angle": camera_angle,
                "resolution": "1024x1024",
                "format": "png",
                "background": "transparent"
            }
            
            response = self.session.post(
                f"{self.base_url}/v1/models/thumbnail",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Thumbnail job started: {result.get('job_id', 'Unknown')}")
                return result
            else:
                logger.error(f"Thumbnail creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Thumbnail creation error: {e}")
            return None

class MeshyModelProcessor:
    """High-level processor for working with Meshy API"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the processor
        
        Args:
            api_key: Meshy API key
        """
        self.client = MeshyAPIClient(api_key)
        self.processed_models: List[Dict[str, Any]] = []
    
    def process_obj_file(self, obj_path: Path, output_dir: Path, 
                        create_thumbnail: bool = True) -> Optional[Dict[str, Any]]:
        """
        Process an OBJ file through Meshy API
        
        Args:
            obj_path: Path to the OBJ file
            output_dir: Directory to save processed files
            create_thumbnail: Whether to create a thumbnail
            
        Returns:
            Dict containing processing results or None if failed
        """
        if not self.client.validate_api_key():
            logger.error("Invalid API key")
            return None
        
        model_name = obj_path.stem
        logger.info(f"Processing model: {model_name}")
        
        # Upload the model
        upload_result = self.client.upload_3d_model(obj_path, model_name)
        if not upload_result:
            return None
        
        model_id = upload_result.get('model_id')
        if not model_id:
            logger.error("No model ID in upload response")
            return None
        
        result = {
            'original_file': str(obj_path),
            'model_name': model_name,
            'model_id': model_id,
            'upload_result': upload_result,
            'conversions': {},
            'thumbnails': {}
        }
        
        # Convert to GLB format (good for web use)
        conversion_result = self.client.convert_model(model_id, "glb")
        if conversion_result:
            job_id = conversion_result.get('job_id')
            if job_id:
                # Wait for conversion
                final_status = self.client.wait_for_conversion(job_id)
                if final_status:
                    # Download converted file
                    glb_path = output_dir / f"{model_name}.glb"
                    if self.client.download_converted_model(job_id, glb_path):
                        result['conversions']['glb'] = {
                            'job_id': job_id,
                            'file_path': str(glb_path),
                            'status': 'completed'
                        }
        
        # Create thumbnail if requested
        if create_thumbnail:
            thumbnail_result = self.client.create_thumbnail(model_id)
            if thumbnail_result:
                thumb_job_id = thumbnail_result.get('job_id')
                if thumb_job_id:
                    # Wait for thumbnail
                    thumb_status = self.client.wait_for_conversion(thumb_job_id)
                    if thumb_status:
                        # Download thumbnail with ! in filename
                        thumb_path = output_dir / f"{model_name}!.png"
                        if self.client.download_converted_model(thumb_job_id, thumb_path):
                            result['thumbnails']['main'] = {
                                'job_id': thumb_job_id,
                                'file_path': str(thumb_path),
                                'status': 'completed'
                            }
        
        self.processed_models.append(result)
        return result
    
    def batch_process_folder(self, input_folder: Path, output_folder: Path) -> List[Dict[str, Any]]:
        """
        Process all OBJ files in a folder
        
        Args:
            input_folder: Folder containing OBJ files
            output_folder: Folder to save processed files
            
        Returns:
            List of processing results
        """
        obj_files = list(input_folder.glob("*.obj"))
        results = []
        
        if not obj_files:
            logger.warning(f"No OBJ files found in {input_folder}")
            return results
        
        logger.info(f"Found {len(obj_files)} OBJ files to process")
        
        for obj_file in obj_files:
            logger.info(f"Processing {obj_file.name}...")
            result = self.process_obj_file(obj_file, output_folder)
            if result:
                results.append(result)
            else:
                logger.error(f"Failed to process {obj_file.name}")
        
        return results
    
    def get_railway_ready_files(self, output_folder: Path) -> Dict[str, List[Path]]:
        """
        Get list of files ready for Railway deployment
        
        Args:
            output_folder: Folder containing processed files
            
        Returns:
            Dict categorizing files for Railway use
        """
        railway_files = {
            'models': [],
            'thumbnails': [],
            'supporting_files': []
        }
        
        # GLB files for 3D models
        railway_files['models'] = list(output_folder.glob("*.glb"))
        
        # PNG files with ! for thumbnails
        railway_files['thumbnails'] = list(output_folder.glob("*!.png"))
        
        # Other supporting files
        for ext in ['.mtl', '.jpg', '.jpeg', '.png']:
            if ext != '.png' or not any('!' in f.name for f in output_folder.glob(f"*{ext}")):
                railway_files['supporting_files'].extend(output_folder.glob(f"*{ext}"))
        
        return railway_files


def test_meshy_integration():
    """Test function to verify Meshy API integration"""
    # This would be used for testing the integration
    api_key = "msy_t9FYfPHBWK1c8VBfX0pLxnEZMdWbg0DEc2qz"
    
    client = MeshyAPIClient(api_key)
    
    print("Testing API key validation...")
    if client.validate_api_key():
        print("✅ API key is valid")
    else:
        print("❌ API key validation failed")
    
    # Additional tests would go here
    return client.validate_api_key()


if __name__ == "__main__":
    test_meshy_integration()