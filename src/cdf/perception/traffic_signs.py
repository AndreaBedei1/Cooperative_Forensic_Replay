"""Deterministic STOP/YIELD perception from transient RGB frames.

A colour-and-shape detector with frame-to-frame tracking.  It uses no CARLA
labels, actor IDs, maps or ground truth: only the pixels of one camera.

Candidates are the external contours of the red mask (HSV, two hue bands,
opened and closed).  A contour touching the image border is rejected: its
shape is truncated and cannot be verified (the S10 false STOP was a red
advertising board cut by the image border).  The remaining ones are classified
by their geometry:

  STOP   a regular convex octagon: hull compactness (4 pi A / P^2; 0.948 for a
         regular octagon) at least ``stop_min_compactness``, at least
         ``stop_min_vertices`` corners once the plate is large enough to show
         them, a nearly square box (perspective narrows a plate seen from the
         side, hence ``stop_aspect``), a red fraction typical of a plate with
         letters (``stop_red_fraction``) and white letters inside it
         (``stop_min_letters``: low-saturation bright pixels in the central band),
         which no brick wall, tail light or red car shows;
  YIELD  an inverted triangle: 3-4 corners (5 when small), box fill about 0.5,
         the top edge much wider than the bottom (apex down), a red border with
         a white interior.

Detections are tracked between frames by class, centre distance (relative to
the image width), size consistency and time gap; a track is confirmed after
``min_detections_per_track`` detections with a stable shape.  Thresholds were
calibrated on CARLA frames (Town05 STOP plates, the Town10HD YIELD sign; S10's
red board and Town05's brick facades as negatives), see the README.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

STOP = "STOP"
YIELD = "YIELD"


def _cv2() -> Any:
    try:
        import cv2
    except ImportError as exc:  # pragma: no cover
        raise ImportError("sign perception needs OpenCV; install opencv-python") from exc
    return cv2


def _get(cfg: Any, key: str, default: Any) -> Any:
    if cfg is None:
        return default
    if hasattr(cfg, "get"):
        try:
            value = cfg.get(key, default)
            if value != default:
                return value
        except TypeError:
            pass
    if isinstance(cfg, Mapping):
        if key in cfg:
            return cfg[key]
        node: Any = cfg
        for part in key.split("."):
            if not isinstance(node, Mapping) or part not in node:
                return default
            node = node[part]
        return node
    return default


def _value(cfg: Any, name: str, default: Any) -> Any:
    got = _get(cfg, "traffic_signs." + name, None)
    if got is None:
        got = _get(cfg, name, None)
    return default if got is None else got


@dataclass
class SignDetection:
    frame: int
    t: float
    sign_class: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    n_vertices: int = 0
    fill_ratio: float = 0.0  # contour area / bounding box area
    redness: float = 0.0  # red fraction inside the contour
    compactness: float = 0.0
    letters: float = 0.0  # white fraction in the central band
    image_width: int = 0
    bearing_deg: float = 0.0  # horizontal angle of the box centre from the camera axis (+ = right)

    @property
    def area(self) -> int:
        return int(self.bbox[2] * self.bbox[3])

    @property
    def size(self) -> int:
        return int(max(self.bbox[2], self.bbox[3]))

    @property
    def aspect(self) -> float:
        return float(self.bbox[2]) / float(max(self.bbox[3], 1))

    @property
    def centre(self) -> Tuple[float, float]:
        x, y, w, h = self.bbox
        return x + w / 2.0, y + h / 2.0

    def as_dict(self) -> Dict[str, Any]:
        return {"frame": self.frame, "t_local": round(self.t, 4), "class": self.sign_class,
                "confidence": round(self.confidence, 4), "bbox": list(self.bbox),
                "n_vertices": self.n_vertices, "fill_ratio": round(self.fill_ratio, 4),
                "redness": round(self.redness, 4), "compactness": round(self.compactness, 4),
                "letters": round(self.letters, 4), "bearing_deg": round(self.bearing_deg, 2)}


@dataclass
class SignTrack:
    track_id: str
    sign_class: str
    detections: List[SignDetection] = field(default_factory=list)
    relevance_bearing_deg: float = 30.0

    @property
    def t_first(self) -> float: return self.detections[0].t
    @property
    def frame_first(self) -> int: return self.detections[0].frame
    @property
    def frame_confirmed(self) -> int:
        # The tracker writes this value at serialization time; callers that do
        # not know the configured threshold use the historical default of 3.
        return self.detections[min(2, len(self.detections) - 1)].frame
    @property
    def t_last(self) -> float: return self.detections[-1].t
    @property
    def best(self) -> SignDetection: return max(self.detections, key=lambda d: d.confidence)
    @property
    def growing(self) -> bool:
        if len(self.detections) < 4:
            return False
        third = max(1, len(self.detections) // 3)
        early = sum(d.area for d in self.detections[:third]) / third
        late = sum(d.area for d in self.detections[-third:]) / third
        return late > early * 1.15

    def centredness(self, image_width: int) -> float:
        if image_width <= 0:
            return 0.0
        x, _ = self.best.centre
        return float(max(0.0, 1.0 - abs(x - image_width / 2.0) / (image_width / 2.0)))

    @property
    def min_bearing_deg(self) -> float:
        return min(abs(d.bearing_deg) for d in self.detections)

    def relevance(self, image_width: int) -> Dict[str, Any]:
        """Image-only judgement whether the sign governs the camera's own path: it came
        within ``relevance_bearing_deg`` of the camera axis and grew as the vehicle approached."""
        near_axis = self.min_bearing_deg <= self.relevance_bearing_deg
        return {"relevant_to_ego_path": bool(near_axis and self.growing),
                "centredness": round(self.centredness(image_width), 4), "growing": self.growing,
                "min_bearing_deg": round(self.min_bearing_deg, 1),
                "basis": "image geometry only: how close to the camera axis the sign came and whether it grew "
                         "as the vehicle approached. No map is consulted"}

    def as_dict(self, image_width: int = 0) -> Dict[str, Any]:
        return {"sign_track_id": self.track_id, "class": self.sign_class,
                "frame_first": self.frame_first, "frame_confirmed": self.frame_confirmed,
                "frame_last": self.detections[-1].frame,
                "n_detections": len(self.detections), "t_first": round(self.t_first, 4),
                "t_confirmed": round(self.detections[min(2, len(self.detections) - 1)].t, 4),
                "t_last": round(self.t_last, 4), "best_confidence": round(self.best.confidence, 4),
                "best_bbox": list(self.best.bbox), "relevance": self.relevance(image_width),
                "detections": [d.as_dict() for d in self.detections]}


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, value))


class SignDetector:
    def __init__(self, cfg: Optional[Any] = None) -> None:
        val = lambda name, default: _value(cfg, name, default)  # noqa: E731
        self.min_area_px = int(val("min_area_px", 100))
        self.min_saturation = int(val("min_saturation", 90))
        self.min_value = int(val("min_value", 50))
        self.close_kernel_px = int(val("close_kernel_px", 5))
        self.border_margin_px = int(val("border_margin_px", 2))
        self.max_centre_row_fraction = float(val("max_centre_row_fraction", 0.56))
        self.approx_epsilon = float(val("approx_epsilon", 0.03))
        self.horizontal_fov_deg = float(val("camera_fov_deg", 110.0))
        self.stop_aspect = tuple(float(v) for v in val("stop_aspect", (0.70, 1.15)))
        self.stop_min_compactness = float(val("stop_min_compactness", 0.85))
        self.stop_min_vertices = int(val("stop_min_vertices", 6))
        self.stop_small_px = int(val("stop_small_px", 24))
        self.stop_red_fraction = tuple(float(v) for v in val("stop_red_fraction", (0.55, 0.88)))
        self.stop_min_letters = float(val("stop_min_letters", 0.30))
        self.yield_aspect = tuple(float(v) for v in val("yield_aspect", (0.80, 1.40)))
        self.yield_box_fill = tuple(float(v) for v in val("yield_box_fill", (0.38, 0.62)))
        self.yield_min_solidity = float(val("yield_min_solidity", 0.80))
        self.yield_red_fraction = tuple(float(v) for v in val("yield_red_fraction", (0.30, 0.78)))
        self.yield_min_white = float(val("yield_min_white", 0.30))
        self.yield_top_bottom_ratio = float(val("yield_top_bottom_ratio", 1.6))
        self.min_confidence = float(val("min_confidence", 0.0))

    def red_mask(self, image: Any) -> Tuple[Any, Any, Any]:
        """(closed red mask, raw red mask, HSV image)."""
        cv2 = _cv2()
        import numpy as np
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        raw = None
        for lo, hi in ((0, 12), (168, 179)):
            band = cv2.inRange(hsv, np.array([lo, self.min_saturation, self.min_value], np.uint8),
                               np.array([hi, 255, 255], np.uint8))
            raw = band if raw is None else cv2.bitwise_or(raw, band)
        mask = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
        k = max(1, self.close_kernel_px)
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8)), raw, hsv

    def _bearing(self, centre_x: float, width: int) -> float:
        focal = width / (2.0 * math.tan(math.radians(self.horizontal_fov_deg) / 2.0))
        return math.degrees(math.atan((centre_x - width / 2.0) / focal))

    def candidates(self, image: Any) -> List[Dict[str, Any]]:
        """Measured shape and colour features of every red contour (also used for calibration)."""
        cv2 = _cv2()
        import numpy as np
        mask, raw, hsv = self.red_mask(image)
        height, width = mask.shape
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        white = (hsv[..., 1] < 90) & (hsv[..., 2] > 100)
        out = []
        for contour in contours:
            area = float(cv2.contourArea(contour))
            if area < self.min_area_px:
                continue
            x, y, w, h = (int(v) for v in cv2.boundingRect(contour))
            margin = self.border_margin_px
            touches = x <= margin or y <= margin or x + w >= width - margin or y + h >= height - margin
            hull = cv2.convexHull(contour)
            hull_area = float(cv2.contourArea(hull))
            perimeter = float(cv2.arcLength(hull, True))
            if hull_area <= 0.0 or perimeter <= 0.0:
                continue
            approx = cv2.approxPolyDP(hull, self.approx_epsilon * perimeter, True)
            filled = np.zeros_like(mask)
            cv2.drawContours(filled, [contour], -1, 255, -1)
            inside = filled > 0
            red_fraction = float((raw[inside] > 0).mean()) if inside.any() else 0.0
            band = np.zeros_like(mask)
            cx, cy = x + w / 2.0, y + h / 2.0
            cv2.rectangle(band, (int(cx - 0.3 * w), int(cy - 0.22 * h)), (int(cx + 0.3 * w), int(cy + 0.22 * h)), 255, -1)
            band = (band > 0) & inside
            letters = float(white[band].mean()) if band.any() else 0.0
            points = approx.reshape(-1, 2)
            mean_y = points[:, 1].mean()
            top, bottom = points[points[:, 1] < mean_y], points[points[:, 1] >= mean_y]
            top_span = float(top[:, 0].max() - top[:, 0].min()) if len(top) else 0.0
            bottom_span = float(bottom[:, 0].max() - bottom[:, 0].min()) if len(bottom) else 0.0
            out.append({"bbox": (x, y, w, h), "area": area, "touches_border": touches,
                        "solidity": area / hull_area, "fill_ratio": area / float(w * h), "aspect": w / float(h),
                        "compactness": 4.0 * math.pi * hull_area / (perimeter * perimeter),
                        "vertices": int(len(approx)), "red_fraction": red_fraction, "letters": letters,
                        "top_span": top_span, "bottom_span": bottom_span,
                        "centre_row": (y + h / 2.0) / float(height), "size": max(w, h),
                        "bearing_deg": self._bearing(cx, width), "image_width": width})
        return out

    def classify(self, c: Mapping[str, Any]) -> Tuple[Optional[str], float]:
        """(class, confidence) of one candidate, or (None, 0)."""
        if c["touches_border"] or c["centre_row"] > self.max_centre_row_fraction:
            return None, 0.0
        aspect, small = c["aspect"], c["size"] < self.stop_small_px
        if (self.stop_aspect[0] <= aspect <= self.stop_aspect[1]
                and c["compactness"] >= self.stop_min_compactness
                and c["vertices"] >= (self.stop_min_vertices - 1 if small else self.stop_min_vertices)
                and self.stop_red_fraction[0] <= c["red_fraction"] <= self.stop_red_fraction[1]
                and c["letters"] >= self.stop_min_letters):
            score = (0.4 * _clip01((c["compactness"] - self.stop_min_compactness) / (0.948 - self.stop_min_compactness))
                     + 0.3 * _clip01((c["letters"] - self.stop_min_letters) / 0.2)
                     + 0.3 * _clip01(1.0 - abs(aspect - 1.0) / 0.3))
            return STOP, round(0.5 + 0.5 * score, 4)
        if (self.yield_aspect[0] <= aspect <= self.yield_aspect[1]
                and 3 <= c["vertices"] <= (5 if small else 4)
                and self.yield_box_fill[0] <= c["fill_ratio"] <= self.yield_box_fill[1]
                and c["solidity"] >= self.yield_min_solidity
                and self.yield_red_fraction[0] <= c["red_fraction"] <= self.yield_red_fraction[1]
                and c["letters"] >= self.yield_min_white
                and c["top_span"] >= self.yield_top_bottom_ratio * max(c["bottom_span"], 1.0)):
            score = (0.5 * _clip01(1.0 - abs(c["fill_ratio"] - 0.5) / 0.12)
                     + 0.5 * _clip01((c["letters"] - self.yield_min_white) / 0.3))
            return YIELD, round(0.5 + 0.5 * score, 4)
        return None, 0.0

    def detect(self, image: Any, frame: int = 0, t: float = 0.0) -> List[SignDetection]:
        out: List[SignDetection] = []
        for c in self.candidates(image):
            sign_class, confidence = self.classify(c)
            if sign_class and confidence >= self.min_confidence:
                out.append(SignDetection(int(frame), float(t), sign_class, confidence, c["bbox"], c["vertices"],
                                         c["fill_ratio"], c["red_fraction"], c["compactness"], c["letters"],
                                         c["image_width"], c["bearing_deg"]))
        return sorted(out, key=lambda d: (-d.confidence, d.bbox))


class SignTracker:
    def __init__(self, cfg: Optional[Any] = None) -> None:
        val = lambda name, default: _value(cfg, name, default)  # noqa: E731
        self.max_centre_gap_fraction = float(val("max_centre_gap_fraction", 0.08))
        self.max_time_gap_s = float(val("max_time_gap_s", 0.6))
        self.max_size_ratio = float(val("max_size_ratio", 1.8))
        self.min_detections = int(val("min_detections_per_track", 3))
        # A plate seen from further aside looks narrower: the aspect changes along the approach.
        self.max_aspect_spread = float(val("max_aspect_spread", 0.35))
        self.relevance_bearing_deg = float(val("relevance_bearing_deg", 30.0))
        self._tracks: List[SignTrack] = []; self._next_id = 0

    def update(self, detections: Sequence[SignDetection]) -> None:
        for detection in detections:
            gap_px = self.max_centre_gap_fraction * max(detection.image_width, 1)
            best, best_gap = None, gap_px
            for track in self._tracks:
                last = track.detections[-1]
                if track.sign_class != detection.sign_class or detection.t - track.t_last > self.max_time_gap_s:
                    continue
                ratio = max(detection.size, last.size) / float(max(min(detection.size, last.size), 1))
                if ratio > self.max_size_ratio:
                    continue
                cx, cy = last.centre; dx, dy = detection.centre
                gap = ((cx - dx) ** 2 + (cy - dy) ** 2) ** 0.5
                if gap < best_gap:
                    best, best_gap = track, gap
            if best is None:
                best = SignTrack("sign-{0}".format(self._next_id), detection.sign_class, [detection],
                                 self.relevance_bearing_deg)
                self._next_id += 1; self._tracks.append(best)
            else:
                best.detections.append(detection)

    def stable(self, track: SignTrack) -> bool:
        """Enough detections whose shape stays consistent (aspect spread) from frame to frame."""
        if len(track.detections) < self.min_detections:
            return False
        aspects = sorted(d.aspect for d in track.detections)
        trimmed = aspects[len(aspects) // 10: len(aspects) - len(aspects) // 10] or aspects
        return trimmed[-1] - trimmed[0] <= self.max_aspect_spread

    def tracks(self, confirmed_only: bool = True) -> List[SignTrack]:
        return sorted([t for t in self._tracks if not confirmed_only or self.stable(t)],
                      key=lambda t: (t.t_first, t.track_id))

    @property
    def n_detections(self) -> int:
        return sum(len(t.detections) for t in self._tracks)

    @property
    def rejected_short_tracks(self) -> int:
        return sum(not self.stable(t) for t in self._tracks)


def detect_signs(frames: Sequence[Tuple[float, int, Any]], cfg: Optional[Any] = None,
                 image_width: int = 0) -> Dict[str, Any]:
    """Run the detector/tracker over ``(timestamp, frame, RGB image)`` tuples."""
    detector = SignDetector(cfg); tracker = SignTracker(cfg)
    all_detections: List[SignDetection] = []; width = int(image_width)
    for timestamp, frame, image in frames:
        if width == 0 and image is not None:
            width = int(image.shape[1])
        detections = detector.detect(image, frame=int(frame), t=float(timestamp))
        all_detections.extend(detections); tracker.update(detections)
    confirmed = tracker.tracks(True)
    provisional = tracker.tracks(False)
    method = ("colour-and-shape detection in HSV (octagon / inverted triangle with white letters or interior), "
              "border-truncated shapes rejected, then association across frames with a shape-stability "
              "check. Deterministic, no training data, no learned weights, no privileged sign labels")
    return {"method": method, "image_width": width, "n_frames": len(frames),
            "n_detections": len(all_detections), "n_tracks": len(confirmed),
            "min_detections_per_track": tracker.min_detections,
            "tracks": [track.as_dict(width) for track in confirmed],
            "rejected_short_tracks": [{"class": track.sign_class,
                "n_detections": len(track.detections), "t_first": round(track.t_first, 4)}
                for track in provisional if track not in confirmed]}
