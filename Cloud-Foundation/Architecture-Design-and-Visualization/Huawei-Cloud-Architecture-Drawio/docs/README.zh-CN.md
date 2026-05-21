# 华为云架构 Draw.io Skill 使用说明

## 简介

`huaweicloud-arch-drawio` 是一个 Codex / Claude Code skill，用来从自然语言或中间 JSON 生成华为云架构图，输出格式为 `.drawio`，可直接用 diagrams.net、draw.io Desktop 或 VS Code Draw.io 插件打开。

当前版本只使用新收集的 201 个华为云官方产品页图标，不依赖旧的第三方 254/382 图标库。

## 目录结构

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

## 安装到 Codex

```powershell
Copy-Item -Recurse -Force .\skill\huaweicloud-arch-drawio "$env:USERPROFILE\.codex\skills\huaweicloud-arch-drawio"
```

安装后，在 Codex 中可以直接提到 `$huaweicloud-arch-drawio`，例如：

```text
使用 $huaweicloud-arch-drawio 画一个华为云墨西哥跟巴西相互容灾的电商架构
```

## 安装到 Claude Code

```powershell
Copy-Item -Recurse -Force .\skill\huaweicloud-arch-drawio "$env:USERPROFILE\.claude\skills\huaweicloud-arch-drawio"
```

## 从 JSON 生成 draw.io

推荐流程是先校验 JSON，再渲染，再校验 draw.io，最后导出资源清单：

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

交付前可以使用严格校验：

```powershell
python .\skill\huaweicloud-arch-drawio\scripts\validate_arch_json.py .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.json --strict
```

## 中间 JSON 示例

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

完整字段说明见 `skill/huaweicloud-arch-drawio/references/json-schema.md`。

## 自建或第三方服务

华为云服务必须使用官方图标。如果是自建服务或第三方系统，请显式标注：

```json
{
  "id": "erp",
  "service": "CUSTOM",
  "label": "ERP 自建服务",
  "custom": true,
  "group": "app_subnet",
  "x": 560,
  "y": 555
}
```

## HaydnCSF / 解决方案工作台风格检查

skill 内置的 JSON 校验会尽量帮助架构图满足以下要求：

- 表达逻辑网络拓扑和业务流向。
- 展示华为云资源类型和数量。
- 服务标签体现业务角色，不只是服务缩写。
- 华为云服务使用对应官方图标。
- 自建或第三方服务显式标注。
- 导出资源清单，方便与配置清单保持一致。

## draw.io 图标库

如果只想在 draw.io 里手动使用图标，可以导入：

```text
icon-library/drawio-libraries/
```

也可以解压：

```text
icon-library/drawio-libraries.zip
```

## 图标权利说明

图标来自华为云公开产品页面，仓库只是为了架构绘图和 skill 使用进行整理。华为云名称、产品名、Logo、图标和商标归华为云/华为及其权利方所有。
