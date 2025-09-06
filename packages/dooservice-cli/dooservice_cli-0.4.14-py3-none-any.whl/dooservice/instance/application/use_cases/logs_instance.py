"""Get instance logs use case."""

from dooservice.core.domain.entities.instance_config import InstanceConfig
from dooservice.instance.domain.services.instance_orchestrator import (
    InstanceOrchestrator,
)


class LogsInstanceUseCase:
    """Use case for retrieving logs from an Odoo instance."""

    def __init__(self, orchestrator: InstanceOrchestrator):
        self._orchestrator = orchestrator

    def execute(
        self,
        config: InstanceConfig,
        tail: int = 50,
        follow: bool = False,
        service: str = "all",
    ) -> str:
        """
        Get logs from an Odoo instance.

        Args:
            config: Instance configuration
            tail: Number of lines to show
            follow: Whether to follow the log stream
            service: "web", "db", or "all"

        Returns:
            Log output as string
        """
        return self._orchestrator.get_instance_logs(
            config, tail=tail, follow=follow, service=service
        )
