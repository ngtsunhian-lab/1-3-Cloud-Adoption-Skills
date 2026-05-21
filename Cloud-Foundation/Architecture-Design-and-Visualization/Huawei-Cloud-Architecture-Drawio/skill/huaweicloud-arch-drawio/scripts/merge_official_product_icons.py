"""
Merge Huawei Cloud product-page icons into the skill icon registry.

Input source is the folder produced by:
  D:\\Codex\\云相关的操作\\Draw.IO\\build_official_drawio_library.py

It reads:
  - official-icons-manifest.json
  - images/<category>/<icon>.png|svg

and updates:
  - assets/icons-color.json
  - assets/official-product-icons-meta.json
  - references/official-product-icons.md
"""
from __future__ import annotations

import argparse
import base64
import json
import re
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"
REFERENCES_DIR = SKILL_ROOT / "references"


def key_from_code(code: str) -> str:
    key = re.sub(r"[^A-Za-z0-9]+", "_", code).strip("_").upper()
    return key or "ICON"


def data_uri(path: Path) -> str:
    ext = path.suffix.lower()
    mime = "image/svg+xml" if ext == ".svg" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to official-huaweicloud-product-icons")
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Replace icons-color.json with official product-page icons only.",
    )
    args = parser.parse_args()

    source = Path(args.source).resolve()
    manifest_path = source / "official-icons-manifest.json"
    image_root = source / "images"
    if not manifest_path.is_file() or not image_root.is_dir():
        raise SystemExit(f"Expected official icon source with manifest/images under: {source}")

    icons_path = ASSETS_DIR / "icons-color.json"
    icons = {} if args.replace_existing else json.loads(icons_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    official_meta: dict[str, dict] = {}
    added_or_replaced = 0
    skipped = 0
    for row in manifest:
        image_key = row["image_key"].replace("\\", "/")
        image_path = image_root.joinpath(*image_key.split("/"))
        if not image_path.is_file():
            skipped += 1
            continue
        key = key_from_code(row["code"])
        icons[key] = data_uri(image_path)
        official_meta[key] = {
            "title": row.get("title", row["code"]),
            "category": row.get("category", ""),
            "code": row.get("code", ""),
            "image_key": image_key,
            "href": row.get("href", ""),
            "description": row.get("description", ""),
            "source": "huaweicloud-product-pages",
        }
        added_or_replaced += 1

    icons_path.write_text(json.dumps(icons, ensure_ascii=False), encoding="utf-8")
    (ASSETS_DIR / "official-product-icons-meta.json").write_text(
        json.dumps(official_meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Huawei Cloud Official Product Icons",
        "",
        "Generated from Huawei Cloud public product pages and merged into `assets/icons-color.json`.",
        "",
        f"- Official product icons: {len(official_meta)}",
        f"- Color registry total after merge: {len(icons)}",
        "",
        "| key | title | category | image |",
        "| --- | --- | --- | --- |",
    ]
    for key in sorted(official_meta):
        row = official_meta[key]
        lines.append(f"| `{key}` | {row['title']} | {row['category']} | {row['image_key']} |")
    (REFERENCES_DIR / "official-product-icons.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"merged official icons: {added_or_replaced}")
    print(f"skipped missing images: {skipped}")
    print(f"color registry total: {len(icons)}")


if __name__ == "__main__":
    main()
