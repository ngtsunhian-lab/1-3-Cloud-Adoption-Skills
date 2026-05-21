# Huawei Cloud Architecture Draw.io Skill / 华为云架构 Draw.io Skill

Generate Huawei Cloud architecture diagrams in `.drawio` / diagrams.net format with locally bundled official Huawei Cloud product icons.

使用本地收集的华为云官方产品图标，生成 `.drawio` / diagrams.net 架构图。

## What Is Included / 仓库内容

- `skill/huaweicloud-arch-drawio/`: Codex / Claude Code skill.
- `icon-library/official-huaweicloud-product-icons/`: 201 Huawei Cloud product icons collected from Huawei Cloud public product pages.
- `icon-library/drawio-libraries/`: draw.io XML icon libraries.
- `examples/mexico-brazil-ecommerce-dr/`: Mexico-Brazil e-commerce disaster recovery sample architecture.
- `docs/README.zh-CN.md`: 中文使用说明.
- `docs/README.en.md`: English usage guide.

## Quick Start / 快速开始

Install the skill into Codex:

```powershell
Copy-Item -Recurse -Force .\skill\huaweicloud-arch-drawio "$env:USERPROFILE\.codex\skills\huaweicloud-arch-drawio"
```

安装到 Claude Code:

```powershell
Copy-Item -Recurse -Force .\skill\huaweicloud-arch-drawio "$env:USERPROFILE\.claude\skills\huaweicloud-arch-drawio"
```

Render the sample:

```powershell
python .\skill\huaweicloud-arch-drawio\scripts\validate_arch_json.py .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.json
python .\skill\huaweicloud-arch-drawio\scripts\render_drawio.py --input .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.json --output .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.drawio
python .\skill\huaweicloud-arch-drawio\scripts\validate_drawio.py .\examples\mexico-brazil-ecommerce-dr\mexico_brazil_ecommerce_dr.drawio
```

Then open the `.drawio` file with diagrams.net, draw.io desktop, or the VS Code Draw.io extension.

## Documentation / 文档

- [中文使用说明](docs/README.zh-CN.md)
- [English Usage Guide](docs/README.en.md)

## Icon Notice / 图标说明

The icon assets are collected from Huawei Cloud public product pages for architecture drawing convenience. Huawei Cloud names, logos, icons, and trademarks belong to Huawei Cloud / Huawei and their respective owners. See [NOTICE.md](NOTICE.md).

图标资产来自华为云公开产品页面，仅用于架构图绘制便利。华为云名称、Logo、图标和商标归华为云/华为及其权利方所有。请阅读 [NOTICE.md](NOTICE.md)。
