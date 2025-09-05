import hashlib
import os
import pickle
import sys
from typing import Dict, List

# Third Party Libraries
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response

app = FastAPI()

# Server-side file storage
FILE_STORAGE = "./remote_files"
os.makedirs(FILE_STORAGE, exist_ok=True)


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
        python_version = sys.version
        pip_freeze = (
            subprocess.check_output([sys.executable, "-m", "pip", "freeze"])
            .decode()
            .strip()
            .split("\n")
        )
        return {"python_version": python_version, "packages": pip_freeze}
    except Exception as e:
        return {"error": f"Failed to capture env metadata: {str(e)}"}


@app.get("/get_env")
async def get_env():
    """Return server environment metadata."""
    return get_env_metadata()


@app.post("/check_files")
async def check_files(manifest: List[Dict]) -> Dict:
    """Check which files need to be uploaded."""
    files_to_upload = []
    for file_info in manifest:
        file_path = os.path.join(FILE_STORAGE, file_info["path"])
        if not os.path.exists(file_path) or get_file_md5(file_path) != file_info["md5"]:
            files_to_upload.append(file_info)
    return {"files_to_upload": files_to_upload}


@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    """Handle file uploads."""
    file_path = os.path.join(FILE_STORAGE, file.filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"status": "success"}


@app.post("/execute")
async def execute_function(payload: Dict):
    """Execute the function remotely."""
    try:
        func = pickle.loads(bytes.fromhex(payload["function"]))
        args = pickle.loads(bytes.fromhex(payload["args"]))
        kwargs = pickle.loads(bytes.fromhex(payload["kwargs"]))

        # Execute function
        result = func(*args, **kwargs)

        # Find new files generated during execution
        new_files = []
        for root, _, files in os.walk(FILE_STORAGE):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, FILE_STORAGE)
                new_files.append({"path": rel_path, "md5": get_file_md5(file_path)})

        return {"result": pickle.dumps(result).hex(), "new_files": new_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/check_new_files")
async def check_new_files():
    """Check for new files generated during execution."""
    new_files = []
    for root, _, files in os.walk(FILE_STORAGE):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, FILE_STORAGE)
            new_files.append({"path": rel_path, "md5": get_file_md5(file_path)})
    return {"new_files": new_files}


@app.get("/download_file")
async def download_file(path: str):
    """Download a file from the server."""
    file_path = os.path.join(FILE_STORAGE, path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, "rb") as f:
        return Response(content=f.read(), media_type="application/octet-stream")


if __name__ == "__main__":
    # Third Party Libraries
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7777)
