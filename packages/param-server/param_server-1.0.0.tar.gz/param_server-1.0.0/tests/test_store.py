"""Tests for parameter store functionality."""

import pytest
import tempfile
from pathlib import Path

from param_server.store import ParameterStore


class TestParameterStore:
    """Test cases for ParameterStore."""

    def test_set_and_get_basic(self, param_store):
        """Test basic set and get operations."""
        # Test different types
        param_store.set("/test/string", "hello")
        param_store.set("/test/int", 42)
        param_store.set("/test/float", 3.14)
        param_store.set("/test/bool", True)

        assert param_store.get("/test/string") == "hello"
        assert param_store.get("/test/int") == 42
        assert param_store.get("/test/float") == 3.14
        assert param_store.get("/test/bool") is True

    def test_path_normalization(self, param_store):
        """Test different path formats are handled correctly."""
        param_store.set("/test/param", "value1")
        param_store.set("test/param2", "value2")
        param_store.set("test.param3", "value3")

        # All should be accessible with different formats
        assert param_store.get("/test/param") == "value1"
        assert param_store.get("test/param") == "value1"
        assert param_store.get("test.param") == "value1"

        assert param_store.get("/test/param2") == "value2"
        assert param_store.get("test.param2") == "value2"

        assert param_store.get("/test/param3") == "value3"
        assert param_store.get("test/param3") == "value3"

    def test_nested_parameters(self, param_store):
        """Test nested parameter structures."""
        param_store.set("/camera/settings/exposure", 0.033)
        param_store.set("/camera/settings/gain", 1.5)
        param_store.set("/camera/resolution/width", 1920)
        param_store.set("/camera/resolution/height", 1080)

        assert param_store.get("/camera/settings/exposure") == 0.033
        assert param_store.get("/camera/settings/gain") == 1.5
        assert param_store.get("/camera/resolution/width") == 1920
        assert param_store.get("/camera/resolution/height") == 1080

    def test_parameter_deletion(self, param_store):
        """Test parameter deletion."""
        param_store.set("/test/param", "value")
        assert param_store.get("/test/param") == "value"

        param_store.delete("/test/param")

        with pytest.raises(KeyError):
            param_store.get("/test/param")

    def test_list_parameters(self, param_store):
        """Test parameter listing functionality."""
        # Set up test parameters
        param_store.set("/camera/exposure", 0.033)
        param_store.set("/camera/gain", 1.5)
        param_store.set("/robot/arm/joint1", 0.0)
        param_store.set("/robot/arm/joint2", 1.57)
        param_store.set("/system/debug", True)

        # Test listing all parameters
        all_params = param_store.list_params()
        assert len(all_params) == 5
        assert "camera/exposure" in all_params
        assert "robot/arm/joint1" in all_params

        # Test listing with prefix
        camera_params = param_store.list_params("/camera")
        assert len(camera_params) == 2
        assert "camera/exposure" in camera_params
        assert "camera/gain" in camera_params

        robot_params = param_store.list_params("/robot")
        assert len(robot_params) == 2
        assert "robot/arm/joint1" in robot_params
        assert "robot/arm/joint2" in robot_params

    def test_invalid_types(self, param_store):
        """Test that invalid parameter types are rejected."""
        with pytest.raises(ValueError):
            param_store.set("/test/list", [1, 2, 3])

        with pytest.raises(ValueError):
            param_store.set("/test/dict", {"key": "value"})

        with pytest.raises(ValueError):
            param_store.set("/test/none", None)

    def test_nonexistent_parameters(self, param_store):
        """Test accessing non-existent parameters."""
        with pytest.raises(KeyError):
            param_store.get("/nonexistent/param")

        with pytest.raises(KeyError):
            param_store.delete("/nonexistent/param")

    def test_yaml_loading(self, param_store, temp_config_file):
        """Test loading parameters from YAML file."""
        param_store.load_from_yaml(temp_config_file)

        # Test loaded values
        assert param_store.get("/test/string_param") == "test_value"
        assert param_store.get("/test/int_param") == 42
        assert param_store.get("/test/float_param") == 3.14
        assert param_store.get("/test/bool_param") is True
        assert param_store.get("/test/nested/deep_param") == "deep_value"
        assert param_store.get("/test/nested/number") == 100
        assert param_store.get("/camera/exposure") == 0.033
        assert param_store.get("/camera/gain") == 1.5

    def test_yaml_saving(self, param_store):
        """Test saving parameters to YAML file."""
        # Set some parameters
        param_store.set("/test/string", "hello")
        param_store.set("/test/number", 42)
        param_store.set("/nested/param", True)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            temp_file = f.name

        try:
            param_store.save_to_yaml(temp_file)

            # Create new store and load
            new_store = ParameterStore()
            new_store.load_from_yaml(temp_file)

            # Verify values
            assert new_store.get("/test/string") == "hello"
            assert new_store.get("/test/number") == 42
            assert new_store.get("/nested/param") is True
        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_clear(self, param_store):
        """Test clearing all parameters."""
        # Set some parameters
        param_store.set("/test/param1", "value1")
        param_store.set("/test/param2", "value2")

        assert len(param_store.list_params()) == 2

        # Clear all
        param_store.clear()

        assert len(param_store.list_params()) == 0

        with pytest.raises(KeyError):
            param_store.get("/test/param1")

    def test_get_all_params(self, param_store):
        """Test getting all parameters as dictionary."""
        param_store.set("/test/param1", "value1")
        param_store.set("/test/param2", 42)
        param_store.set("/nested/param", True)

        all_params = param_store.get_all_params()

        assert isinstance(all_params, dict)
        assert all_params["test"]["param1"] == "value1"
        assert all_params["test"]["param2"] == 42
        assert all_params["nested"]["param"] is True

    def test_thread_safety(self, param_store):
        """Test basic thread safety (simplified test)."""
        import threading
        import time

        errors = []

        def worker(worker_id):
            try:
                for i in range(100):
                    param_store.set(f"/worker_{worker_id}/param_{i}", i)
                    value = param_store.get(f"/worker_{worker_id}/param_{i}")
                    assert value == i
                    time.sleep(0.001)  # Small delay to increase contention
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check no errors occurred
        assert len(errors) == 0, f"Thread safety test failed with errors: {errors}"

        # Verify all parameters were set correctly
        all_params = param_store.list_params()
        assert len(all_params) == 300  # 3 workers * 100 params each
