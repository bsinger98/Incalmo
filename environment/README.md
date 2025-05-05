# Terraform

## Manually setup simple network

Setup credentials in `crenditals.tfvars`

`cd` into the deployment directory

Deploy network `terraform apply -var-file=../credentials.tfvars`

Destroy network `terraform destroy -var-file=../credentials.tfvars`
