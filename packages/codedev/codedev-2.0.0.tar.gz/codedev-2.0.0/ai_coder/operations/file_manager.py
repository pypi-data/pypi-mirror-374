"""
File operations with history and versioning
"""

import os
import shutil
import datetime
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

from ..utils.logger import get_logger, ActionLogger
from ..core.config import Config


@dataclass
class FileVersion:
    """File version metadata"""
    timestamp: str
    size: int
    hash: str
    backup_path: str
    operation: str
    user_note: Optional[str] = None


class FileManager:
    """Advanced file manager with history and versioning"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(__name__)
        self.action_logger = ActionLogger()
        self.history_dir = Path(config.workspace.history_dir)
        self.history_dir.mkdir(exist_ok=True)
        
        # Initialize metadata storage
        self.metadata_file = self.history_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, List[FileVersion]]:
        """Load file metadata from storage"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    # Convert back to FileVersion objects
                    metadata = {}
                    for file_path, versions in data.items():
                        metadata[file_path] = [
                            FileVersion(**version) for version in versions
                        ]
                    return metadata
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load metadata: {e}")
            return {}
    
    def _save_metadata(self) -> None:
        """Save file metadata to storage"""
        try:
            # Convert FileVersion objects to dicts
            data = {}
            for file_path, versions in self.metadata.items():
                data[file_path] = [asdict(version) for version in versions]
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {e}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get simple hash of file content"""
        try:
            import hashlib
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _create_backup(self, file_path: str, operation: str) -> Optional[str]:
        """Create backup of file"""
        try:
            if not os.path.exists(file_path):
                return None
            
            # Create backup directory for this file
            safe_path = file_path.replace("/", "__").replace("\\", "__")
            backup_dir = self.history_dir / safe_path
            backup_dir.mkdir(exist_ok=True)
            
            # Generate backup filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            backup_filename = f"{timestamp}.bak"
            backup_path = backup_dir / backup_filename
            
            # Copy file
            shutil.copy2(file_path, backup_path)
            
            # Create version entry
            file_size = os.path.getsize(file_path)
            file_hash = self._get_file_hash(file_path)
            
            version = FileVersion(
                timestamp=timestamp,
                size=file_size,
                hash=file_hash,
                backup_path=str(backup_path),
                operation=operation
            )
            
            # Add to metadata
            if file_path not in self.metadata:
                self.metadata[file_path] = []
            
            self.metadata[file_path].append(version)
            
            # Cleanup old backups if necessary
            self._cleanup_old_backups(file_path)
            
            # Save metadata
            self._save_metadata()
            
            self.logger.debug(f"Created backup: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create backup for {file_path}: {e}")
            return None
    
    def _cleanup_old_backups(self, file_path: str) -> None:
        """Cleanup old backups if limit exceeded"""
        if file_path not in self.metadata:
            return
        
        versions = self.metadata[file_path]
        max_files = self.config.workspace.max_history_files
        
        if len(versions) > max_files:
            # Remove oldest backups
            versions_to_remove = versions[:-max_files]
            
            for version in versions_to_remove:
                try:
                    if os.path.exists(version.backup_path):
                        os.remove(version.backup_path)
                except Exception as e:
                    self.logger.warning(f"Failed to remove old backup {version.backup_path}: {e}")
            
            # Update metadata
            self.metadata[file_path] = versions[-max_files:]
    
    def read_file(self, file_path: str) -> str:
        """Read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.action_logger.log_file_operation("READ", file_path, True)
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            self.action_logger.log_file_operation("READ", file_path, False)
            return ""
    
    def write_file(self, file_path: str, content: str, create_backup: bool = True) -> bool:
        """Write content to file with optional backup"""
        try:
            # Create backup if file exists and backup is enabled
            if create_backup and self.config.workspace.backup_on_edit:
                self._create_backup(file_path, "WRITE")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"File written: {file_path}")
            self.action_logger.log_file_operation("WRITE", file_path, True)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write file {file_path}: {e}")
            self.action_logger.log_file_operation("WRITE", file_path, False)
            return False
    
    def delete_file(self, file_path: str, create_backup: bool = True) -> bool:
        """Delete file with optional backup"""
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"File not found: {file_path}")
                return False
            
            # Create backup before deletion
            if create_backup:
                self._create_backup(file_path, "DELETE")
            
            # Delete file
            os.remove(file_path)
            
            self.logger.info(f"File deleted: {file_path}")
            self.action_logger.log_file_operation("DELETE", file_path, True)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete file {file_path}: {e}")
            self.action_logger.log_file_operation("DELETE", file_path, False)
            return False
    
    def move_file(self, src_path: str, dest_path: str, create_backup: bool = True) -> bool:
        """Move/rename file with optional backup"""
        try:
            if not os.path.exists(src_path):
                self.logger.warning(f"Source file not found: {src_path}")
                return False
            
            # Create backup
            if create_backup:
                self._create_backup(src_path, "MOVE")
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Move file
            shutil.move(src_path, dest_path)
            
            self.logger.info(f"File moved: {src_path} -> {dest_path}")
            self.action_logger.log_file_operation("MOVE", f"{src_path} -> {dest_path}", True)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to move file {src_path} -> {dest_path}: {e}")
            self.action_logger.log_file_operation("MOVE", f"{src_path} -> {dest_path}", False)
            return False
    
    def copy_file(self, src_path: str, dest_path: str) -> bool:
        """Copy file"""
        try:
            if not os.path.exists(src_path):
                self.logger.warning(f"Source file not found: {src_path}")
                return False
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Copy file
            shutil.copy2(src_path, dest_path)
            
            self.logger.info(f"File copied: {src_path} -> {dest_path}")
            self.action_logger.log_file_operation("COPY", f"{src_path} -> {dest_path}", True)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to copy file {src_path} -> {dest_path}: {e}")
            self.action_logger.log_file_operation("COPY", f"{src_path} -> {dest_path}", False)
            return False
    
    def get_file_history(self, file_path: str) -> List[FileVersion]:
        """Get file version history"""
        return self.metadata.get(file_path, [])
    
    def undo_last_change(self, file_path: str) -> bool:
        """Undo last change to file"""
        try:
            versions = self.get_file_history(file_path)
            if len(versions) < 2:
                self.logger.warning(f"No previous version available for {file_path}")
                return False
            
            # Get the second-to-last version (skip the current one)
            prev_version = versions[-2]
            
            # Restore from backup
            if os.path.exists(prev_version.backup_path):
                shutil.copy2(prev_version.backup_path, file_path)
                self.logger.info(f"Undo applied: {file_path} -> {prev_version.timestamp}")
                self.action_logger.log_file_operation("UNDO", file_path, True)
                return True
            else:
                self.logger.error(f"Backup file not found: {prev_version.backup_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to undo changes for {file_path}: {e}")
            self.action_logger.log_file_operation("UNDO", file_path, False)
            return False
    
    def redo_last_undo(self, file_path: str) -> bool:
        """Redo last undo operation"""
        try:
            versions = self.get_file_history(file_path)
            if not versions:
                self.logger.warning(f"No version history available for {file_path}")
                return False
            
            # Get the latest version
            latest_version = versions[-1]
            
            # Restore from backup
            if os.path.exists(latest_version.backup_path):
                shutil.copy2(latest_version.backup_path, file_path)
                self.logger.info(f"Redo applied: {file_path} -> {latest_version.timestamp}")
                self.action_logger.log_file_operation("REDO", file_path, True)
                return True
            else:
                self.logger.error(f"Backup file not found: {latest_version.backup_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to redo changes for {file_path}: {e}")
            self.action_logger.log_file_operation("REDO", file_path, False)
            return False
    
    def restore_version(self, file_path: str, timestamp: str) -> bool:
        """Restore file to specific version"""
        try:
            versions = self.get_file_history(file_path)
            target_version = None
            
            for version in versions:
                if version.timestamp == timestamp:
                    target_version = version
                    break
            
            if not target_version:
                self.logger.warning(f"Version {timestamp} not found for {file_path}")
                return False
            
            # Create backup of current state before restore
            self._create_backup(file_path, "RESTORE")
            
            # Restore from backup
            if os.path.exists(target_version.backup_path):
                shutil.copy2(target_version.backup_path, file_path)
                self.logger.info(f"Restored: {file_path} -> {timestamp}")
                self.action_logger.log_file_operation("RESTORE", f"{file_path} -> {timestamp}", True)
                return True
            else:
                self.logger.error(f"Backup file not found: {target_version.backup_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to restore {file_path} to {timestamp}: {e}")
            self.action_logger.log_file_operation("RESTORE", f"{file_path} -> {timestamp}", False)
            return False
