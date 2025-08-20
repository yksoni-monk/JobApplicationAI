"""
Cache Utility Functions for Document Parsing
Handles caching of parsed resume and job description text with timestamp validation
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DocumentCache:
    """Handles caching of parsed documents with timestamp validation"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self._ensure_cache_directory()
    
    def _ensure_cache_directory(self):
        """Create cache directory if it doesn't exist"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.debug(f"Cache directory ready: {self.cache_dir}")
        except Exception as e:
            logger.error(f"Error creating cache directory: {e}")
            raise
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate a hash for the file content"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.error(f"Error generating file hash: {e}")
            raise
    
    def _get_file_timestamp(self, file_path: str) -> float:
        """Get the last modification timestamp of a file"""
        try:
            return os.path.getmtime(file_path)
        except Exception as e:
            logger.error(f"Error getting file timestamp: {e}")
            raise
    
    def _get_cache_file_path(self, file_path: str, file_type: str) -> str:
        """Generate cache file path based on file hash and type"""
        file_hash = self._get_file_hash(file_path)
        return os.path.join(self.cache_dir, f"{file_type}_{file_hash}.json")
    
    def _load_cache(self, cache_file_path: str) -> Optional[Dict[str, Any]]:
        """Load cached data from file"""
        try:
            if os.path.exists(cache_file_path):
                with open(cache_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
            return None
    
    def _save_cache(self, cache_file_path: str, data: Dict[str, Any]):
        """Save data to cache file"""
        try:
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Cache saved to: {cache_file_path}")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            raise
    
    def get_cached_resume(self, resume_path: str) -> Tuple[Optional[str], bool]:
        """
        Get cached resume text if available and valid
        
        Args:
            resume_path: Path to the resume file
            
        Returns:
            Tuple of (cached_text, is_valid)
        """
        try:
            cache_file_path = self._get_cache_file_path(resume_path, "resume")
            cached_data = self._load_cache(cache_file_path)
            
            if not cached_data:
                return None, False
            
            # Check if file has been modified since caching
            cached_timestamp = cached_data.get("timestamp", 0)
            current_timestamp = self._get_file_timestamp(resume_path)
            
            if current_timestamp > cached_timestamp:
                logger.info(f"Resume file modified, cache invalid: {resume_path}")
                return None, False
            
            logger.info(f"Using cached resume: {resume_path}")
            return cached_data.get("parsed_text"), True
            
        except Exception as e:
            logger.error(f"Error checking resume cache: {e}")
            return None, False
    
    def get_cached_job_description(self, job_path: str) -> Tuple[Optional[str], bool]:
        """
        Get cached job description text if available and valid
        
        Args:
            job_path: Path to the job description file
            
        Returns:
            Tuple of (cached_text, is_valid)
        """
        try:
            cache_file_path = self._get_cache_file_path(job_path, "job")
            cached_data = self._load_cache(cache_file_path)
            
            if not cached_data:
                return None, False
            
            # Check if file has been modified since caching
            cached_timestamp = cached_data.get("timestamp", 0)
            current_timestamp = self._get_file_timestamp(job_path)
            
            if current_timestamp > cached_timestamp:
                logger.info(f"Job description file modified, cache invalid: {job_path}")
                return None, False
            
            logger.info(f"Using cached job description: {job_path}")
            return cached_data.get("parsed_text"), True
            
        except Exception as e:
            logger.error(f"Error checking job description cache: {e}")
            return None, False
    
    def cache_resume(self, resume_path: str, parsed_text: str):
        """
        Cache parsed resume text
        
        Args:
            resume_path: Path to the resume file
            parsed_text: Parsed text content
        """
        try:
            cache_file_path = self._get_cache_file_path(resume_path, "resume")
            timestamp = self._get_file_timestamp(resume_path)
            
            cache_data = {
                "file_path": resume_path,
                "parsed_text": parsed_text,
                "timestamp": timestamp,
                "cached_at": datetime.now().isoformat(),
                "file_size": os.path.getsize(resume_path)
            }
            
            self._save_cache(cache_file_path, cache_data)
            logger.info(f"Resume cached: {resume_path}")
            
        except Exception as e:
            logger.error(f"Error caching resume: {e}")
            raise
    
    def cache_job_description(self, job_path: str, parsed_text: str):
        """
        Cache parsed job description text
        
        Args:
            job_path: Path to the job description file
            parsed_text: Parsed text content
        """
        try:
            cache_file_path = self._get_cache_file_path(job_path, "job")
            timestamp = self._get_file_timestamp(job_path)
            
            cache_data = {
                "file_path": job_path,
                "parsed_text": parsed_text,
                "timestamp": timestamp,
                "cached_at": datetime.now().isoformat(),
                "file_size": os.path.getsize(job_path)
            }
            
            self._save_cache(cache_file_path, cache_data)
            logger.info(f"Job description cached: {job_path}")
            
        except Exception as e:
            logger.error(f"Error caching job description: {e}")
            raise
    
    def clear_cache(self):
        """Clear all cached files"""
        try:
            for file_name in os.listdir(self.cache_dir):
                if file_name.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, file_name)
                    os.remove(file_path)
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            raise
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached files"""
        try:
            cache_info = {
                "cache_directory": self.cache_dir,
                "cached_files": [],
                "total_size": 0
            }
            
            for file_name in os.listdir(self.cache_dir):
                if file_name.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, file_name)
                    file_size = os.path.getsize(file_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            cached_data = json.load(f)
                            cache_info["cached_files"].append({
                                "file": file_name,
                                "original_file": cached_data.get("file_path", "Unknown"),
                                "cached_at": cached_data.get("cached_at", "Unknown"),
                                "size": file_size
                            })
                            cache_info["total_size"] += file_size
                    except Exception:
                        # Skip corrupted cache files
                        continue
            
            return cache_info
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {"error": str(e)}
