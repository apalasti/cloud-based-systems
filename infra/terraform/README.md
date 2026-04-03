## Terraform (AWS ECS/Fargate)

This folder provisions the infrastructure to run this app on **AWS ECS/Fargate** behind an **ALB**, with **PostgreSQL on RDS**, persistent uploads on **EFS**, and secrets in **Secrets Manager**.

### Architecture

Traffic and data flow (single VPC, multi-AZ public + private subnets):

```mermaid
flowchart TB
  subgraph clients [Clients]
    Browser[Browser]
  end

  subgraph vpc [VPC]
    subgraph pub [Public_subnets]
      ALB[Application_Load_Balancer]
      NAT[NAT_Gateway]
    end
    subgraph priv [Private_subnets]
      ECS[ECS_Fargate_tasks]
      RDS_db[(RDS_PostgreSQL)]
      EFS_fs[EFS_file_system]
    end
  end

  ECR[ECR_repository]
  SM[Secrets_Manager]
  CW[CloudWatch_Logs]
  CI[GitHub_Actions]

  Browser -->|HTTP_80| ALB
  ALB -->|HTTP_5000| ECS
  ECS -->|PostgreSQL| RDS_db
  ECS -->|NFS_2049| EFS_fs
  ECS -->|application_logs| CW
  ECS -.->|RDS_PASSWORD_SECRET_KEY_at_task_start| SM
  ECS -->|egress_for_image_pull| NAT
  NAT -->|internet| Internet((Internet))
  CI -->|docker_push| ECR
  ECS -.->|pull_image| ECR
```

- **Public subnets**: ALB and NAT Gateway (outbound internet for private tasks).
- **Private subnets**: ECS tasks, RDS, EFS mount targets.
- **Secrets Manager**: database password and app `SECRET_KEY` are referenced in the task definition; the **task execution role** reads them at container start.

### Prereqs

- AWS credentials configured (profile or env vars)
- Terraform installed

Defaults:
- **Region**: `eu-north-1`
- **HTTP only** (ALB DNS). HTTPS/custom domain can be added later (ACM + Route53).

---

## Remote state bootstrap (one-time)

Terraform’s S3 backend can’t create its own backend bucket/table, so bootstrap it first.

1. Create backend resources:

```bash
cd infra/terraform/bootstrap
terraform init
terraform apply
```

2. Note the outputs:
- `state_bucket`
- `lock_table`

---

## Provision the stack

1. Configure backend.

Edit `infra/terraform/backend.tf` and set:
- bucket = the `state_bucket` output
- dynamodb_table = the `lock_table` output

2. Deploy:

```bash
cd infra/terraform
terraform init
terraform apply
```

3. After apply, open the app:
- Use the `alb_dns_name` output.

---

## Container deploy (image updates)

Terraform provisions an ECR repo. You can:
- build/push an image to ECR
- update the ECS service to the new image tag

An optional GitHub Actions workflow is provided in `.github/workflows/deploy-ecs.yml`.

Notes:
- The ECS task uses the `:latest` image tag by default; the workflow pushes both `:latest` and `:${{ github.sha }}` and then forces a new deployment.
- The app is configured via `RDS_*` environment variables, with `RDS_PASSWORD` and `SECRET_KEY` loaded from Secrets Manager.

