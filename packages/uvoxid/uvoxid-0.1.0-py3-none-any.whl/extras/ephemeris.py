# ephemeris.py (Sun + Moon alt/az + tidal forces + phase)

import math
from datetime import datetime, timezone
from uvoxid.core import encode_uvoxid, decode_uvoxid
from uvoxid.formats import uvoxid_to_b32

# --- Constants ---
AU_UM = 149_597_870_700_000_000   # 1 AU in µm
MOON_DIST_UM = 384_400_000_000    # Earth–Moon avg distance
M_MOON = 7.35e22                  # Moon mass (kg)
M_SUN = 1.989e30                  # Sun mass (kg)
R_EARTH_M = 6.371e6               # Earth radius (m)
G = 6.67430e-11                   # gravitational constant

def deg2rad(d): return d * math.pi / 180
def rad2deg(r): return r * 180 / math.pi

# --- Sun barycenter ---
def sun_barycenter_uvoxid(when: datetime) -> int:
    jd = (when - datetime(2000,1,1,12,tzinfo=timezone.utc)).total_seconds()/86400.0 + 2451545.0
    n = jd - 2451545.0
    L = (280.46 + 0.9856474 * n) % 360
    g = (357.528 + 0.9856003 * n) % 360
    lam = L + 1.915*math.sin(deg2rad(g)) + 0.020*math.sin(2*deg2rad(g))
    return encode_uvoxid(AU_UM, 0, int(lam * 1e6))

# --- Moon barycenter ---
def moon_barycenter_uvoxid(when: datetime) -> int:
    jd = (when - datetime(2000,1,1,12,tzinfo=timezone.utc)).total_seconds()/86400.0 + 2451545.0
    n = jd - 2451545.0
    L = (218.316 + 13.176396*n) % 360
    return encode_uvoxid(MOON_DIST_UM, 0, int(L * 1e6))

# --- Generic alt/az calculator ---
def alt_az_from_body(voxel_uvoxid: int, body_uvoxid: int):
    r_um, lat_microdeg, lon_microdeg = decode_uvoxid(voxel_uvoxid)
    lat_rad, lon_rad = math.radians(lat_microdeg/1e6), math.radians(lon_microdeg/1e6)

    _, body_lat_microdeg, body_lon_microdeg = decode_uvoxid(body_uvoxid)
    body_lat_rad, body_lon_rad = math.radians(body_lat_microdeg/1e6), math.radians(body_lon_microdeg/1e6)

    H = lon_rad - body_lon_rad
    delta = body_lat_rad

    alt = rad2deg(math.asin(
        math.sin(lat_rad)*math.sin(delta) +
        math.cos(lat_rad)*math.cos(delta)*math.cos(H)
    ))
    az = rad2deg(math.atan2(
        -math.sin(H),
        math.tan(delta)*math.cos(lat_rad) - math.sin(lat_rad)*math.cos(H)
    ))
    return alt, (az + 360) % 360

def solar_alt_az(voxel_uvoxid: int, when: datetime):
    return alt_az_from_body(voxel_uvoxid, sun_barycenter_uvoxid(when))

def lunar_alt_az(voxel_uvoxid: int, when: datetime):
    return alt_az_from_body(voxel_uvoxid, moon_barycenter_uvoxid(when))

# --- Tidal forces ---
def tidal_force(mass: float, dist_m: float) -> float:
    return 2 * G * mass * R_EARTH_M / (dist_m**3)

def lunar_tide_strength() -> float:
    return tidal_force(M_MOON, 384400e3)

def solar_tide_strength() -> float:
    return tidal_force(M_SUN, 1.496e11)

# --- Moon phase ---
def moon_phase_angle(when: datetime) -> float:
    """
    Returns elongation angle Sun–Earth–Moon in degrees.
    0° = New Moon, 180° = Full Moon.
    """
    sun_uv = sun_barycenter_uvoxid(when)
    moon_uv = moon_barycenter_uvoxid(when)

    _, _, sun_lon_microdeg = decode_uvoxid(sun_uv)
    _, _, moon_lon_microdeg = decode_uvoxid(moon_uv)

    sun_lon = sun_lon_microdeg/1e6
    moon_lon = moon_lon_microdeg/1e6

    elong = abs(moon_lon - sun_lon) % 360
    if elong > 180:
        elong = 360 - elong
    return elong

def moon_phase_name(when: datetime) -> str:
    angle = moon_phase_angle(when)
    if angle < 10: return "New Moon"
    if angle < 80: return "Waxing Crescent"
    if angle < 100: return "First Quarter"
    if angle < 170: return "Waxing Gibbous"
    if angle < 190: return "Full Moon"
    if angle < 260: return "Waning Gibbous"
    if angle < 280: return "Last Quarter"
    if angle < 350: return "Waning Crescent"
    return "New Moon"

# --- Pretty print UVoxID ---
def print_uvoxid(label: str, uvoxid: int):
    r_um, lat_microdeg, lon_microdeg = decode_uvoxid(uvoxid)
    print(f"{label}:")
    print("  Base32:", uvoxid_to_b32(uvoxid))
    print(f"  Decoded → r={r_um:,} µm, lat={lat_microdeg/1e6:.4f}°, lon={lon_microdeg/1e6:.4f}°")

# --- Example ---
if __name__ == "__main__":
    now = datetime.now(timezone.utc)

    sun_uv = sun_barycenter_uvoxid(now)
    moon_uv = moon_barycenter_uvoxid(now)

    print_uvoxid("Sun UVoxID", sun_uv)
    print_uvoxid("Moon UVoxID", moon_uv)

    EARTH_RADIUS_UM = 6_371_000_000_000
    voxel = encode_uvoxid(EARTH_RADIUS_UM, int(25.76*1e6), int(-80.19*1e6))  # Miami

    sun_alt, sun_az = solar_alt_az(voxel, now)
    moon_alt, moon_az = lunar_alt_az(voxel, now)

    print(f"Solar altitude: {sun_alt:.2f}°, azimuth: {sun_az:.2f}°")
    print(f"Lunar altitude: {moon_alt:.2f}°, azimuth: {moon_az:.2f}°")
    print(f"Moon tidal accel: {lunar_tide_strength():.2e} m/s²")
    print(f"Sun tidal accel:  {solar_tide_strength():.2e} m/s²")
    print(f"Moon phase: {moon_phase_name(now)} ({moon_phase_angle(now):.1f}° elongation)")
