# ============================================================================
# Azure Configuration
# ============================================================================

variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

# ============================================================================
# Project Configuration
# ============================================================================

variable "project_name" {
  description = "Project name prefix for resource naming"
  type        = string
  default     = "maf"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Resource group name (optional, defaults to auto-generated)"
  type        = string
  default     = ""
}

# ============================================================================
# Container Registry Configuration
# ============================================================================

variable "acr_sku" {
  description = "Azure Container Registry SKU"
  type        = string
  default     = "Basic"
  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "ACR SKU must be Basic, Standard, or Premium."
  }
}

# ============================================================================
# Container App Configuration
# ============================================================================

variable "container_app_name" {
  description = "Container App name"
  type        = string
  default     = "mafagent"
}

variable "container_app_min_replicas" {
  description = "Minimum number of container replicas"
  type        = number
  default     = 1
}

variable "container_app_max_replicas" {
  description = "Maximum number of container replicas"
  type        = number
  default     = 3
}

variable "container_cpu" {
  description = "CPU allocation for container (in cores)"
  type        = number
  default     = 1.0
}

variable "container_memory" {
  description = "Memory allocation for container (in Gi)"
  type        = string
  default     = "2Gi"
}

# ============================================================================
# Azure OpenAI Configuration
# ============================================================================

variable "openai_sku_name" {
  description = "Azure OpenAI SKU"
  type        = string
  default     = "S0"
}

variable "openai_deployment_name" {
  description = "Azure OpenAI model deployment name"
  type        = string
  default     = "gpt-5-nano"
}

variable "openai_model_name" {
  description = "Azure OpenAI model name"
  type        = string
  default     = "gpt-4o-mini"
}

variable "openai_model_version" {
  description = "Azure OpenAI model version"
  type        = string
  default     = "2024-07-18"
}

variable "openai_capacity" {
  description = "Azure OpenAI deployment capacity (TPM in thousands)"
  type        = number
  default     = 10
}

# ============================================================================
# Cosmos DB Configuration
# ============================================================================

variable "cosmos_db_name" {
  description = "Cosmos DB database name"
  type        = string
  default     = "maf_db"
}

variable "cosmos_container_name" {
  description = "Cosmos DB container name"
  type        = string
  default     = "conversations"
}

variable "cosmos_partition_key" {
  description = "Cosmos DB partition key"
  type        = string
  default     = "/session_id"
}

variable "cosmos_throughput" {
  description = "Cosmos DB throughput (RU/s)"
  type        = number
  default     = 400
}

# ============================================================================
# Static Web App Configuration
# ============================================================================

variable "static_web_app_sku_tier" {
  description = "Static Web App SKU tier"
  type        = string
  default     = "Free"
  validation {
    condition     = contains(["Free", "Standard"], var.static_web_app_sku_tier)
    error_message = "Static Web App SKU must be Free or Standard."
  }
}

variable "static_web_app_sku_size" {
  description = "Static Web App SKU size"
  type        = string
  default     = "Free"
}

# ============================================================================
# Tags
# ============================================================================

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "MAF"
    ManagedBy   = "Terraform"
    Environment = "Production"
  }
}
