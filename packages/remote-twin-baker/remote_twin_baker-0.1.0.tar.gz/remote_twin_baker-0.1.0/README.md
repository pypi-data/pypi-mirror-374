# Remote Twin Baker

**Remote Twin Baker** is a Python framework for seamless remote task execution. By adding a simple decorator to your Python functions, it automates file synchronization, environment validation, and result retrieval between a local client and a remote server. Designed for data science, AI, edge computing, and collaborative development, it minimizes manual overhead while ensuring consistency across environments.

## Key Features
- **Decorator-Based Execution**: Use `@remote_execution_decorator` to run local Python functions on a remote server.
- **Efficient File Sync**: Transfers only new or modified files using MD5 hash checks.
- **Environment Validation**: Compares client and server environments, reporting mismatches for manual correction.
- **Environment Sync**: Use `utils/merge_env_requirements.py` to merge base and custom requirements and update the remote server.
- **Result Retrieval**: Returns Python objects and new files, with 10-second polling for asynchronous file sync.
- **Scalable Deployment**: Runs a FastAPI server on port 7777, with Nginx for HTTPS in production.
- **Versatile Use Cases**: Supports large-scale data processing, AI model training, IoT, and team collaboration.

## Project Structure
```
remote-twin-baker/
├── LICENSE
├── README.md
├── app/
│   └── server.py              # FastAPI server for remote execution
├── client/
│   └── remote_execution.py    # Client-side decorator logic
├── config.local.yaml          # Local testing configuration
├── config.yaml                # Production configuration
├── nginx/
│   └── remote_twin_baker.conf # Nginx configuration for HTTPS
├── requirements.txt           # Base dependencies for client and server
├── test/
│   └── test_server.py         # Test script for local validation
└── utils/
    └── merge_env_requirements.py # Utility for merging and syncing environments
```

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/remote-twin-baker.git
   cd remote-twin-baker
   ```

2. **Set Up Environment**:
   Create a Python 3.12 Conda/virtual environment:
   ```bash
   conda create -n remote_twin_baker python=3.12
   conda activate remote_twin_baker
   pip install -r requirements.txt
   ```

3. **Configure the Server**:
   - For local testing, use `config.local.yaml` (sets `url: http://localhost:7777`).
   - For production, update `config.yaml` with your server URL (e.g., `https://xxx.com/twin_baker`).

4. **Set Up Nginx (Production)**:
   - Copy `nginx/remote_twin_baker.conf` to `/etc/nginx/conf.d/`.
   - Update SSL certificate paths in the config.
   - Test and reload Nginx:
     ```bash
     nginx -t
     systemctl reload nginx
     ```

## Usage

1. **Start the Server**:
   ```bash
   python app/server.py
   ```
   The server runs on `http://localhost:7777`. In production, Nginx proxies `https://xxx.com/twin_baker` to this port.

2. **Use the Decorator**:
   Apply the decorator to any function:
   ```python
   from client.remote_execution import remote_execution_decorator
   import pandas as pd

   @remote_execution_decorator
   def process_big_excel(file_path: str) -> str:
       df = pd.read_excel(file_path)
       result = df.describe().to_string()
       output_path = "result.xlsx"
       df.to_excel(output_path, index=False)
       return result

   result = process_big_excel(file_path="data.xlsx")
   print(result)
   ```
   This syncs `data.xlsx` to the server, executes the function remotely, and returns the result and `result.xlsx`.

3. **Sync Environments**:
   If an environment mismatch is detected (e.g., during execution or tests), run:
   ```bash
   python utils/merge_env_requirements.py
   ```
   - This merges `requirements.txt` with `custom_requirements.txt` (if exists).
   - Uploads the merged file to the server.
   - Triggers `pip install` on the remote server to align environments.
   - Note: Create `custom_requirements.txt` in the root directory for additional packages.

4. **Run Tests**:
   Validate the system locally:
   ```bash
   python -m pytest test/test_server.py -v
   ```
   Tests verify connectivity, execution, file sync, and environment consistency.

## Developer Tasks
- **Nginx Setup**: Configure SSL certificates and DNS for `xxx.com`. Ensure HTTPS requests to `/twin_baker` proxy to `localhost:7777`.
- **Environment Sync**: Run `utils/merge_env_requirements.py` to align client and server environments. Fix any remaining mismatches manually based on test reports.
- **Server Deployment**: Deploy `app/server.py` on the remote host, ensuring port 7777 is accessible.
- **Configuration**: Update `config.yaml` with the production URL (`https://xxx.com/twin_baker`).

## Testing Locally
1. Activate the environment:
   ```bash
   conda activate remote_twin_baker
   ```
2. Start the server:
   ```bash
   python app/server.py
   ```
3. Run tests:
   ```bash
   python -m pytest test/test_server.py -v
   ```
4. Check for test results and environment mismatch reports.

## Use Cases
- **Data Science/AI**: Offload large Excel processing or model training to remote GPUs.
- **Team Collaboration**: Ensure environment consistency across development, testing, and ops.
- **Edge Computing/IoT**: Enable resource-constrained devices to leverage remote compute power.
- **Personal Projects**: Develop locally while executing heavy tasks on cloud servers.

## Contributing
Submit pull requests or open issues for bugs, features, or improvements. Follow the coding style in existing files.

## License
MIT License