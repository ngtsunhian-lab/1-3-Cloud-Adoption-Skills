---
name: huaweicloud-arch-drawio
description: Generate Huawei Cloud architecture diagrams in draw.io / diagrams.net format from natural language or JSON, using the locally bundled 201 official Huawei Cloud product icons collected from Huawei Cloud public product pages. Supports Region/VPC/AZ/Subnet containers, explicit geometry, draw.io layers, validation, automatic tier layout, and common Huawei Cloud service aliases.
metadata:
  version: 0.4.0
  icon_source: Huawei Cloud public product pages
  icon_count: 201
---

# Huawei Cloud Architecture Draw.io

Use this skill when the user wants a Huawei Cloud architecture diagram, topology diagram, network diagram, DR diagram, or `.drawio` / diagrams.net file.

This skill follows draw.io-compatible generation practices:

- valid `mxfile` / `mxGraphModel` XML
- separate layers for containers, services, and connectors
- nested containers with correct parent-relative geometry
- square service icon geometry to preserve product icon proportions
- embedded image data URI icons
- pre-render architecture validation inspired by Huawei Cloud HaydnCSF / solution-design review expectations
- resource inventory export for keeping the diagram and configuration/resource list aligned
- post-generation validation

User-specific rule: only use the 201 newly collected official Huawei Cloud product-page icons. Do not restore or depend on the old third-party 254 color / 382 mono registries.

## Bundled Assets

- `assets/icons-color.json`: 201 official product icons.
- `assets/official-product-icons-meta.json`: metadata for those icons.
- `references/service-catalog.md`: full icon key catalog.
- `scripts/render_drawio.py`: JSON to `.drawio` renderer.
- `scripts/validate_arch_json.py`: pre-render architecture JSON validator.
- `scripts/validate_drawio.py`: generated `.drawio` validator.
- `scripts/export_resource_inventory.py`: resource inventory exporter from architecture JSON.
- `scripts/merge_official_product_icons.py`: refresh tool for newly crawled official icons.

## Workflow

1. Parse the user's request into the JSON schema in `references/json-schema.md`.
2. Use `references/service-catalog.md` for icon keys.
3. For small diagrams, tier auto-layout is acceptable.
4. For multi-region, DR, or production diagrams, provide explicit `x/y/w/h` for groups and `x/y` for nodes.
5. Mark non-Huawei or self-built systems as `custom: true` or `type: self_built`; their labels must say self-built/third-party explicitly.
6. Validate, render, validate the draw.io, then export the resource inventory:

```bash
python <skill-dir>/scripts/validate_arch_json.py arch.json
python <skill-dir>/scripts/render_drawio.py --input arch.json --output arch.drawio
python <skill-dir>/scripts/validate_drawio.py arch.drawio
python <skill-dir>/scripts/export_resource_inventory.py arch.json --output arch.resources.csv
```

7. If validation fails, fix the JSON or renderer and regenerate. Do not deliver a diagram with missing icons, red fallback nodes, distorted icons, obvious overlap, broken edge references, or unlabelled self-built/third-party systems.

## HaydnCSF / Solution Review Checklist

When the diagram is intended for Huawei Cloud solution review or HaydnCSF-style delivery, make sure it shows:

- logical network topology and business flow
- Huawei Cloud resource types and approximate quantities
- business/application roles deployed on the resources, not only generic service acronyms
- official Huawei Cloud icons for Huawei Cloud services
- explicit self-built or third-party labels for non-Huawei systems
- resource inventory/configuration list that matches the diagram nodes

## Common Aliases

The renderer maps common abbreviations to the official product-page icon keys:

- `RDS` -> `RDSFORMYSQL`
- `DCS` / `DCS_REDIS` -> `REDIS`
- `NATGW` -> `NAT`
- `ROCKETMQ` / `DMS_ROCKETMQ` -> `DMS`

## Minimal JSON

```json
{
  "title": "Three-tier Huawei Cloud Architecture",
  "style": "color",
  "groups": [
    { "id": "vpc1", "type": "VPC", "label": "vpc-prod", "x": 40, "y": 120, "w": 520, "h": 360 }
  ],
  "nodes": [
    { "id": "elb1", "service": "ELB", "label": "ELB", "group": "vpc1", "x": 110, "y": 180 },
    { "id": "ecs1", "service": "ECS", "label": "web", "group": "vpc1", "x": 260, "y": 280 },
    { "id": "rds1", "service": "RDS", "label": "RDS MySQL", "group": "vpc1", "x": 410, "y": 380 }
  ],
  "edges": [
    { "from": "elb1", "to": "ecs1" },
    { "from": "ecs1", "to": "rds1" }
  ]
}
```

## Layout Guidance

- Keep global traffic and security at the top.
- Put regions side by side for disaster recovery or active-active diagrams.
- Put replication, monitoring, logging, backup, and IAM in a separate operations/governance zone.
- Keep service icons at least 100px apart.
- Prefer short labels; use edge labels only for meaningful routes such as active path, failover path, replication, backup copy, and private sync.
- Do not put service nodes outside their intended parent container.

## Maintenance

To refresh icons:

```bash
python <skill-dir>/scripts/merge_official_product_icons.py --source <path-to-official-huaweicloud-product-icons> --replace-existing
```

Then copy `references/official-product-icons.md` to `references/service-catalog.md` if the catalog changed.

## Limits

- Generates new `.drawio` files; it does not edit existing diagrams in place.
- It does not export PNG/SVG.
- Automatic tier layout is intentionally simple; production-grade diagrams should use explicit geometry.
