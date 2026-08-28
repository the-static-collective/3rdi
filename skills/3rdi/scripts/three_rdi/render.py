"""Receipt-only deterministic SVG/HTML rendering for GlyphTrace formations."""

from __future__ import annotations

from html import escape
from typing import Any

from .model import FieldError


RECEIPT_SCHEMA = "3rdi.glyph-formation-receipt/v0"
WIDTH = 640.0
HEIGHT = 480.0
MARGIN = 60.0


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FieldError(f"{path} must be an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise FieldError(f"{path} must be a non-empty string")
    return value


def _fmt(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text if text else "0"


def _project_landmarks(landmarks: dict[str, Any]) -> dict[str, tuple[float, float]]:
    if not landmarks:
        raise FieldError("formation receipt render_model.landmarks must not be empty")
    coordinates: dict[str, tuple[float, float]] = {}
    for name, raw in landmarks.items():
        if (
            not isinstance(name, str)
            or not name
            or not isinstance(raw, list)
            or len(raw) != 2
            or any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in raw)
        ):
            raise FieldError("formation receipt contains invalid landmark geometry")
        coordinates[name] = (float(raw[0]), float(raw[1]))

    xs = [point[0] for point in coordinates.values()]
    ys = [point[1] for point in coordinates.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1.0)
    span_y = max(max_y - min_y, 1.0)
    scale = min((WIDTH - 2 * MARGIN) / span_x, (HEIGHT - 2 * MARGIN) / span_y)
    drawn_width = (max_x - min_x) * scale
    drawn_height = (max_y - min_y) * scale
    left = (WIDTH - drawn_width) / 2.0
    top = (HEIGHT - drawn_height) / 2.0

    return {
        name: (
            left + (x - min_x) * scale,
            top + (max_y - y) * scale,
        )
        for name, (x, y) in coordinates.items()
    }


def _readout(title: str, rows: list[tuple[str, Any]]) -> str:
    items = "".join(
        f"<li><strong>{escape(str(key))}:</strong> {escape(str(value))}</li>"
        for key, value in rows
    )
    return f"<section><h2>{escape(title)}</h2><ul>{items}</ul></section>"


def render_glyph_trace(raw_receipt: Any) -> str:
    """Render one GlyphTrace formation receipt as deterministic standalone HTML."""

    receipt = _mapping(raw_receipt, "formation receipt")
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise FieldError("formation receipt schema is required for GlyphTrace rendering")

    carrier = _mapping(receipt.get("carrier"), "formation receipt.carrier")
    formation = _mapping(receipt.get("formation"), "formation receipt.formation")
    metrics = _mapping(receipt.get("metrics"), "formation receipt.metrics")
    gates = _mapping(receipt.get("gates"), "formation receipt.gates")
    tool_results = _mapping(
        receipt.get("tool_results"), "formation receipt.tool_results"
    )
    render_model = _mapping(
        receipt.get("render_model"), "formation receipt.render_model"
    )
    non_authority = _string(
        receipt.get("non_authority"), "formation receipt.non_authority"
    )

    carrier_id = _string(carrier.get("id"), "formation receipt.carrier.id")
    formation_id = _string(
        formation.get("id"), "formation receipt.formation.id"
    )
    landmarks_raw = _mapping(
        render_model.get("landmarks"), "formation receipt.render_model.landmarks"
    )
    points = _project_landmarks(landmarks_raw)

    carrier_lines: list[str] = []
    segments = render_model.get("carrier_segments")
    if not isinstance(segments, list):
        raise FieldError("formation receipt.render_model.carrier_segments must be an array")
    for segment in segments:
        if not isinstance(segment, list) or len(segment) != 2:
            raise FieldError("formation receipt contains invalid carrier segment")
        left, right = segment
        if left not in points or right not in points:
            raise FieldError("formation receipt carrier segment references unknown landmark")
        x1, y1 = points[left]
        x2, y2 = points[right]
        carrier_lines.append(
            "<line class=\"carrier\" "
            f"x1=\"{_fmt(x1)}\" y1=\"{_fmt(y1)}\" "
            f"x2=\"{_fmt(x2)}\" y2=\"{_fmt(y2)}\" />"
        )

    trace_paths: list[str] = []
    stroke_rows: list[tuple[str, Any]] = []
    strokes = render_model.get("strokes")
    if not isinstance(strokes, list):
        raise FieldError("formation receipt.render_model.strokes must be an array")
    traversal_ordinal = 0
    for stroke in strokes:
        stroke_map = _mapping(stroke, "formation receipt.render_model.strokes[]")
        stroke_index = stroke_map.get("stroke_index")
        operation_id = _string(
            stroke_map.get("operation_id"),
            "formation receipt.render_model.strokes[].operation_id",
        )
        traversals = stroke_map.get("traversals")
        if not isinstance(stroke_index, int) or isinstance(stroke_index, bool):
            raise FieldError("formation receipt stroke_index must be an integer")
        if not isinstance(traversals, list):
            raise FieldError("formation receipt stroke traversals must be an array")
        stroke_rows.append((f"stroke {stroke_index + 1}", operation_id))
        for traversal in traversals:
            segment = _mapping(traversal, "formation receipt traversal")
            left = _string(segment.get("from"), "formation receipt traversal.from")
            right = _string(segment.get("to"), "formation receipt traversal.to")
            if left not in points or right not in points:
                raise FieldError("formation receipt traversal references unknown landmark")
            x1, y1 = points[left]
            x2, y2 = points[right]
            delay = traversal_ordinal * 0.55
            trace_paths.append(
                "<path class=\"trace\" "
                f"data-stroke-index=\"{stroke_index}\" "
                f"data-operation-id=\"{escape(operation_id, quote=True)}\" "
                f"d=\"M {_fmt(x1)} {_fmt(y1)} L {_fmt(x2)} {_fmt(y2)}\" "
                f"style=\"animation-delay:{_fmt(delay)}s\" />"
            )
            traversal_ordinal += 1

    metrics_rows = [(key, metrics[key]) for key in sorted(metrics)]
    gate_rows = [(key, gates[key]) for key in sorted(gates)]
    tool_rows = [(key, tool_results[key]) for key in sorted(tool_results)]

    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        f"<title>GlyphTrace — {escape(formation_id)}</title>\n"
        "<style>"
        "body{font-family:system-ui,sans-serif;max-width:980px;margin:0 auto;padding:24px;line-height:1.45}"
        "svg{width:100%;height:auto;border:1px solid currentColor}"
        ".carrier{stroke:currentColor;stroke-width:5;opacity:.18}"
        ".trace{fill:none;stroke:currentColor;stroke-width:7;stroke-linecap:round;"
        "stroke-dasharray:1000;stroke-dashoffset:1000;animation:draw .5s linear forwards}"
        "@keyframes draw{to{stroke-dashoffset:0}}"
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}"
        ".notice{border-left:4px solid currentColor;padding-left:12px}"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        "<main>\n"
        "<h1>GlyphTrace formation witness</h1>\n"
        f"<p><strong>Carrier:</strong> {escape(carrier_id)}<br>"
        f"<strong>Formation:</strong> {escape(formation_id)}</p>\n"
        f"<svg viewBox=\"0 0 {int(WIDTH)} {int(HEIGHT)}\" role=\"img\" "
        f"aria-label=\"Formation replay for {escape(formation_id, quote=True)}\">\n"
        + "\n".join(carrier_lines)
        + "\n"
        + "\n".join(trace_paths)
        + "\n</svg>\n"
        "<div class=\"grid\">\n"
        + _readout("Stroke order", stroke_rows)
        + _readout("Metrics", metrics_rows)
        + _readout("Gates", gate_rows)
        + _readout("Tool results", tool_rows)
        + "</div>\n"
        f"<p class=\"notice\">{escape(non_authority)}</p>\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
    )
