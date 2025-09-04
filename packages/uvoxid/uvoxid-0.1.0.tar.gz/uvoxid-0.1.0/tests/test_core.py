import pytest
from datetime import datetime, timezone

from uvoxid.core import encode_uvoxid, decode_uvoxid
from uvoxid.formats import (
    uvoxid_to_bin, bin_to_uvoxid,
    uvoxid_to_hex, hex_to_uvoxid,
    uvoxid_to_b32, b32_to_uvoxid,
    uvoxid_to_flatb32, flatb32_to_uvoxid,
)
from uvoxid.corrections import earth_radius_at_lat, is_inside_earth
from uvoxid.scale import uvoxid_scale
from extras.moon import classify_moon_r, is_inside_moon
from extras.sun import classify_sun_r, is_inside_sun
from extras.ephemeris import sun_barycenter_uvoxid, moon_phase_name


def test_encode_decode_roundtrip():
    r = 6_371_000_000_000
    lat = 12_345_678
    lon = -98_765_432
    uv = encode_uvoxid(r, lat, lon)
    r2, lat2, lon2 = decode_uvoxid(uv)
    assert (r, lat, lon) == (r2, lat2, lon2)


def test_format_roundtrips():
    r = 6_371_000_000_000
    uv = encode_uvoxid(r, 0, 0)

    # Binary
    assert bin_to_uvoxid(uvoxid_to_bin(uv)) == uv

    # Hex
    assert hex_to_uvoxid(uvoxid_to_hex(uv)) == uv

    # Base32 (3-field grouped)
    assert b32_to_uvoxid(uvoxid_to_b32(uv)) == uv

    # Flat Base32 (ungrouped)
    assert flatb32_to_uvoxid(uvoxid_to_flatb32(uv)) == uv


def test_earth_radius_at_lat():
    eq = earth_radius_at_lat(0)
    pole = earth_radius_at_lat(90_000_000)
    # Within ~1 km tolerance
    assert abs(eq - 6_378_137_000_000) < 1e9
    assert abs(pole - 6_356_752_000_000) < 1e9


def test_is_inside_earth():
    r_inside = 6_371_000_000_000
    r_outside = 7_000_000_000_000
    assert is_inside_earth(r_inside, 0, 0)
    assert not is_inside_earth(r_outside, 0, 0)


def test_scale_function():
    res_m, info = uvoxid_scale("uvoxid:AAAAAAAAAAAAAAAF")
    assert isinstance(res_m, float)
    assert "Resolution" in info


def test_moon_layers():
    r = 0
    assert classify_moon_r(r) in {"Inner Core", "Outer Core", "Mantle", "Crust", "Space"}
    assert is_inside_moon(r)


def test_sun_layers():
    r = 0
    assert classify_sun_r(r) in {
        "Core", "Radiative Zone", "Convective Zone",
        "Photosphere", "Corona (approx)", "Interplanetary Space"
    }
    assert is_inside_sun(r)


def test_ephemeris_basics():
    now = datetime.now(timezone.utc)
    uv = sun_barycenter_uvoxid(now)
    assert isinstance(uv, int)
    phase = moon_phase_name(now)
    assert phase in {
        "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
        "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"
    }
