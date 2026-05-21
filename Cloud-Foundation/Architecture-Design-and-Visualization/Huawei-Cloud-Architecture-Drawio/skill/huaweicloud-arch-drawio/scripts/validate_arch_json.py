"""
Validate the intermediate Huawei Cloud architecture JSON before rendering.

This catches solution-design problems that are hard to see from draw.io XML alone:
- Huawei Cloud service nodes must resolve to bundled official icon keys.
- Self-built / third-party nodes must be explicitly marked and labelled.
- Edges must reference known nodes.
- Complex diagrams should keep nodes inside explicit containers.

Usage:
  python validate_arch_json.py arch.json
  python validate_arch_json.py arch.json --strict
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
ASSETS_DIR = SKILL_ROOT / "assets"
sys.path.insert(0, str(SCRIPT_DIR))

from render_drawio import SERVICE_ALIASES  # noqa: E402


GENERIC_SERVICE_KEYS = {
    "APIG",
    "CBR",
    "CCE",
    "CES",
    "CFW",
    "CDN",
    "DCS",
    "DC",
    "DNS",
    "DRS",
    "ECS",
    "ELB",
    "GA",
    "IAM",
    "LTS",
    "OBS",
    "RDS",
    "REDIS",
    "SMN",
    "WAF",
}

CUSTOM_MARKERS = ("自建", "第三方", "self-built", "self built", "third-party", "third party", "custom")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - command-line guard
        raise SystemExit(f"[ERROR] Cannot read JSON: {path}: {exc}") from exc


def load_icons() -> dict[str, str]:
    path = ASSETS_DIR / "icons-color.json"
    if not path.is_file():
        raise SystemExit(f"[ERROR] Icon registry missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_service(service: str) -> str:
    key = (service or "").strip().upper()
    return SERVICE_ALIASES.get(key, key)


def is_custom_node(node: dict) -> bool:
    node_type = str(node.get("type", "")).strip().lower()
    return bool(node.get("custom") or node_type in {"custom", "third_party", "third-party", "self_built", "self-built"})


def validate_arch(data: dict, strict: bool = False) -> tuple[list[str], list[str]]:
    icons = load_icons()
    groups = {str(g.get("id")) for g in data.get("groups", []) if g.get("id")}
    nodes = data.get("nodes", [])
    node_ids: set[str] = set()
    errors: list[str] = []
    warnings: list[str] = []

    for idx, node in enumerate(nodes, start=1):
        node_id = str(node.get("id", "")).strip()
        service = str(node.get("service", "")).strip()
        label = str(node.get("label", "")).strip()
        label_lc = label.lower()

        if not node_id:
            errors.append(f"nodes[{idx}] is missing id")
            continue
        if node_id in node_ids:
            errors.append(f"duplicate node id: {node_id}")
        node_ids.add(node_id)

        if not service:
            errors.append(f"node {node_id} is missing service")
            continue

        if is_custom_node(node):
            if not any(marker in label_lc or marker in label for marker in CUSTOM_MARKERS):
                warnings.append(
                    f"custom node {node_id} should label itself as self-built/third-party, for example '{label} 自建服务'"
                )
            continue

        canonical = canonical_service(service)
        if canonical not in icons:
            errors.append(f"node {node_id} uses unknown Huawei Cloud service/icon key: {service} -> {canonical}")

        group_id = node.get("group")
        if groups and not group_id:
            warnings.append(f"node {node_id} has no group; complex diagrams should place every service in a boundary")
        elif group_id and str(group_id) not in groups:
            errors.append(f"node {node_id} references missing group: {group_id}")

        generic_labels = {service.upper(), canonical, canonical.replace("_", " ")}
        if canonical in GENERIC_SERVICE_KEYS or service.upper() in GENERIC_SERVICE_KEYS:
            if not label or label.upper() in generic_labels:
                warnings.append(f"node {node_id} label is generic; add business purpose or role")

    for idx, edge in enumerate(data.get("edges", []), start=1):
        src = str(edge.get("from", "")).strip()
        dst = str(edge.get("to", "")).strip()
        if src not in node_ids:
            errors.append(f"edges[{idx}] references missing source node: {src}")
        if dst not in node_ids:
            errors.append(f"edges[{idx}] references missing target node: {dst}")
        if src == dst and src:
            warnings.append(f"edges[{idx}] is self-referential: {src}")

    if strict:
        errors.extend(f"strict: {item}" for item in warnings)
        warnings = []

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Architecture JSON file")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    data = load_json(args.input)
    errors, warnings = validate_arch(data, strict=args.strict)
    for item in warnings:
        print(f"[WARN] {item}")
    for item in errors:
        print(f"[ERROR] {item}")
    if errors:
        print(f"Architecture JSON validation failed: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"Architecture JSON validation passed: {len(data.get('nodes', []))} node(s), {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
