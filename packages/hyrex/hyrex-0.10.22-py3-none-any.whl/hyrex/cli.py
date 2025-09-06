import multiprocessing as mp
import tempfile
from datetime import datetime
from importlib.metadata import version, PackageNotFoundError

# To ensure consistency between MacOS and Linux
try:
    mp.set_start_method("spawn")
except RuntimeError:
    # Context already set, which is fine
    pass


import cProfile
import importlib
import os
import pstats
import sys
from pathlib import Path

import typer

from hyrex import constants
from hyrex.env_vars import EnvVars
from hyrex.init_db import init_postgres_db
from hyrex.worker.root_process import WorkerRootProcess


def get_hyrex_version():
    """Get the installed hyrex package version."""
    try:
        return version("hyrex")
    except PackageNotFoundError:
        return "unknown"


def load_env_file():
    """Load .env file if it exists in the current directory."""
    try:
        from dotenv import load_dotenv
        env_path = Path.cwd() / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            return True
    except ImportError:
        env_path = Path.cwd() / ".env"
        if env_path.exists():
            print("Warning: python-dotenv not installed, skipping .env file loading")
    return False

# Load .env file on module import
load_env_file()

cli = typer.Typer()


@cli.command()
def init():
    """
    Initialize a new Hyrex project with interactive setup
    """
    from hyrex.hyrex_init import main as init_main
    init_main()


@cli.command()
def init_db(
    database_string: str = typer.Option(
        None,
        "--database-string",
        help="Database connection string",
    )
):
    """
    Creates the tables for hyrex tasks/workers in the given Postgres database
    """
    # Get database string from option or environment
    if not database_string:
        database_string = os.getenv(EnvVars.DATABASE_URL)
    
    if os.getenv(EnvVars.API_KEY) is not None:
        typer.echo(f"{EnvVars.API_KEY} is set. Skipping database initialization.")
        return

    if database_string:
        init_postgres_db(database_string)
        typer.echo("Hyrex tables initialized.")
        return

    typer.echo(
        f"Error: Database connection string must be provided either through the --database-string flag or the {EnvVars.DATABASE_URL} env variable."
    )


def validate_app_module_path(app_module_path):
    try:
        sys.path.append(str(Path.cwd()))
        module_path, instance_name = app_module_path.split(":")
        # Import the worker module
        app_module = importlib.import_module(module_path)
        app_instance = getattr(app_module, instance_name)
    except ModuleNotFoundError as e:
        typer.echo(f"Error: {e}")
        sys.exit(1)


# Profile a specific function
def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()

    # Create a temporary file with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    profile_dir = tempfile.gettempdir()  # Gets the system temp directory
    profile_path = os.path.join(profile_dir, f"hyrex_profile_{timestamp}.prof")

    # Save stats to the file
    stats = pstats.Stats(profiler)
    stats.dump_stats(profile_path)

    # Also print the top 20 time-consuming calls to console
    stats.sort_stats("cumulative")
    stats.print_stats(20)

    # Print the file path for reference
    print(f"\nProfile data saved to: {profile_path}")

    return result


@cli.command()
def run_worker(
    app_module_path: str = typer.Argument(..., help="Module path to the Hyrex app"),
    queue_pattern: str = typer.Option(
        constants.ANY_QUEUE,
        "--queue-pattern",
        "-q",
        help="Which queue(s) to pull tasks from. Glob patterns supported. Defaults to `*`",
    ),
    num_processes: int = typer.Option(
        8, "--num-processes", "-p", help="Number of executor processes to run"
    ),
    log_level: str = typer.Option(
        "INFO",
        "--log-level",
        "-l",
        help="Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        case_sensitive=False,
        show_default=True,
    ),
    profiling: bool = False,
):
    """
    Run a Hyrex worker for the specified app module path
    """
    # Print ASCII logo as first action
    print(constants.ASCII_HYREX_LOGO)
    
    # Print hyrex version
    hyrex_version = get_hyrex_version()
    print(f"Hyrex version: {hyrex_version}\n")
    
    database_url = os.environ.get(EnvVars.DATABASE_URL)

    if not database_url and not os.environ.get(EnvVars.API_KEY):
        raise EnvironmentError(
            f"Either {EnvVars.DATABASE_URL} (local) or {EnvVars.API_KEY} (Hyrex Cloud) must be set to run Hyrex worker."
        )

    # Try to initialize DB in worker
    if database_url:
        init_db(database_string=database_url)

    # Prevents HyrexRegistry instances from creating their own dispatchers
    os.environ[EnvVars.WORKER_PROCESS] = "true"

    validate_app_module_path(app_module_path)
    # TODO: Validate queue pattern?

    try:
        worker_root = WorkerRootProcess(
            log_level=log_level.upper(),
            app_module_path=app_module_path,
            queue_pattern=queue_pattern,
            num_processes=num_processes,
        )

        if profiling:
            profile_function(worker_root.run)  # Pass the function, not the result
        else:
            worker_root.run()

    except Exception as e:
        typer.echo(f"Error running worker: {e}")
        sys.exit(1)


@cli.command()
def studio(
    port: int = typer.Option(
        int(os.getenv("STUDIO_PORT", 1337)),
        "--port",
        "-p",
        help="Port to run the studio server on",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
):
    """
    Run Hyrex Studio server for database inspection and query execution
    """
    database_url = os.environ.get(EnvVars.DATABASE_URL) or os.environ.get("PGURL")
    
    if not database_url:
        typer.echo(
            f"Error: Database connection string must be provided through HYREX_DATABASE_URL or PGURL environment variable."
        )
        sys.exit(1)
    
    # Set environment variables for the studio server
    os.environ["STUDIO_PORT"] = str(port)
    if verbose:
        os.environ["STUDIO_VERBOSE"] = "true"
    
    try:
        from hyrex.hyrex_studio_server import main
        
        # The studio server handles its own startup
        main()
    except ImportError as e:
        typer.echo(f"Error importing studio server: {e}")
        if "asyncpg" in str(e).lower():
            typer.echo("Install it with: pip install asyncpg")
        elif "colorama" in str(e).lower():
            typer.echo("Install it with: pip install colorama")
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Error running studio server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
