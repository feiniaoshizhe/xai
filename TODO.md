# 项目待办事项清单

## 🔥 高优先级（生产必备）
---

## ⚡ 中优先级（提升开发体验）

## 💾 未来扩展（有数据库需求时）

### ✅ 4. 数据持久化层（已完成）
**Azure Cosmos DB for NoSQL**

**已添加：**
```
src/
├── db/             # Cosmos DB 连接配置
│   ├── __init__.py
│   └── cosmos.py
├── models/         # 数据模型（Pydantic）
│   ├── __init__.py
│   └── conversation.py
└── repositories/   # 数据访问层（CRUD）
    ├── __init__.py
    └── conversation_repo.py
```

**配置：**
- 认证方式：Azure Identity（ManagedIdentity + AzureCLI）
- 环境变量：`COSMOS_ENDPOINT`
- 数据库：`maf_db`
- 容器：`conversations`（分区键：`/session_id`）

---

## 🚫 不需要添加

### ❌ Terraform
**原因：**
- 项目规模较小
- 手动部署到 Azure Container Apps 更简单
- 不需要复杂的基础设施管理

**何时考虑：**
- 团队协作需要基础设施版本控制
- 需要管理多环境（dev/staging/prod）
- 服务数量超过 5 个


## 🎯 当前项目状态

**已完成：**
- ✅ FastAPI 应用结构
- ✅ 两个 agent（flight + chart）
- ✅ Workflow 实现
- ✅ Session 管理（内存）
- ✅ API 端点（AG-UI /copilotkit）
- ✅ Ruff 配置（代码格式化）
- ✅ 异常处理（exceptions.py）
- ✅ 单元测试（pytest - 21 tests passed）
- ✅ Dockerfile + docker-compose（前后端一键启动）
- ✅ MCP 工具集成（chart-generator）
- ✅ CopilotKit 前端（Next.js）
- ✅ OpenTelemetry 监控（Azure Monitor 集成）
- ✅ Application Insights（traces、logs、metrics）
- ✅ pre-commit 配置
- ✅ 数据持久化层（Azure Cosmos DB）

**待添加：**
- ⬜ 升级 azure-monitor-opentelemetry-exporter（等待微软修复兼容性）

---

## 📚 参考资源

**OpenTelemetry：**
- 官方文档：https://opentelemetry.io/docs/languages/python/
- FastAPI 集成：https://opentelemetry-python-contrib.readthedocs.io/

**CI/CD：**
- GitHub Actions 文档：https://docs.github.com/actions
- Azure Container Apps CI/CD：https://learn.microsoft.com/azure/container-apps/github-actions
- Azure 服务主体创建：https://learn.microsoft.com/cli/azure/create-an-azure-service-principal-azure-cli

---

_最后更新：2025-11-30_
