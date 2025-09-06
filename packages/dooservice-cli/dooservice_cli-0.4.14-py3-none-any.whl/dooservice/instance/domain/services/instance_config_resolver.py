"""Instance configuration resolution service."""

from dataclasses import asdict
from typing import Any, Dict

from dooservice.core.domain.entities.instance_config import InstanceConfig
from dooservice.shared.config.placeholder_resolver import PlaceholderResolver


class InstanceConfigResolver:
    """Service for resolving instance configuration placeholders and transformations."""

    def __init__(self, placeholder_resolver: PlaceholderResolver = None):
        self._placeholder_resolver = placeholder_resolver or PlaceholderResolver()

    def resolve_config(
        self,
        instance_config: InstanceConfig,
        instance_name: str,
        context: Dict[str, Any] = None,
    ) -> InstanceConfig:
        """
        Resolve placeholders in instance configuration.

        Args:
            instance_config: The instance configuration to resolve
            instance_name: Name of the instance
            context: Additional context for placeholder resolution

        Returns:
            Resolved instance configuration
        """
        # Resolve placeholders iteratively
        resolved_config = instance_config
        for _ in range(5):  # Iterate to resolve nested placeholders
            config_context = asdict(resolved_config)
            config_context["name"] = instance_name

            # Merge additional context if provided
            if context:
                config_context.update(context)

            resolved_config = self._placeholder_resolver.resolve(
                resolved_config, config_context
            )

        # Convert port values to int
        resolved_config.ports = {k: int(v) for k, v in resolved_config.ports.items()}

        # Set the instance name
        resolved_config.instance_name = instance_name

        return resolved_config
