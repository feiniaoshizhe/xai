# Azure 部署指南

## 项目概述

本项目是基于 Microsoft Agent Framework + CopilotKit + Azure OpenAI 的 AI Agent 模板，支持 Docker 化部署到 Azure Container Apps。

---

## 部署架构

```
GitHub Repository
    ↓ (git push)
GitHub Actions (CI/CD)
    ↓ (build & push)
Azure Container Registry (mafagentacr)
    ↓ (deploy)
Azure Container App (mafagent)
    ↓ (authenticate)
Azure OpenAI (Managed Identity)
```

---

## 前置准备

### 本地环境

- ✅ Python 3.13 + uv
- ✅ Docker + docker-compose
- ✅ Azure CLI (`az login` 已完成)
- ✅ GitHub 账号
- ✅ Azure 订阅

### Azure 资源

- Azure OpenAI 服务 (`llmmvptest1`)
  - 部署名称：`gpt-5-nano`
  - 端点：`https://llmmvptest1.openai.azure.com/`

---

## 部署步骤

### 第一步：创建 Azure Container Registry

1. 访问 [Azure Portal](https://portal.azure.com)
2. 搜索 **Container Registry** → 创建
3. 填写配置：
   - **Registry name**: `mafagentacr`（必须全球唯一）
   - **Resource group**: `llmmvp`（或新建）
   - **Location**: `Japan East`
   - **Pricing plan**: `Basic`
4. 点击 **Review + create** → **Create**
5. 创建完成后，进入 Registry
6. 左侧 **Settings → Access keys**
7. 开启 **Admin user** ✅

---

### 第二步：创建 Azure Container App

#### 2.1 基础配置

1. 搜索 **Container Apps** → 创建
2. **Basics** 标签页：
   - **Resource group**: `llmmvp`
   - **Container app name**: `mafagent`
   - **Region**: `Japan East`（与 Registry 同区）
   - **Optimize for Azure Functions**: ❌ 不勾选

3. **Container** 标签页：
   - **Use quickstart image**: ✅ 勾选（先用示例镜像创建）
   - **Image source**: `Azure Container Registry`
   - **Registry**: `mafagentacr`

4. 点击 **Review + create** → **Create**

#### 2.2 配置 Ingress（重要！）

1. 进入创建好的 Container App
2. 左侧 **Networking → Ingress**
3. 配置：
   - **Ingress**: ✅ Enabled
   - **Ingress traffic**: `Accepting traffic from anywhere`
   - **Ingress type**: `HTTP`
   - **Target port**: `8000` ⚠️（默认是 80，必须改成 8000）
4. 点击 **Save**

---

### 第三步：配置 Managed Identity 认证

#### 3.1 开启 Managed Identity

1. Container App → **Settings → Identity**
2. **System assigned** 标签页
3. **Status** 改成 **On**
4. 点击 **Save**
5. 记下生成的 **Object (principal) ID**

#### 3.2 授权访问 Azure OpenAI

1. 搜索你的 Azure OpenAI 资源：`llmmvptest1`
2. 左侧 **Access control (IAM)**
3. 点击 **+ Add → Add role assignment**
4. **Role** 标签页：
   - 选择 **Cognitive Services OpenAI User**
   - 点击 **Next**
5. **Members** 标签页：
   - **Assign access to**: `Managed identity`
   - 点击 **+ Select members**
   - **Managed identity**: 选择 `Container App (1)`
   - 在列表中选择 `mafagent`
   - 点击 **Select**
6. 点击 **Review + assign** → **Assign**

---

### 第四步：配置环境变量

1. Container App → **Application → Containers** 或 **Settings → Environment variables**
2. 点击 **Edit and deploy** 或 **Add**
3. 添加以下环境变量：

| Name | Value |
|------|-------|
| `AZURE_OPENAI_ENDPOINT` | `https://llmmvptest1.openai.azure.com/` |
| `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` | `gpt-5-nano` |

4. 点击 **Save**

> ⚠️ **注意**：不需要 `AZURE_OPENAI_API_KEY`，因为使用 Managed Identity 认证。

---

### 第五步：配置 GitHub Actions CI/CD

#### 5.1 配置自动部署

1. Container App → **Settings → Deployment**
2. 点击 **Continuous deployment** 标签页
3. 点击 **Sign in with GitHub** 并授权
4. 配置：
   - **Organization**: `xxyckiki`
   - **Repository**: `maf-copilotkit-agent-template`
   - **Branch**: `main`
5. **Registry settings**：
   - **Repository source**: `Azure Container Registry`
   - **Registry**: `mafagentacr`
   - **Image**: `mafagent`
   - **Dockerfile location**: `./Dockerfile`
6. **Azure access**：
   - **Authentication type**: `User-assigned Identity` ✅
7. 点击 **Start continuous deployment**

#### 5.2 修复自动生成的 Workflow

Azure 生成的 workflow 文件可能有占位符错误，需要手动修复：

**文件路径**：`.github/workflows/mafagent-AutoDeployTrigger-*.yml`

修复前：
```yaml
_dockerfilePathKey_: _dockerfilePath_
_targetLabelKey_: _targetLabel_
```

修复后：
```yaml
dockerfilePath: ./Dockerfile
```

提交修复：
```bash
git add .
git commit -m "Fix workflow dockerfile path"
git push
```

---

### 第六步：修改代码支持云端部署

#### 6.1 使用 ChainedTokenCredential

**文件**：`src/services/agent.py`

```python
import os
from azure.identity import ManagedIdentityCredential, AzureCliCredential, ChainedTokenCredential
from agent_framework.azure import AzureOpenAIChatClient


def get_credential():
    """Get credential based on environment."""
    # 云端优先使用 Managed Identity，本地用 Azure CLI
    return ChainedTokenCredential(
        ManagedIdentityCredential(),  # 云端
        AzureCliCredential(),          # 本地
    )


# Create the chat client
chat_client = AzureOpenAIChatClient(
    credential=get_credential(),
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-5-nano"),
)
```

#### 6.2 推送代码触发部署

```bash
git add .
git commit -m "Use ChainedTokenCredential for Managed Identity"
git push
```

---

## 验证部署

### 查看部署状态

1. **GitHub Actions**：https://github.com/xxyckiki/maf-copilotkit-agent-template/actions
   - 等待 workflow 变成 ✅ 绿色

2. **Azure Container App Revisions**：
   - Container App → **Application → Revisions and replicas**
   - 新的 Revision 状态变成 **Running** ✅

### 测试 API

访问你的应用 URL：

```
https://mafagent.bravebeach-3e2d28d0.japaneast.azurecontainerapps.io
```

预期响应：
```json
{
  "message": "Flight Agent API",
  "docs": "/docs",
  "version": "1.0.0"
}
```

API 文档：
```
https://mafagent.bravebeach-3e2d28d0.japaneast.azurecontainerapps.io/docs
```

---

## 常见问题排查

### 1. 服务启动后立即关闭

**症状**：
```
INFO: Application startup complete.
INFO: Shutting down
```

**原因**：Ingress Target port 配置错误

**解决**：
- 检查 **Networking → Ingress → Target port** 是否为 `8000`
- 如果不是，改成 `8000` 并保存
- 推送空 commit 触发重新部署：
  ```bash
  git commit --allow-empty -m "Trigger redeploy"
  git push
  ```

---

### 2. Azure CLI not found 错误

**症状**：
```
AzureCliCredential.get_token failed: Azure CLI not found on path
```

**原因**：DefaultAzureCredential 尝试 Azure CLI 认证失败

**解决**：使用 `ChainedTokenCredential`，优先尝试 Managed Identity

---

### 3. Managed Identity 认证失败

**检查清单**：

1. ✅ Container App 已开启 System-assigned Managed Identity
2. ✅ Managed Identity 已被授予 `Cognitive Services OpenAI User` 角色
3. ✅ 环境变量 `AZURE_OPENAI_ENDPOINT` 和 `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` 已配置
4. ✅ 代码使用 `ManagedIdentityCredential` 或 `ChainedTokenCredential`

---

### 4. Docker 镜像构建失败

**检查**：
- Dockerfile 路径是否正确（`./Dockerfile`）
- GitHub Actions workflow 文件是否有占位符错误
- Container Registry Admin user 是否已开启

---

## CI/CD 工作流程

```
1. 开发者 git push 到 main 分支
    ↓
2. GitHub Actions 自动触发
    ↓
3. 构建 Docker 镜像
    ↓
4. 推送到 Azure Container Registry
    ↓
5. 部署到 Azure Container App
    ↓
6. 健康检查通过 → 流量切换到新版本
```

---

## 认证方式对比

| 方式 | 本地开发 | Azure 云端 | 安全性 | 复杂度 |
|------|---------|-----------|-------|-------|
| **API Key** | ✅ | ✅ | ⚠️ 中 | ⭐ 简单 |
| **Azure CLI** | ✅ | ❌ | ✅ 高 | ⭐ 简单 |
| **Managed Identity** | ❌ | ✅ | ✅ 最高 | ⭐⭐ 中等 |
| **ChainedTokenCredential** | ✅ | ✅ | ✅ 最高 | ⭐⭐ 中等 |

**推荐**：使用 `ChainedTokenCredential(ManagedIdentityCredential(), AzureCliCredential())`

---

## 成本估算

| 资源 | 配置 | 月成本（估算） |
|------|------|--------------|
| Container Registry | Basic | ~$5 |
| Container App | 按需计费 | ~$0-20（取决于流量） |
| Azure OpenAI | 按 token 计费 | 取决于使用量 |

**注意**：Container App 在无流量时可以缩容到 0，节省成本。

---

## 项目配置文件

### 关键文件清单

```
.
├── .github/
│   └── workflows/
│       └── mafagent-AutoDeployTrigger-*.yml  # CI/CD workflow
├── src/
│   └── services/
│       └── agent.py                          # Agent 配置（Managed Identity）
├── Dockerfile                                # 后端容器配置
├── docker-compose.yml                        # 本地开发环境
├── .env                                      # 本地环境变量（不提交）
└── AZURE_DEPLOYMENT.md                       # 本文档
```

### 环境变量配置

**本地开发**（`.env` 文件）：
```env
AZURE_OPENAI_ENDPOINT=https://llmmvptest1.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-5-nano
```

**Azure Container App**（Environment variables）：
```
AZURE_OPENAI_ENDPOINT=https://llmmvptest1.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-5-nano
```

---

## 下一步

### 前端部署

可选方案：

1. **Vercel**（推荐 Next.js）
   - 免费
   - 自动 CI/CD
   - 访问：https://vercel.com

2. **Azure Static Web Apps**
   - 免费额度
   - 与 Azure 集成

3. **另一个 Container App**
   - 统一管理
   - 需要额外配置

---

## 参考资源

- [Azure Container Apps 文档](https://learn.microsoft.com/azure/container-apps/)
- [Managed Identity 文档](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/)
- [GitHub Actions 文档](https://docs.github.com/actions)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)

---

## 支持

如有问题，请查看：
- GitHub Issues: https://github.com/xxyckiki/maf-copilotkit-agent-template/issues
- Azure Container App 日志：Container App → **Monitoring → Log stream**

---

_最后更新：2025-12-01_
