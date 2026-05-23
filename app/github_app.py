import time
import httpx
import jwt
from typing import Optional
from app.config import get_settings

def generate_jwt(app_id: str, private_key: str) -> str:
    """
    Generates a JWT signed with the GitHub App's private key using the RS256 algorithm.
    """
    payload = {
        # Issued at time (set slightly in the past to account for clock drift)
        "iat": int(time.time()) - 60,
        # JWT expiration time (10 minutes max)
        "exp": int(time.time()) + (10 * 60),
        # GitHub App ID as issuer (must be a string per PyJWT requirements)
        "iss": str(app_id)
    }
    
    # Clean up line endings of private key and strip any wrapping quotes
    private_key_str = private_key.strip().strip('"').strip("'")
    
    # If the private_key is a file path rather than the actual key, read it from the file path
    if not private_key_str.startswith("-----BEGIN"):
        try:
            with open(private_key_str, "r") as f:
                key_content = f.read()
        except Exception as e:
            raise ValueError(f"Could not read private key from file path '{private_key_str}': {e}")
    else:
        # Convert literal '\n' or '\\n' text in env values back to actual newlines
        key_content = private_key_str.replace("\\n", "\n")

    # Sign the JWT with the RS256 algorithm
    encoded_jwt = jwt.encode(payload, key_content, algorithm="RS256")
    return encoded_jwt

async def get_installation_access_token(app_id: str, private_key: str, installation_id: int) -> str:
    """
    Exchanges the GitHub App JWT for a short-lived (1 hour) installation access token.
    """
    jwt_token = generate_jwt(app_id, private_key)
    
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "OpenReviewer-App"
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, timeout=10.0)
        if res.status_code == 201:
            token_data = res.json()
            return token_data["token"]
        else:
            raise Exception(
                f"Failed to fetch installation token from GitHub (status {res.status_code}): {res.text}"
            )
