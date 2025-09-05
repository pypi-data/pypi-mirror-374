import hashlib
import inspect
import os
import pickle
import subprocess
import sys
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Tuple

# Third Party Libraries
import requests
import yaml


# Load configuration from config.yaml or config.local.yaml
def load_config(config_path: str = "config.yaml") -> Dict:
    if not os.path.exists(config_path):
        config_path = "config.local.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


CONFIG = load_config()
SERVER_URL = CONFIG["server"]["url"]
ENDPOINTS = CONFIG["server"]["endpoints"]


def get_file_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_env_metadata() -> Dict:
    """Capture Conda/virtualenv metadata."""
    try:
        # Get Python version and pip freeze output
        python_version = sys.version
        pip_freeze = (
            subprocess.check_output([sys.executable, "-m", "pip", "freeze"])
            .decode()
            .strip()
            .split("\n")
        )
        env_info = {"python_version": python_version, "packages": pip_freeze}
        return env_info
    except Exception as e:
        return {"error": f"Failed to capture env metadata: {str(e)}"}


def compare_envs(local_env: Dict, remote_env: Dict) -> Tuple[bool, str]:
    """Compare local and remote environment metadata, return report if different."""
    if local_env.get("error") or remote_env.get("error"):
        return False, "Environment capture failed on one or both sides."

    if local_env["python_version"] != remote_env["python_version"]:
        report = f"Python version mismatch:\nLocal: {local_env['python_version']}\nRemote: {remote_env['python_version']}"
        return False, report

    local_packages = set(local_env["packages"])
    remote_packages = set(remote_env["packages"])
    if local_packages != remote_packages:
        missing_in_remote = local_packages - remote_packages
        missing_in_local = remote_packages - local_packages
        report = f"Package mismatch detected:\nMissing in remote: {missing_in_remote}\nMissing in local: {missing_in_local}"
        return False, report

    return True, "Environments match."


def find_referenced_files(func: Callable, args: tuple, kwargs: Dict) -> List[str]:
    """Find file paths referenced in function arguments and source code."""
    file_paths = []

    # Check args and kwargs for file paths
    for arg in list(args) + list(kwargs.values()):
        if isinstance(arg, str) and os.path.isfile(arg):
            file_paths.append(arg)

    # Inspect source code for file references
    source = inspect.getsource(func)
    for line in source.split("\n"):
        if "open(" in line or "Path(" in line:
            # Extract potential file paths (simple heuristic)
            parts = line.split('"') + line.split("'")
            for part in parts:
                if os.path.isfile(part):
                    file_paths.append(part)

    return list(set(file_paths))


def serialize_function(func: Callable) -> bytes:
    """Serialize a function for transmission."""
    return pickle.dumps(func)


def deserialize_function(func_bytes: bytes) -> Callable:
    """Deserialize a function from bytes."""
    return pickle.loads(func_bytes)


def serialize_file(file_path: str) -> bytes:
    """Serialize a file to bytes."""
    with open(file_path, "rb") as f:
        return f.read()


def deserialize_file(file_bytes: bytes, file_path: str) -> None:
    """Deserialize bytes to a file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file_bytes)


def remote_execution_decorator(func: Callable) -> Callable:
    """Decorator to handle remote execution and file synchronization."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Step 1: Clearpoint - Find referenced files
        file_paths = find_referenced_files(func, args, kwargs)

        # Step 2: Send file manifest and check with server
        manifest = []
        for path in file_paths:
            if os.path.exists(path):
                manifest.append({"path": path, "md5": get_file_md5(path)})

        response = requests.post(
            f"{SERVER_URL}{ENDPOINTS['check_files']}", json=manifest
        )
        files_to_upload = response.json().get("files_to_upload", [])

        # Step 3: Upload only necessary files
        for file_info in files_to_upload:
            file_path = file_info["path"]
            file_bytes = serialize_file(file_path)
            requests.post(
                f"{SERVER_URL}{ENDPOINTS['upload_file']}",
                files={"file": (file_path, file_bytes)},
            )

        # Step 4: Send function and execute remotely
        func_bytes = serialize_function(func)
        payload = {
            "function": func_bytes.hex(),
            "args": pickle.dumps(args).hex(),
            "kwargs": pickle.dumps(kwargs).hex(),
        }
        response = requests.post(f"{SERVER_URL}{ENDPOINTS['execute']}", json=payload)
        result_data = response.json()

        # Step 5: Handle results and poll for new files
        result = pickle.loads(bytes.fromhex(result_data["result"]))
        new_files = result_data.get("new_files", [])

        # Download new files
        for file_info in new_files:
            file_path = file_info["path"]
            if (
                not os.path.exists(file_path)
                or get_file_md5(file_path) != file_info["md5"]
            ):
                file_response = requests.get(
                    f"{SERVER_URL}{ENDPOINTS['download_file']}?path={file_path}"
                )
                deserialize_file(file_response.content, file_path)

        # Poll for additional files (10-second intervals, max 30 seconds)
        start_time = time.time()
        while time.time() - start_time < 30:
            response = requests.get(f"{SERVER_URL}{ENDPOINTS['check_new_files']}")
            new_files = response.json().get("new_files", [])
            for file_info in new_files:
                file_path = file_info["path"]
                if (
                    not os.path.exists(file_path)
                    or get_file_md5(file_path) != file_info["md5"]
                ):
                    file_response = requests.get(
                        f"{SERVER_URL}{ENDPOINTS['download_file']}?path={file_path}"
                    )
                    deserialize_file(file_response.content, file_path)
            if not new_files:
                break
            time.sleep(10)

        # Check environment compatibility
        local_env = get_env_metadata()
        response = requests.get(f"{SERVER_URL}{ENDPOINTS['get_env']}")
        remote_env = response.json()
        env_match, env_report = compare_envs(local_env, remote_env)
        if not env_match:
            print(
                f"Environment mismatch detected. Please run 'python utils/merge_env_requirements.py' to sync or fix manually:\n{env_report}"
            )

        return result

    return wrapper


# Example usage
@remote_execution_decorator
def process_big_excel(file_path: str) -> str:
    """Example function to process an Excel file."""
    # Third Party Libraries
    import pandas as pd

    df = pd.read_excel(file_path)
    result = df.describe().to_string()
    output_path = "result.xlsx"
    df.to_excel(output_path, index=False)
    return result


if __name__ == "__main__":
    # Example call
    result = process_big_excel(file_path="data.xlsx")
    print(result)
