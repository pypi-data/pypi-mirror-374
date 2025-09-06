from pathlib import Path

import click

from dooservice.core.domain.services.config_service import create_config_service
from dooservice.core.domain.services.diff_manager import DiffManager
from dooservice.core.domain.services.lock_file_checksum_service import (
    LockFileChecksumService,
)
from dooservice.core.domain.services.lock_manager import LockManager
from dooservice.core.infrastructure.driven_adapters.file_lock_repository import (
    FileLockRepository,
)
from dooservice.core.infrastructure.driven_adapters.os_filesystem_repository import (
    OsFilesystemRepository,
)
from dooservice.core.infrastructure.driven_adapters.yaml_config_repository import (
    YAMLConfigRepository,
)
from dooservice.instance.application.use_case_factory import InstanceUseCaseFactory
from dooservice.instance.domain.services.instance_config_resolver import (
    InstanceConfigResolver,
)
from dooservice.instance.domain.services.instance_config_service import (
    InstanceConfigService,
)
from dooservice.instance.domain.services.lock_file_manager import LockFileManager
from dooservice.instance.domain.services.repository_manager import RepositoryManager
from dooservice.instance.infrastructure.driven_adapters.docker_instance_repository import (  # noqa: E501
    DockerInstanceRepository,
)
from dooservice.instance.infrastructure.driven_adapters.local_instance_environment_repository import (  # noqa: E501
    LocalInstanceEnvironmentRepository,
)
from dooservice.repository.domain.services.module_detector import ModuleDetectorService
from dooservice.repository.infrastructure.driven_adapters.filesystem_module_repository import (  # noqa: E501
    FilesystemModuleRepository,
)
from dooservice.repository.infrastructure.driven_adapters.git_python_repository import (
    GitPythonRepository,
)
from dooservice.shared.infrastructure.console_message_handler import (
    ConsoleMessageHandler,
)
from dooservice.shared.infrastructure.message_container import set_message_handler
from dooservice.shared.interfaces.message_handler import MessageHandler


class InstanceConfigContext:
    """Centralized configuration context for instance CLI commands."""

    def __init__(
        self,
        config_file: str = "dooservice.yml",
        message_handler: MessageHandler = None,
    ):
        """Initialize config context with configuration file."""
        self.config_file = Path(config_file)

        # Initialize and set global message handler
        self._msg = message_handler or ConsoleMessageHandler()
        set_message_handler(self._msg)

        # Initialize repositories
        self._filesystem_repo = OsFilesystemRepository()
        self._git_repo = GitPythonRepository()
        self._module_repo = FilesystemModuleRepository()
        self._instance_repo = DockerInstanceRepository()
        self._lock_repo = FileLockRepository(self.config_file.parent)
        self._config_repo = YAMLConfigRepository(str(self.config_file))

        # Initialize core services
        self._lock_manager = LockManager(LockFileChecksumService())
        self._config_service = create_config_service()
        self._diff_manager = DiffManager()

        # Initialize specialized services
        self._config_resolver = InstanceConfigResolver()
        self._config_service_manager = InstanceConfigService(
            self._config_repo, self._config_service, self._config_resolver
        )
        self._lock_file_manager = LockFileManager(self._lock_manager, self._lock_repo)

        # Initialize domain services
        self._module_detector = ModuleDetectorService(self._module_repo)
        self._instance_env_repo = LocalInstanceEnvironmentRepository(
            self._module_detector
        )
        self._repository_manager = RepositoryManager(
            self._git_repo, self._filesystem_repo
        )

        # Initialize use case factory
        self._use_case_factory = InstanceUseCaseFactory()

        # Get use cases from factory for backward compatibility
        self.create_instance_use_case = (
            self._use_case_factory.create_instance_use_case()
        )
        self.sync_instance_use_case = self._use_case_factory.sync_instance_use_case()

    @property
    def config_service(self) -> InstanceConfigService:
        """Get the configuration service."""
        return self._config_service_manager

    @property
    def lock_file_manager(self) -> LockFileManager:
        """Get the lock file manager."""
        return self._lock_file_manager

    # Expose only necessary internal services for commands that need them
    @property
    def diff_manager(self) -> DiffManager:
        """Get the diff manager for synchronization commands."""
        return self._diff_manager

    @property
    def instance_repo(self) -> DockerInstanceRepository:
        """Get the instance repository for direct container operations."""
        return self._instance_repo


# Decorators for instance CLI commands
def instance_config_context(f):
    """Decorator to inject config context into instance CLI commands."""

    @click.pass_context
    def wrapper(ctx, *args, **kwargs):
        config_file = ctx.params.get("config", "dooservice.yml")
        ctx.obj = InstanceConfigContext(config_file)
        return f(*args, **kwargs)

    return wrapper


# Standard config option decorator
def config_option():
    """Standard --config option decorator for instance CLI commands."""
    return click.option(
        "--config",
        "-c",
        "config",
        type=click.Path(exists=True),
        default="dooservice.yml",
        help="Path to dooservice.yml configuration file",
    )
