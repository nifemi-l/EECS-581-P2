import os  # Used to build full asset paths
import shutil  # Used to copy files into the assets folder
from typing import Optional  # return type hint
from settings import ASSETS_DIR  # base assets directory


def save_profile_image(source_path: str, username: str) -> Optional[str]:
    """Copy a chosen image into store and return the new path."""
    # Make sure the folder exists
    images_dir = os.path.join(ASSETS_DIR, "images", "profiles")
    os.makedirs(images_dir, exist_ok=True)

    # Keep original extension if available; default to .jpg
    _, ext = os.path.splitext(source_path)
    ext = (ext or ".jpg").lower()
    # Use username-based unique filename
    target_path = os.path.join(images_dir, f"{username}{ext}")
    try:
        # Copy the file into our assets/images directory
        shutil.copyfile(source_path, target_path)
        # Return the path so callers can store it
        return target_path
    except Exception:
        # Any error (missing input, permissions) returns None so UI can show a message
        return None

