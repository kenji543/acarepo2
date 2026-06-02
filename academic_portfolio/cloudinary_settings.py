"""
Cloudinary configuration loaded from the process environment only.

Host platforms (Railway, etc.) must set:
  CLOUDINARY_CLOUD_NAME
  CLOUDINARY_API_KEY
  CLOUDINARY_API_SECRET

Do not hardcode credentials here or in settings defaults.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def _read_env(name: str) -> str:
    return (os.environ.get(name) or "").strip()


def get_cloudinary_credentials() -> dict[str, str]:
    return {
        "cloud_name": _read_env("CLOUDINARY_CLOUD_NAME"),
        "api_key": _read_env("CLOUDINARY_API_KEY"),
        "api_secret": _read_env("CLOUDINARY_API_SECRET"),
    }


def is_cloudinary_configured() -> bool:
    creds = get_cloudinary_credentials()
    return all(creds.values())


def configure_cloudinary() -> bool:
    """
    Initialize the Cloudinary SDK and return True when all credentials are present.
    """
    creds = get_cloudinary_credentials()
    if not is_cloudinary_configured():
        logger.warning(
            "Cloudinary is not fully configured. Set CLOUDINARY_CLOUD_NAME, "
            "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET in the host environment."
        )
        return False

    import cloudinary

    cloudinary.config(
        cloud_name=creds["cloud_name"],
        api_key=creds["api_key"],
        api_secret=creds["api_secret"],
        secure=True,
    )
    return True


def build_django_cloudinary_storage() -> dict[str, str]:
    creds = get_cloudinary_credentials()
    return {
        "CLOUD_NAME": creds["cloud_name"],
        "API_KEY": creds["api_key"],
        "API_SECRET": creds["api_secret"],
    }
