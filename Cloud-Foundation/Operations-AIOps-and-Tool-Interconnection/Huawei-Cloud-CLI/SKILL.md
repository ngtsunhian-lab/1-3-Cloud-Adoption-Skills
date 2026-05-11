---
name: hwcloud
description: Use this skill when querying or managing Huawei Cloud resources via the hcloud CLI (KooCLI). Triggers include: listing CSS clusters, managing IAM users, querying ECS instances, managing VPCs, operating EVS volumes, configuring ELB load balancers, managing RDS instances, operating CCE clusters, managing OBS buckets, or any Huawei Cloud resource operation that can be performed through the KooCLI.
---

# Huawei Cloud CLI Skill

## Overview

This skill wraps Huawei Cloud KooCLI (`hcloud`) for querying and managing cloud resources. It provides a unified interface for all Huawei Cloud services with auto-filled region/project defaults, destructive operation confirmation, and formatted output.

## Use This Skill When

- Querying Huawei Cloud resource status (CSS, ECS, VPC, RDS, etc.)
- Managing IAM users, projects, or access keys
- Creating, updating, or deleting cloud resources
- Listing infrastructure details for audit or review
- Performing bulk operations across Huawei Cloud services

## Pre-configured defaults

These values are auto-populated from the current CLI profile. Override them by passing explicit parameters.

- **CLI path**: auto-detected from `hcloud.exe` on the system, or use the `HCLOUD_PATH` environment variable. Common locations:
  - Windows: `D:/软件/huaweicloud-cli-windows-amd64/hcloud.exe`
  - Linux/macOS: `hcloud` (assumed in $PATH)
- **Region**: `la-north-2` (override with `--region=<value>`)
- **Project ID**: `afc631438d8941d0b10aaa2cee2bf94c` (override with `--project_id=<value>`)
- **Domain ID**: `8c4d02c8a23a44609afd2e668b0f1ca1`

## Execution rules

1. Parse the user's input as `<Service> <Operation> [parameters]`. For example:
   - `/hwcloud CSS ListClustersDetails` → list all CSS clusters
   - `/hwcloud IAM KeystoneListUsers` → list all IAM users
   - `/hwcloud CSS DeleteCluster --cluster_id=xxx` → delete a CSS cluster
   - `/hwcloud VPC ListVpcs` → list VPCs

2. Always include `--region=la-north-2` in the command. If the service requires `--project_id`, add `--project_id=afc631438d8941d0b10aaa2cee2bf94c` automatically unless the user explicitly provides a different one.

3. Run the command using Bash:
   ```
   hcloud <Service> <Operation> --region=la-north-2 [--project_id=afc631438d8941d0b10aaa2cee2bf94c] [user_params]
   ```

4. If the user's input is ambiguous or missing the service/operation, run `hcloud <Service> --help` to list available operations and ask the user to clarify.

5. If the user just types `/hwcloud` without arguments, show a brief help:
   ```
   Usage: /hwcloud <Service> <Operation> [params]
   Example: /hwcloud CSS ListClustersDetails
   Common services: CSS, IAM, VPC, ECS, EVS, ELB, RDS, CCE, OBS, DNS, NAT
   ```

6. For **destructive operations** (Delete, Remove, Terminate, etc.), ALWAYS confirm with the user before executing. Show the resource details and ask "Confirm this destructive operation? It cannot be undone." Wait for explicit confirmation.

7. If the command returns an error, check:
   - Whether `--project_id` is needed but missing
   - Whether the operation name is correct (suggest running `--help`)
   - Whether the region supports the service

8. Format JSON output for readability. For list results, summarize key fields in a table when possible (name, id, status, type).

## Common service quick references

- **CSS** (Cloud Search Service): ListClustersDetails, ShowClusterDetail, DeleteCluster, CreateCluster
- **IAM** (Identity): KeystoneListUsers, KeystoneListProjects, ListPermanentAccessKeys
- **ECS** (Elastic Cloud Server): ListServersDetails, ShowServer, DeleteServer
- **VPC** (Virtual Private Cloud): ListVpcs, ShowVpc, DeleteVpc
- **EVS** (Elastic Volume Service): ListVolumes, ShowVolume, DeleteVolume
- **ELB** (Elastic Load Balance): ListLoadbalancers, ShowLoadbalancer, DeleteLoadbalancer
- **RDS** (Relational Database): ListInstances, ShowInstance, DeleteInstance
- **CCE** (Cloud Container Engine): ListClusters, ShowCluster, DeleteCluster
- **OBS** (Object Storage): list, delete
- **NAT** (NAT Gateway): ListNatGateways, ShowNatGateway, DeleteNatGateway
