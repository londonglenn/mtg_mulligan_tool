from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os

import joblib
import requests


# =========================================================
# CONFIG
# =========================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_CACHE_DIR = PROJECT_ROOT / "model_cache"
MANIFEST_CACHE_PATH = MODEL_CACHE_DIR / "latest_manifest.json"

MODEL_LATEST_URL = os.environ.get(
    "MODEL_LATEST_URL",
    "https://mulligan-server.onrender.com/model/latest",
)
MODEL_FILES_BASE_URL = os.environ.get(
    "MODEL_FILES_BASE_URL",
    "https://mulligan-server.onrender.com/model/files",
)

REQUEST_TIMEOUT = 20


# =========================================================
# LOCAL JSON / PATH HELPERS
# =========================================================
def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_json(path: str | Path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str | Path, obj) -> None:
    path = Path(path)
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def get_cached_file_paths() -> dict[str, Path]:
    return {
        "cache_dir": MODEL_CACHE_DIR,
        "manifest": MANIFEST_CACHE_PATH,
        "model": MODEL_CACHE_DIR / "model.pkl",
        "feature_columns": MODEL_CACHE_DIR / "feature_columns.json",
        "metadata": MODEL_CACHE_DIR / "metadata.json",
        "metrics": MODEL_CACHE_DIR / "metrics.json",
    }


# =========================================================
# HASH HELPERS
# =========================================================
def sha256_file(path: Path, chunk_size: int = 8192) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


# =========================================================
# REMOTE HELPERS
# =========================================================
def fetch_remote_manifest() -> dict:
    response = requests.get(MODEL_LATEST_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def build_remote_file_url(filename: str) -> str:
    return f"{MODEL_FILES_BASE_URL}/{filename}"


def download_file(url: str, destination: Path) -> None:
    ensure_dir(destination.parent)

    response = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


# =========================================================
# CACHE HELPERS
# =========================================================
def load_cached_manifest() -> dict | None:
    return read_json(MANIFEST_CACHE_PATH, default=None)


def has_complete_cached_bundle() -> bool:
    paths = get_cached_file_paths()
    required = [
        paths["manifest"],
        paths["model"],
        paths["feature_columns"],
        paths["metadata"],
        paths["metrics"],
    ]
    return all(path.exists() for path in required)


def verify_cached_bundle(manifest: dict | None = None) -> bool:
    paths = get_cached_file_paths()

    required = {
        "model.pkl": paths["model"],
        "feature_columns.json": paths["feature_columns"],
        "metadata.json": paths["metadata"],
        "metrics.json": paths["metrics"],
    }

    if not all(path.exists() for path in required.values()):
        return False

    manifest = manifest or load_cached_manifest()
    if not manifest:
        return True

    sha_map = manifest.get("sha256", {})
    if not sha_map:
        return True

    for filename, path in required.items():
        expected = sha_map.get(filename)
        if not expected:
            continue
        actual = sha256_file(path)
        if actual != expected:
            return False

    return True


def load_cached_bundle(status: str = "cached") -> dict | None:
    if not has_complete_cached_bundle():
        return None

    manifest = load_cached_manifest()
    if not verify_cached_bundle(manifest):
        return None

    paths = get_cached_file_paths()

    model = joblib.load(paths["model"])
    feature_columns = read_json(paths["feature_columns"], default=[])
    metadata = read_json(paths["metadata"], default={})
    metrics = read_json(paths["metrics"], default={})

    bundle_version = None
    if manifest:
        bundle_version = manifest.get("bundle_version") or manifest.get("latest_version")

    bundle_version = (
        bundle_version
        or metadata.get("bundle_version")
        or metadata.get("model_version")
        or metadata.get("run_id")
        or "cached"
    )

    return {
        "status": status,
        "source": "cache",
        "bundle_version": bundle_version,
        "run_id": metadata.get("run_id"),
        "model": model,
        "feature_columns": feature_columns,
        "metadata": metadata,
        "metrics": metrics,
        "manifest": manifest or {},
    }


# =========================================================
# DOWNLOAD / UPDATE
# =========================================================
def download_and_cache_bundle(manifest: dict) -> dict:
    files = manifest.get("files", {})
    if not files:
        raise ValueError("Manifest missing 'files' section.")

    paths = get_cached_file_paths()
    ensure_dir(paths["cache_dir"])

    mapping = {
        "model": paths["model"],
        "feature_columns": paths["feature_columns"],
        "metadata": paths["metadata"],
        "metrics": paths["metrics"],
    }

    for key, local_path in mapping.items():
        remote_name = files.get(key)
        if not remote_name:
            raise ValueError(f"Manifest missing files['{key}'].")

        url = build_remote_file_url(remote_name)
        download_file(url, local_path)

    write_json(paths["manifest"], manifest)

    if not verify_cached_bundle(manifest):
        raise ValueError("Downloaded model bundle failed checksum verification.")

    bundle = load_cached_bundle(status="ready")
    if bundle is None:
        raise ValueError("Downloaded model bundle could not be loaded.")

    return bundle


def is_remote_newer(remote_manifest: dict, local_manifest: dict | None) -> bool:
    if local_manifest is None:
        return True

    remote_version = (
        remote_manifest.get("bundle_version")
        or remote_manifest.get("latest_version")
    )
    local_version = (
        local_manifest.get("bundle_version")
        or local_manifest.get("latest_version")
    )

    return remote_version != local_version


# =========================================================
# MAIN ENTRY POINT
# =========================================================
def initialize_model_bundle() -> dict | None:
    local_manifest = load_cached_manifest()

    try:
        remote_manifest = fetch_remote_manifest()

        if is_remote_newer(remote_manifest, local_manifest) or not has_complete_cached_bundle():
            return download_and_cache_bundle(remote_manifest)

        cached = load_cached_bundle(status="ready")
        if cached is not None:
            return cached

    except Exception as e:
        print(f"Model sync warning: {e}")

    cached = load_cached_bundle(status="cached")
    if cached is not None:
        return cached

    return None