import base64
import json

import pytest
import yaml

from app import (
    app,
    build_secret,
    parse_env,
    parse_metadata_pairs,
    serialize_secret,
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


class TestParseMetadataPairs:
    """Tests for parse_metadata_pairs function."""

    def test_parse_basic_pairs(self):
        """Test parsing comma-separated key=value pairs."""
        result = parse_metadata_pairs("app=my-app,env=production")
        assert result == {"app": "my-app", "env": "production"}

    def test_parse_pairs_with_whitespace(self):
        """Test whitespace around pairs, keys and values is stripped."""
        result = parse_metadata_pairs(" app = my-app , env = production ")
        assert result == {"app": "my-app", "env": "production"}

    def test_parse_empty_input(self):
        """Test empty and None input return an empty dict."""
        assert parse_metadata_pairs("") == {}
        assert parse_metadata_pairs(None) == {}

    def test_parse_pair_without_equals_skipped(self):
        """Test segments without '=' are skipped (or absorbed into values)."""
        # A leading segment without '=' is skipped in both modes.
        assert parse_metadata_pairs("invalid,app=my-app") == {"app": "my-app"}
        # In label mode every comma separates pairs, so trailing junk is dropped.
        result = parse_metadata_pairs("app=my-app,invalid", validate_values=True)
        assert result == {"app": "my-app"}

    def test_annotation_value_keeps_commas(self):
        """Test annotation values keep commas that don't start a new pair."""
        result = parse_metadata_pairs("description=Deployed by Martin, do not delete")
        assert result == {"description": "Deployed by Martin, do not delete"}

    def test_annotation_value_comma_before_new_pair_splits(self):
        """Test a comma followed by key= still starts a new pair."""
        result = parse_metadata_pairs("a=1, b=2")
        assert result == {"a": "1", "b": "2"}

    def test_label_mode_rejects_invalid_values(self):
        """Test label values must be valid Kubernetes label values."""
        result = parse_metadata_pairs(
            "owner=platform team,app=my-app", validate_values=True
        )
        assert result == {"app": "my-app"}
        too_long = "v" * 64
        assert parse_metadata_pairs(f"app={too_long}", validate_values=True) == {}
        assert parse_metadata_pairs("app=-bad-", validate_values=True) == {}

    def test_label_mode_allows_empty_and_valid_values(self):
        """Test empty and well-formed label values are accepted."""
        result = parse_metadata_pairs("flag=,app=my_app.v1", validate_values=True)
        assert result == {"flag": "", "app": "my_app.v1"}

    def test_invalid_keys_rejected(self):
        """Test keys Kubernetes would reject are skipped."""
        assert parse_metadata_pairs("-app=x") == {}
        assert parse_metadata_pairs("app-=x") == {}
        assert parse_metadata_pairs("a/b/c=x") == {}
        assert parse_metadata_pairs("App.Kubernetes.IO/name=x") == {}
        assert parse_metadata_pairs("/name=x") == {}
        long_name = "k" * 64
        assert parse_metadata_pairs(f"{long_name}=x") == {}

    def test_boundary_keys_accepted(self):
        """Test keys at the limits are accepted."""
        name_63 = "k" * 63
        assert parse_metadata_pairs(f"{name_63}=x") == {name_63: "x"}
        prefix_253 = ("a" * 61 + ".") * 4 + "a" * 5  # 253 chars
        assert len(prefix_253) == 253
        result = parse_metadata_pairs(f"{prefix_253}/name=x")
        assert result == {f"{prefix_253}/name": "x"}

    def test_parse_invalid_key_skipped(self):
        """Test pairs with invalid keys are skipped."""
        result = parse_metadata_pairs("bad key=value,app=my-app")
        assert result == {"app": "my-app"}

    def test_parse_prefixed_key(self):
        """Test keys with a '/'-separated prefix are accepted."""
        result = parse_metadata_pairs("app.kubernetes.io/name=my-app")
        assert result == {"app.kubernetes.io/name": "my-app"}

    def test_parse_value_with_equals(self):
        """Test values containing '=' are kept intact."""
        result = parse_metadata_pairs("note=a=b")
        assert result == {"note": "a=b"}

    def test_parse_empty_value(self):
        """Test empty values are allowed."""
        result = parse_metadata_pairs("flag=")
        assert result == {"flag": ""}


class TestBuildSecret:
    """Tests for build_secret function."""

    def test_build_secret_defaults(self):
        """Test secret dict without labels/annotations."""
        secret = build_secret("my-secret", "default", {"KEY": "dmFsdWU="})
        assert secret == {
            "kind": "Secret",
            "apiVersion": "v1",
            "metadata": {"name": "my-secret", "namespace": "default"},
            "type": "Opaque",
            "data": {"KEY": "dmFsdWU="},
        }

    def test_build_secret_with_labels_and_annotations(self):
        """Test labels and annotations are included in metadata."""
        secret = build_secret(
            "my-secret",
            "default",
            {},
            labels={"app": "my-app"},
            annotations={"owner": "team"},
        )
        assert secret["metadata"]["labels"] == {"app": "my-app"}
        assert secret["metadata"]["annotations"] == {"owner": "team"}

    def test_build_secret_omits_empty_metadata_maps(self):
        """Test empty labels/annotations dicts are omitted from metadata."""
        secret = build_secret("my-secret", "default", {}, labels={}, annotations={})
        assert "labels" not in secret["metadata"]
        assert "annotations" not in secret["metadata"]


class TestSerializeSecret:
    """Tests for serialize_secret function."""

    def test_serialize_json(self):
        """Test JSON serialization matches the original format."""
        secret = build_secret("my-secret", "default", {"KEY": "dmFsdWU="})
        output = serialize_secret(secret, "json")
        assert output == json.dumps(secret, indent=4)

    def test_serialize_yaml_round_trip(self):
        """Test YAML serialization can be loaded back to the same dict."""
        secret = build_secret("my-secret", "default", {"KEY": "dmFsdWU="})
        output = serialize_secret(secret, "yaml")
        assert yaml.safe_load(output) == secret

    def test_serialize_unknown_format_falls_back_to_json(self):
        """Test unknown formats fall back to JSON."""
        secret = build_secret("my-secret", "default", {})
        assert serialize_secret(secret, "xml") == json.dumps(secret, indent=4)


class TestRoutes:
    """Tests for Flask routes."""

    def test_index_get(self, client):
        """Test GET request to index route."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Kubernetes Secret Generator" in response.data

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

    def test_download_json_default_unchanged(self, client):
        """Test download without a format field keeps the original JSON output."""
        data = {
            "env_content": "KEY=value",
            "secret_name": "test-secret",
            "namespace": "default",
        }
        response = client.post("/download", data=data)

        assert response.status_code == 200
        assert response.content_type == "application/json"
        assert ".json" in response.headers.get("Content-Disposition")

        json_data = json.loads(response.data)
        assert json_data["metadata"] == {
            "name": "test-secret",
            "namespace": "default",
        }
        assert "labels" not in json_data["metadata"]
        assert "annotations" not in json_data["metadata"]

    def test_download_yaml_format(self, client):
        """Test download with YAML format."""
        data = {
            "env_content": "KEY1=value1\nKEY2=value2",
            "secret_name": "test-secret",
            "namespace": "test-namespace",
            "format": "yaml",
        }
        response = client.post("/download", data=data)

        assert response.status_code == 200
        assert response.content_type == "application/yaml"
        assert ".yaml" in response.headers.get("Content-Disposition")

        yaml_data = yaml.safe_load(response.data)
        assert yaml_data["kind"] == "Secret"
        assert yaml_data["apiVersion"] == "v1"
        assert yaml_data["metadata"]["name"] == "test-secret"
        assert yaml_data["metadata"]["namespace"] == "test-namespace"
        assert base64.b64decode(yaml_data["data"]["KEY1"]).decode() == "value1"

    def test_download_invalid_format_falls_back_to_json(self, client):
        """Test download with an unknown format falls back to JSON."""
        data = {
            "env_content": "KEY=value",
            "secret_name": "test-secret",
            "namespace": "default",
            "format": "xml",
        }
        response = client.post("/download", data=data)

        assert response.status_code == 200
        assert response.content_type == "application/json"
        json.loads(response.data)

    def test_download_with_labels_and_annotations(self, client):
        """Test download includes parsed labels and annotations."""
        data = {
            "env_content": "KEY=value",
            "secret_name": "test-secret",
            "namespace": "default",
            "labels": "app=my-app,env=production",
            "annotations": "owner=platform-team",
        }
        response = client.post("/download", data=data)

        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data["metadata"]["labels"] == {
            "app": "my-app",
            "env": "production",
        }
        assert json_data["metadata"]["annotations"] == {"owner": "platform-team"}

    def test_download_annotation_value_with_comma(self, client):
        """Test an annotation value containing a comma survives intact."""
        data = {
            "env_content": "KEY=value",
            "secret_name": "test-secret",
            "namespace": "default",
            "annotations": "note=keep this, and this too",
        }
        response = client.post("/download", data=data)

        assert response.status_code == 200
        json_data = json.loads(response.data)
        assert json_data["metadata"]["annotations"] == {
            "note": "keep this, and this too"
        }

    def test_index_post_yaml_format(self, client):
        """Test POST to index with YAML format renders YAML output."""
        data = {
            "env_content": "KEY=value",
            "secret_name": "test-secret",
            "namespace": "default",
            "format": "yaml",
        }
        response = client.post("/", data=data)

        assert response.status_code == 200
        assert b"kind: Secret" in response.data


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
