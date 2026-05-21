"""
Render a Huawei Cloud architecture description (JSON) to a .drawio file.

Input JSON schema:
{
  "title": "...",                       # optional, sets diagram name
  "style": "color",                    # optional; official product icons are color only
  "groups": [
    { "id": "vpc1", "type": "VPC", "label": "vpc-prod" },
    { "id": "az1",  "type": "AZ",  "label": "AZ1", "parent": "vpc1" }
  ],
  "nodes": [
    { "id": "elb1", "service": "ELB", "label": "ELB",
      "group": "vpc1", "tier": 1 }
  ],
  "edges": [
    { "from": "elb1", "to": "ecs1", "label": "" }
  ]
}

Layout: tier-based grid. Nodes with the same `tier` are placed in the same row.
Groups auto-size to fit their member nodes, with padding.
Nested groups are supported via `parent`.

Usage:
  python render_drawio.py --input arch.json --output arch.drawio
  cat arch.json | python render_drawio.py > arch.drawio
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"

NODE_W = 72
NODE_H = 90
ICON_H = 72          # square icon image area inside the node (label sits below)
H_GAP = 100          # horizontal gap between nodes in same tier
V_GAP = 140          # vertical gap between tiers
GROUP_PAD_X = 30     # horizontal padding inside group around child bbox
GROUP_PAD_TOP = 40   # top padding (extra for group label)
GROUP_PAD_BOTTOM = 20
CANVAS_PAD = 40      # outer canvas padding
LAYER_CONTAINERS = "layer_containers"
LAYER_SERVICES = "layer_services"
LAYER_CONNECTORS = "layer_connectors"

GROUP_STYLES: dict[str, str] = {
    "VPC": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=none;"
        "strokeColor=#f85835;absoluteArcSize=1;arcSize=20;fontColor=#f85835;"
        "verticalAlign=top;align=left;spacingLeft=10;fontFamily=Arial;spacingTop=4;fontSize=12;"
    ),
    "REGION": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=none;"
        "strokeColor=#3771c8;dashed=1;absoluteArcSize=1;arcSize=20;fontColor=#3771c8;"
        "verticalAlign=top;align=left;spacingLeft=10;fontFamily=Arial;spacingTop=4;fontSize=12;"
    ),
    "AZ": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=none;"
        "strokeColor=#3298ff;dashed=1;absoluteArcSize=1;arcSize=20;fontColor=#3298ff;"
        "verticalAlign=top;align=left;spacingLeft=10;fontFamily=Arial;spacingTop=4;fontSize=12;"
    ),
    "SUBNET": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;"
        "strokeColor=#999999;dashed=1;absoluteArcSize=1;arcSize=20;fontColor=#666666;"
        "verticalAlign=top;align=left;spacingLeft=10;fontFamily=Arial;spacingTop=4;fontSize=11;"
    ),
    "CLOUD": (
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff7ea;"
        "strokeColor=#c7000b;absoluteArcSize=1;arcSize=20;fontColor=#c7000b;"
        "verticalAlign=top;align=left;spacingLeft=10;fontFamily=Arial;spacingTop=4;fontSize=12;"
    ),
}
DEFAULT_GROUP_STYLE = GROUP_STYLES["SUBNET"]


def node_style(data_uri: str) -> str:
    data_uri = data_uri.replace(";", "%3B")
    # Put `image=` LAST so the data URI consumes the rest of the style string.
    return (
        "shape=image;verticalLabelPosition=bottom;labelBackgroundColor=none;"
        "verticalAlign=top;aspect=fixed;imageAspect=1;fontSize=11;fontFamily=Arial;"
        "whiteSpace=wrap;html=1;"
        f"image={data_uri}"
    )


EDGE_STYLE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
    "exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
    "endArrow=classic;endFill=1;strokeColor=#666666;"
)

# Short aliases to canonical official product icon keys.
SERVICE_ALIASES: dict[str, str] = {
    "DCS": "REDIS",
    "DCS_REDIS": "REDIS",
    "RDS": "RDSFORMYSQL",
    "RDS_MYSQL": "RDSFORMYSQL",
    "RDS_POSTGRESQL": "RDSFORPOSTGRESQL",
    "RDS_PG": "RDSFORPOSTGRESQL",
    "RDS_SQLSERVER": "RDSFORSQLSERVER",
    "RDS_SQL_SERVER": "RDSFORSQLSERVER",
    "RDS_MARIADB": "RDSFORMARIADB",
    "NATGW": "NAT",
    "ROCKETMQ": "DMS",
    "DMS_ROCKETMQ": "DMS",
}


@dataclass
class Node:
    id: str
    service: str
    label: str = ""
    group: str | None = None
    tier: int = 0
    x: float = 0
    y: float = 0
    manual: bool = False
    custom: bool = False


@dataclass
class Group:
    id: str
    type: str
    label: str = ""
    parent: str | None = None
    children: list[str] = field(default_factory=list)   # node ids
    child_groups: list[str] = field(default_factory=list)
    x: float = 0
    y: float = 0
    w: float = 0
    h: float = 0
    manual: bool = False


def load_icons(style: str) -> dict[str, str]:
    path = ASSETS_DIR / "icons-color.json"
    if not path.is_file():
        raise SystemExit(f"Icon registry missing: {path}. Run merge_official_product_icons.py first.")
    return json.loads(path.read_text(encoding="utf-8"))


def attr(name: str, value: str | float) -> str:
    return f'{name}="{escape(str(value), {chr(34): "&quot;"})}"'


def compute_layout(nodes: list[Node], groups: dict[str, Group]) -> tuple[float, float]:
    """Place every node, size every group. Returns total canvas (w, h)."""
    # Group nodes by tier
    tiers: dict[int, list[Node]] = {}
    for n in nodes:
        if n.manual:
            continue
        tiers.setdefault(n.tier, []).append(n)
    sorted_tiers = sorted(tiers.keys())

    # Step 1: tentative x by global tier-row ordering
    y_cursor = CANVAS_PAD + (GROUP_PAD_TOP if groups else 0)
    max_x = CANVAS_PAD
    for t in sorted_tiers:
        row = tiers[t]
        # Group nodes in row by their `group` so members of the same group sit together.
        row.sort(key=lambda n: (n.group or "", n.id))
        x_cursor = CANVAS_PAD + (GROUP_PAD_X if groups else 0)
        for n in row:
            n.x = x_cursor
            n.y = y_cursor
            x_cursor += NODE_W + H_GAP
        max_x = max(max_x, x_cursor - H_GAP + GROUP_PAD_X)
        y_cursor += NODE_H + V_GAP

    canvas_w = max(max_x + CANVAS_PAD, 400)
    canvas_h = y_cursor - V_GAP + GROUP_PAD_BOTTOM + CANVAS_PAD

    # Step 2: size groups from member bboxes (post-order traversal)
    def group_bbox(g: Group) -> tuple[float, float, float, float]:
        xs: list[float] = []
        ys: list[float] = []
        for nid in g.children:
            n = next((x for x in nodes if x.id == nid), None)
            if n:
                xs.extend([n.x, n.x + NODE_W])
                ys.extend([n.y, n.y + NODE_H])
        for cgid in g.child_groups:
            cg = groups[cgid]
            size_group(cg)
            xs.extend([cg.x, cg.x + cg.w])
            ys.extend([cg.y, cg.y + cg.h])
        if not xs:
            return (CANVAS_PAD, CANVAS_PAD, 200, 100)
        return (min(xs), min(ys), max(xs), max(ys))

    def size_group(g: Group) -> None:
        if g.manual and g.w > 0 and g.h > 0:
            return
        x0, y0, x1, y1 = group_bbox(g)
        g.x = x0 - GROUP_PAD_X
        g.y = y0 - GROUP_PAD_TOP
        g.w = (x1 - x0) + 2 * GROUP_PAD_X
        g.h = (y1 - y0) + GROUP_PAD_TOP + GROUP_PAD_BOTTOM

    # only size top-level groups; nested groups sized recursively from inside
    for g in groups.values():
        if g.parent is None:
            size_group(g)

    # Step 3: extend canvas if groups overflow
    for n in nodes:
        canvas_w = max(canvas_w, n.x + NODE_W + CANVAS_PAD)
        canvas_h = max(canvas_h, n.y + NODE_H + CANVAS_PAD)
    for g in groups.values():
        canvas_w = max(canvas_w, g.x + g.w + CANVAS_PAD)
        canvas_h = max(canvas_h, g.y + g.h + CANVAS_PAD)

    return canvas_w, canvas_h


def build_xml(
    title: str,
    nodes: list[Node],
    groups: dict[str, Group],
    edges: list[dict],
    icons: dict[str, str],
    canvas_w: float,
    canvas_h: float,
) -> str:
    cells: list[str] = []
    cells.append('<mxCell id="0"/>')
    cells.append('<mxCell id="1" parent="0"/>')
    cells.append(f'<mxCell id="{LAYER_CONTAINERS}" value="Containers" parent="0"/>')
    cells.append(f'<mxCell id="{LAYER_SERVICES}" value="Services" parent="0"/>')
    cells.append(f'<mxCell id="{LAYER_CONNECTORS}" value="Connectors" parent="0"/>')

    # Emit groups (parents first so children can reference them)
    emitted: set[str] = set()

    def emit_group(g: Group) -> None:
        if g.id in emitted:
            return
        parent_id = LAYER_CONTAINERS
        if g.parent and g.parent in groups:
            emit_group(groups[g.parent])
            parent_id = f"g_{g.parent}"
        style = GROUP_STYLES.get(g.type.upper(), DEFAULT_GROUP_STYLE)
        label = g.label or g.type
        gx, gy = g.x, g.y
        if parent_id != "1" and g.parent in groups:
            parent_group = groups[g.parent]
            gx, gy = g.x - parent_group.x, g.y - parent_group.y
        cells.append(
            f'<mxCell id="g_{escape(g.id)}" value="{escape(label)}" '
            f'style="{escape(style, {chr(34): "&quot;"})}" vertex="1" parent="{parent_id}">'
            f'<mxGeometry x="{gx}" y="{gy}" width="{g.w}" height="{g.h}" as="geometry"/>'
            f'</mxCell>'
        )
        emitted.add(g.id)

    for g in groups.values():
        emit_group(g)

    # Emit nodes
    for n in nodes:
        svc_key = n.service.upper()
        svc_key = SERVICE_ALIASES.get(svc_key, svc_key)
        data_uri = icons.get(svc_key)
        if n.custom:
            style_str = (
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;"
                "strokeColor=#666666;fontColor=#333333;fontSize=11;fontFamily=Arial;"
            )
            value = n.label or n.service
        elif data_uri is None:
            fallback_style = (
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe0e0;"
                "strokeColor=#c7000b;fontColor=#c7000b;fontSize=11;fontFamily=Arial;"
            )
            style_str = fallback_style
            value = n.label or f"{n.service} (missing icon)"
        else:
            style_str = node_style(data_uri)
            value = n.label or n.service

        parent_id = f"g_{n.group}" if (n.group and n.group in groups) else LAYER_SERVICES
        # Convert absolute coords to relative if parented to group
        if parent_id != LAYER_SERVICES:
            pg = groups[n.group]
            nx, ny = n.x - pg.x, n.y - pg.y
        else:
            nx, ny = n.x, n.y

        cells.append(
            f'<mxCell id="n_{escape(n.id)}" value="{escape(value)}" '
            f'style="{escape(style_str, {chr(34): "&quot;"})}" vertex="1" parent="{parent_id}">'
            f'<mxGeometry x="{nx}" y="{ny}" width="{NODE_W}" height="{ICON_H}" as="geometry"/>'
            f'</mxCell>'
        )

    # Emit edges
    for i, e in enumerate(edges):
        src = f'n_{e["from"]}'
        tgt = f'n_{e["to"]}'
        label = e.get("label", "")
        cells.append(
            f'<mxCell id="e_{i}" value="{escape(label)}" '
            f'style="{escape(EDGE_STYLE, {chr(34): "&quot;"})}" edge="1" parent="{LAYER_CONNECTORS}" '
            f'source="{src}" target="{tgt}">'
            f'<mxGeometry relative="1" as="geometry"/>'
            f'</mxCell>'
        )

    diagram_name = title or "Architecture"
    body = "\n        ".join(cells)
    return (
        f'<mxfile host="app.diagrams.net" modified="" agent="huaweicloud-arch-drawio" version="22.0.0">\n'
        f'  <diagram id="d1" name="{escape(diagram_name)}">\n'
        f'    <mxGraphModel dx="{int(canvas_w)}" dy="{int(canvas_h)}" grid="1" gridSize="10" '
        f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        f'pageWidth="{int(canvas_w)}" pageHeight="{int(canvas_h)}" math="0" shadow="0">\n'
        f'      <root>\n'
        f'        {body}\n'
        f'      </root>\n'
        f'    </mxGraphModel>\n'
        f'  </diagram>\n'
        f'</mxfile>\n'
    )


def parse_input(spec: dict) -> tuple[str, list[Node], dict[str, Group], list[dict], str]:
    title = spec.get("title", "")
    style = spec.get("style", "color")
    if style != "color":
        style = "color"

    groups: dict[str, Group] = {}
    for g in spec.get("groups", []) or []:
        gid = g["id"]
        groups[gid] = Group(
            id=gid,
            type=g.get("type", "SUBNET"),
            label=g.get("label", ""),
            parent=g.get("parent"),
            x=float(g.get("x", 0)),
            y=float(g.get("y", 0)),
            w=float(g.get("w", 0)),
            h=float(g.get("h", 0)),
            manual=("x" in g and "y" in g and "w" in g and "h" in g),
        )
    # Build child_groups links
    for g in groups.values():
        if g.parent and g.parent in groups:
            groups[g.parent].child_groups.append(g.id)

    nodes: list[Node] = []
    for n in spec.get("nodes", []) or []:
        node = Node(
            id=n["id"],
            service=n["service"],
            label=n.get("label", ""),
            group=n.get("group"),
            tier=int(n.get("tier", 0)),
            x=float(n.get("x", 0)),
            y=float(n.get("y", 0)),
            manual=("x" in n and "y" in n),
            custom=bool(n.get("custom", False) or n.get("type", "").lower() in {"custom", "third_party", "self_built"}),
        )
        nodes.append(node)
        if node.group and node.group in groups:
            groups[node.group].children.append(node.id)

    edges = spec.get("edges", []) or []
    return title, nodes, groups, edges, style


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="Input JSON file. Defaults to stdin.")
    ap.add_argument("--output", help="Output .drawio file. Defaults to stdout.")
    ap.add_argument("--style", choices=["color"], help="Override JSON style field.")
    args = ap.parse_args()

    if args.input:
        spec = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        spec = json.loads(sys.stdin.read())

    title, nodes, groups, edges, style = parse_input(spec)
    if args.style:
        style = args.style

    icons = load_icons(style)
    canvas_w, canvas_h = compute_layout(nodes, groups)
    xml_out = build_xml(title, nodes, groups, edges, icons, canvas_w, canvas_h)

    if args.output:
        Path(args.output).write_text(xml_out, encoding="utf-8")
        print(f"wrote: {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(xml_out)


if __name__ == "__main__":
    main()
