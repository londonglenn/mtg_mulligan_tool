from __future__ import annotations

from pathlib import Path
import requests

from config import UPLOAD_URL


def upload_results(file_path: Path, username: str, deck_name: str, client_version: str = "0.1.0") -> tuple[bool, str]:
    """
    Upload a CSV results file to the server.

    Returns:
        (success, message)
    """
    if not file_path.exists():
        return False, f"Results file does not exist: {file_path}"

    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                UPLOAD_URL,
                files={"file": (file_path.name, f, "text/csv")},
                data={
                    "username": username,
                    "deck_name": deck_name,
                    "client_version": client_version,
                },
                timeout=30,
            )

        if response.status_code == 200:
            return True, "Upload successful."

        return False, f"Upload failed: {response.status_code} {response.text}"

    except Exception as e:
        return False, f"Upload error: {e}"