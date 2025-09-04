# core.py

def encode_uvoxid(r_um: int, lat_microdeg: int, lon_microdeg: int) -> int:
    """
    Encode spherical coordinates into a 192-bit UVoxID integer.
    Fixed units:
      - r_um: radius in micrometers (µm)
      - lat_microdeg: latitude in millionths of a degree (-90e6 to +90e6)
      - lon_microdeg: longitude in millionths of a degree (-180e6 to +180e6)
    Returns: 192-bit integer UVoxID.
    """
    lat_enc = lat_microdeg + 90_000_000
    lon_enc = lon_microdeg + 180_000_000

    # Pack fields: [ r (64b) | lat (64b) | lon (64b) ]
    return (r_um << (64 + 64)) | (lat_enc << 64) | lon_enc


def decode_uvoxid(uvoxid: int) -> tuple[int, int, int]:
    """
    Decode a 192-bit UVoxID integer back into spherical coordinates.
    Returns:
      - r_um (micrometers, µm)
      - lat_microdeg (latitude in millionths of a degree)
      - lon_microdeg (longitude in millionths of a degree)
    """
    mask64 = (1 << 64) - 1

    lon_enc = uvoxid & mask64
    lat_enc = (uvoxid >> 64) & mask64
    r_um = (uvoxid >> (64 + 64)) & mask64

    lat_microdeg = lat_enc - 90_000_000
    lon_microdeg = lon_enc - 180_000_000

    return r_um, lat_microdeg, lon_microdeg
