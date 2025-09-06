"""
Centralized instance management commands.

This module contains all instance CLI commands using the centralized
configuration context pattern, removing configuration dependencies
from use cases.
"""

import click

from dooservice.instance.infrastructure.driving_adapters.cli.config_context import (
    config_option,
    instance_config_context,
)
from dooservice.shared.errors.config_validation_error import ConfigValidationError
from dooservice.shared.errors.instance_exists_error import InstanceExistsError


@click.command(name="create")
@click.argument("name")
@config_option()
@instance_config_context
def create_instance(config: str, name: str):
    """
    Create a new Odoo instance based on the configuration.

    This command reads the dooservice.yml file, validates the specified
    instance configuration, and orchestrates the entire setup process.
    """
    try:
        config_context = click.get_current_context().obj

        # Validate instance exists in configuration
        config_context.get_instance_config(name)

        # Display instance details before creation
        resolved_display_config = config_context.resolve_instance_config(name)

        click.secho(f"➤ Preparing to create instance '{name}'...", bold=True)
        click.secho("\nInstance Details:", bold=True)
        click.secho(f"  Name: {name}")
        click.secho(f"  Odoo Version: {resolved_display_config.odoo_version}")
        click.secho(f"  Data Directory: {resolved_display_config.data_dir}")

        if resolved_display_config.repositories:
            click.secho("  Repositories:")
            for repo_name, repo_config in resolved_display_config.repositories.items():
                click.secho(
                    f"    - {repo_name}: {repo_config.repository_url} "
                    f"(Branch: {repo_config.branch})"
                )

        if resolved_display_config.python_dependencies:
            click.secho("  Python Dependencies:")
            for dep in resolved_display_config.python_dependencies:
                click.secho(f"    - {dep}")

        # Execute creation with progress
        click.secho(f"\n➤ Creating instance '{name}'...", bold=True)
        config_context.create_instance_with_progress(name)

        click.secho(f"\n✔ Instance '{name}' created successfully.", fg="green")

    except (ConfigValidationError, InstanceExistsError) as e:
        click.secho(f"Configuration Error: {e}", fg="red")
        raise click.Abort() from e
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="start")
@click.argument("name")
@config_option()
@instance_config_context
def start_instance(config: str, name: str):
    """Start an instance."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)
        config_context._use_case_factory.start_instance_use_case().execute(
            resolved_config
        )

        click.secho(f"✔ Instance '{name}' started successfully.", fg="green")

    except Exception as e:
        click.secho(f"Error starting instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="stop")
@click.argument("name")
@config_option()
@instance_config_context
def stop_instance(config: str, name: str):
    """Stop an instance."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        config_context._use_case_factory.stop_instance_use_case().execute(
            resolved_config
        )

        click.secho(f"✔ Instance '{name}' stopped successfully.", fg="green")

    except Exception as e:
        click.secho(f"Error stopping instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="status")
@click.argument("name")
@config_option()
@instance_config_context
def status_instance(config: str, name: str):
    """Show instance status."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        # Ejecutamos el caso de uso real
        status = config_context._use_case_factory.status_instance_use_case().execute(
            resolved_config
        )

        # Render principal del estado de la instancia
        click.secho(
            f"Estado de la instancia '{name}': {status.get('web', 'desconocido')}",
            fg="green",
        )

        # Si el caso de uso también devuelve info de la base de datos, la mostramos
        if "db" in status:
            click.secho(
                f"  Base de datos: {status.get('db', 'desconocido')}", fg="blue"
            )

    except Exception as e:
        click.secho(f"Error al obtener estado de la instancia: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="logs")
@click.argument("name")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--lines", "-n", default=100, help="Number of lines to show")
@click.option(
    "--service",
    type=click.Choice(["web", "db", "all"], case_sensitive=False),
    default="all",
    help="Select service logs: web, db or both",
)
@config_option()
@instance_config_context
def logs_instance(config: str, name: str, follow: bool, lines: int, service: str):
    """Show instance logs."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        logs_output = config_context._use_case_factory.logs_instance_use_case().execute(
            resolved_config,
            tail=lines,
            follow=follow,
            service=service,
        )

        if logs_output:
            click.secho(logs_output, fg="white")
        else:
            click.secho(f"No logs found for instance '{name}'", fg="yellow")

    except Exception as e:
        click.secho(f"Error getting instance logs: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="sync")
@click.argument("name")
@config_option()
@instance_config_context
def sync_instance(config: str, name: str):
    """Synchronize instance with configuration changes."""
    try:
        config_context = click.get_current_context().obj

        click.secho(f"➤ Synchronizing instance '{name}'...", bold=True)

        diffs, new_lock_file = config_context.sync_instance_with_diff(name)

        if not diffs:
            click.secho(f"✔ Instance '{name}' is already synchronized.", fg="green")
            return

        # Display changes
        click.secho("\nChanges detected:", bold=True)
        for diff in diffs:
            field_path = ".".join(diff.path)
            click.secho(f"  {field_path}: {diff.old_value} -> {diff.new_value}")

        click.secho(f"\n✔ Instance '{name}' synchronized successfully.", fg="green")

    except Exception as e:
        click.secho(f"Error synchronizing instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="delete")
@click.argument("name")
@click.option(
    "--force", "-f", is_flag=True, help="Skip confirmation before deleting the instance"
)
@config_option()
@instance_config_context
def delete_instance(config: str, name: str, force: bool):
    """Delete an instance and optionally its data."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        if not force:
            click.confirm(
                f"Are you sure you want to delete the instance '{name}'?",
                abort=True,
            )

        config_context._use_case_factory.delete_instance_use_case().execute(
            resolved_config
        )

        msg = f"\n✔ Instance '{name}' deleted successfully."

        click.secho(msg, fg="green")

    except Exception as e:
        click.secho(f"Error deleting instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="exec")
@click.argument("name")
@click.argument("command", nargs=-1, required=True)
@click.option(
    "--service",
    type=click.Choice(["web", "db", "all"], case_sensitive=False),
    default="web",
    help="Select service where to execute the command (web, db or all).",
)
@config_option()
@instance_config_context
def exec_instance(config: str, name: str, command: tuple, service: str):
    """Execute a command inside an instance container (web, db or both)."""
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.resolve_instance_config(name)

        command_str = " ".join(command)

        result = config_context._use_case_factory.exec_instance_use_case().execute(
            resolved_config,
            command=command_str,
            service=service,
        )

        if result:
            click.secho(result, fg="white")
        else:
            click.secho(f"No output from command in instance '{name}'", fg="yellow")

    except Exception as e:
        click.secho(f"Error executing command: {e}", fg="red")
        raise click.Abort() from e
