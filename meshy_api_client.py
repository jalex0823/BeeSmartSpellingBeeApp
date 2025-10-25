"""
Meshy API Client for 3D Model Processing
Handles communication with Meshy.ai for OBJ file conversion and processing
"""

import os
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MeshyTask:
    """Represents a Meshy API task"""
    task_id: str
    task_type: str
    status: str
    progress: int = 0
    result_urls: Optional[List[str]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.result_urls is None:
            self.result_urls = []

class MeshyAPIClient:
    """Client for interacting with Meshy.ai API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.meshy.ai"):
        """
        Initialize Meshy API client
        
        Args:
            api_key: Your Meshy API key
            base_url: Base URL for Meshy API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def upload_file(self, file_path: Path) -> Optional[str]:
        """
        Upload a file to Meshy for processing
        
        Args:
            file_path: Path to the OBJ file to upload
            
        Returns:
            Upload URL or None if failed
        """
        try:
            # First, get upload URL
            upload_response = self.session.post(f"{self.base_url}/v1/file-upload")
            upload_response.raise_for_status()
            upload_data = upload_response.json()
            
            upload_url = upload_data.get('upload_url')
            if not upload_url:
                logger.error("No upload URL received from Meshy")
                return None
            
            # Upload the file
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                upload_result = requests.post(upload_url, files=files)
                upload_result.raise_for_status()
            
            logger.info(f"Successfully uploaded {file_path.name}")
            return upload_data.get('file_id')
            
        except Exception as e:
            logger.error(f"Failed to upload {file_path}: {e}")
            return None
    
    def create_texture_task(self, file_id: str, style_prompt: str = "high quality, detailed textures") -> Optional[MeshyTask]:
        """
        Create a texture generation task
        
        Args:
            file_id: ID of uploaded file
            style_prompt: Style description for texture generation
            
        Returns:
            MeshyTask object or None if failed
        """
        try:
            payload = {
                "mode": "preview",
                "file_id": file_id,
                "style_prompt": style_prompt,
                "art_style": "realistic",
                "negative_prompt": "low quality, blurry, distorted"
            }
            
            response = self.session.post(f"{self.base_url}/v2/text-to-texture", json=payload)
            response.raise_for_status()
            result = response.json()
            
            task = MeshyTask(
                task_id=result.get('result'),
                task_type='texture',
                status='PENDING'
            )
            
            logger.info(f"Created texture task: {task.task_id}")
            return task
            
        except Exception as e:
            logger.error(f"Failed to create texture task: {e}")
            return None
    
    def create_refine_task(self, file_id: str) -> Optional[MeshyTask]:
        """
        Create a mesh refinement task
        
        Args:
            file_id: ID of uploaded file
            
        Returns:
            MeshyTask object or None if failed
        """
        try:
            payload = {
                "mode": "refine",
                "file_id": file_id
            }
            
            response = self.session.post(f"{self.base_url}/v1/text-to-3d", json=payload)
            response.raise_for_status()
            result = response.json()
            
            task = MeshyTask(
                task_id=result.get('result'),
                task_type='refine',
                status='PENDING'
            )
            
            logger.info(f"Created refine task: {task.task_id}")
            return task
            
        except Exception as e:
            logger.error(f"Failed to create refine task: {e}")
            return None
    
    def get_task_status(self, task: MeshyTask) -> MeshyTask:
        """
        Get the current status of a task
        
        Args:
            task: MeshyTask object to check
            
        Returns:
            Updated MeshyTask object
        """
        try:
            if task.task_type == 'texture':
                endpoint = f"{self.base_url}/v2/text-to-texture/{task.task_id}"
            else:
                endpoint = f"{self.base_url}/v1/text-to-3d/{task.task_id}"
            
            response = self.session.get(endpoint)
            response.raise_for_status()
            result = response.json()
            
            task.status = result.get('status', 'UNKNOWN')
            task.progress = result.get('progress', 0)
            
            if task.status == 'SUCCEEDED':
                if task.task_type == 'texture':
                    task.result_urls = [result.get('model_url', '')]
                else:
                    task.result_urls = [
                        result.get('model_url', ''),
                        result.get('thumbnail_url', '')
                    ]
            elif task.status == 'FAILED':
                task.error_message = result.get('error', 'Unknown error')
            
            return task
            
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            task.error_message = str(e)
            return task
    
    def wait_for_completion(self, task: MeshyTask, timeout: int = 300, poll_interval: int = 10) -> MeshyTask:
        """
        Wait for a task to complete
        
        Args:
            task: MeshyTask to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
            
        Returns:
            Updated MeshyTask object
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task = self.get_task_status(task)
            
            if task.status in ['SUCCEEDED', 'FAILED']:
                break
            
            logger.info(f"Task {task.task_id} status: {task.status} ({task.progress}%)")
            time.sleep(poll_interval)
        
        if task.status not in ['SUCCEEDED', 'FAILED']:
            task.status = 'TIMEOUT'
            task.error_message = f"Task did not complete within {timeout} seconds"
        
        return task
    
    def download_result(self, url: str, output_path: Path) -> bool:
        """
        Download a result file from Meshy
        
        Args:
            url: URL to download from
            output_path: Where to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded result to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return False
    
    def process_obj_file(self, obj_path: Path, output_dir: Path, 
                        style_prompt: str = "high quality, detailed textures") -> Dict[str, Any]:
        """
        Complete workflow: upload OBJ, create tasks, wait for completion, download results
        
        Args:
            obj_path: Path to OBJ file to process
            output_dir: Directory to save results
            style_prompt: Style description for texture generation
            
        Returns:
            Dictionary with processing results
        """
        results = {
            'success': False,
            'original_file': str(obj_path),
            'output_dir': str(output_dir),
            'tasks': [],
            'downloaded_files': [],
            'errors': []
        }
        
        try:
            # Upload file
            logger.info(f"Uploading {obj_path}")
            file_id = self.upload_file(obj_path)
            if not file_id:
                results['errors'].append("Failed to upload file")
                return results
            
            # Create texture task
            logger.info("Creating texture generation task")
            texture_task = self.create_texture_task(file_id, style_prompt)
            if texture_task:
                results['tasks'].append({
                    'type': 'texture',
                    'task_id': texture_task.task_id,
                    'status': 'created'
                })
                
                # Wait for texture completion
                logger.info("Waiting for texture generation...")
                texture_task = self.wait_for_completion(texture_task)
                
                if texture_task.status == 'SUCCEEDED':
                    # Download textured model
                    if texture_task.result_urls:
                        for i, url in enumerate(texture_task.result_urls):
                            if url:
                                file_ext = '.glb' if 'glb' in url else '.obj'
                                output_file = output_dir / f"{obj_path.stem}_textured{file_ext}"
                                if self.download_result(url, output_file):
                                    results['downloaded_files'].append(str(output_file))
                    
                    results['tasks'][0]['status'] = 'completed'
                else:
                    error_msg = f"Texture task failed: {texture_task.error_message}"
                    results['errors'].append(error_msg)
                    results['tasks'][0]['status'] = 'failed'
            
            # Create refine task
            logger.info("Creating mesh refinement task")
            refine_task = self.create_refine_task(file_id)
            if refine_task:
                results['tasks'].append({
                    'type': 'refine',
                    'task_id': refine_task.task_id,
                    'status': 'created'
                })
                
                # Wait for refinement completion
                logger.info("Waiting for mesh refinement...")
                refine_task = self.wait_for_completion(refine_task)
                
                if refine_task.status == 'SUCCEEDED':
                    # Download refined model and thumbnail
                    if refine_task.result_urls:
                        for i, url in enumerate(refine_task.result_urls):
                            if url:
                                if 'thumbnail' in url.lower() or i == 1:
                                    output_file = output_dir / f"{obj_path.stem}_refined!.png"
                                else:
                                    file_ext = '.glb' if 'glb' in url else '.obj'
                                    output_file = output_dir / f"{obj_path.stem}_refined{file_ext}"
                                
                                if self.download_result(url, output_file):
                                    results['downloaded_files'].append(str(output_file))
                    
                    results['tasks'][1]['status'] = 'completed'
                else:
                    error_msg = f"Refine task failed: {refine_task.error_message}"
                    results['errors'].append(error_msg)
                    results['tasks'][1]['status'] = 'failed'
            
            results['success'] = len(results['downloaded_files']) > 0
            
        except Exception as e:
            error_msg = f"Process failed: {str(e)}"
            results['errors'].append(error_msg)
            logger.error(error_msg)
        
        return results

def test_meshy_api():
    """Test function for Meshy API client"""
    # This would need a real API key to work
    api_key = "msy_t9FYfPHBWK1c8VBfX0pLxnEZMdWbg0DEc2qz"
    
    client = MeshyAPIClient(api_key)
    
    # Test with a sample OBJ file
    obj_file = Path("sample.obj")
    output_dir = Path("meshy_output")
    
    if obj_file.exists():
        results = client.process_obj_file(obj_file, output_dir)
        print(json.dumps(results, indent=2))
    else:
        print("No sample OBJ file found for testing")

if __name__ == "__main__":
    test_meshy_api()