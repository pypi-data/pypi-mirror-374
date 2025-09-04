"""
Voxelized Moon model for UVoxID.
All distances are in micrometers (µm).
Layer boundaries are approximate — this is a simplified model.
"""

from uvoxid.core import decode_uvoxid

# --- Moon constants ---
R_MOON_UM = 1_737_000_000_000  # Moon mean radius (µm)

# Approximate layer boundaries
moon_layers = [
    {"name": "Inner Core", "r_min": 0, "r_max": int(0.14 * R_MOON_UM)},   # ~240 km
    {"name": "Outer Core", "r_min": int(0.14 * R_MOON_UM), "r_max": int(0.20 * R_MOON_UM)},  # ~330–350 km
    {"name": "Mantle",     "r_min": int(0.20 * R_MOON_UM), "r_max": int(0.97 * R_MOON_UM)},  # crust base ~50 km down
    {"name": "Crust",      "r_min": int(0.97 * R_MOON_UM), "r_max": R_MOON_UM},              # 30–50 km thick
]

def classify_moon_r(r_um: int) -> str:
    """
    Return lunar layer name for a given radius in µm.
    """
    for layer in moon_layers:
        if layer["r_min"] <= r_um <= layer["r_max"]:
            return layer["name"]
    return "Space"

def classify_moon_uvoxid(uvoxid: int) -> str:
    """
    Return lunar layer name for a given UVoxID.
    """
    r_um, _, _ = decode_uvoxid(uvoxid)
    return classify_moon_r(r_um)

def is_inside_moon(r_um: int) -> bool:
    """
    Check if a radius is inside the lunar body (≤ mean radius).
    """
    return r_um <= R_MOON_UM


# --- Example usage ---
if __name__ == "__main__":
    test_radii = [
        0,
        int(0.1 * R_MOON_UM),   # Inner Core
        int(0.18 * R_MOON_UM),  # Outer Core
        int(0.5 * R_MOON_UM),   # Mantle
        int(0.99 * R_MOON_UM),  # Crust
        int(1.2 * R_MOON_UM),   # Outside
    ]
    for r in test_radii:
        print(r, "→", classify_moon_r(r))
