from daydream.cli.graph._app import graph_app
from daydream.cli.graph._background import (
    cleanup_pid_file,
    get_log_file,
    get_pid_file,
    is_process_running,
)
from daydream.cli.options import PROFILE_OPTION


@graph_app.command()
def status(profile: str = PROFILE_OPTION) -> None:
    """Check if graph build is running"""
    pid_file = get_pid_file(profile)

    if not pid_file.exists():
        print(f"No graph build running for profile '{profile}'")
        return

    try:
        pid = int(pid_file.read_text().strip())
        if is_process_running(pid):
            print(f"Graph build running for profile '{profile}' (PID: {pid})")

            # Show log file info if it exists
            log_file = get_log_file(profile)
            if log_file.exists():
                print(f"View logs: daydream graph logs --profile {profile} --follow")
        else:
            print(f"Stale PID file found for profile '{profile}', cleaning up...")
            cleanup_pid_file(profile)
    except ValueError:
        print(f"Corrupted PID file found for profile '{profile}', cleaning up...")
        cleanup_pid_file(profile)
