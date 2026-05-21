"""
Export a resource inventory from Huawei Cloud architecture JSON.

The inventory helps keep the draw.io architecture diagram aligned with the
solution/resource list required during architecture review.

Usage:
  python export_resource_inventory.py arch.json --output arch.resources.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_ROOT / "assets"
sys.path.insert(0, str(SCRIPT_DIR))

from render_drawio import SERVICE_ALIASES  # noqa: E402


def canonical_service(service: str) -> str:
    key = (service or "").strip().upper()
    return SERVICE_ALIASES.get(key, key)


def is_custom_node(node: dict) -> bool:
    node_type = str(node.get("type", "")).strip().lower()
    return bool(node.get("custom") or node_type in {"custom", "third_party", "third-party", "self_built", "self-built"})


def load_meta() -> dict:
    path = ASSETS_DIR / "official-product-icons-meta.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_rows(data: dict) -> list[dict[str, str]]:
    meta = load_meta()
    group_labels = {g.get("id"): g.get("label", g.get("id", "")) for g in data.get("groups", [])}
    rows: list[dict[str, str]] = []
    for node in data.get("nodes", []):
        custom = is_custom_node(node)
        service = str(node.get("service", "")).strip()
        key = "CUSTOM" if custom else canonical_service(service)
        info = meta.get(key, {})
        group_id = node.get("group", "")
        rows.append(
            {
                "node_id": str(node.get("id", "")),
                "resource_key": key,
                "resource_title": "Self-built / third-party" if custom else str(info.get("title", key)),
                "label_or_business_role": str(node.get("label", "")),
                "group_id": str(group_id),
                "group_label": str(group_labels.get(group_id, "")),
                "quantity": "1",
                "source": "custom" if custom else "official-huaweicloud-icon",
            }
        )
    return rows


def write_csv(rows: list[dict[str, str]], output: Path) -> None:
    fieldnames = [
        "node_id",
        "resource_key",
        "resource_title",
        "label_or_business_role",
        "group_id",
        "group_label",
        "quantity",
        "source",
    ]
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]], output: Path) -> None:
    counts = Counter(row["resource_key"] for row in rows)
    lines = ["# Huawei Cloud Resource Inventory", "", "## Aggregated Counts", ""]
    lines.extend(f"- `{key}`: {count}" for key, count in sorted(counts.items()))
    lines.extend(["", "## Detail", "", "| node_id | resource_key | label_or_business_role | group_label |", "| --- | --- | --- | --- |"])
    for row in rows:
        lines.append(
            f"| {row['node_id']} | {row['resource_key']} | {row['label_or_business_role']} | {row['group_label']} |"
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Architecture JSON file")
    parser.add_argument("--output", type=Path, required=True, help="Output .csv or .md")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    rows = build_rows(data)
    if args.output.suffix.lower() in {".md", ".markdown"}:
        write_markdown(rows, args.output)
    else:
        write_csv(rows, args.output)
    counts = Counter(row["resource_key"] for row in rows)
    print(f"Exported {len(rows)} resource row(s), {len(counts)} resource type(s): {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
