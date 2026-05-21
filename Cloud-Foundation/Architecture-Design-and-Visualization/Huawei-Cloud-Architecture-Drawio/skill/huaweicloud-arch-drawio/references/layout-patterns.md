# 常见架构模板

LLM 遇到下列描述时，可直接套用对应模板，再按用户细节调整。

---

## 1. 经典三层 Web 架构

**关键词**：三层、Web 应用、负载均衡、ELB + ECS + RDS

```json
{
  "title": "三层 Web 架构",
  "style": "color",
  "groups": [
    { "id": "vpc",  "type": "VPC", "label": "vpc-prod" }
  ],
  "nodes": [
    { "id": "user", "service": "INTERNET", "label": "用户",     "tier": 0 },
    { "id": "elb",  "service": "ELB",      "label": "ELB",      "group": "vpc", "tier": 1 },
    { "id": "ecs1", "service": "ECS",      "label": "web-1",    "group": "vpc", "tier": 2 },
    { "id": "ecs2", "service": "ECS",      "label": "web-2",    "group": "vpc", "tier": 2 },
    { "id": "rds",  "service": "RDS",      "label": "MySQL",    "group": "vpc", "tier": 3 }
  ],
  "edges": [
    { "from": "user", "to": "elb"  },
    { "from": "elb",  "to": "ecs1" },
    { "from": "elb",  "to": "ecs2" },
    { "from": "ecs1", "to": "rds"  },
    { "from": "ecs2", "to": "rds"  }
  ]
}
```

> 若 `INTERNET` 在图标库中不存在，回退渲染器会画一个浅色矩形带文字，可接受。

---

## 2. 容器化微服务

**关键词**：CCE、Kubernetes、容器、微服务、Service Mesh

```json
{
  "title": "CCE 容器化部署",
  "groups": [
    { "id": "vpc",   "type": "VPC",    "label": "vpc-app" },
    { "id": "cce",   "type": "SUBNET", "label": "CCE 集群", "parent": "vpc" }
  ],
  "nodes": [
    { "id": "elb",   "service": "ELB",  "label": "ELB",      "group": "vpc", "tier": 1 },
    { "id": "ing",   "service": "CCE",  "label": "Ingress",  "group": "cce", "tier": 2 },
    { "id": "svc1",  "service": "CCE",  "label": "svc-user", "group": "cce", "tier": 3 },
    { "id": "svc2",  "service": "CCE",  "label": "svc-order","group": "cce", "tier": 3 },
    { "id": "dcs",   "service": "DCS",  "label": "Redis",    "group": "vpc", "tier": 4 },
    { "id": "rds",   "service": "RDS",  "label": "MySQL",    "group": "vpc", "tier": 5 }
  ],
  "edges": [
    { "from": "elb",  "to": "ing" },
    { "from": "ing",  "to": "svc1" },
    { "from": "ing",  "to": "svc2" },
    { "from": "svc1", "to": "dcs" },
    { "from": "svc1", "to": "rds" },
    { "from": "svc2", "to": "rds" }
  ]
}
```

---

## 3. 双 AZ 高可用 / 容灾

**关键词**：高可用、双活、容灾、跨 AZ、多 AZ

```json
{
  "title": "双 AZ 容灾",
  "groups": [
    { "id": "vpc", "type": "VPC", "label": "vpc-prod" },
    { "id": "az1", "type": "AZ",  "label": "AZ-1", "parent": "vpc" },
    { "id": "az2", "type": "AZ",  "label": "AZ-2", "parent": "vpc" }
  ],
  "nodes": [
    { "id": "elb",   "service": "ELB", "label": "ELB",    "group": "vpc", "tier": 1 },
    { "id": "ecs1a", "service": "ECS", "label": "web-1a", "group": "az1", "tier": 2 },
    { "id": "ecs2a", "service": "ECS", "label": "web-2a", "group": "az2", "tier": 2 },
    { "id": "rds1",  "service": "RDS", "label": "RDS 主", "group": "az1", "tier": 3 },
    { "id": "rds2",  "service": "RDS", "label": "RDS 备", "group": "az2", "tier": 3 }
  ],
  "edges": [
    { "from": "elb",   "to": "ecs1a" },
    { "from": "elb",   "to": "ecs2a" },
    { "from": "ecs1a", "to": "rds1"  },
    { "from": "ecs2a", "to": "rds2"  },
    { "from": "rds1",  "to": "rds2", "label": "同步" }
  ]
}
```

---

## 4. 混合云 / 专线接入

**关键词**：混合云、IDC、专线、DC、Direct Connect、VPN

```json
{
  "title": "混合云专线接入",
  "groups": [
    { "id": "idc",  "type": "CLOUD", "label": "本地数据中心 IDC" },
    { "id": "vpc",  "type": "VPC",   "label": "vpc-prod" }
  ],
  "nodes": [
    { "id": "onprem", "service": "ECS", "label": "本地业务",  "group": "idc", "tier": 1 },
    { "id": "dc",     "service": "DC",  "label": "云专线",                    "tier": 2 },
    { "id": "vgw",    "service": "VPC", "label": "VPC 网关",  "group": "vpc", "tier": 3 },
    { "id": "ecs",    "service": "ECS", "label": "云端 ECS", "group": "vpc", "tier": 4 }
  ],
  "edges": [
    { "from": "onprem", "to": "dc" },
    { "from": "dc",     "to": "vgw" },
    { "from": "vgw",    "to": "ecs" }
  ]
}
```

---

## 模板选取启发

| 用户提到的词 | 套哪个模板 |
| --- | --- |
| 三层、Web 应用、传统架构 | 1 经典三层 |
| 容器、K8s、CCE、微服务 | 2 容器化 |
| 双活、高可用、容灾、多 AZ | 3 双 AZ |
| 专线、混合云、IDC 上云、迁移 | 4 混合云 |
| 其他 | 自由组合，从最近模板裁剪 |

如用户描述明确给了节点和连线，直接按描述生成，不必硬套模板。模板只是兜底起点。
