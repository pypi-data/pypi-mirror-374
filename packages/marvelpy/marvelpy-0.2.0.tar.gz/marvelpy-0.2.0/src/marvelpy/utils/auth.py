"""Authentication utilities for Marvel API."""

import hashlib
import time
from typing import Dict, Any


def generate_auth_params(public_key: str, private_key: str) -> Dict[str, str]:
    """Generate authentication parameters for Marvel API.
    
    Args:
        public_key: Marvel API public key
        private_key: Marvel API private key
        
    Returns:
        Dictionary with authentication parameters
    """
    timestamp = str(int(time.time()))
    hash_string = f"{timestamp}{private_key}{public_key}"
    hash_md5 = hashlib.md5(hash_string.encode()).hexdigest()
    
    return {
        "apikey": public_key,
        "ts": timestamp,
        "hash": hash_md5
    }