## Terraform (AWS ECS/Fargate)

This folder provisions the infrastructure to run this app on **AWS ECS/Fargate** behind an **ALB**, with **PostgreSQL on RDS**, persistent uploads on **EFS**, and secrets in **Secrets Manager**.

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

