"""
Voxelized Sun model for UVoxID.
All distances are in micrometers (µm).
Layer boundaries are approximate — simplified for simulation.
"""

from uvoxid.core import decode_uvoxid

# --- Solar constants ---
R_SUN_UM = 696_340_000_000_000  # Sun mean radius (µm)

# Approximate layer boundaries (fractions of solar radius)
solar_layers = [
    {"name": "Core", "r_min": 0, "r_max": int(0.25 * R_SUN_UM)},       # ~25%
    {"name": "Radiative Zone", "r_min": int(0.25 * R_SUN_UM), "r_max": int(0.70 * R_SUN_UM)},  # 25–70%
    {"name": "Convective Zone", "r_min": int(0.70 * R_SUN_UM), "r_max": int(1.00 * R_SUN_UM)}, # 70–100%
    {"name": "Photosphere", "r_min": int(0.999 * R_SUN_UM), "r_max": R_SUN_UM},                # thin skin
    {"name": "Corona (approx)", "r_min": R_SUN_UM, "r_max": int(2.00 * R_SUN_UM)},             # extended
]

def classify_sun_r(r_um: int) -> str:
    """
    Return solar layer name for a given radius in µm.
    """
    for layer in solar_layers:
        if layer["r_min"] <= r_um <= layer["r_max"]:
            return layer["name"]
    return "Interplanetary Space"

def classify_sun_uvoxid(uvoxid: int) -> str:
    """
    Return solar layer name for a given UVoxID.
    """
    r_um, _, _ = decode_uvoxid(uvoxid)
    return classify_sun_r(r_um)

def is_inside_sun(r_um: int) -> bool:
    """
    Check if a radius is inside the solar body (≤ mean radius).
    """
    return r_um <= R_SUN_UM

# --- Example usage ---
if __name__ == "__main__":
    test_radii = [
        0,
        int(0.2 * R_SUN_UM),    # Core
        int(0.5 * R_SUN_UM),    # Radiative Zone
        int(0.8 * R_SUN_UM),    # Convective Zone
        int(0.9995 * R_SUN_UM), # Photosphere
        int(1.5 * R_SUN_UM),    # Corona
        int(3.0 * R_SUN_UM),    # Outside
    ]
    for r in test_radii:
        print(r, "→", classify_sun_r(r))
