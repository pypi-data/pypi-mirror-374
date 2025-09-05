"""Utility functions for Builder MCP server."""

import logging
import sys
from pathlib import Path
from typing import Any, cast

import yaml


def initialize_logging() -> None:
    """Initialize logging configuration for the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


def _filter_config_secrets_recursive(
    config_obj: dict[str, Any] | list[Any] | Any,  # noqa: ANN401
) -> dict[str, Any] | list[Any] | Any:  # noqa: ANN401
    """Recursively filter sensitive information from configuration.

    Args:
        config_obj: Configuration object (dict, list, or any other type)

    Returns:
        Configuration object with sensitive values masked
    """
    if isinstance(config_obj, dict):
        filtered = config_obj.copy()
        sensitive_keys = {
            "password",
            "token",
            "key",
            "secret",
            "credential",
            "api_key",
            "access_token",
            "refresh_token",
            "client_secret",
        }

        for key, value in filtered.items():
            if isinstance(value, dict | list):
                filtered[key] = _filter_config_secrets_recursive(value)
            elif any(sensitive in key.lower() for sensitive in sensitive_keys):
                filtered[key] = "***REDACTED***"

        return filtered

    if isinstance(config_obj, list):
        return [_filter_config_secrets_recursive(item) for item in config_obj]

    return config_obj


def filter_config_secrets(
    config: dict[str, Any],
) -> dict[str, Any]:
    """Filter sensitive information from configuration for logging.

    This function calls a recursive implementation which works on any input type.
    However, the return type of this function is always the same as its input (a dictionary).

    Args:
        config: Configuration dictionary, list, or other value that may contain secrets

    Returns:
        Configuration dictionary with sensitive values masked
    """
    return cast(
        dict[str, Any],  # noqa: TC006
        _filter_config_secrets_recursive(config),
    )


def parse_manifest_input(manifest: str) -> dict[str, Any]:
    """Parse manifest input from YAML string or file path.

    Args:
        manifest: Either a YAML string or a file path to a YAML file

    Returns:
        Parsed manifest as dictionary

    Raises:
        ValueError: If input cannot be parsed or file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    if not isinstance(manifest, str):
        raise ValueError(f"manifest must be a string, got {type(manifest)}")

    if len(manifest.splitlines()) == 1:
        # If the manifest is a single line, treat it as a file path
        path = Path(manifest)
        if path.exists() and path.is_file():
            contents = path.read_text(encoding="utf-8")
            result = yaml.safe_load(contents)
            if not isinstance(result, dict):
                raise ValueError(
                    f"YAML file content must be a dictionary/object, got {type(result)}\n"
                    f" File path: {manifest}\n"
                    f" File content: \n{contents.splitlines()[:25]}\n..."  # Show first 100 chars
                )
            return result

    try:
        # Otherwise, treat it as a YAML string
        result = yaml.safe_load(manifest)
        if not isinstance(result, dict):
            raise ValueError(  # noqa: TRY004
                f"Error when parsing YAML string. Expected to parse a dictionary/object, got {type(result)}."
                f" Manifest content: {manifest[:100]}..."  # Show first 100 chars
            )

    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML string: {e}") from e
    else:
        # No exceptions, return parsed result
        return result


def validate_manifest_structure(manifest: dict[str, Any]) -> bool:
    """Basic validation of manifest structure.

    Args:
        manifest: Connector manifest dictionary

    Returns:
        True if manifest has required structure, False otherwise
    """
    required_fields = ["version", "type", "check"]
    has_required = all(field in manifest for field in required_fields)

    has_streams = "streams" in manifest or "dynamic_streams" in manifest

    return has_required and has_streams
