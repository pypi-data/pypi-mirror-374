from typing import List, Optional

from dooservice.core.domain.entities.instance_config import InstanceConfig
from dooservice.core.domain.services.diff_manager import Diff
from dooservice.instance.domain.repositories.instance_environment_repository import (
    InstanceEnvironmentRepository,
)
from dooservice.instance.domain.repositories.instance_repository import (
    InstanceRepository,
)
from dooservice.instance.domain.services.database_manager import DatabaseManager
from dooservice.instance.domain.services.repository_manager import RepositoryManager
from dooservice.shared.infrastructure.message_container import get_message_handler


class SyncInstanceUseCase:
    """Pure domain use case for synchronizing an instance."""

    def __init__(
        self,
        repository_manager: RepositoryManager,
        database_manager: DatabaseManager,
        instance_repo: InstanceRepository,
        instance_env_repo: InstanceEnvironmentRepository,
    ):
        self._repository_manager = repository_manager
        self._database_manager = database_manager
        self._instance_repo = instance_repo
        self._instance_env_repo = instance_env_repo
        self._msg = get_message_handler()

    def execute(
        self,
        resolved_instance_config: InstanceConfig,
        locked_instance_config: InstanceConfig,
    ) -> None:
        """
        Execute the synchronization process for an instance.

        Args:
            resolved_instance_config: New resolved configuration.
            locked_instance_config: Current locked configuration.
        """
        # 1. Sync repositories
        self._repository_manager.sync_repositories(
            resolved_instance_config,
            locked_instance_config,
        )

        # 2. Update instance environment (odoo.conf, .env files)
        self._instance_env_repo.setup(resolved_instance_config)

        # 3. Recreate Docker containers
        self._instance_repo.recreate(resolved_instance_config)

    def sync_database_credentials(
        self,
        db_container_name: str,
        old_user: Optional[str],
        new_user: str,
        new_password: str,
        superuser: Optional[str] = None,
    ) -> None:
        """
        Synchronize database credentials using the domain service.

        Args:
            db_container_name: Name of the database container.
            old_user: Previous username (if available).
            new_user: New username.
            new_password: New password.
            superuser: Database superuser to connect as.
        """
        self._database_manager.sync_credentials(
            db_container_name,
            old_user,
            new_user,
            new_password,
            superuser,
        )

    def sync_database_credentials_if_needed(
        self,
        diffs: List[Diff],
        resolved_instance_config: InstanceConfig,
        locked_instance_config: Optional[InstanceConfig],
    ) -> None:
        """
        Check if database credentials changed and sync them if necessary.

        Args:
            diffs: List of configuration differences
            resolved_instance_config: New resolved configuration
            locked_instance_config: Current locked configuration
        """
        # Check if there are database credential changes
        if not self._has_database_credential_changes(diffs):
            return

        # Ensure we have the necessary deployment configuration
        if (
            not resolved_instance_config.deployment
            or not resolved_instance_config.deployment.docker
            or not resolved_instance_config.deployment.docker.db
        ):
            return

        # Extract credential information
        db_container = resolved_instance_config.deployment.docker.db
        new_user = resolved_instance_config.env_vars.get("DB_USER")
        new_password = resolved_instance_config.env_vars.get("DB_PASSWORD")

        if not new_user or not new_password:
            return

        # Get old credentials if available
        old_user = None
        if locked_instance_config and locked_instance_config.env_vars:
            old_user = locked_instance_config.env_vars.get("DB_USER")

        # Execute credential sync through use case
        # Use old_user as superuser if available, otherwise new_user
        # This handles cases where user is changing vs password only
        superuser = old_user if old_user else new_user

        self._msg.progress("Synchronizing database credentials...")
        self.sync_database_credentials(
            db_container.container_name,
            old_user,
            new_user,
            new_password,
            superuser,
        )
        self._msg.progress("Synchronizing database credentials...", completed=True)

    def _has_database_credential_changes(self, diffs: List[Diff]) -> bool:
        """
        Check if any of the diffs involve database credential changes.

        Args:
            diffs: List of configuration differences.

        Returns:
            True if DB_USER or DB_PASSWORD have changed.
        """
        db_credential_paths = {
            ("env_vars", "DB_USER"),
            ("env_vars", "DB_PASSWORD"),
        }

        for diff in diffs:
            if diff.type == "changed" and len(diff.path) >= 2:
                path_tuple = tuple(diff.path[-2:])  # Get last two path elements
                if path_tuple in db_credential_paths:
                    return True
        return False
