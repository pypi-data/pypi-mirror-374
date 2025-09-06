"""Instance configuration service."""

from typing import List

import click

from dooservice.core.domain.entities.dooservice_config import DooServiceConfig
from dooservice.core.domain.entities.instance_config import InstanceConfig
from dooservice.core.domain.services.config_service import ConfigService
from dooservice.core.infrastructure.driven_adapters.yaml_config_repository import (
    YAMLConfigRepository,
)
from dooservice.instance.domain.services.instance_config_resolver import (
    InstanceConfigResolver,
)


class InstanceConfigService:
    """Service for managing instance configuration operations."""

    def __init__(
        self,
        config_repository: YAMLConfigRepository,
        config_service: ConfigService,
        config_resolver: InstanceConfigResolver,
    ):
        self._config_repository = config_repository
        self._config_service = config_service
        self._config_resolver = config_resolver
        self._dooservice_config = None

    @property
    def dooservice_config(self) -> DooServiceConfig:
        """Load and validate dooservice configuration."""
        if self._dooservice_config is None:
            self._load_config()
        return self._dooservice_config

    def _load_config(self):
        """Load and validate configuration."""
        try:
            raw_config = self._config_repository.load()
            self._dooservice_config = self._config_service.validate(raw_config)
        except Exception as e:
            raise click.ClickException(f"Error loading configuration: {e}") from e

    def get_instance_config(self, instance_name: str) -> InstanceConfig:
        """Get configuration for a specific instance."""
        instance_config = self.dooservice_config.instances.get(instance_name)
        if not instance_config:
            raise click.ClickException(
                f"Instance '{instance_name}' not found in configuration"
            )
        return instance_config

    def resolve_instance_config(self, instance_name: str) -> InstanceConfig:
        """Resolve placeholders in instance configuration."""
        instance_config = self.get_instance_config(instance_name)
        return self._config_resolver.resolve_config(instance_config, instance_name)

    def get_all_instance_names(self) -> List[str]:
        """Get list of all instance names."""
        return list(self.dooservice_config.instances.keys())

    def validate_instance_exists(self, instance_name: str) -> None:
        """Validate that instance exists in configuration."""
        self.get_instance_config(instance_name)  # Will raise if not found
