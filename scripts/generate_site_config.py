#!/usr/bin/env python3
"""Generate the public landing-page configuration from a local .env file."""

from argparse import ArgumentParser
from json import dumps
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def read_setting(path: Path, name: str) -> str:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == name:
            return value.strip().strip('"\'')
    raise SystemExit(f"Missing {name} in {path}")


def validate_public_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SystemExit("APP_URL must be an absolute HTTP or HTTPS URL")
    return value


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--env", type=Path, default=PROJECT_ROOT / ".env")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "site-config.js")
    args = parser.parse_args()

    app_url = validate_public_url(read_setting(args.env, "APP_URL"))
    contents = (
        "window.APICOLORS_CONFIG = Object.freeze({\n"
        f"  appUrl: {dumps(app_url)},\n"
        "});\n"
    )
    args.output.write_text(contents, encoding="utf-8")
    print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
