import ssl
import urllib3
import json
import certifi
import os
import platform


def get_system_ca_bundle():
    """
    Try to detect a system CA bundle.
    Returns a path if found, else None (so urllib3/ssl can use system defaults).
    """
    candidate_paths = []
    system = platform.system()

    if system == "Linux":
        candidate_paths = [
            "/etc/ssl/certs/ca-certificates.crt",           # Debian/Ubuntu/Alpine
            "/etc/pki/tls/certs/ca-bundle.crt",             # RHEL/Fedora/CentOS
            "/etc/ssl/ca-bundle.pem",                       # OpenSUSE, Arch
            "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",  # Fedora newer
        ]
    elif system == "Darwin":  # macOS
        candidate_paths = [
            "/etc/ssl/cert.pem",
            "/private/etc/ssl/cert.pem",
        ]
    elif system == "Windows":
        # No constant CA bundle file — Python/urllib3 uses certifi by default
        candidate_paths = []

    # 1. Environment variable (common in corp setups)
    env_path = os.environ.get("SSL_CERT_FILE")
    if env_path and os.path.exists(env_path):
        return env_path

    # 2. Known candidate paths
    for path in candidate_paths:
        if os.path.exists(path):
            return path

    # 3. None → means “let ssl/urllib3 use system defaults”
    return None


def create_pool_manager():
    """Create a PoolManager with system/Certifi CA bundle."""
    cafile = get_system_ca_bundle()
    if cafile:
        ctx = ssl.create_default_context(cafile=cafile)
    else:
        ctx = ssl.create_default_context()
        ctx.load_verify_locations(cafile=certifi.where())

    return urllib3.PoolManager(ssl_context=ctx), cafile or "System/Certifi default"


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.http, self.cafile = create_pool_manager()

    def post(self, endpoint: str, payload: dict) -> dict:
        """Send a POST request and return parsed JSON response."""
        try:
            resp = self.http.request(
                "POST",
                f"{self.base_url}{endpoint}",
                body=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )
            if resp.status >= 400:
                body = resp.data.decode(errors="ignore")
                snippet = body[:200].replace("\n", " ") + ("..." if len(body) > 200 else "")
                raise RuntimeError(f"HTTP {resp.status}: {snippet}")
            return json.loads(resp.data.decode())
        except Exception as e:
            raise RuntimeError(f"Request failed: {e}") from e
