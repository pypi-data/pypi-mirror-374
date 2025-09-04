"""
Core encoding and decoding functionality for EncypherAI.
"""

from encypher.core.keys import generate_ed25519_key_pair as generate_key_pair
from encypher.core.keys import load_private_key_from_data as load_private_key
from encypher.core.keys import load_public_key_from_data as load_public_key
from encypher.core.payloads import BasicPayload, ManifestPayload
from encypher.core.signing import sign_payload, verify_signature
from encypher.core.unicode_metadata import MetadataTarget, UnicodeMetadata

__all__ = [
    "BasicPayload",
    "ManifestPayload",
    "MetadataTarget",
    "UnicodeMetadata",
    "generate_key_pair",
    "load_private_key",
    "load_public_key",
    "sign_payload",
    "verify_signature",
]
