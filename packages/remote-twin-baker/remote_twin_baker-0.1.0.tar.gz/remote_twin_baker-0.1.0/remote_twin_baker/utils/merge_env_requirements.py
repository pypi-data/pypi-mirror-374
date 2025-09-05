import os
import sys

# Third Party Libraries
import requests

# Local Libraries
from remote_twin_baker.utils.paths import to_absolute_path
from remote_twin_baker.utils.util import load_config


def merge_requirements(
    base_path: str = "requirements.txt", custom_path: str = "custom_requirements.txt"
) -> str:
    """Merge base and custom requirements into a single file."""
    requirements = set()

    # Convert to absolute paths
    base_path = to_absolute_path(base_path)
    custom_path = to_absolute_path(custom_path)

    # Read base requirements
    if os.path.exists(base_path):
        with open(base_path, "r") as f:
            requirements.update(
                line.strip() for line in f if line.strip() and not line.startswith("#")
            )

    # Read custom requirements if available
    if os.path.exists(custom_path):
        with open(custom_path, "r") as f:
            requirements.update(
                line.strip() for line in f if line.strip() and not line.startswith("#")
            )

    # Write merged requirements
    merged_path = to_absolute_path("merged_requirements.txt")
    with open(merged_path, "w") as f:
        for req in sorted(requirements):
            f.write(f"{req}\n")

    return merged_path

def sync_env_to_remote(merged_path: str):
    """Upload merged requirements to remote server and trigger update."""
    merged_path = to_absolute_path(merged_path)
    config = load_config()
    server_url = config["server"]["url"]
    endpoint = config["server"]["endpoints"]["update_env"]

    with open(merged_path, "rb") as f:
        files = {"file": (os.path.basename(merged_path), f)}
        response = requests.post(f"{server_url}{endpoint}", files=files)

    if response.status_code == 200:
        print("Environment sync successful.")
    else:
        print(f"Environment sync failed: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    merged_path = merge_requirements()
    if merged_path:
        sync_env_to_remote(merged_path)
        os.remove(merged_path)  # Clean up merged file
    else:
        print("No requirements to merge.")