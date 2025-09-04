"""
UVoxID: Universal Voxel Identifier

A Python library for encoding and decoding spherical spatial coordinates
at micrometer precision into a 192-bit integer format.

Features:
- Encode/decode UVoxID (r, latitude, longitude).
- Multiple conversion formats: binary, hex, grouped Base32, flat Base32.
- Earth model corrections (WGS84 ellipsoid).
- Scale introspection (estimate voxel resolution at different radii).
"""

from .core import (
    encode_uvoxid,
    decode_uvoxid,
)

from .formats import (
    uvoxid_to_bin,
    bin_to_uvoxid,
    uvoxid_to_hex,
    hex_to_uvoxid,
    uvoxid_to_b32,
    b32_to_uvoxid,
    uvoxid_to_flatb32,
    flatb32_to_uvoxid,
)

from .corrections import (
    earth_radius_at_lat,
    terrain_offset,
    is_inside_earth,
)

from .scale import (
    uvoxid_scale,
)

__all__ = [
    # Core
    "encode_uvoxid",
    "decode_uvoxid",

    # Formats
    "uvoxid_to_bin",
    "bin_to_uvoxid",
    "uvoxid_to_hex",
    "hex_to_uvoxid",
    "uvoxid_to_b32",
    "b32_to_uvoxid",
    "uvoxid_to_flatb32",
    "flatb32_to_uvoxid",

    # Corrections
    "earth_radius_at_lat",
    "terrain_offset",
    "is_inside_earth",

    # Scale
    "uvoxid_scale",
]
