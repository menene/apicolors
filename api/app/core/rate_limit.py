from slowapi import Limiter
from slowapi.util import get_ipaddr

from app.core.config import settings


limiter = Limiter(
    key_func=get_ipaddr,
    default_limits=[settings.api_rate_limit],
    headers_enabled=True,
)
