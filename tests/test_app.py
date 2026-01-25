import base64
import json
import pytest
from app import (
    app,
    parse_env,
    _parse_env_line,
    _remove_inline_comments,
    _is_valid_k8s_key,
)


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestParseEnvLine:
    """Tests for _parse_env_line function."""

    def test_parse_key_equals_value(self):
        """Test parsing KEY=value format."""
        key, value = _parse_env_line("KEY=value")
        assert key == "KEY"
        assert value == "value"

    def test_parse_key_equals_quoted_value(self):
        """Test parsing KEY="value" format."""
        key, value = _parse_env_line('KEY="value"')
        assert key == "KEY"
        assert value == "value"

    def test_parse_key_equals_single_quoted_value(self):
        """Test parsing KEY='value' format."""
        key, value = _parse_env_line("KEY='value'")
        assert key == "KEY"
        assert value == "value"

    def test_parse_key_colon_value(self):
        """Test parsing KEY: value format."""
        key, value = _parse_env_line("KEY: value")
        assert key == "KEY"
        assert value == "value"

    def test_parse_key_colon_quoted_value(self):
        """Test parsing KEY: "value" format."""
        key, value = _parse_env_line('KEY: "value"')
        assert key == "KEY"
        assert value == "value"

    def test_parse_empty_value_equals(self):
        """Test parsing KEY= (empty value)."""
        key, value = _parse_env_line("KEY=")
        assert key == "KEY"
        assert value == ""

    def test_parse_empty_value_colon(self):
        """Test parsing KEY: (empty value)."""
        key, value = _parse_env_line("KEY:")
        assert key == "KEY"
        assert value == ""

    def test_parse_whitespace_handling(self):
        """Test whitespace is properly handled."""
        key, value = _parse_env_line("  KEY  =  value  ")
        assert key == "KEY"
        assert value == "value"

    def test_parse_invalid_format(self):
        """Test invalid format raises ValueError."""
        with pytest.raises(ValueError):
            _parse_env_line("invalid line without delimiter")


class TestRemoveInlineComments:
    """Tests for _remove_inline_comments function."""

    def test_remove_comment_after_value(self):
        """Test removing inline comment."""
        result = _remove_inline_comments("KEY=value # this is a comment")
        assert result == "KEY=value "

    def test_preserve_hash_in_double_quotes(self):
        """Test preserving # inside double quotes."""
        result = _remove_inline_comments('KEY="value#with#hash"')
        assert result == 'KEY="value#with#hash"'

    def test_preserve_hash_in_single_quotes(self):
        """Test preserving # inside single quotes."""
        result = _remove_inline_comments("KEY='value#with#hash'")
        assert result == "KEY='value#with#hash'"

    def test_no_comment(self):
        """Test line without comment."""
        result = _remove_inline_comments("KEY=value")
        assert result == "KEY=value"

    def test_handle_escaped_quotes(self):
        """Test handling escaped quotes."""
        result = _remove_inline_comments('KEY="value\\"escaped"')
        assert 'KEY="value\\"escaped"' in result


class TestIsValidK8sKey:
    """Tests for _is_valid_k8s_key function."""

    def test_valid_alphanumeric_key(self):
        """Test valid alphanumeric key."""
        assert _is_valid_k8s_key("KEY123") is True

    def test_valid_key_with_underscore(self):
        """Test valid key with underscore."""
        assert _is_valid_k8s_key("MY_KEY") is True

    def test_valid_key_with_dash(self):
        """Test valid key with dash."""
        assert _is_valid_k8s_key("my-key") is True

    def test_valid_key_with_dot(self):
        """Test valid key with dot."""
        assert _is_valid_k8s_key("my.key") is True

    def test_invalid_empty_key(self):
        """Test empty key is invalid."""
        assert _is_valid_k8s_key("") is False

    def test_invalid_key_with_space(self):
        """Test key with space is invalid."""
        assert _is_valid_k8s_key("MY KEY") is False

    def test_invalid_key_with_special_char(self):
        """Test key with special character is invalid."""
        assert _is_valid_k8s_key("MY@KEY") is False


class TestParseEnv:
    """Tests for parse_env function."""

    def test_parse_simple_env(self):
        """Test parsing simple .env content."""
        env_content = "KEY1=value1\nKEY2=value2"
        result = parse_env(env_content)

        assert "KEY1" in result
        assert "KEY2" in result
        assert base64.b64decode(result["KEY1"]).decode() == "value1"
        assert base64.b64decode(result["KEY2"]).decode() == "value2"

    def test_parse_env_with_comments(self):
        """Test parsing .env with comments."""
        env_content = "# Comment\nKEY=value\n# Another comment"
        result = parse_env(env_content)

        assert "KEY" in result
        assert len(result) == 1

    def test_parse_env_with_empty_lines(self):
        """Test parsing .env with empty lines."""
        env_content = "KEY1=value1\n\nKEY2=value2\n\n"
        result = parse_env(env_content)

        assert len(result) == 2

    def test_parse_env_mixed_formats(self):
        """Test parsing mixed formats."""
        env_content = 'KEY1=value1\nKEY2: value2\nKEY3="value3"'
        result = parse_env(env_content)

        assert len(result) == 3
        assert base64.b64decode(result["KEY3"]).decode() == "value3"

    def test_parse_env_invalid_key(self):
        """Test parsing with invalid Kubernetes key."""
        env_content = "VALID_KEY=value\nINVALID KEY=value"
        result = parse_env(env_content)

        assert "VALID_KEY" in result
        assert "INVALID KEY" not in result
        assert len(result) == 1

    def test_parse_env_empty_value(self):
        """Test parsing empty value."""
        env_content = "KEY="
        result = parse_env(env_content)

        assert "KEY" in result
        assert base64.b64decode(result["KEY"]).decode() == ""

    def test_parse_env_special_characters(self):
        """Test parsing values with special characters."""
        env_content = 'KEY="p@ssw0rd!"'
        result = parse_env(env_content)

        assert "KEY" in result
        assert base64.b64decode(result["KEY"]).decode() == "p@ssw0rd!"


class TestRoutes:
    """Tests for Flask routes."""

    def test_index_get(self, client):
        """Test GET request to index route."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Kubernetes Secret JSON Generator" in response.data

    def test_index_post(self, client):
        """Test POST request to index route."""
        data = {
            "env_content": "KEY1=value1\nKEY2=value2",
            "secret_name": "test-secret",
            "namespace": "test-namespace",
        }
        response = client.post("/", data=data)

        assert response.status_code == 200
        assert b"test-secret" in response.data
        assert b"test-namespace" in response.data

    def test_index_post_with_invalid_data(self, client):
        """Test POST with invalid data."""
        data = {
            "env_content": "INVALID LINE WITHOUT DELIMITER",
            "secret_name": "test-secret",
            "namespace": "default",
        }
        response = client.post("/", data=data)

        assert response.status_code == 200

    def test_download_route(self, client):
        """Test download route."""
        data = {
            "env_content": "KEY1=value1\nKEY2=value2",
            "secret_name": "test-secret",
            "namespace": "test-namespace",
        }
        response = client.post("/download", data=data)

        assert response.status_code == 200
        assert response.content_type == "application/json"

        json_data = json.loads(response.data)
        assert json_data["kind"] == "Secret"
        assert json_data["apiVersion"] == "v1"
        assert json_data["metadata"]["name"] == "test-secret"
        assert json_data["metadata"]["namespace"] == "test-namespace"
        assert "KEY1" in json_data["data"]
        assert "KEY2" in json_data["data"]

    def test_download_route_sanitizes_filename(self, client):
        """Test download route sanitizes secret name."""
        data = {
            "env_content": "KEY=value",
            "secret_name": "../../../malicious",
            "namespace": "default",
        }
        response = client.post("/download", data=data)

        assert response.status_code == 200
        content_disposition = response.headers.get("Content-Disposition")
        assert "../" not in content_disposition

    def test_download_route_empty_env(self, client):
        """Test download with empty env content."""
        data = {
            "env_content": "",
            "secret_name": "empty-secret",
            "namespace": "default",
        }
        response = client.post("/download", data=data)

        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data["data"] == {}


class TestIntegration:
    """Integration tests for complete workflow."""

    def test_complete_secret_generation_workflow(self, client):
        """Test complete workflow from env to secret JSON."""
        env_content = """
# Database Configuration
DB_HOST=localhost
DB_PORT: "5432"
DB_USER="admin"
DB_PASSWORD='secret123'

# Application Settings
APP_ENV=production
DEBUG=false
"""

        data = {
            "env_content": env_content,
            "secret_name": "my-app-secret",
            "namespace": "production",
        }

        response = client.post("/download", data=data)
        assert response.status_code == 200

        json_data = json.loads(response.data)
        assert json_data["kind"] == "Secret"
        assert json_data["type"] == "Opaque"
        assert json_data["metadata"]["name"] == "my-app-secret"
        assert json_data["metadata"]["namespace"] == "production"

        # Verify all keys are present and base64 encoded
        assert "DB_HOST" in json_data["data"]
        assert "DB_PORT" in json_data["data"]
        assert "DB_USER" in json_data["data"]
        assert "DB_PASSWORD" in json_data["data"]
        assert "APP_ENV" in json_data["data"]
        assert "DEBUG" in json_data["data"]

        # Verify values can be decoded
        assert base64.b64decode(json_data["data"]["DB_HOST"]).decode() == "localhost"
        assert base64.b64decode(json_data["data"]["DB_PORT"]).decode() == "5432"
        assert (
            base64.b64decode(json_data["data"]["DB_PASSWORD"]).decode() == "secret123"
        )
