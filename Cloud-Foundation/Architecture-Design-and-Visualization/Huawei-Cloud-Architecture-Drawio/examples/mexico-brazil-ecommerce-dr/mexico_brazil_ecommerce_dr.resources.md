# Huawei Cloud Resource Inventory

## Aggregated Counts

- `APIG`: 2
- `CBR`: 1
- `CCE`: 2
- `CDN`: 1
- `CES`: 1
- `CFW`: 3
- `DC`: 1
- `DNS`: 1
- `DRS`: 1
- `ECS`: 2
- `ELB`: 2
- `GA`: 1
- `IAM`: 1
- `LTS`: 1
- `OBS`: 2
- `RDSFORMYSQL`: 2
- `REDIS`: 2
- `SMN`: 1
- `WAF`: 1

## Detail

| node_id | resource_key | label_or_business_role | group_label |
| --- | --- | --- | --- |
| dns | DNS | DNS failover | Global traffic, security and protection |
| cdn | CDN | CDN static acceleration | Global traffic, security and protection |
| ga | GA | Global Accelerator | Global traffic, security and protection |
| waf | WAF | WAF web protection | Global traffic, security and protection |
| cfw_global | CFW | Cloud Firewall policy | Global traffic, security and protection |
| mx_cfw | CFW | Cloud Firewall | Public subnet |
| mx_elb | ELB | Public ELB | Public subnet |
| mx_apig | APIG | API Gateway | Public subnet |
| mx_cce | CCE | CCE e-commerce services | Application subnet |
| mx_ecs | ECS | ECS admin / jobs | Application subnet |
| mx_redis | REDIS | DCS Redis | Data subnet |
| mx_rds | RDSFORMYSQL | RDS MySQL primary | Data subnet |
| mx_obs | OBS | OBS product images | Data subnet |
| br_cfw | CFW | Cloud Firewall | Public subnet |
| br_elb | ELB | Standby ELB | Public subnet |
| br_apig | APIG | Standby API Gateway | Public subnet |
| br_cce | CCE | CCE warm standby | Application subnet |
| br_ecs | ECS | ECS DR jobs | Application subnet |
| br_redis | REDIS | DCS Redis standby | Data subnet |
| br_rds | RDSFORMYSQL | RDS MySQL standby | Data subnet |
| br_obs | OBS | OBS replicated objects | Data subnet |
| dc | DC | Private cross-region connectivity | Cross-region replication, monitoring and governance |
| drs | DRS | DRS database replication | Cross-region replication, monitoring and governance |
| cbr | CBR | CBR backup copy | Cross-region replication, monitoring and governance |
| ces | CES | Cloud Eye | Cross-region replication, monitoring and governance |
| lts | LTS | LTS logs | Cross-region replication, monitoring and governance |
| smn | SMN | SMN alerts | Cross-region replication, monitoring and governance |
| iam | IAM | IAM least-privilege access | Cross-region replication, monitoring and governance |
