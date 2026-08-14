from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    ".gitattributes",
    ".gitignore",
    ".env.example",
    "docker-compose.yml",
    "LICENSE",
    "NOTICE",
    "README.md",
    "pyproject.toml",
    "docs/LICENSE.md",
    "docs/charter/project-charter.md",
    "docs/architecture/architecture-v1.md",
    "docs/data/source-catalog.md",
    "docs/data/storage-strategy.md",
    "docs/planning/backlog.md",
    "docs/planning/definition-of-done.md",
    "docs/adr/0002-use-minio-as-object-storage.md",
    "docs/adr/0008-adopt-garage-as-s3-compatible-object-storage.md",
    "infrastructure/garage/config/garage.toml",
    "scripts/bootstrap/bootstrap_foundation.py",
]

EXPECTED_BUCKETS = {
    "olist-raw",
    "olist-bronze",
    "olist-silver",
    "olist-gold",
    "olist-ml",
}


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> int:
    try:
        missing = [item for item in REQUIRED if not (ROOT / item).exists()]
        if missing:
            fail("Missing required files: " + ", ".join(missing))

        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        if not re.search(r"(?m)^\.env$", gitignore):
            fail(".gitignore does not ignore .env")

        env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
        if "POSTGRES_ADMIN_PASSWORD=change_me_" not in env_example:
            fail(".env.example must contain placeholders, not real passwords")

        found_buckets = {
            match.group(1)
            for match in re.finditer(
                r"^S3_BUCKET_[A-Z_]+=(.+)$",
                env_example,
                re.MULTILINE,
            )
        }
        if found_buckets != EXPECTED_BUCKETS:
            fail(
                "Unexpected bucket contract. "
                f"Expected {sorted(EXPECTED_BUCKETS)}, got {sorted(found_buckets)}"
            )

        adr2 = (
            ROOT / "docs/adr/0002-use-minio-as-object-storage.md"
        ).read_text(encoding="utf-8")
        if "**Status:** Superseded" not in adr2:
            fail("ADR-0002 must be Superseded")

        adr8 = (
            ROOT
            / "docs/adr/0008-adopt-garage-as-s3-compatible-object-storage.md"
        ).read_text(encoding="utf-8")
        if "**Status:** Accepted" not in adr8:
            fail("ADR-0008 must be Accepted")

        compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        if "postgres:17.11-bookworm" not in compose:
            fail("PostgreSQL image is not pinned as approved")
        if "dxflrs/garage:v2.3.0" not in compose:
            fail("Garage image is not pinned as approved")
        if "127.0.0.1:${POSTGRES_PORT" not in compose:
            fail("PostgreSQL host exposure is not loopback-only")
        if "127.0.0.1:${GARAGE_S3_PORT" not in compose:
            fail("Garage S3 host exposure is not loopback-only")

        garage = (
            ROOT / "infrastructure/garage/config/garage.toml"
        ).read_text(encoding="utf-8")
        if "replication_factor = 1" not in garage:
            fail("Garage single-node replication contract is missing")

        if (ROOT / ".env").exists():
            print("[m0] NOTE: local .env exists; ensure it is never committed.")

        print("[m0] Static Foundation validation: PASS")
        return 0

    except RuntimeError as exc:
        print(f"[m0] FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
