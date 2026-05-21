# Huawei Cloud Architecture Draw.io Skill Usage Guide

## Overview

`huaweicloud-arch-drawio` is a Codex / Claude Code skill for generating Huawei Cloud architecture diagrams from natural language or intermediate JSON. It outputs `.drawio` files that can be opened by diagrams.net, draw.io Desktop, or the VS Code Draw.io extension.

This version uses only the newly collected 201 official Huawei Cloud product-page icons. It does not depend on the old third-party 254/382 icon registries.

## Repository Layout

```text
skill/huaweicloud-arch-drawio/
  SKILL.md
  assets/
    icons-color.json
    official-product-icons-meta.json
  references/
    json-schema.md
    service-catalog.md
  scripts/
    validate_arch_json.py
    render_drawio.py
    validate_drawio.py
    export_resource_inventory.py
    merge_official_product_icons.py

icon-library/
  official-huaweicloud-product-icons/
  drawio-libraries/
  official-huaweicloud-product-icons.zip
  drawio-libraries.zip

examples/
  mexico-brazil-ecommerce-dr/
```

## Install for Codex

```powershell
Copy-Item -Recurse -Force .\skill\huaweicloud-arch-drawio "$env:USERPROFILE\.codex\skills\huaweicloud-arch-drawio"
```

After installation, mention `$huaweicloud-arch-drawio` in Codex, for example:

```text
Use $huaweicloud-arch-drawio to draw a Huawei Cloud Mexico-Brazil e-commerce disaster recovery architecture.
```

## Install for Claude Code

```powershell
Copy-Item -Recurse -Force .\skill\huaweicloud-arch-drawio "$env:USERPROFILE\.claude\skills\huaweicloud-arch-drawio"
```

## Render a Diagram from JSON

The recommended flow is: validate JSON, render the `.drawio` file, validate the generated diagram, then export a resource inventory.

```powershell
python .\skill\huaweicloud-arch-drawio\scripts\validate_arch_json.py .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.json

python .\skill\huaweicloud-arch-drawio\scripts\render_drawio.py `
  --input .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.json `
  --output .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.drawio

python .\skill\huaweicloud-arch-drawio\scripts\validate_drawio.py .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.drawio

python .\skill\huaweicloud-arch-drawio\scripts\export_resource_inventory.py `
  .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.json `
  --output .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.resources.csv
```

Use strict validation before final delivery:

```powershell
python .\skill\huaweicloud-arch-drawio\scripts\validate_arch_json.py .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.json --strict
```

## Intermediate JSON Example

```json
{
  "title": "Three-tier Huawei Cloud Architecture",
  "style": "color",
  "groups": [
    { "id": "vpc1", "type": "VPC", "label": "prod-vpc", "x": 40, "y": 120, "w": 520, "h": 360 }
  ],
  "nodes": [
    { "id": "elb1", "service": "ELB", "label": "Public ELB", "group": "vpc1", "x": 110, "y": 180 },
    { "id": "ecs1", "service": "ECS", "label": "Web ECS", "group": "vpc1", "x": 260, "y": 280 },
    { "id": "rds1", "service": "RDS", "label": "RDS MySQL primary", "group": "vpc1", "x": 410, "y": 380 }
  ],
  "edges": [
    { "from": "elb1", "to": "ecs1" },
    { "from": "ecs1", "to": "rds1" }
  ]
}
```

See `skill/huaweicloud-arch-drawio/references/json-schema.md` for the full schema.

## Self-built or Third-party Services

Huawei Cloud services must use official icons. For self-built or third-party systems, mark the node explicitly:

```json
{
  "id": "erp",
  "service": "CUSTOM",
  "label": "ERP self-built service",
  "custom": true,
  "group": "app_subnet",
  "x": 560,
  "y": 555
}
```

## HaydnCSF / Solution-Design Style Checks

The built-in JSON validator helps diagrams satisfy these review-oriented expectations:

- Show logical network topology and business flow.
- Show Huawei Cloud resource types and quantities.
- Use business-role labels instead of service acronyms only.
- Use official Huawei Cloud icons for Huawei Cloud services.
- Explicitly label self-built or third-party services.
- Export a resource inventory that can be aligned with configuration lists.

## draw.io Icon Libraries

If you only want to use the icons manually in draw.io, import files from:

```text
icon-library/drawio-libraries/
```

Or extract:

```text
icon-library/drawio-libraries.zip
```

## Icon Rights Notice

The icons were collected from Huawei Cloud public product pages and organized for architecture drawing and skill usage. Huawei Cloud names, product names, logos, icons, and trademarks belong to Huawei Cloud / Huawei and their respective owners.
