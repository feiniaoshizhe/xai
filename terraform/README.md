# Terraform Configuration for MAF

This directory contains Terraform configuration to provision all Azure resources for the MAF (Microsoft Agent Framework - AG-UI Azure Template) project.

## 🎯 What Gets Created

Running `terraform apply` will create:

| Resource | Name Pattern | Description |
|----------|-------------|-------------|
| Resource Group | `maf-prod-rg` | Container for all resources |
| Container Registry | `mafprodacrXXXXXX` | Docker image storage |
| Container App Environment | `maf-prod-env` | Container Apps environment |
| Container App | `mafagent` | Backend API (FastAPI) |
| Azure OpenAI | `maf-prod-openai-XXXXXX` | LLM service with gpt-5-nano |
| Cosmos DB Account | `maf-prod-cosmos-XXXXXX` | NoSQL database |
| Cosmos DB Database | `maf_db` | Database for app data |
| Cosmos DB Container | `conversations` | Chat message storage |
| Application Insights | `maf-prod-insights` | Monitoring and telemetry |
| Log Analytics Workspace | `maf-prod-workspace-XXXXXX` | Logs storage |
| Static Web App | `maf-prod-frontend` | Frontend (Next.js) |
| User Assigned Identity | `maf-prod-identity` | Managed Identity |

**Plus RBAC role assignments for secure access between resources.**

## 📋 Prerequisites

1. **Terraform** (>= 1.5.0)
   ```bash
   # Install on Windows (using Chocolatey)
   choco install terraform

   # Install on macOS
   brew install terraform

   # Install on Linux
   wget https://releases.hashicorp.com/terraform/1.7.0/terraform_1.7.0_linux_amd64.zip
   unzip terraform_1.7.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

2. **Azure CLI**
   ```bash
   # Install Azure CLI
   # Windows: https://aka.ms/installazurecliwindows
   # macOS: brew install azure-cli
   # Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

   # Login
   az login

   # Set subscription (if you have multiple)
   az account set --subscription "YOUR_SUBSCRIPTION_ID"
   ```

3. **Azure Subscription** with permissions to create resources

## 🚀 Quick Start

### 1. Configure Variables

```bash
# Copy the example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
# Note: This file is gitignored and contains sensitive data
vim terraform.tfvars  # or use your preferred editor
```

**Example `terraform.tfvars`:**

```hcl
project_name        = "maf"
environment         = "prod"
location            = "eastus"
resource_group_name = ""  # Leave empty to auto-generate, or use "llmmvp"

# Container settings
container_app_name = "mafagent"

# Azure OpenAI settings
openai_deployment_name = "gpt-5-nano"
openai_model_name      = "gpt-4o-mini"
```

### 2. Initialize Terraform

```bash
terraform init
```

This downloads the Azure provider and prepares Terraform.

### 3. Preview Changes

```bash
terraform plan
```

Review the resources that will be created.

### 4. Create Resources

```bash
# Apply with manual confirmation
terraform apply

# Or auto-approve (use with caution)
terraform apply -auto-approve
```

**Expected time: 10-15 minutes** ⏱️

### 5. View Outputs

```bash
# View all outputs
terraform output

# View specific output
terraform output container_app_url
terraform output -json deployment_summary
```

## 📝 Usage Examples

### Create a Development Environment

```bash
# Create dev.tfvars
cat > dev.tfvars <<EOF
project_name = "maf"
environment  = "dev"
location     = "eastus"
EOF

# Apply with dev configuration
terraform workspace new dev
terraform apply -var-file="dev.tfvars"
```

### Update Container App Configuration

```hcl
# Edit terraform.tfvars
container_cpu    = 2.0  # Increase from 1.0
container_memory = "4Gi"  # Increase from 2Gi

# Apply changes
terraform apply
```

### View Connection Strings

```bash
# Get all sensitive outputs
terraform output -json | jq '.deployment_summary.value'

# Get specific sensitive output
terraform output -raw openai_key
terraform output -raw cosmos_primary_key
```

## 🛡️ Security Best Practices

### 1. Use Remote State

Store your state file in Azure Storage (not locally):

```bash
# Create storage account for state
az group create --name terraform-state-rg --location eastus
az storage account create --name tfstatemaf --resource-group terraform-state-rg --sku Standard_LRS
az storage container create --name tfstate --account-name tfstatemaf

# Uncomment backend configuration in providers.tf
```

### 2. Never Commit Sensitive Files

These files are already in `.gitignore`:
- `terraform.tfvars` (contains real values)
- `*.tfstate` (may contain secrets)
- `.terraform/` (provider cache)

### 3. Use Environment Variables for Secrets

Instead of putting secrets in `terraform.tfvars`:

```bash
export TF_VAR_openai_api_key="sk-..."
terraform apply
```

## 🔧 Common Commands

| Command | Description |
|---------|-------------|
| `terraform init` | Initialize providers and modules |
| `terraform validate` | Check configuration syntax |
| `terraform fmt` | Format configuration files |
| `terraform plan` | Preview changes |
| `terraform apply` | Create/update resources |
| `terraform destroy` | Delete all resources |
| `terraform output` | Show output values |
| `terraform show` | Show current state |
| `terraform state list` | List resources in state |

## 🌍 Multi-Environment Setup

### Using Workspaces

```bash
# Create workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Switch between environments
terraform workspace select dev
terraform apply -var-file="dev.tfvars"

terraform workspace select prod
terraform apply -var-file="prod.tfvars"

# List workspaces
terraform workspace list
```

### Using Separate Directories

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf -> ../../main.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── main.tf -> ../../main.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf -> ../../main.tf
│       └── terraform.tfvars
```

## 🗑️ Cleanup

### Destroy All Resources

```bash
# Review what will be deleted
terraform plan -destroy

# Destroy (with confirmation)
terraform destroy

# Destroy (auto-approve, use with caution!)
terraform destroy -auto-approve
```

**Warning:** This will DELETE all resources and their data!

### Destroy Specific Resources

```bash
# Target a specific resource
terraform destroy -target=azurerm_container_app.main
```

## 🐛 Troubleshooting

### Issue: "Resource already exists"

If you manually created resources:

```bash
# Import existing resource
terraform import azurerm_resource_group.main /subscriptions/{sub-id}/resourceGroups/llmmvp

# Then apply
terraform apply
```

### Issue: "Quota exceeded"

Some Azure OpenAI regions have limited availability:

```hcl
# Try a different region
location = "westus"  # or "westeurope"
```

### Issue: State is locked

```bash
# Force unlock (use carefully)
terraform force-unlock LOCK_ID
```

### Issue: Provider version conflicts

```bash
# Upgrade providers
terraform init -upgrade
```

## 📚 Learn More

- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/)
- [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/)
- [Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/)

## 🤝 Contributing

When adding new resources:

1. Add resource definition in `main.tf`
2. Add variables in `variables.tf`
3. Add outputs in `outputs.tf`
4. Update `terraform.tfvars.example`
5. Document in this README

## 📄 License

Apache 2.0
