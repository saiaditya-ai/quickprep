"""
Auth0 JWT Token Verification
Handles Auth0 JWT token validation using RS256 algorithm
"""

import jwt
import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from functools import lru_cache
from typing import Dict

security = HTTPBearer()

# Auth0 configuration from environment variables
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
AUTH0_ALGORITHM = "RS256"

if not AUTH0_DOMAIN or not AUTH0_API_AUDIENCE:
    raise ValueError("AUTH0_DOMAIN and AUTH0_API_AUDIENCE must be set in environment variables")

@lru_cache(maxsize=32)
def get_jwks() -> Dict:
    """Fetch Auth0 JSON Web Key Set (JWKS) with caching"""
    try:
        jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch JWKS from Auth0: {str(e)}"
        )

def get_rsa_key(token: str) -> Dict:
    """Extract RSA key from JWKS based on token's kid (key ID)"""
    try:
        # Decode token header to get kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise HTTPException(
                status_code=401,
                detail="Token header missing 'kid' field"
            )

        # Get JWKS and find matching key
        jwks = get_jwks()
        rsa_key = {}

        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = {
                    "kty": key.get("kty"),
                    "kid": key.get("kid"),
                    "use": key.get("use"),
                    "n": key.get("n"),
                    "e": key.get("e")
                }
                break

        if not rsa_key:
            raise HTTPException(
                status_code=401,
                detail="Unable to find appropriate key in JWKS"
            )

        return rsa_key

    except jwt.DecodeError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )

def verify_token_internal(token: str) -> Dict:
    """Verify and decode Auth0 JWT token"""
    try:
        # Get RSA key for token verification
        rsa_key = get_rsa_key(token)

        # Convert RSA key to public key
        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(rsa_key)

        # Verify and decode token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[AUTH0_ALGORITHM],
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Token verification failed: {str(e)}"
        )

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    FastAPI dependency for Auth0 JWT token verification
    Returns decoded token payload if valid
    """
    token = credentials.credentials
    return verify_token_internal(token)
