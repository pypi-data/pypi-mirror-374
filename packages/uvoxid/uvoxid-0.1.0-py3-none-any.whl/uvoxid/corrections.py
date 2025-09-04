import math

# --- Earth constants (WGS84 ellipsoid, in µm) ---
R_EQ_UM = 6_378_137_000_000   # equatorial radius in µm
R_POL_UM = 6_356_752_000_000  # polar radius in µm

def earth_radius_at_lat(lat_microdeg: int) -> int:
    """
    Return Earth's radius (in µm) at a given latitude.
    Uses ellipsoid formula for an oblate spheroid (WGS84).
    """
    lat_rad = math.radians(lat_microdeg / 1e6)
    cos_phi = math.cos(lat_rad)
    sin_phi = math.sin(lat_rad)

    numerator = (R_EQ_UM**2 * cos_phi)**2 + (R_POL_UM**2 * sin_phi)**2
    denominator = (R_EQ_UM * cos_phi)**2 + (R_POL_UM * sin_phi)**2
    return int(math.sqrt(numerator / denominator))

def terrain_offset(lat_microdeg: int, lon_microdeg: int) -> int:
    """
    Apply local terrain correction in µm.
    TODO: integrate DEM dataset (e.g., SRTM/ETOPO).
    Currently always returns 0.
    """
    return 0

def is_inside_earth(r_um: int, lat_microdeg: int, lon_microdeg: int) -> bool:
    """
    Check if a voxel at r_um is inside Earth's ellipsoid,
    including optional local terrain adjustments.
    """
    surface_r = earth_radius_at_lat(lat_microdeg)
    surface_r += terrain_offset(lat_microdeg, lon_microdeg)
    return r_um <= surface_r
