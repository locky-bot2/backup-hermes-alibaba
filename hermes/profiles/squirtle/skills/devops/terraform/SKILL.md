---
name: terraform
description: "Manage cloud infrastructure as code with Terraform"
version: 1.0.0
author: Squirtle
platforms: [linux, macos]
metadata:
  squirtle:
    tags: [terraform, infrastructure, cloud]
    team: squirtle
---

# Terraform Workflow

Provision and manage cloud infrastructure as code.

## Standard Layout

```
terraform/
  main.tf           # provider config + main resources
  variables.tf      # input variables
  outputs.tf        # output values
  terraform.tfvars  # variable values (gitignored)
  modules/          # reusable modules
```

## Best Practices

- Store state in remote backend (GCS / S3), never locally
- Use workspaces for environment separation (dev / staging / prod)
- Tag all resources with `project`, `environment`, `managed_by`
- Run `terraform plan` before every `terraform apply`
- Pin provider versions

## Common Resources to Manage

- Cloud Run services
- GKE / K8s clusters
- Cloud SQL databases
- VPC networks and firewalls
- IAM roles and service accounts
- Load balancers and DNS

## After Ash Merges

- Pull latest main
- Run `terraform plan` to preview changes
- Run `terraform apply` to deploy infrastructure changes
- Verify with health checks