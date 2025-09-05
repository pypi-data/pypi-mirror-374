import os
import subprocess
import time
from multiprocessing import Process

# Third Party Libraries
import pandas as pd
import pytest
import requests
from remote_execution import compare_envs, get_env_metadata, process_big_excel

# Configuration for local testing
CONFIG_PATH = "rem_shop.yaml"
TEST_FILE = "test_data.xlsx"
RESULT_FILE = "result.xlsx"
SERVER_URL = "http://localhost:7777"


def start_server():
    """Start the FastAPI server in a separate process."""
    subprocess.run(
        ["python", "server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


@pytest.fixture(scope="module", autouse=True)
def setup_server():
    """Start the server and ensure it's running before tests."""
    server_process = Process(target=start_server)
    server_process.start()
    time.sleep(2)  # Wait for server to start
    yield
    server_process.terminate()


@pytest.fixture
def setup_test_file():
    """Create a sample Excel file for testing."""
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    df.to_excel(TEST_FILE, index=False)
    yield
    # Cleanup
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    if os.path.exists(RESULT_FILE):
        os.remove(RESULT_FILE)
    # Clear server storage
    remote_storage = "./remote_files"
    if os.path.exists(remote_storage):
        for root, _, files in os.walk(remote_storage):
            for file in files:
                os.remove(os.path.join(root, file))


def test_server_connectivity():
    """Test if the server is running and accessible."""
    response = requests.get(f"{SERVER_URL}/get_env")
    assert response.status_code == 200, "Server is not running or inaccessible"
    assert "python_version" in response.json(), "Environment metadata not returned"


def test_process_big_excel(setup_test_file):
    """Test the full workflow of the decorated function."""
    # Call the decorated function
    result = process_big_excel(file_path=TEST_FILE)

    # Verify the result is a string (from df.describe().to_string())
    assert isinstance(result, str), "Expected string result from process_big_excel"
    assert "mean" in result, "Expected statistical summary in result"

    # Verify the output file was created locally
    assert os.path.exists(RESULT_FILE), "Result file was not synced back"

    # Verify file content
    result_df = pd.read_excel(RESULT_FILE)
    assert result_df.equals(pd.read_excel(TEST_FILE)), "Result file content mismatch"


def test_file_synchronization(setup_test_file):
    """Test file synchronization logic."""
    # Check if file was uploaded to server
    remote_file_path = os.path.join("./remote_files", TEST_FILE)
    assert os.path.exists(remote_file_path), "Test file was not synced to server"

    # Verify MD5 hash
    local_md5 = hashlib.md5(open(TEST_FILE, "rb").read()).hexdigest()
    remote_md5 = hashlib.md5(open(remote_file_path, "rb").read()).hexdigest()
    assert local_md5 == remote_md5, "File content mismatch between local and remote"


def test_environment_comparison():
    """Test environment metadata comparison."""
    local_env = get_env_metadata()
    response = requests.get(f"{SERVER_URL}/get_env")
    remote_env = response.json()
    env_match, env_report = compare_envs(local_env, remote_env)

    if not env_match:
        print(f"Environment mismatch detected:\n{env_report}")
    assert env_match, "Environment mismatch detected, please fix manually"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
