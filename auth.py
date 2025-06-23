#!/usr/bin/env python3
"""
Authentication utilities for PreciseMCP Server
"""

import asyncio
import logging
import json
import time
import jwt
import httpx
from config import RADFLOW_PARTNER_API_URL, PARTNER_API_KEY

logger = logging.getLogger("precise-mcp-server")

# In-memory cache for the JWT
JWT_CACHE = {"token": None, "expires_at": 0}

async def get_and_cache_jwt_token() -> str:
    """
    Get a JWT token, using a cache to avoid repeated requests.
    If the cached token is expired or not present, it fetches a new one.

    Returns:
        The JWT token string.

    Raises:
        Exception: If fetching or parsing the token fails.
    """
    # Check if the cached token is still valid (with a 60-second buffer)
    if JWT_CACHE["token"] and JWT_CACHE["expires_at"] > time.time() + 60:
        logger.info("Using cached JWT token.")
        return JWT_CACHE["token"]

    logger.info("Fetching new JWT token.")
    url = f"{RADFLOW_PARTNER_API_URL}?partnerApiKey={PARTNER_API_KEY}"
    headers = {"Accept": "application/json"}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(url, headers=headers, timeout=30.0)
            response.raise_for_status()  # Will raise an exception for 4xx/5xx status
            
            data = response.json()
            token_data = data.get("result") # The token data is in the 'result' field

            if not token_data:
                raise ValueError("API response missing 'result' object")

            jwt_token = token_data.get("jwtToken")

            if not jwt_token:
                raise ValueError("JWT token is missing or invalid in API response")

            # Decode the token to get the expiration time from its payload
            decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
            expires_at = decoded_token.get("exp")

            if not expires_at:
                raise ValueError("Expiration time ('exp') not found in JWT payload")

            # Update cache
            JWT_CACHE["token"] = jwt_token
            JWT_CACHE["expires_at"] = expires_at
            logger.info("Successfully fetched and cached new JWT token.")
            
            return jwt_token

        except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError, ValueError, jwt.PyJWTError) as e:
            logger.error(f"Failed to get or cache JWT token: {e}")
            raise Exception(f"Could not retrieve authentication token: {e}") 