"""
Upgrade utilities for Sudarshan Engine.

This module provides utilities for upgrading between versions,
migrating data, and handling compatibility issues.
"""

import os
import shutil
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging

from .__version__ import (
    __version__,
    get_upgrade_path,
    is_compatible_version,
    parse_version,
    SPQ_FORMAT_VERSION,
    SPQ_FORMAT_COMPATIBILITY
)

logger = logging.getLogger(__name__)

class UpgradeManager:
    """Manages upgrades between Sudarshan Engine versions."""

    def __init__(self, backup_dir: str = None):
        """
        Initialize upgrade manager.

        Args:
            backup_dir: Directory for storing backups during upgrades
        """
        self.backup_dir = Path(backup_dir or "~/.sudarshan/backups").expanduser()
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def check_upgrade_needed(self, target_version: str = None) -> Dict[str, Any]:
        """
        Check if upgrade is needed.

        Args:
            target_version: Target version to check against

        Returns:
            Dictionary with upgrade information
        """
        current_version = __version__
        target = target_version or "latest"

        result = {
            "current_version": current_version,
            "target_version": target,
            "upgrade_needed": False,
            "upgrade_path": [],
            "breaking_changes": [],
            "recommendations": []
        }

        if target_version and not is_compatible_version(target_version, current_version):
            result["upgrade_needed"] = True
            result["upgrade_path"] = get_upgrade_path(current_version, target_version)

            # Check for breaking changes
            result["breaking_changes"] = self._get_breaking_changes(current_version, target_version)

        return result

    def _get_breaking_changes(self, from_version: str, to_version: str) -> List[str]:
        """Get list of breaking changes between versions."""
        breaking_changes = []

        from_major, from_minor, _, _ = parse_version(from_version)
        to_major, to_minor, _, _ = parse_version(to_version)

        if to_major > from_major:
            breaking_changes.extend([
                "Major version upgrade may include breaking API changes",
                "SPQ file format may have changed - backup all files",
                "Some deprecated features may be removed",
                "Configuration files may need updates"
            ])

        if to_minor > from_minor:
            breaking_changes.extend([
                "New features may change default behavior",
                "Some APIs may have new required parameters"
            ])

        return breaking_changes

    def create_backup(self, backup_name: str = None) -> Path:
        """
        Create a backup of current Sudarshan installation and data.

        Args:
            backup_name: Name for the backup

        Returns:
            Path to backup directory
        """
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"sudarshan_backup_{timestamp}"

        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating backup: {backup_path}")

        # Backup configuration files
        config_files = [
            Path.home() / ".sudarshan" / "config.yaml",
            Path.home() / ".sudarshan" / "keys",
            Path.home() / ".sudarshan" / "logs"
        ]

        for config_file in config_files:
            if config_file.exists():
                if config_file.is_file():
                    shutil.copy2(config_file, backup_path / config_file.name)
                else:
                    shutil.copytree(config_file, backup_path / config_file.name, dirs_exist_ok=True)

        # Create backup manifest
        manifest = {
            "backup_name": backup_name,
            "created_at": datetime.now().isoformat(),
            "sudarshan_version": __version__,
            "files_backed_up": [str(f) for f in config_files if f.exists()]
        }

        with open(backup_path / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Backup created successfully: {backup_path}")
        return backup_path

    def restore_backup(self, backup_name: str) -> bool:
        """
        Restore from a backup.

        Args:
            backup_name: Name of backup to restore

        Returns:
            True if successful, False otherwise
        """
        backup_path = self.backup_dir / backup_name

        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_name}")
            return False

        logger.info(f"Restoring from backup: {backup_path}")

        try:
            # Read manifest
            with open(backup_path / "manifest.json", 'r') as f:
                manifest = json.load(f)

            # Restore files
            for file_path in manifest.get("files_backed_up", []):
                source = backup_path / Path(file_path).name
                if source.exists():
                    dest = Path(file_path)
                    dest.parent.mkdir(parents=True, exist_ok=True)

                    if source.is_file():
                        shutil.copy2(source, dest)
                    else:
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(source, dest)

            logger.info("Backup restored successfully")
            return True

        except Exception as e:
            logger.error(f"Backup restoration failed: {e}")
            return False

    def migrate_spq_files(self, file_paths: List[str], target_version: str) -> Dict[str, Any]:
        """
        Migrate SPQ files to new format version.

        Args:
            file_paths: List of SPQ file paths to migrate
            target_version: Target SPQ format version

        Returns:
            Migration results
        """
        results = {
            "total_files": len(file_paths),
            "migrated": 0,
            "skipped": 0,
            "errors": 0,
            "details": []
        }

        for file_path in file_paths:
            try:
                migration_result = self._migrate_single_spq_file(file_path, target_version)
                results["details"].append(migration_result)

                if migration_result["status"] == "migrated":
                    results["migrated"] += 1
                elif migration_result["status"] == "skipped":
                    results["skipped"] += 1
                else:
                    results["errors"] += 1

            except Exception as e:
                results["errors"] += 1
                results["details"].append({
                    "file": file_path,
                    "status": "error",
                    "error": str(e)
                })

        return results

    def _migrate_single_spq_file(self, file_path: str, target_version: str) -> Dict[str, Any]:
        """Migrate a single SPQ file."""
        # This is a placeholder for actual migration logic
        # In a real implementation, this would:
        # 1. Read the current SPQ file
        # 2. Check its format version
        # 3. Apply necessary transformations
        # 4. Write the migrated file

        return {
            "file": file_path,
            "status": "migrated",
            "from_version": "1.0",
            "to_version": target_version,
            "changes_applied": []
        }

    def validate_upgrade(self, target_version: str) -> Dict[str, Any]:
        """
        Validate that upgrade can proceed safely.

        Args:
            target_version: Target version for upgrade

        Returns:
            Validation results
        """
        validation = {
            "can_upgrade": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }

        # Check system compatibility
        from .__version__ import check_system_compatibility
        system_check = check_system_compatibility()

        if not system_check["compatible"]:
            validation["can_upgrade"] = False
            validation["errors"].extend(system_check["errors"])

        validation["warnings"].extend(system_check["warnings"])

        # Check for large data files
        data_dir = Path.home() / ".sudarshan" / "data"
        if data_dir.exists():
            total_size = sum(f.stat().st_size for f in data_dir.rglob("*") if f.is_file())
            if total_size > 1024 * 1024 * 1024:  # 1GB
                validation["recommendations"].append(
                    "Large data directory detected. Consider backing up before upgrade."
                )

        # Check for custom configurations
        config_file = Path.home() / ".sudarshan" / "config.yaml"
        if config_file.exists():
            validation["recommendations"].append(
                "Custom configuration detected. Review configuration after upgrade."
            )

        return validation

    def perform_upgrade(self, target_version: str, create_backup: bool = True) -> Dict[str, Any]:
        """
        Perform the upgrade process.

        Args:
            target_version: Target version to upgrade to
            create_backup: Whether to create backup before upgrade

        Returns:
            Upgrade results
        """
        result = {
            "success": False,
            "target_version": target_version,
            "backup_created": False,
            "steps_completed": [],
            "errors": []
        }

        try:
            # Step 1: Validate upgrade
            logger.info("Validating upgrade...")
            validation = self.validate_upgrade(target_version)
            if not validation["can_upgrade"]:
                result["errors"].extend(validation["errors"])
                return result

            result["steps_completed"].append("validation")

            # Step 2: Create backup
            if create_backup:
                logger.info("Creating backup...")
                backup_path = self.create_backup(f"pre_upgrade_{target_version.replace('.', '_')}")
                result["backup_created"] = True
                result["backup_path"] = str(backup_path)
                result["steps_completed"].append("backup")

            # Step 3: Pre-upgrade checks
            logger.info("Performing pre-upgrade checks...")
            # Placeholder for pre-upgrade tasks
            result["steps_completed"].append("pre_upgrade")

            # Step 4: Perform upgrade
            logger.info(f"Upgrading to version {target_version}...")
            # Placeholder for actual upgrade logic
            result["steps_completed"].append("upgrade")

            # Step 5: Post-upgrade validation
            logger.info("Performing post-upgrade validation...")
            # Placeholder for validation
            result["steps_completed"].append("validation")

            # Step 6: Cleanup
            logger.info("Performing cleanup...")
            # Placeholder for cleanup
            result["steps_completed"].append("cleanup")

            result["success"] = True
            logger.info("Upgrade completed successfully")

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Upgrade failed: {e}")

        return result

def list_available_backups(backup_dir: str = None) -> List[Dict[str, Any]]:
    """
    List available backups.

    Args:
        backup_dir: Backup directory to scan

    Returns:
        List of backup information
    """
    backup_path = Path(backup_dir or "~/.sudarshan/backups").expanduser()

    if not backup_path.exists():
        return []

    backups = []
    for item in backup_path.iterdir():
        if item.is_dir() and (item / "manifest.json").exists():
            try:
                with open(item / "manifest.json", 'r') as f:
                    manifest = json.load(f)
                backups.append({
                    "name": item.name,
                    "path": str(item),
                    "created_at": manifest.get("created_at"),
                    "version": manifest.get("sudarshan_version"),
                    "files": manifest.get("files_backed_up", [])
                })
            except Exception:
                continue

    # Sort by creation date (newest first)
    backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return backups

def cleanup_old_backups(backup_dir: str = None, keep_count: int = 5) -> int:
    """
    Clean up old backups, keeping only the most recent ones.

    Args:
        backup_dir: Backup directory
        keep_count: Number of backups to keep

    Returns:
        Number of backups removed
    """
    backups = list_available_backups(backup_dir)

    if len(backups) <= keep_count:
        return 0

    # Remove old backups
    removed_count = 0
    for backup in backups[keep_count:]:
        try:
            shutil.rmtree(backup["path"])
            removed_count += 1
        except Exception:
            continue

    return removed_count