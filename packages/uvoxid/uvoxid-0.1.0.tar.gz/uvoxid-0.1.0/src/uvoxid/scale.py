def uvoxid_scale(uvoxid_str: str) -> tuple[float, str]:
    """
    Estimate the spatial resolution for a UVoxID Base32 string.

    Args:
        uvoxid_str: Base32 UVoxID string (with or without "uvoxid:" prefix).

    Returns:
        (res_m, info_str):
          - res_m: resolution in meters (float)
          - info_str: human-readable string summary
    """
    # Remove prefix and dashes
    clean = uvoxid_str.replace("uvoxid:", "").replace("-", "")

    # Count leading 'A's
    leading_as = len(clean) - len(clean.lstrip("A"))
    total_len = len(clean)

    sig_chars = total_len - leading_as

    # --- Compute resolution ---
    bits_used = sig_chars * 5
    bits_unused = (total_len * 5) - bits_used

    base_res_m = 1e-6  # 1 µm base resolution

    res_m = base_res_m * (2 ** bits_unused)

    # Human-readable scaling
    if res_m >= 1_000:
        scale = f"{res_m/1000:.2f} km"
    elif res_m >= 1:
        scale = f"{res_m:.2f} m"
    elif res_m >= 0.01:
        scale = f"{res_m*100:.2f} cm"
    elif res_m >= 1e-6:
        scale = f"{res_m*1e6:.2f} µm"
    elif res_m >= 1e-9:
        scale = f"{res_m*1e9:.2f} nm"
    else:
        scale = f"{res_m:.2e} m"

    return res_m, f"Resolution ≈ {scale} [{sig_chars} sig chars, {bits_used} bits used]"
