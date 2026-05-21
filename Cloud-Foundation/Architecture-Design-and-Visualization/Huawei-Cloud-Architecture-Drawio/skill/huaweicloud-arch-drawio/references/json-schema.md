# 中间 JSON 结构规范

LLM 先把用户的自然语言架构描述转换成此 JSON，再交给 `scripts/render_drawio.py` 渲染为 `.drawio`。复杂生产图建议显式写 `x/y/w/h`，不要只依赖自动排版。

## 顶层字段

```json
{
  "title": "架构图名称",
  "style": "color",
  "groups": [],
  "nodes": [],
  "edges": []
}
```

- `title`：可选，作为 draw.io diagram 名称。
- `style`：可选，目前只支持 `color`；即使传入 `mono` 也会回退到官方彩色图标。
- `groups`：可选，容器，如 Region、VPC、AZ、Subnet、治理区。
- `nodes`：必填，服务节点或显式标注的自建/第三方节点。
- `edges`：可选，节点之间的连接和业务流向。

## groups

容器用于表达 Region、VPC、AZ、Subnet 等边界。支持嵌套，坐标使用画布绝对坐标；渲染时会自动转换成 draw.io 父子相对坐标。

```json
{
  "id": "mx_vpc",
  "type": "VPC",
  "label": "Mexico production VPC",
  "parent": "mx_region",
  "x": 70,
  "y": 300,
  "w": 640,
  "h": 620
}
```

常用 `type`：

| type | 含义 | 视觉 |
| --- | --- | --- |
| `CLOUD` | 全局区、运维区、云上总体边界 | 红色实线浅底 |
| `REGION` | 区域 | 蓝色虚线 |
| `VPC` | 虚拟私有云 | 红色实线 |
| `AZ` | 可用区 | 浅蓝虚线 |
| `SUBNET` | 子网 | 灰色虚线浅底 |

## nodes

```json
{
  "id": "mx_ecs",
  "service": "ECS",
  "label": "ECS admin / jobs",
  "group": "mx_app",
  "tier": 3,
  "x": 410,
  "y": 555
}
```

- `id`：必填，唯一 ID，`edges` 使用它引用节点。
- `service`：必填，官方服务图标 key。查 `references/service-catalog.md`。
- `label`：可选，节点下方显示文字；生产图应体现业务作用，而不只是服务缩写。
- `group`：可选，所属容器 ID。复杂图应填写。
- `tier`：可选，自动布局时使用，数字越小越靠上。
- `x/y`：可选，显式画布坐标。复杂图建议填写。
- `custom`：可选，`true` 表示自建或第三方服务，不使用华为云官方图标。
- `type`：可选，设为 `custom`、`third_party`、`self_built` 时等同于 `custom: true`。

自建/第三方服务示例：

```json
{
  "id": "erp",
  "service": "CUSTOM",
  "label": "ERP 自建服务",
  "custom": true,
  "group": "mx_app",
  "x": 560,
  "y": 555
}
```

服务图标固定使用正方形几何，避免 PNG 图标被压扁。没有官方图标的华为云服务不要强行画成普通服务节点，应先补图标库或标注为自建/第三方。

## edges

```json
{
  "from": "mx_elb",
  "to": "mx_cce",
  "label": "active traffic"
}
```

- `from` / `to`：必填，只能连接节点，不能直接连接容器。
- `label`：可选，建议只标注关键路由，如主路径、容灾路径、复制、备份、专线同步。

## HaydnCSF 架构审核要点

参考华为云 HaydnCSF/解决方案工作台文档，架构图应尽量满足：

- 体现逻辑网络拓扑和业务流向。
- 展示华为云资源类型和数量，并能导出资源清单。
- 表达哪些业务或应用部署在哪些资源上。
- 华为云服务使用对应的华为云图标。
- 自建或第三方服务使用 `custom: true`，并在 `label` 中明确“自建服务”或“第三方服务”。
- 资源清单、配置清单与架构图里的资源节点保持一致。

## 生成与验证

```bash
python <skill-dir>/scripts/validate_arch_json.py arch.json
python <skill-dir>/scripts/render_drawio.py --input arch.json --output arch.drawio
python <skill-dir>/scripts/validate_drawio.py arch.drawio
python <skill-dir>/scripts/export_resource_inventory.py arch.json --output arch.resources.csv
```

`validate_arch_json.py --strict` 会把所有警告当成错误，适合交付前收口。

`validate_drawio.py` 会检查：

- XML 是否可解析。
- 服务节点是否嵌入了图标 data URI。
- 图标几何是否为正方形。
- 是否出现红色兜底节点。
- 是否有重复坐标或明显重叠。

## 常用服务 key

| 服务 | key |
| --- | --- |
| Elastic Cloud Server | `ECS` |
| Elastic Load Balance | `ELB` |
| Virtual Private Cloud | `VPC` |
| Elastic IP | `EIP` |
| Object Storage Service | `OBS` |
| Cloud Container Engine | `CCE` |
| Cloud Container Instance | `CCI` |
| RDS for MySQL | `RDSFORMYSQL` 或 `RDS` |
| Distributed Cache Service Redis | `REDIS` 或 `DCS` |
| Web Application Firewall | `WAF` |
| Cloud Firewall | `CFW` |
| API Gateway | `APIG` |
| Direct Connect | `DC` |
| Data Replication Service | `DRS` |
| Cloud Backup and Recovery | `CBR` |
| Cloud Eye | `CES` |
| Log Tank Service | `LTS` |
| Simple Message Notification | `SMN` |
| IAM | `IAM` |

完整 201 个官方产品图标见 `references/service-catalog.md`。

## 布局建议

- 中大型架构优先显式设置 `x/y/w/h`，不要完全依赖 `tier` 自动布局。
- Region / VPC / Subnet 使用大容器，服务节点至少间隔 100px。
- 全局入口放顶部，业务 Region 左右并列，复制/监控/治理放底部或侧边。
- 线上主路径和容灾路径都要标注，但避免给每条边都写长文字。
