"""Parameter storage and management with hierarchical structure."""

import yaml
import time
import threading

from typing import Any, Dict, List, Union
from pathlib import Path


class ParameterStore:
    """Thread-safe hierarchical parameter storage."""

    def __init__(self):
        self._params: Dict[str, Any] = {}
        self._lock = threading.RLock()

    def get(self, path: str) -> Any:
        """Get parameter value by path.

        Args:
            path: Parameter path (e.g., '/camera/exposure' or 'camera.exposure')

        Returns:
            Parameter value

        Raises:
            KeyError: If parameter doesn't exist
        """
        normalized_path = self._normalize_path(path)

        with self._lock:
            return self._get_nested(normalized_path)

    def set(self, path: str, value: Union[str, int, float, bool]) -> None:
        """Set parameter value by path.

        Args:
            path: Parameter path
            value: Parameter value (str, int, float, or bool)

        Raises:
            ValueError: If value type is not supported
        """
        if not isinstance(value, (str, int, float, bool)):
            raise ValueError(f"Unsupported parameter type: {type(value)}")

        normalized_path = self._normalize_path(path)

        with self._lock:
            self._set_nested(normalized_path, value)

    def delete(self, path: str) -> None:
        """Delete parameter by path.

        Args:
            path: Parameter path

        Raises:
            KeyError: If parameter doesn't exist
        """
        normalized_path = self._normalize_path(path)

        with self._lock:
            self._delete_nested(normalized_path)

    def list_params(self, prefix: str = "") -> List[str]:
        """List all parameter paths with optional prefix filter.

        Args:
            prefix: Optional prefix to filter parameters

        Returns:
            List of parameter paths
        """
        all_paths = []
        self._collect_paths(self._params, "", all_paths)

        with self._lock:
            if prefix:
                normalized_prefix = self._normalize_path(prefix)
                prefix_str = "/".join(normalized_prefix)
                return [path for path in all_paths if path.startswith(prefix_str)]

            return all_paths

    def load_from_yaml(self, file_path: Union[str, Path]) -> None:
        """Load parameters from YAML file.

        Args:
            file_path: Path to YAML file
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")

        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        with self._lock:
            if data:
                self._params = {}
                self._load_nested_dict(data)

    def save_to_yaml(self, file_path: Union[str, Path]) -> None:
        """Save parameters to YAML file.

        Args:
            file_path: Path to save YAML file
        """
        with self._lock:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w") as f:
                yaml.dump(self._params, f, default_flow_style=False, indent=2)

    def get_all_params(self) -> Dict[str, Any]:
        """Get all parameters as a dictionary.

        Returns:
            Dictionary containing all parameters
        """
        with self._lock:
            return self._params.copy()

    def clear(self) -> None:
        """Clear all parameters."""
        with self._lock:
            self._params.clear()

    def _normalize_path(self, path: str) -> List[str]:
        """Normalize parameter path to list of keys."""
        if not path:
            return []

        # Remove leading/trailing slashes and split
        path = path.strip("/")
        if not path:
            return []

        # Support both '/' and '.' as separators
        if "/" in path:
            return path.split("/")
        else:
            return path.split(".")

    def _get_nested(self, path_parts: List[str]) -> Any:
        """Get value from nested dictionary structure."""

        current = self._params

        for part in path_parts:
            if not isinstance(current, dict) or part not in current:
                raise KeyError(f"Parameter not found: /{'/'.join(path_parts)}")
            current = current[part]

        return current

    def _set_nested(self, path_parts: List[str], value: Any) -> None:
        """Set value in nested dictionary structure."""
        if not path_parts:
            raise ValueError("Empty path not allowed")

        current = self._params

        # Navigate to parent of target
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Convert leaf to dict if needed
                current[part] = {}
            current = current[part]

        # Set the final value
        current[path_parts[-1]] = value

    def _delete_nested(self, path_parts: List[str]) -> None:
        """Delete value from nested dictionary structure."""
        if not path_parts:
            raise ValueError("Empty path not allowed")

        current = self._params

        # Navigate to parent of target
        for part in path_parts[:-1]:
            if not isinstance(current, dict) or part not in current:
                raise KeyError(f"Parameter not found: /{'/'.join(path_parts)}")
            current = current[part]

        # Delete the final key
        if not isinstance(current, dict) or path_parts[-1] not in current:
            raise KeyError(f"Parameter not found: /{'/'.join(path_parts)}")

        del current[path_parts[-1]]

    def _collect_paths(self, data: Dict[str, Any], current_path: str, paths: List[str]) -> None:
        """Recursively collect all parameter paths."""
        for key, value in data.items():
            path = f"{current_path}/{key}" if current_path else key

            if isinstance(value, dict):
                # If dict has nested dicts, recurse
                has_nested_dict = any(isinstance(v, dict) for v in value.values())
                if has_nested_dict:
                    self._collect_paths(value, path, paths)
                else:
                    # If dict only has leaf values, add all as paths
                    for sub_key in value.keys():
                        paths.append(f"{path}/{sub_key}")
            else:
                paths.append(path)

    def _load_nested_dict(self, data: Dict[str, Any], path_prefix: str = "") -> None:
        """Load nested dictionary into parameter store."""
        for key, value in data.items():
            current_path = f"{path_prefix}/{key}" if path_prefix else key

            if isinstance(value, dict):
                self._load_nested_dict(value, current_path)
            else:
                if isinstance(value, (str, int, float, bool)):
                    self.set(current_path, value)
