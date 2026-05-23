import hmac
import hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verifies that the webhook payload was signed by GitHub using our shared secret.
    """
    if not signature:
        return False
    
    # GitHub signature is in 'sha256=XXXX' format
    if signature.startswith("sha256="):
        signature = signature[7:]
        
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
