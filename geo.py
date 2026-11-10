"""
Pixel <-> real-world coordinate conversion (Stub for Lite Edition).

In the Pro Edition, this module performs affine georeferencing and automatic
UTM zone projection (EPSG:326xx) for accurate hectare/meter calculations.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeoTransform:
    top_left_lon: float
    top_left_lat: float
    bottom_right_lon: float
    bottom_right_lat: float
    width: int
    height: int


def suggest_utm_epsg(lon: float, lat: float) -> str:
    zone = int((lon + 180) / 6) + 1
    hemisphere_code = 32600 if lat >= 0 else 32700
    return f"EPSG:{hemisphere_code + zone}"