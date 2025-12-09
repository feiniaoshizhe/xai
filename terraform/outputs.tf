# ============================================================================
# Resource Group Outputs
# ============================================================================

output "resource_group_name" {
  description = "Resource Group name"
  value       = azurerm_resource_group.main.name
}

output "resource_group_location" {
  description = "Resource Group location"
  value       = azurerm_resource_group.main.location
}

# ============================================================================
# Container Registry Outputs
# ============================================================================

output "acr_login_server" {
  description = "Container Registry login server URL"
  value       = azurerm_container_registry.acr.login_server
}

output "acr_admin_username" {
  description = "Container Registry admin username"
  value       = azurerm_container_registry.acr.admin_username
  sensitive   = true
}

output "acr_admin_password" {
  description = "Container Registry admin password"
  value       = azurerm_container_registry.acr.admin_password
  sensitive   = true
}

# ============================================================================
# Container App Outputs
# ============================================================================

output "container_app_url" {
  description = "Container App public URL"
  value       = "https://${azurerm_container_app.main.ingress[0].fqdn}"
}

output "container_app_fqdn" {
  description = "Container App FQDN"
  value       = azurerm_container_app.main.ingress[0].fqdn
}

# ============================================================================
# Azure OpenAI Outputs
# ============================================================================

output "openai_endpoint" {
  description = "Azure OpenAI endpoint URL"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "openai_key" {
  description = "Azure OpenAI primary key"
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
}

output "openai_deployment_name" {
  description = "Azure OpenAI model deployment name"
  value       = azurerm_cognitive_deployment.model.name
}

# ============================================================================
# Cosmos DB Outputs
# ============================================================================

output "cosmos_endpoint" {
  description = "Cosmos DB endpoint URL"
  value       = azurerm_cosmosdb_account.main.endpoint
}

output "cosmos_primary_key" {
  description = "Cosmos DB primary key"
  value       = azurerm_cosmosdb_account.main.primary_key
  sensitive   = true
}

output "cosmos_connection_string" {
  description = "Cosmos DB connection string"
  value       = azurerm_cosmosdb_account.main.primary_sql_connection_string
  sensitive   = true
}

output "cosmos_database_name" {
  description = "Cosmos DB database name"
  value       = azurerm_cosmosdb_sql_database.main.name
}

output "cosmos_container_name" {
  description = "Cosmos DB container name"
  value       = azurerm_cosmosdb_sql_container.conversations.name
}

# ============================================================================
# Application Insights Outputs
# ============================================================================

output "appinsights_instrumentation_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.main.instrumentation_key
  sensitive   = true
}

output "appinsights_connection_string" {
  description = "Application Insights connection string"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

# ============================================================================
# Static Web App Outputs
# ============================================================================

output "static_web_app_url" {
  description = "Static Web App default hostname"
  value       = "https://${azurerm_static_web_app.frontend.default_host_name}"
}

output "static_web_app_deployment_token" {
  description = "Static Web App deployment token (for GitHub Actions)"
  value       = azurerm_static_web_app.frontend.api_key
  sensitive   = true
}

# ============================================================================
# Managed Identity Outputs
# ============================================================================

output "managed_identity_id" {
  description = "User Assigned Identity ID"
  value       = azurerm_user_assigned_identity.main.id
}

output "managed_identity_client_id" {
  description = "User Assigned Identity client ID"
  value       = azurerm_user_assigned_identity.main.client_id
}

output "managed_identity_principal_id" {
  description = "User Assigned Identity principal ID"
  value       = azurerm_user_assigned_identity.main.principal_id
}

# ============================================================================
# Summary Output (for quick reference)
# ============================================================================

output "deployment_summary" {
  description = "Summary of deployed resources"
  value = {
    resource_group      = azurerm_resource_group.main.name
    location            = azurerm_resource_group.main.location
    backend_url         = "https://${azurerm_container_app.main.ingress[0].fqdn}"
    frontend_url        = "https://${azurerm_static_web_app.frontend.default_host_name}"
    acr_server          = azurerm_container_registry.acr.login_server
    cosmos_endpoint     = azurerm_cosmosdb_account.main.endpoint
    openai_endpoint     = azurerm_cognitive_account.openai.endpoint
    openai_deployment   = azurerm_cognitive_deployment.model.name
  }
}
