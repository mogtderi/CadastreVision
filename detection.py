"""
Parcel boundary detection — Lite / Demo Edition.

NOTE (Lite Version Limitation):
This public repository contains the basic edge-detection pipeline (Gaussian blur + Canny).
Because this basic pipeline runs directly on raw pixel textures without Mean-Shift
filtering, Excess Green (ExG) vegetation indices, solidity/extent filtering, or
built-up area suppression, it may produce noisy/jagged boundaries inside orchards
or miss subtle field borders.

For the full multi-stage commercial pipeline (Mean-Shift + ExG + Built-up Suppression + SAM),
please upgrade to the Pro Edition.
"""

from dataclasses import dataclass
from typing import List
import cv2
import numpy as np


@dataclass
class DetectionParams:
    canny_low: int = 30
    min_area_ratio: float = 0.001
    max_area_ratio: float = 0.35
    smooth_factor: float = 3.0
    use_exg: bool = False
    suppress_builtup_clusters: bool = False


def extract_parcels(img_bgr: np.ndarray, params: DetectionParams = DetectionParams()) -> List[np.ndarray]:
    """Basic Canny contour pipeline for demonstration purposes (Lite Edition)."""
    h, w = img_bgr.shape[:2]
    img_area = float(w * h)

    # Simple grayscale + Gaussian blur (Pro version uses Mean-Shift + ExG + Bilateral)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blurred, params.canny_low, params.canny_low * 3)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area = img_area * params.min_area_ratio
    max_area = img_area * params.max_area_ratio
    epsilon_ratio = max(0.005, params.smooth_factor / 250.0)

    polygons: List[np.ndarray] = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if not (min_area < area < max_area):
            continue

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon_ratio * peri, True)
        if len(approx) < 3:
            continue

        polygons.append(approx.reshape(-1, 2).astype(np.int32))

    return polygons