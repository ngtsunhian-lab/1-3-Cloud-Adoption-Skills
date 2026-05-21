"""
Validate generated Huawei Cloud draw.io files.

Checks:
  - XML parses
  - all service nodes use embedded image data unless explicitly allowed fallback
  - icon geometries are square
  - no duplicate node positions in the same parent
  - no obvious node overlap in absolute coordinates
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def fnum(value: str | None, default: float = 0) -> float:
    try:
        return float(value) if value is not None else default
    except ValueError:
        return default


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("drawio", help="Path to .drawio file")
    parser.add_argument("--allow-fallback", action="store_true", help="Allow plain red fallback service nodes")
    args = parser.parse_args()

    path = Path(args.drawio)
    text = path.read_text(encoding="utf-8")
    root = ET.fromstring(text)
    cells = {cell.get("id"): cell for cell in root.findall(".//mxCell") if cell.get("id")}
    problems: list[str] = []

    abs_cache: dict[str, tuple[float, float, float, float]] = {}

    def absolute_bbox(cell_id: str) -> tuple[float, float, float, float]:
        if cell_id in abs_cache:
            return abs_cache[cell_id]
        cell = cells[cell_id]
        geo = cell.find("mxGeometry")
        x = fnum(geo.get("x") if geo is not None else None)
        y = fnum(geo.get("y") if geo is not None else None)
        w = fnum(geo.get("width") if geo is not None else None)
        h = fnum(geo.get("height") if geo is not None else None)
        parent_id = cell.get("parent")
        if parent_id and parent_id in cells and parent_id not in {"0", "1", "layer_services", "layer_containers", "layer_connectors"}:
            px, py, _, _ = absolute_bbox(parent_id)
            x += px
            y += py
        abs_cache[cell_id] = (x, y, w, h)
        return abs_cache[cell_id]

    node_cells = [
        cell
        for cell in cells.values()
        if cell.get("vertex") == "1" and (cell.get("id") or "").startswith("n_")
    ]
    image_nodes = 0
    position_keys: dict[tuple[str | None, str | None, str | None], str] = {}
    for cell in node_cells:
        cell_id = cell.get("id", "")
        style = cell.get("style", "")
        geo = cell.find("mxGeometry")
        width = geo.get("width") if geo is not None else None
        height = geo.get("height") if geo is not None else None
        if "shape=image" in style:
            image_nodes += 1
            if width != height:
                problems.append(f"{cell_id}: icon geometry is not square ({width}x{height})")
            if "data:image/" not in style:
                problems.append(f"{cell_id}: image node has no embedded data URI")
        elif "fillColor=#ffe0e0" in style and not args.allow_fallback:
            problems.append(f"{cell_id}: fallback red node detected")

        key = (cell.get("parent"), geo.get("x") if geo is not None else None, geo.get("y") if geo is not None else None)
        if key in position_keys:
            problems.append(f"{cell_id}: duplicate node position with {position_keys[key]}")
        position_keys[key] = cell_id

    for i, left in enumerate(node_cells):
        lx, ly, lw, lh = absolute_bbox(left.get("id", ""))
        for right in node_cells[i + 1 :]:
            rx, ry, rw, rh = absolute_bbox(right.get("id", ""))
            if lx < rx + rw and lx + lw > rx and ly < ry + rh and ly + lh > ry:
                problems.append(f"{left.get('id')}: overlaps {right.get('id')}")

    if image_nodes == 0:
        problems.append("no image service nodes found")

    if problems:
        print(f"FAILED: {path}")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)

    print(f"OK: {path}")
    print(f"service_nodes={len(node_cells)} image_nodes={image_nodes}")


if __name__ == "__main__":
    main()
