import base64
import json
import logging
import os
import re
from datetime import datetime, timezone
from io import BytesIO

import yaml
from flask import Flask, request, render_template, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Flask app initialization
app = Flask(__name__)

# Configuration from environment variables
app.config["MAX_CONTENT_LENGTH"] = int(
    os.environ.get("MAX_CONTENT_LENGTH", 1024 * 1024)
)  # Default 1MB
RATE_LIMIT = os.environ.get("RATE_LIMIT", "10 per minute")
ENABLE_SECURITY_HEADERS = (
    os.environ.get("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
)

# Security Headers with Flask-Talisman
if ENABLE_SECURITY_HEADERS:
    # Content Security Policy
    csp = {
        "default-src": "'self'",
        "style-src": ["'self'", "'unsafe-inline'"],  # Allow inline styles
        "img-src": ["'self'", "https://bondit.services", "data:"],
        "script-src": "'self'",
    }

    Talisman(
        app,
        force_https=False,  # Don't force HTTPS (may be behind reverse proxy)
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        content_security_policy=csp,
        content_security_policy_nonce_in=["script-src"],
        frame_options="DENY",
        referrer_policy="strict-origin-when-cross-origin",
    )
    logger.info("Security headers enabled")

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[RATE_LIMIT],
    storage_uri="memory://",
)
logger.info("Rate limiting enabled: %s", RATE_LIMIT)


# Error handlers
@app.errorhandler(413)
def request_entity_too_large(error):  # pylint: disable=unused-argument
    """Handle file size limit exceeded."""
    max_size_mb = app.config["MAX_CONTENT_LENGTH"] / (1024 * 1024)
    logger.warning(
        "Request entity too large",
        extra={
            "action": "request_too_large",
            "ip": get_remote_address(),
            "max_size_mb": max_size_mb,
        },
    )
    return (
        render_template(
            "error.html",
            error_message=f"File size exceeds maximum allowed size of {max_size_mb:.1f} MB",
        ),
        413,
    )


@app.errorhandler(429)
def ratelimit_handler(error):  # pylint: disable=unused-argument
    """Handle rate limit exceeded."""
    logger.warning(
        "Rate limit exceeded",
        extra={
            "action": "rate_limit_exceeded",
            "ip": get_remote_address(),
        },
    )
    return (
        render_template(
            "error.html",
            error_message="Rate limit exceeded. Please try again later.",
        ),
        429,
    )


def parse_env(env_content):
    """Parses .env content and converts it to a dictionary supporting multiple formats.

    Supported formats:
    - KEY=value
    - KEY="value"
    - KEY='value'
    - KEY: value
    - KEY: "value"
    - KEY: 'value'
    - Comments with # (ignored)
    - Empty lines (ignored)
    - Empty values (KEY= or KEY:)
    """
    env_dict = {}
    errors = []

    # Split content into lines for better error reporting
    lines = env_content.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Strip whitespace
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Remove inline comments (but preserve # in quoted values)
        cleaned_line = _remove_inline_comments(line)
        if not cleaned_line.strip():
            continue

        # Try to parse the line
        try:
            key, value = _parse_env_line(cleaned_line)
            if key:
                # Validate Kubernetes secret key naming
                if not _is_valid_k8s_key(key):
                    errors.append(
                        f"Line {line_num}: Invalid Kubernetes secret key '{key}'. "
                        f"Keys must contain only alphanumeric characters, '.', '-', and '_'"
                    )
                    continue

                # Base64 encode the value
                encoded_value = base64.b64encode(value.encode("utf-8")).decode("ascii")
                env_dict[key] = encoded_value
        except ValueError as e:
            errors.append(f"Line {line_num}: {str(e)} - '{line}'")
            continue

    # If we have errors but also some successful parses, we can still proceed
    # Store errors for potential logging/debugging
    if errors:
        # For now, we'll just continue - could add error reporting later
        pass

    return env_dict


def _remove_inline_comments(line):
    """Remove inline comments while preserving # inside quoted strings."""
    in_single_quote = False
    in_double_quote = False
    escaped = False

    result = []

    for char in line:
        if escaped:
            result.append(char)
            escaped = False
            continue

        if char == "\\":
            escaped = True
            result.append(char)
            continue

        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif char == "#" and not in_single_quote and not in_double_quote:
            # Found unquoted comment, truncate here
            break

        result.append(char)

    return "".join(result)


def _parse_env_line(line):
    """Parse a single environment variable line.

    Returns tuple of (key, value) or raises ValueError if invalid.
    """
    # Patterns to try in order of preference
    patterns = [
        # KEY="value" or KEY='value'
        r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*["\']([^"\']*)["\']\s*$',
        # KEY=value (unquoted)
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^\s#].*?)\s*$",
        # KEY= (empty value)
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*$",
        # KEY: "value" or KEY: 'value'
        r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*["\']([^"\']*)["\']\s*$',
        # KEY: value (unquoted)
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*([^\s#].*?)\s*$",
        # KEY: (empty value)
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*$",
    ]

    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            key = match.group(1).strip()
            value = (
                match.group(2).strip()
                if len(match.groups()) > 1 and match.group(2)
                else ""
            )
            return key, value

    # If no pattern matches, it's an invalid line
    raise ValueError("Invalid environment variable format")


def _is_valid_k8s_key(key):
    """Validate that the key conforms to Kubernetes secret key requirements.

    Keys must:
    - Start with alphanumeric or underscore
    - Contain only alphanumeric, '.', '-', and '_'
    - Not be empty
    """
    if not key:
        return False

    # Kubernetes allows alphanumeric, '.', '-', and '_'
    pattern = r"^[a-zA-Z0-9._-]+$"
    return bool(re.match(pattern, key))


# Kubernetes "qualified name" segment: max 63 chars, alphanumeric at both
# ends, '-', '_' and '.' allowed in between. Used for label/annotation key
# names and for label values.
_NAME_SEGMENT_RE = re.compile(r"^[A-Za-z0-9]([-A-Za-z0-9_.]*[A-Za-z0-9])?$")
# Optional key prefix: a lowercase DNS subdomain (e.g. app.kubernetes.io).
_DNS_PREFIX_RE = re.compile(
    r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$"
)
# Split annotation input only on commas that start a new key=value pair,
# so annotation values may themselves contain commas.
_PAIR_SPLIT_RE = re.compile(r",(?=\s*[A-Za-z0-9._/-]+\s*=)")


def _is_valid_metadata_key(key):
    """Validate a Kubernetes label/annotation key (qualified name).

    An optional DNS-subdomain prefix (lowercase, max 253 chars) separated by
    a single '/', followed by a name segment of at most 63 chars that starts
    and ends with an alphanumeric character (e.g. app.kubernetes.io/name).
    """
    if not key or key.count("/") > 1:
        return False
    if "/" in key:
        prefix, name = key.split("/")
        if not prefix or len(prefix) > 253 or not _DNS_PREFIX_RE.match(prefix):
            return False
    else:
        name = key
    return len(name) <= 63 and bool(_NAME_SEGMENT_RE.match(name))


def _is_valid_label_value(value):
    """Validate a Kubernetes label value.

    Must be empty, or at most 63 chars starting and ending alphanumeric.
    """
    if value == "":
        return True
    return len(value) <= 63 and bool(_NAME_SEGMENT_RE.match(value))


def parse_metadata_pairs(raw_pairs, validate_values=False):
    """Parse comma-separated key=value pairs into a metadata dict.

    Example input: "app=my-app, env=production".
    Pairs without '=' or with an invalid key are skipped; values may be
    empty and may contain '=' (the split happens on the first '=').

    With validate_values=True (labels), entries split on every comma and
    values must be valid Kubernetes label values or the pair is skipped.
    Without it (annotations), entries split only on commas that start a new
    key=value pair, so free-text values may contain commas.
    """
    metadata = {}
    if not raw_pairs:
        return metadata

    if validate_values:
        entries = raw_pairs.split(",")
    else:
        entries = _PAIR_SPLIT_RE.split(raw_pairs)

    for pair in entries:
        pair = pair.strip()
        if not pair or "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not _is_valid_metadata_key(key):
            continue
        if validate_values and not _is_valid_label_value(value):
            continue
        metadata[key] = value

    return metadata


def build_secret(secret_name, namespace, env_dict, labels=None, annotations=None):
    """Build a Kubernetes Opaque Secret manifest as a plain dict.

    Empty labels/annotations maps are omitted from the metadata.
    """
    metadata = {"name": secret_name, "namespace": namespace}
    if labels:
        metadata["labels"] = labels
    if annotations:
        metadata["annotations"] = annotations

    return {
        "kind": "Secret",
        "apiVersion": "v1",
        "metadata": metadata,
        "type": "Opaque",
        "data": env_dict,
    }


def serialize_secret(secret, output_format):
    """Serialize a secret dict as JSON (default) or YAML."""
    if output_format == "yaml":
        return yaml.safe_dump(secret, sort_keys=False, default_flow_style=False)
    return json.dumps(secret, indent=4)


def _get_output_format(form):
    """Read the requested output format from a form, defaulting to JSON."""
    output_format = form.get("format", "json").strip().lower()
    return output_format if output_format in ("json", "yaml") else "json"


@app.route("/", methods=["GET", "POST"])
@limiter.limit("20 per minute")  # More lenient for main page
def index():
    manifest_output = None
    secret_name = ""  # nosec B105 - Not a password, just form field initialization
    namespace = ""
    labels_input = ""
    annotations_input = ""
    output_format = "json"

    if request.method == "POST":
        env_content = request.form.get("env_content", "")
        secret_name = request.form.get("secret_name", "my-secret")
        namespace = request.form.get("namespace", "default")
        labels_input = request.form.get("labels", "")
        annotations_input = request.form.get("annotations", "")
        output_format = _get_output_format(request.form)

        # Audit log: Secret generation request
        logger.info(
            "Secret generation request",
            extra={
                "action": "generate_secret",
                "ip": get_remote_address(),
                "secret_name": secret_name,
                "namespace": namespace,
                "output_format": output_format,
                "content_length": len(env_content),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        env_dict = parse_env(env_content)
        secret = build_secret(
            secret_name,
            namespace,
            env_dict,
            labels=parse_metadata_pairs(labels_input, validate_values=True),
            annotations=parse_metadata_pairs(annotations_input),
        )
        manifest_output = serialize_secret(secret, output_format)

        # Audit log: Success
        logger.info(
            "Secret generated successfully",
            extra={
                "action": "generate_secret_success",
                "ip": get_remote_address(),
                "secret_name": secret_name,
                "keys_count": len(env_dict),
            },
        )

    return render_template(
        "index.html",
        manifest_output=manifest_output,
        secret_name=secret_name,
        namespace=namespace,
        labels=labels_input,
        annotations=annotations_input,
        output_format=output_format,
    )


@app.route("/download", methods=["POST"])
@limiter.limit("10 per minute")  # Stricter limit for downloads
def download():
    env_content = request.form.get("env_content", "")
    secret_name = secure_filename(
        request.form.get("secret_name", "my-secret")
    )  # Sanitize the secret name
    namespace = request.form.get("namespace", "default")
    output_format = _get_output_format(request.form)

    # Audit log: Download request
    logger.info(
        "Secret download request",
        extra={
            "action": "download_secret",
            "ip": get_remote_address(),
            "secret_name": secret_name,
            "namespace": namespace,
            "output_format": output_format,
            "content_length": len(env_content),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    env_dict = parse_env(env_content)
    secret = build_secret(
        secret_name,
        namespace,
        env_dict,
        labels=parse_metadata_pairs(
            request.form.get("labels", ""), validate_values=True
        ),
        annotations=parse_metadata_pairs(request.form.get("annotations", "")),
    )

    output = serialize_secret(secret, output_format)
    file_download = BytesIO(output.encode())
    file_download.seek(0)

    extension = "yaml" if output_format == "yaml" else "json"
    mimetype = "application/yaml" if output_format == "yaml" else "application/json"

    # Ensure the filename is safe
    safe_filename = secure_filename(f"{secret_name}.{extension}")

    # Audit log: Success
    logger.info(
        "Secret downloaded successfully",
        extra={
            "action": "download_secret_success",
            "ip": get_remote_address(),
            "secret_name": secret_name,
            "download_filename": safe_filename,
        },
    )

    return send_file(
        file_download,
        mimetype=mimetype,
        as_attachment=True,
        download_name=safe_filename,
    )


if __name__ == "__main__":
    # Binding to all interfaces is intentional for Docker containerization
    app.run(host="0.0.0.0", port=5000, debug=False)  # nosec B104
