from __future__ import annotations

import re
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable


ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_EXAMPLE_PATH = ROOT_DIR / ".env.example"
ENV_PATH = ROOT_DIR / ".env"

POSTGRES_CONTAINER = "olist-postgres"
GARAGE_CONTAINER = "olist-garage"

PLACEHOLDER_PREFIXES = ("change_me", "generate_me")


def generate_password() -> str:
    """Generate a dotenv-safe random password."""
    return secrets.token_urlsafe(32)


def generate_hex_secret(bytes_length: int = 32) -> str:
    """Generate a hexadecimal cryptographic secret."""
    return secrets.token_hex(bytes_length)


def generate_garage_access_key() -> str:
    """Generate a Garage-compatible access key ID."""
    return f"GK{secrets.token_hex(16)}"


FOUNDATION_SECRETS: dict[str, Callable[[], str]] = {
    "POSTGRES_ADMIN_PASSWORD": generate_password,
    "GARAGE_RPC_SECRET": generate_hex_secret,
    "GARAGE_ADMIN_TOKEN": generate_password,
    "GARAGE_METRICS_TOKEN": generate_password,
    "S3_PIPELINE_ACCESS_KEY": generate_garage_access_key,
    "S3_PIPELINE_SECRET_KEY": generate_hex_secret,
}


def run_command(
    command: list[str],
    *,
    check: bool = True,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess from the repository root."""
    return subprocess.run(
        command,
        cwd=ROOT_DIR,
        check=check,
        text=True,
        capture_output=capture_output,
    )


def is_placeholder(value: str) -> bool:
    """Return whether an env value is unset or still a template placeholder."""
    normalized = value.strip()
    return not normalized or normalized.startswith(PLACEHOLDER_PREFIXES)


def initialize_env_file() -> None:
    """Create .env and generate only the secrets required by M0."""
    if not ENV_EXAMPLE_PATH.exists():
        raise RuntimeError(f"Missing required file: {ENV_EXAMPLE_PATH}")

    if not ENV_PATH.exists():
        shutil.copyfile(ENV_EXAMPLE_PATH, ENV_PATH)
        print("[bootstrap] Created .env from .env.example")

    content = ENV_PATH.read_text(encoding="utf-8")

    for key, generator in FOUNDATION_SECRETS.items():
        pattern = re.compile(rf"^{re.escape(key)}=(.*)$", re.MULTILINE)
        match = pattern.search(content)

        if match is None:
            content = f"{content.rstrip()}\n{key}={generator()}\n"
            print(f"[bootstrap] Added {key}")
            continue

        if not is_placeholder(match.group(1)):
            continue

        content = pattern.sub(f"{key}={generator()}", content, count=1)
        print(f"[bootstrap] Generated {key}")

    with ENV_PATH.open("w", encoding="utf-8", newline="\n") as env_file:
        env_file.write(content)


def load_env() -> dict[str, str]:
    """Read simple KEY=VALUE entries from .env."""
    values: dict[str, str] = {}

    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def validate_foundation_secrets(env: dict[str, str]) -> None:
    """Fail before Docker startup when Foundation credentials are invalid."""
    missing = [
        key
        for key in FOUNDATION_SECRETS
        if not env.get(key) or is_placeholder(env[key])
    ]
    if missing:
        raise RuntimeError(
            "Foundation secrets are missing: " + ", ".join(sorted(missing))
        )

    if not re.fullmatch(r"[0-9a-f]{64}", env["GARAGE_RPC_SECRET"]):
        raise RuntimeError(
            "GARAGE_RPC_SECRET must be a 32-byte hexadecimal value."
        )

    if not re.fullmatch(r"GK[0-9a-f]{32}", env["S3_PIPELINE_ACCESS_KEY"]):
        raise RuntimeError("S3_PIPELINE_ACCESS_KEY has an invalid format.")

    if not re.fullmatch(r"[0-9a-f]{64}", env["S3_PIPELINE_SECRET_KEY"]):
        raise RuntimeError("S3_PIPELINE_SECRET_KEY has an invalid format.")


def validate_docker() -> None:
    """Ensure Docker Engine and Docker Compose are available and valid."""
    run_command(["docker", "info"], capture_output=True)
    run_command(["docker", "compose", "version"], capture_output=True)
    run_command(["docker", "compose", "config", "--quiet"])
    print("[bootstrap] Docker Compose configuration is valid")


def start_foundation() -> None:
    """Start only M0 services."""
    run_command(
        ["docker", "compose", "up", "-d", "postgres", "garage"]
    )


def container_health(container_name: str) -> str:
    """Return Docker health status for a container."""
    result = run_command(
        [
            "docker",
            "inspect",
            "--format",
            (
                "{{if .State.Health}}"
                "{{.State.Health.Status}}"
                "{{else}}"
                "{{.State.Status}}"
                "{{end}}"
            ),
            container_name,
        ],
        check=False,
        capture_output=True,
    )
    return "missing" if result.returncode != 0 else result.stdout.strip()


def wait_for_healthy(
    container_name: str,
    timeout_seconds: int = 120,
) -> None:
    """Wait for a container to become healthy."""
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        status = container_health(container_name)

        if status == "healthy":
            print(f"[bootstrap] {container_name}: healthy")
            return

        if status in {"unhealthy", "exited", "dead"}:
            raise RuntimeError(
                f"{container_name} entered state: {status}"
            )

        time.sleep(2)

    raise TimeoutError(f"Timed out waiting for {container_name}")


def garage_command(
    *arguments: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Execute Garage CLI inside its container."""
    return run_command(
        ["docker", "exec", GARAGE_CONTAINER, "/garage", *arguments],
        check=check,
        capture_output=True,
    )


def ensure_bucket(bucket: str) -> None:
    """Create a Garage bucket only when absent."""
    result = garage_command("bucket", "info", bucket, check=False)

    if result.returncode == 0:
        print(f"[bootstrap] Bucket exists: {bucket}")
        return

    garage_command("bucket", "create", bucket)
    print(f"[bootstrap] Created bucket: {bucket}")


def grant_pipeline_access(bucket: str, access_key: str) -> None:
    """Ensure the pipeline key has read/write access to an engineering bucket."""
    garage_command(
        "bucket",
        "allow",
        "--read",
        "--write",
        bucket,
        "--key",
        access_key,
    )
    print(f"[bootstrap] Pipeline read/write granted: {bucket}")


def provision_garage(env: dict[str, str]) -> None:
    """Provision approved M0 buckets and permissions."""
    buckets = {
        "raw": env["S3_BUCKET_RAW"],
        "bronze": env["S3_BUCKET_BRONZE"],
        "silver": env["S3_BUCKET_SILVER"],
        "gold": env["S3_BUCKET_GOLD"],
        "ml": env["S3_BUCKET_ML"],
    }

    for bucket in buckets.values():
        ensure_bucket(bucket)

    access_key = env["S3_PIPELINE_ACCESS_KEY"]

    # Raw access is created by Garage --default-bucket.
    # Engineering pipeline receives Bronze/Silver/Gold.
    for layer in ("bronze", "silver", "gold"):
        grant_pipeline_access(buckets[layer], access_key)

    # Deliberately no pipeline access to olist-ml in M0.
    result = garage_command("bucket", "list")
    print("[bootstrap] Garage buckets:")
    print(result.stdout.rstrip())


def show_status() -> None:
    """Display final Foundation state."""
    run_command(["docker", "compose", "ps", "postgres", "garage"])


def main() -> int:
    try:
        print("[bootstrap] Initializing Foundation")
        initialize_env_file()
        env = load_env()
        validate_foundation_secrets(env)
        validate_docker()
        start_foundation()
        wait_for_healthy(POSTGRES_CONTAINER)
        wait_for_healthy(GARAGE_CONTAINER)
        provision_garage(env)
        show_status()
        print("[bootstrap] Foundation ready")
        return 0
    except (
        RuntimeError,
        TimeoutError,
        subprocess.CalledProcessError,
        FileNotFoundError,
    ) as exc:
        print(f"[bootstrap] ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
