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


@click.command(name="create", help="Create a new Odoo instance")
@click.argument("name")
@config_option()
@instance_config_context
def create_instance(config: str, name: str):
    """Create a new Odoo instance with repositories, dependencies, and containers.

    Creates a complete Odoo instance including:
    - Cloning and setting up repositories
    - Installing Python dependencies
    - Generating configuration files (odoo.conf)
    - Creating and starting Docker containers
    - Generating lock file for version tracking

    Example:
        dooservice instance create my-project
    """
    try:
        config_context = click.get_current_context().obj

        # Validate instance exists in configuration
        config_context.config_service.get_instance_config(name)

        # Display instance details before creation
        resolved_display_config = config_context.config_service.resolve_instance_config(
            name
        )

        click.secho(f"➤ Preparing to create instance '{name}'...", bold=True)
        config_context._msg.info("Instance Details:")
        config_context._msg.info("  Name: %s", name)
        config_context._msg.info(
            "  Odoo Version: %s", resolved_display_config.odoo_version
        )
        config_context._msg.info(
            "  Data Directory: %s", resolved_display_config.data_dir
        )

        if resolved_display_config.repositories:
            config_context._msg.info("  Repositories:")
            for repo_name, repo_config in resolved_display_config.repositories.items():
                config_context._msg.info(
                    "    - %s: %s (Branch: %s)",
                    repo_name,
                    repo_config.repository_url,
                    repo_config.branch,
                )

        if resolved_display_config.python_dependencies:
            config_context._msg.info("  Python Dependencies:")
            for dep in resolved_display_config.python_dependencies:
                config_context._msg.info("    - %s", dep)

        # Execute creation with progress
        click.secho(f"\n➤ Creating instance '{name}'...", bold=True)

        # Execute core creation logic through use case
        config_context._msg.progress("Executing instance creation...")
        config_context.create_instance_use_case.execute(resolved_display_config)
        config_context._msg.progress("Executing instance creation...", completed=True)

        # Install Python dependencies if needed
        if resolved_display_config.python_dependencies:
            config_context._msg.progress("Installing Python dependencies...")
            config_context.create_instance_use_case.install_dependencies(
                resolved_display_config
            )
            config_context._msg.progress(
                "Installing Python dependencies...", completed=True
            )

        # Generate and save lock file
        config_context._msg.progress("Generating lock file...")
        config_context.lock_file_manager.generate_and_save_lock_file(
            config_context.config_service.dooservice_config,
            name,
            resolved_display_config,
        )
        config_context._msg.progress("Generating lock file...", completed=True)

        # Start instance
        config_context._msg.progress("Starting instance...")
        config_context.instance_repo.start(
            resolved_display_config.deployment.docker.web.container_name
        )
        config_context._msg.progress("Starting instance...", completed=True)

        config_context._msg.success("Instance '%s' created successfully!", name)

    except (ConfigValidationError, InstanceExistsError) as e:
        try:
            config_context = click.get_current_context().obj
            config_context._msg.error("Configuration Error: %s", e)
        except (AttributeError, RuntimeError):
            click.secho(f"Configuration Error: {e}", fg="red")
        raise click.Abort() from e
    except Exception as e:
        try:
            config_context = click.get_current_context().obj
            config_context._msg.error("An unexpected error occurred: %s", e)
        except (AttributeError, RuntimeError):
            click.secho(f"An unexpected error occurred: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="start", help="Start an existing instance")
@click.argument("name")
@config_option()
@instance_config_context
def start_instance(config: str, name: str):
    """Start an existing Odoo instance by starting its Docker containers.

    Starts the database and web containers for the specified instance
    in the correct order (database first, then web service).

    Example:
        dooservice instance start my-project
    """
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.config_service.resolve_instance_config(name)
        config_context._use_case_factory.start_instance_use_case().execute(
            resolved_config
        )

        click.secho(f"✔ Instance '{name}' started successfully.", fg="green")

    except Exception as e:
        click.secho(f"Error starting instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="stop", help="Stop a running instance")
@click.argument("name")
@config_option()
@instance_config_context
def stop_instance(config: str, name: str):
    """Stop a running Odoo instance by stopping its Docker containers.

    Gracefully stops the web and database containers for the specified
    instance in the correct order (web first, then database).

    Example:
        dooservice instance stop my-project
    """
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.config_service.resolve_instance_config(name)

        config_context._use_case_factory.stop_instance_use_case().execute(
            resolved_config
        )

        click.secho(f"✔ Instance '{name}' stopped successfully.", fg="green")

    except Exception as e:
        click.secho(f"Error stopping instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="status", help="Show instance status")
@click.argument("name")
@config_option()
@instance_config_context
def status_instance(config: str, name: str):
    """Display the current status of an Odoo instance and its services.

    Shows the running state of all containers (web, database) and
    provides an overall instance status summary.

    Status values:
    - running: All services are running
    - stopped: All services are stopped
    - partial: Some services are running
    - error: Status could not be determined

    Example:
        dooservice instance status my-project
    """
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.config_service.resolve_instance_config(name)

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


@click.command(name="logs", help="Display instance logs")
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
    """Display logs from instance containers with filtering options.

    Shows real-time or historical logs from the specified instance's containers.
    Use --follow to stream logs in real-time, or --lines to limit output.

    Options:
    - --service: Choose which service logs to show (web, db, or all)
    - --follow/-f: Stream logs continuously (like tail -f)
    - --lines/-n: Number of historical log lines to display

    Examples:
        dooservice instance logs my-project
        dooservice instance logs my-project --service web --follow
        dooservice instance logs my-project --lines 50
    """
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.config_service.resolve_instance_config(name)

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


@click.command(name="sync", help="Synchronize instance with config changes")
@click.argument("name")
@config_option()
@instance_config_context
def sync_instance(config: str, name: str):
    """Synchronize an existing instance with configuration file changes.

    Detects and applies changes between the current dooservice.yml configuration
    and the locked configuration from when the instance was created or last synced.

    Synchronization includes:
    - Repository updates (new repositories, branch changes, URL changes)
    - Environment variable updates
    - Database credential synchronization
    - Container recreation if needed
    - Configuration file regeneration

    Requires a valid lock file from a previous create or sync operation.

    Example:
        dooservice instance sync my-project
    """
    try:
        config_context = click.get_current_context().obj

        click.secho(f"➤ Synchronizing instance '{name}'...", bold=True)

        # Check lock file exists
        lock_file = config_context.lock_file_manager.load_lock_file()
        if not lock_file:
            config_context._msg.error(
                "No lock file found. Please create instance first."
            )
            raise click.Abort()

        # Get configurations
        resolved_instance_config = (
            config_context.config_service.resolve_instance_config(name)
        )
        locked_instance_config = lock_file.instances.items.get(name)

        # Compare configurations
        diffs = config_context.diff_manager.compare(
            locked_instance_config, resolved_instance_config
        )

        if not diffs:
            config_context._msg.success("Instance '%s' is already synchronized.", name)
            return

        # Display changes
        config_context._msg.info("Changes detected:")
        for diff in diffs:
            field_path = ".".join(diff.path)
            config_context._msg.info(
                "  %s: %s -> %s", field_path, diff.old_value, diff.new_value
            )

        # Sync database credentials BEFORE other synchronization if needed
        config_context.sync_instance_use_case.sync_database_credentials_if_needed(
            diffs, resolved_instance_config, locked_instance_config
        )

        # Execute synchronization through use case
        config_context.sync_instance_use_case.execute(
            resolved_instance_config, locked_instance_config
        )

        # Generate new lock file
        config_context.lock_file_manager.generate_and_save_lock_file(
            config_context.config_service.dooservice_config,
            name,
            resolved_instance_config,
        )

        config_context._msg.success("Instance '%s' synchronized successfully.", name)

    except Exception as e:
        try:
            config_context = click.get_current_context().obj
            config_context._msg.error("Error synchronizing instance: %s", e)
        except (AttributeError, RuntimeError):
            click.secho(f"Error synchronizing instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="delete", help="Delete an instance and its containers")
@click.argument("name")
@click.option(
    "--force", "-f", is_flag=True, help="Skip confirmation before deleting the instance"
)
@config_option()
@instance_config_context
def delete_instance(config: str, name: str, force: bool):
    """Completely remove an Odoo instance and its Docker containers.

    Permanently deletes all containers associated with the instance and
    optionally removes data directories. This action cannot be undone.

    The deletion process:
    1. Stops all running containers gracefully
    2. Removes web and database containers
    3. Removes associated data directories (with confirmation)

    Use --force to skip confirmation prompts (use with caution).

    Example:
        dooservice instance delete my-project
        dooservice instance delete my-project --force
    """
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.config_service.resolve_instance_config(name)

        if not force:
            click.confirm(
                f"Are you sure you want to delete the instance '{name}'?",
                abort=True,
            )

        config_context._use_case_factory.delete_instance_use_case().execute(
            resolved_config, True
        )

        msg = f"\n✔ Instance '{name}' deleted successfully."

        click.secho(msg, fg="green")

    except Exception as e:
        click.secho(f"Error deleting instance: {e}", fg="red")
        raise click.Abort() from e


@click.command(name="exec", help="Execute commands inside containers")
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
    r"""Execute shell commands inside instance containers.

    Runs the specified command inside the selected container(s) and
    displays the output. Useful for debugging, maintenance, and
    running Odoo-specific commands.

    Options:
    - --service: Choose which container to execute in (web, db, or all)

    Common use cases:
    - Database operations: --service db
    - Odoo CLI commands: --service web
    - System maintenance: --service all

    Examples:
        dooservice instance exec my-project ls -la
        dooservice instance exec my-project --service web odoo --help
        dooservice instance exec my-project --service db psql -U odoo -c \\
            "SELECT version();"
    """
    try:
        config_context = click.get_current_context().obj
        resolved_config = config_context.config_service.resolve_instance_config(name)

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
