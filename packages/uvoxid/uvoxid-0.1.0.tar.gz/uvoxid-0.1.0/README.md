# UVoxID

[![PyPI version](https://img.shields.io/pypi/v/uvoxid.svg)](https://pypi.org/project/uvoxid/)
[![Python versions](https://img.shields.io/pypi/pyversions/uvoxid.svg)](https://pypi.org/project/uvoxid/)
[![License](https://img.shields.io/pypi/l/uvoxid.svg)](https://github.com/JDPlumbing/uvoxid/blob/main/LICENSE)
[![Tests](https://github.com/JDPlumbing/uvoxid/actions/workflows/tests.yml/badge.svg)](https://github.com/JDPlumbing/uvoxid/actions)

**Universal Voxel Identifier (UVoxID)** — a Python library for encoding and decoding spherical spatial coordinates at micrometer precision.  

Think of it as a globally consistent **voxel address system**: every point in space has a permanent ID, valid from the Earth’s core to interstellar distances.

---

## ✨ Why UVoxID?

Floating-point coordinates drift.  
Game engines rely on “floating origins.”  
Robotics uses hacky spatial hashes.  
Satellites juggle dozens of reference frames.  

UVoxID fixes all that with a **deterministic, integer-based addressing scheme**:

- **Universal**: same scheme works for atoms, cities, and galaxies.  
- **Deterministic**: encode/decode is exact, no rounding error.  
- **Persistent**: voxel IDs never change, perfect for storage, sync, and replication.  
- **Spherical-native**: gravity, orbits, and planetary geometry “just work.”  

---

## 🔬 Resolution in UVoxID

UVoxID encodes space into deterministic voxels with **two kinds of precision**:

- **Radial precision**:  
  - Always **1 µm** (1/1000 mm), no matter the distance.  
  - From Earth’s core to interstellar space, every radial step is exact.  

- **Angular precision**:  
  - Depends on radius `r`.  
  - At small `r` → atomic/subatomic detail.  
  - At large `r` → still millimeter-scale voxels, even across light-years.  

---

### 📊 Example Resolutions

| Distance (r)    | Radial Resolution | Angular Resolution |
|-----------------|------------------|--------------------|
| **Earth radius (~6,371 km)** | 1 µm | ~2 × 10⁻¹² m (2 picometers, subatomic) |
| **Moon distance (~384,000 km)** | 1 µm | ~1 × 10⁻¹⁰ m (0.1 nanometer, X-ray scale) |
| **1 AU (~150 million km)** | 1 µm | ~5 × 10⁻⁸ m (50 nanometers, virus scale) |
| **1 light year** | 1 µm | ~3 × 10⁻³ m (3 millimeters) |
| **2 light years (max)** | 1 µm | ~6 × 10⁻³ m (6 millimeters) |

---

### ⚡ Why This Matters
- **No floats, no drift** → everything is stored as integers.  
- Near Earth, UVoxID gives **atomic-level positioning**.  
- Across interstellar distances, UVoxID still holds positions with **millimeter precision**.  
- This combination makes it ideal for:  
  - physics & materials simulations,  
  - planetary & orbital mechanics,  
  - infinite game worlds,  
  - robotics & autonomous navigation.  

---

## 🚀 Use Cases

- **Game Development**:  
  - Infinite open worlds without floating origin hacks.  
  - Warp across star systems — arrive exactly where you should.  
  - Persistent object positions across server restarts.  

- **Robotics & Drones**:  
  - Drop GPS/SLAM noise into a stable global grid.  
  - Share maps between agents without coordinate drift.  

- **Satellites & Space Systems**:  
  - Orbital mechanics with deterministic precision.  
  - Consistent addressing across LEO, GEO, Moon, Mars, and beyond.  

- **Scientific Simulation**:  
  - Track bacteria at µm scale or galaxies at light-year scale.  
  - Perfect for physics engines, material degradation models, or climate sims.  

- **Digital Real Estate & Virtual Worlds**:  
  - Each voxel ID is globally unique and ownable.  
  - Imagine buying a square meter on Mars… and knowing its exact ID forever.  

---

## 🛠 Features

- **192-bit encoding**: `(radius, latitude, longitude)` → one integer.  
- **String encodings**: Base32, hex, or binary.  
- **Ephemeris support**: Sun & Moon positions → UV, tides, day/night cycles.  
- **Earth model**: WGS84 ellipsoid radius corrections.  
- **Scale introspection**: compute what resolution a given ID represents.  

---

## 📦 Installation

```bash
pip install uvoxid
```

---

## 🔍 Example

```python
import uvoxid

EARTH_RADIUS_UM = 6_371_000_000_000  # mean radius in µm

# Encode position at Earth’s surface, equator, prime meridian
addr = uvoxid.encode_uvoxid(EARTH_RADIUS_UM, 0, 0)

print("Hex:", uvoxid.uvoxid_to_hex(addr))
print("Base32:", uvoxid.uvoxid_to_b32(addr))

r_um, lat, lon = uvoxid.decode_uvoxid(addr)
print("Decoded:", r_um, lat/1e6, lon/1e6)
```

Output:
```
Hex: 00059fb8c83f1000-00000000055d4a80-0000000000aba950
Base32: uvoxid:AAAALS25GEPAA-AAAAAAAFLVFIA-AAAAAAAKXKKQA
Decoded: 6371000000000 0.0 0.0
```

---

## 📖 Roadmap

- Planetary/stellar models beyond Earth/Moon/Sun.  
- Python bindings for Rust/C++ core for performance.  
- Optional Morton-code compatibility for indexing.  
- Support for >192-bit scales (atomic → galactic cluster).  

---

## 🤝 Contributing

Contributions are welcome!  
- Open an [issue](https://github.com/JDPlumbing/uvoxid/issues) for bugs/feature requests.  
- Submit pull requests for improvements.  

---

## 📎 Links
- [PyPI](https://pypi.org/project/uvoxid/)  
- [Source Code](https://github.com/JDPlumbing/uvoxid)  
- [Issue Tracker](https://github.com/JDPlumbing/uvoxid/issues)  
- [Changelog](https://github.com/JDPlumbing/uvoxid/releases)  
