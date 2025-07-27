import os, requests
from jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from functools import lru_cache

AUTH0_DOMAIN   = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE")
ALGORITHMS     = ["RS256"]

print(f"DEBUG: AUTH0_DOMAIN = {AUTH0_DOMAIN}")
print(f"DEBUG: AUTH0_AUDIENCE = {AUTH0_AUDIENCE}")

if not AUTH0_DOMAIN or not AUTH0_AUDIENCE:
    raise ValueError("AUTH0_DOMAIN and AUTH0_AUDIENCE must be set in environment variables")

@lru_cache(maxsize=1)
def get_jwks():
    """Fetch JWKS with caching"""
    try:
        response = requests.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching JWKS: {e}")
        raise

token_scheme = HTTPBearer()

def _get_key(token):
    jwks = get_jwks()
    kid = jwt.get_unverified_header(token)["kid"]
    key = next(k for k in jwks["keys"] if k["kid"] == kid)
    return jwt.construct_rsa_public_key(key)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(token_scheme)):
    try:
        payload = jwt.decode(
            creds.credentials,
            _get_key(creds.credentials),
            algorithms=ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
        return payload            # has "sub", "email", …
    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token")
