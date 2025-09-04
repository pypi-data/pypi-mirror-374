"""
formats.py — encoding/decoding helpers for UVoxID

Provides consistent, reversible conversions between the core 192-bit UVoxID
integer and common formats:
  - Binary (24-byte)
  - Hexadecimal (48-character string with dashes)
  - Base32 (3-field grouped string)
  - Flat Base32 (single ungrouped string)
"""

import base64


# --- Binary ---
def uvoxid_to_bin(uvoxid: int) -> bytes:
    """Convert 192-bit int → 24-byte binary."""
    return uvoxid.to_bytes(24, byteorder="big")

def bin_to_uvoxid(b: bytes) -> int:
    """Convert 24-byte binary → 192-bit int."""
    return int.from_bytes(b, "big")


# --- Hexadecimal ---
def uvoxid_to_hex(uvoxid: int) -> str:
    """Convert 192-bit int → 48-char hex string with dashes."""
    raw_hex = f"{uvoxid:048x}"
    return f"{raw_hex[:16]}-{raw_hex[16:32]}-{raw_hex[32:]}"

def hex_to_uvoxid(h: str) -> int:
    """Convert 48-char hex string (with or without dashes) → 192-bit int."""
    clean = h.replace("-", "")
    return int(clean, 16)


# --- Base32 (3-field grouped) ---
def uvoxid_to_b32(uvoxid: int) -> str:
    """
    Convert to Base32 string grouped by field:
      uvoxid:RRRRRRRRRRRRR-LLLLLLLLLLLLL-MMMMMMMMMMMMM
    Each field (64 bits) -> 13 Base32 chars (unpadded).
    """
    raw = uvoxid.to_bytes(24, "big")
    r_bytes, lat_bytes, lon_bytes = raw[:8], raw[8:16], raw[16:24]

    r_b32 = base64.b32encode(r_bytes).decode("ascii").rstrip("=")
    lat_b32 = base64.b32encode(lat_bytes).decode("ascii").rstrip("=")
    lon_b32 = base64.b32encode(lon_bytes).decode("ascii").rstrip("=")

    return f"uvoxid:{r_b32}-{lat_b32}-{lon_b32}"

def b32_to_uvoxid(s: str) -> int:
    """Decode from 3-field Base32 string back into 192-bit UVoxID."""
    clean = s.replace("uvoxid:", "")
    r_b32, lat_b32, lon_b32 = clean.split("-")

    def pad_b32(field: str) -> str:
        padlen = (8 - len(field) % 8) % 8
        return field + "=" * padlen

    r_bytes = base64.b32decode(pad_b32(r_b32))
    lat_bytes = base64.b32decode(pad_b32(lat_b32))
    lon_bytes = base64.b32decode(pad_b32(lon_b32))

    return int.from_bytes(r_bytes + lat_bytes + lon_bytes, "big")


# --- Flat Base32 (ungrouped) ---
def uvoxid_to_flatb32(uvoxid: int) -> str:
    """Convert to flat Base32 string (no grouping)."""
    raw = uvoxid.to_bytes(24, "big")
    return "uvoxid:" + base64.b32encode(raw).decode("ascii").rstrip("=")

def flatb32_to_uvoxid(s: str) -> int:
    """Decode flat Base32 string back into 192-bit UVoxID."""
    clean = s.replace("uvoxid:", "").replace("-", "")
    padlen = (8 - len(clean) % 8) % 8
    return int.from_bytes(base64.b32decode(clean + "="*padlen), "big")


# --- Example usage ---
if __name__ == "__main__":
    example_uv = 1234567890123456789012345678901234567890  # dummy 192-bit int
    print("Binary →", uvoxid_to_bin(example_uv))
    print("Hex →", uvoxid_to_hex(example_uv))
    print("B32 grouped →", uvoxid_to_b32(example_uv))
    print("B32 flat →", uvoxid_to_flatb32(example_uv))
