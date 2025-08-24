#!/usr/bin/env python3

"""
DATABASE BACKUP SCRIPT FOR RENDER DEPLOYMENT
Automated database backup with cloud storage integration.
"""

import os
import sys
import datetime
import subprocess
import gzip
import shutil
from pathlib import Path
import json
import logging
from typing import Optional
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Handle database backup operations for Render deployment."""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.backup_storage_url = os.getenv('BACKUP_STORAGE_URL', '')
        self.backup_retention_days = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
        self.backup_dir = Path('/tmp/backups')
        self.backup_dir.mkdir(exist_ok=True)
        
        # Webhook for notifications
        self.webhook_url = os.getenv('BACKUP_WEBHOOK_URL', '')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
    
    def create_backup(self) -> Optional[Path]:
        """Create a database backup using pg_dump."""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"crypto_tracker_backup_{timestamp}.sql"
        backup_path = self.backup_dir / backup_filename
        
        logger.info(f"Creating database backup: {backup_filename}")
        
        try:
            # Use pg_dump to create backup
            cmd = [
                'pg_dump',
                '--verbose',
                '--clean',
                '--no-acl',
                '--no-owner',
                '--format=plain',
                '--file', str(backup_path),
                self.database_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Database backup created successfully: {backup_path}")
                
                # Compress the backup
                compressed_path = self.compress_backup(backup_path)
                return compressed_path
            else:
                logger.error(f"❌ Database backup failed: {result.stderr}")
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ pg_dump failed: {e}")
            logger.error(f"STDERR: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            return None
    
    def compress_backup(self, backup_path: Path) -> Path:
        """Compress backup file using gzip."""
        compressed_path = backup_path.with_suffix('.sql.gz')
        
        logger.info(f"Compressing backup: {compressed_path.name}")
        
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove uncompressed file
        backup_path.unlink()
        
        # Get file size
        size_mb = compressed_path.stat().st_size / (1024 * 1024)
        logger.info(f"✅ Backup compressed: {compressed_path.name} ({size_mb:.2f} MB)")
        
        return compressed_path
    
    def upload_to_cloud_storage(self, backup_path: Path) -> bool:
        """Upload backup to cloud storage if configured."""
        if not self.backup_storage_url:
            logger.info("No cloud storage URL configured, skipping upload")
            return True
        
        logger.info(f"Uploading backup to cloud storage: {backup_path.name}")
        
        try:
            # This is a placeholder for cloud storage integration
            # You would implement actual cloud storage upload here
            # Examples: AWS S3, Google Cloud Storage, Azure Blob Storage
            
            if self.backup_storage_url.startswith('s3://'):
                return self._upload_to_s3(backup_path)
            elif self.backup_storage_url.startswith('gs://'):
                return self._upload_to_gcs(backup_path)
            elif self.backup_storage_url.startswith('http'):
                return self._upload_via_http(backup_path)
            else:
                logger.warning(f"Unsupported storage URL: {self.backup_storage_url}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Cloud storage upload failed: {e}")
            return False
    
    def _upload_to_s3(self, backup_path: Path) -> bool:
        """Upload backup to AWS S3."""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # Parse S3 URL
            url_parts = self.backup_storage_url.replace('s3://', '').split('/', 1)
            bucket = url_parts[0]
            prefix = url_parts[1] if len(url_parts) > 1 else ''
            
            s3_key = f"{prefix}/{backup_path.name}" if prefix else backup_path.name
            
            s3_client = boto3.client('s3')
            s3_client.upload_file(str(backup_path), bucket, s3_key)
            
            logger.info(f"✅ Backup uploaded to S3: s3://{bucket}/{s3_key}")
            return True
            
        except ImportError:
            logger.error("boto3 not installed, cannot upload to S3")
            return False
        except ClientError as e:
            logger.error(f"❌ S3 upload failed: {e}")
            return False
    
    def _upload_to_gcs(self, backup_path: Path) -> bool:
        """Upload backup to Google Cloud Storage."""
        try:
            from google.cloud import storage
            
            # Parse GCS URL
            url_parts = self.backup_storage_url.replace('gs://', '').split('/', 1)
            bucket_name = url_parts[0]
            prefix = url_parts[1] if len(url_parts) > 1 else ''
            
            blob_name = f"{prefix}/{backup_path.name}" if prefix else backup_path.name
            
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            blob.upload_from_filename(str(backup_path))
            
            logger.info(f"✅ Backup uploaded to GCS: gs://{bucket_name}/{blob_name}")
            return True
            
        except ImportError:
            logger.error("google-cloud-storage not installed, cannot upload to GCS")
            return False
        except Exception as e:
            logger.error(f"❌ GCS upload failed: {e}")
            return False
    
    def _upload_via_http(self, backup_path: Path) -> bool:
        """Upload backup via HTTP POST."""
        try:
            with open(backup_path, 'rb') as f:
                files = {'backup': (backup_path.name, f, 'application/gzip')}
                response = requests.post(self.backup_storage_url, files=files, timeout=300)
                response.raise_for_status()
            
            logger.info(f"✅ Backup uploaded via HTTP: {self.backup_storage_url}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"❌ HTTP upload failed: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove old backup files from local storage."""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.backup_retention_days)
        
        logger.info(f"Cleaning up backups older than {cutoff_date.strftime('%Y-%m-%d')}")
        
        for backup_file in self.backup_dir.glob("crypto_tracker_backup_*.sql.gz"):
            try:
                # Extract timestamp from filename
                timestamp_str = backup_file.stem.split('_')[-2] + '_' + backup_file.stem.split('_')[-1]
                file_date = datetime.datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                
                if file_date < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"🗑️ Removed old backup: {backup_file.name}")
                    
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse date from filename: {backup_file.name}")
    
    def send_notification(self, success: bool, backup_file: str = "", error_message: str = ""):
        """Send backup status notification via webhook."""
        if not self.webhook_url:
            return
        
        timestamp = datetime.datetime.now().isoformat()
        
        if success:
            message = {
                "text": f"✅ Database backup completed successfully",
                "attachments": [
                    {
                        "color": "good",
                        "fields": [
                            {"title": "File", "value": backup_file, "short": True},
                            {"title": "Timestamp", "value": timestamp, "short": True}
                        ]
                    }
                ]
            }
        else:
            message = {
                "text": f"❌ Database backup failed",
                "attachments": [
                    {
                        "color": "danger",
                        "fields": [
                            {"title": "Error", "value": error_message, "short": False},
                            {"title": "Timestamp", "value": timestamp, "short": True}
                        ]
                    }
                ]
            }
        
        try:
            response = requests.post(self.webhook_url, json=message, timeout=30)
            response.raise_for_status()
            logger.info("✅ Notification sent successfully")
        except Exception as e:
            logger.error(f"❌ Failed to send notification: {e}")
    
    def run_backup(self) -> bool:
        """Run the complete backup process."""
        logger.info("🚀 Starting database backup process...")
        
        try:
            # Create backup
            backup_path = self.create_backup()
            if not backup_path:
                self.send_notification(False, error_message="Failed to create database backup")
                return False
            
            # Upload to cloud storage
            upload_success = self.upload_to_cloud_storage(backup_path)
            if not upload_success:
                logger.warning("⚠️ Cloud storage upload failed, but backup exists locally")
            
            # Cleanup old backups
            self.cleanup_old_backups()
            
            # Send success notification
            self.send_notification(True, backup_file=backup_path.name)
            
            logger.info("✅ Database backup process completed successfully!")
            return True
            
        except Exception as e:
            error_msg = f"Backup process failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.send_notification(False, error_message=error_msg)
            return False

def main():
    """Main entry point for the backup script."""
    try:
        backup = DatabaseBackup()
        success = backup.run_backup()
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()