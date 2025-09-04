"""C2PA interoperability helpers for EncypherAI.

This package groups utilities that allow EncypherAI to produce and consume
strictly-compliant C2PA artefacts. Sub-modules are organised by media type.

Exports:
  - Low-level text wrapper helpers from ``text_wrapper``
  - Conversion helpers from ``c2pa_core`` (module previously named ``c2pa.py``)
"""

from typing import Any  # noqa: F401  (kept for public API type hints, if needed)

# Conversion helpers (public re-exports)
from ..c2pa_core import (
    c2pa_like_dict_to_encypher_manifest,
    encypher_manifest_to_c2pa_like_dict,
    get_c2pa_manifest_schema,
)  # noqa: F401

# Text manifest wrapper utilities (public re-exports)
from .text_wrapper import ALGORITHM_IDS, MAGIC, VERSION, encode_wrapper, find_and_decode  # noqa: F401
