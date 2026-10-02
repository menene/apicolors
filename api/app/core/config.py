from dataclasses import dataclass
from os import getenv


def csv_setting(name: str, default: str) -> tuple[str, ...]:
    return tuple(value.strip() for value in getenv(name, default).split(",") if value.strip())


@dataclass(frozen=True)
class Settings:
    cors_origins: tuple[str, ...]
    trusted_hosts: tuple[str, ...]
    api_rate_limit: str
    palette_rate_limit: str


settings = Settings(
    cors_origins=csv_setting(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ),
    trusted_hosts=csv_setting(
        "TRUSTED_HOSTS",
        "localhost,127.0.0.1,api,testserver",
    ),
    api_rate_limit=getenv("API_RATE_LIMIT", "10/second"),
    palette_rate_limit=getenv("PALETTE_RATE_LIMIT", "2/second"),
)
