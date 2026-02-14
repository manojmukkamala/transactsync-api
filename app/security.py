import os

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

# Read API key from environment. If not set, security is disabled (useful for local dev).
EXPECTED_API_KEY = os.getenv('API_KEY')
API_KEY_NAME = 'x-api-key'

# APIKeyHeader will create the OpenAPI security scheme automatically when used with Security
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def get_api_key(api_key: str | None = Security(api_key_header)) -> str | None:
    """
    Security dependency using `APIKeyHeader`.

    - If `API_KEY` is not set, returns None (no enforcement).
    - If `API_KEY` is set, requires the header `x-api-key` to match it.
    """
    if not EXPECTED_API_KEY:
        return None

    if not api_key or api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail='Forbidden: invalid API key')

    return api_key
