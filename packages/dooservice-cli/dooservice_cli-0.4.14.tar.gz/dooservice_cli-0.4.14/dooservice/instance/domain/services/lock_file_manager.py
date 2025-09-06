"""Lock file management service."""

from dooservice.core.domain.entities.dooservice_config import DooServiceConfig
from dooservice.core.domain.entities.instance_config import InstanceConfig
from dooservice.core.domain.entities.lockfile import LockFile
from dooservice.core.domain.services.lock_manager import LockManager
from dooservice.core.infrastructure.driven_adapters.file_lock_repository import (
    FileLockRepository,
)


class LockFileManager:
    """Service for managing lock file operations."""

    def __init__(self, lock_manager: LockManager, lock_repository: FileLockRepository):
        self._lock_manager = lock_manager
        self._lock_repository = lock_repository

    def create_updated_config(
        self,
        base_config: DooServiceConfig,
        instance_name: str,
        resolved_config: InstanceConfig,
    ) -> DooServiceConfig:
        """Create updated configuration with resolved instance."""
        return DooServiceConfig(
            version=base_config.version,
            domains=base_config.domains,
            repositories=base_config.repositories,
            instances={
                **base_config.instances,
                instance_name: resolved_config,
            },
        )

    def generate_and_save_lock_file(
        self,
        base_config: DooServiceConfig,
        instance_name: str,
        resolved_config: InstanceConfig,
    ) -> LockFile:
        """
        Generate and save lock file with updated instance configuration.

        Args:
            base_config: Base dooservice configuration
            instance_name: Name of the instance
            resolved_config: Resolved instance configuration

        Returns:
            Generated lock file
        """
        updated_config = self.create_updated_config(
            base_config, instance_name, resolved_config
        )
        new_lock_file = self._lock_manager.generate_from_config(updated_config)
        self._lock_repository.save(new_lock_file)
        return new_lock_file

    def load_lock_file(self) -> LockFile:
        """Load lock file if it exists."""
        try:
            return self._lock_repository.get()
        except (FileNotFoundError, ValueError, KeyError):
            return None
