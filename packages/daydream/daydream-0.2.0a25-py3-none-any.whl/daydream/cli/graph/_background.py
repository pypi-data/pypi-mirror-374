import os
from pathlib import Path

from daydream.config.utils import get_config_dir


def get_pid_file(profile: str) -> Path:
    """Get the PID file path for a given profile graph build"""
    return get_config_dir(profile) / "graph_build.pid"


def get_log_file(profile: str) -> Path:
    """Get the log file path for a given profile graph build"""
    return get_config_dir(profile) / "graph_build.log"


def is_process_running(pid: int) -> bool:
    """Check if a process with given PID is running"""
    try:
        # Send signal 0 to check if process exists (doesn't actually kill it)
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def check_and_create_lock(profile: str) -> bool:
    """Returns True if we can proceed, False if already running"""
    pid_file = get_pid_file(profile)

    if pid_file.exists():
        try:
            existing_pid = int(pid_file.read_text().strip())
            if is_process_running(existing_pid):
                print(f"Graph build already running for profile '{profile}' (PID: {existing_pid})")
                print(f"Use 'daydream graph stop --profile {profile}' to stop it if needed")
                return False
            else:
                # Stale PID file, remove it
                print("Found stale PID file, cleaning up...")
                pid_file.unlink()
        except (ValueError, FileNotFoundError):
            # Corrupted or missing file, remove it
            pid_file.unlink(missing_ok=True)

    return True


def create_pid_file(profile: str, pid: int) -> None:
    """Create PID file with given process ID"""
    pid_file = get_pid_file(profile)
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(pid))


def cleanup_pid_file(profile: str) -> None:
    get_pid_file(profile).unlink(missing_ok=True)
