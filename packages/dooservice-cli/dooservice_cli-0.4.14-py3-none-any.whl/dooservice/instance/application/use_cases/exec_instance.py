"""Execute command in instance use case."""

from dooservice.core.domain.entities.instance_config import InstanceConfig
from dooservice.instance.domain.services.instance_orchestrator import (
    InstanceOrchestrator,
)


class ExecInstanceUseCase:
    """Use case for executing commands inside an Odoo instance."""

    def __init__(self, orchestrator: InstanceOrchestrator):
        self.orchestrator = orchestrator

    def execute(
        self,
        config: InstanceConfig,
        command: str,
        service: str = "web",
    ) -> str:
        """
        Execute a command in one or more containers of an instance.

        Args:
            config: Instance configuration
            command: Command to execute
            service: "web", "db" or "all"

        Returns:
            Command output as string
        """
        return self.orchestrator.exec_instance_command(config, command, service=service)
