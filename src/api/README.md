# API 架构说明

## 为什么没有传统的 REST API？

本项目使用 **AG-UI (Agent Framework UI) + Agent Framework** 架构，前后端通过 **AG-UI 协议**通信，而不是传统的 REST API。

### 架构对比

#### 传统 REST API 架构（未使用）
```
前端 → REST API (/api/chat) → 手动调用 LLM → 手动保存到数据库
     ↓ 需要定义
     - API 路由 (FastAPI Router)
     - 数据模型 (Pydantic Models)
     - 仓储层 (Repository Pattern)
```

#### 当前 AG-UI 架构（正在使用）✅
```
前端 CopilotKit → AG-UI 协议 (/copilotkit) → Agent Framework
                                                ↓ 自动处理
                                           - LLM 调用
                                           - 对话管理
                                           - 持久化存储
```

### 技术栈

**前端**：
- CopilotKit - 聊天 UI 组件
- AG-UI Client - Agent Framework 前端集成
- Next.js - React 框架

**后端**：
- Agent Framework - AI Agent 框架
- AG-UI Server - Agent Framework FastAPI 集成
- CosmosChatMessageStore - 自动持久化到 Cosmos DB

**连接协议**：
- AG-UI Protocol（基于 WebSocket/SSE）

---

## 为什么不需要定义 Models 和 Repositories？

### Agent Framework 自动处理持久化

Agent Framework 提供了 **ChatMessageStore** 机制，自动管理对话历史的存储和检索。

#### 如果使用 Agent Framework（当前方案）✅

```python
# src/services/agent.py

from agent_framework import ChatAgent
from ..db import CosmosChatMessageStore

agent = ChatAgent(
    chat_message_store_factory=lambda: CosmosChatMessageStore(),
    # 👆 框架自动调用，无需手动保存
)

# 对话自动持久化，无需额外代码
response = await agent.run("你好", thread=thread)  # ✅ 自动保存到 Cosmos DB
```

**不需要**：
- ❌ `models/conversation.py` - 框架内置 ChatMessage 模型
- ❌ `repositories/conversation_repo.py` - 框架自动调用 ChatMessageStore
- ❌ `api/conversations.py` - 不需要手动 CRUD API

---

#### 如果不使用 Agent Framework（需要手动实现）

```python
# 手动实现的聊天机器人

from openai import AzureOpenAI
from .models import Conversation  # 👈 需要定义数据模型
from .repositories import ConversationRepository  # 👈 需要定义仓储层

class ManualChatbot:
    async def chat(self, user_message: str, session_id: str):
        # 1. 手动从数据库获取历史
        repo = ConversationRepository()  # 👈 需要
        conversation = repo.get_or_create(session_id)

        # 2. 手动添加用户消息
        conversation.add_message("user", user_message)
        repo.update(conversation)  # 👈 手动保存

        # 3. 手动调用 LLM
        client = AzureOpenAI()
        response = client.chat.completions.create(
            messages=conversation.messages
        )

        # 4. 手动保存 AI 回复
        conversation.add_message("assistant", response.content)
        repo.update(conversation)  # 👈 手动保存

        return response
```

**需要**：
- ✅ `models/conversation.py` - 定义 Conversation 和 Message 数据模型
- ✅ `repositories/conversation_repo.py` - 实现 CRUD 操作
- ✅ `api/conversations.py` - 提供 REST API 端点

---

## 实际实现

### 当前项目的持久化实现

📁 `src/db/cosmos_chat_store.py` - CosmosChatMessageStore

```python
class CosmosChatMessageStore:
    """实现 Agent Framework 的 ChatMessageStore 协议"""

    async def add_messages(self, messages: Sequence[ChatMessage]) -> None:
        """自动保存消息到 Cosmos DB"""
        # 框架自动调用此方法

    async def list_messages(self) -> list[ChatMessage]:
        """从 Cosmos DB 获取历史消息"""
        # 框架自动调用此方法
```

### 端点说明

| 端点 | 用途 | 协议 |
|------|------|------|
| `/copilotkit` | Agent Framework 通信 | AG-UI Protocol |
| `/docs` | FastAPI 自动文档 | HTTP |
| `/` | API 根路径 | HTTP |

---

## 总结

### 使用 Agent Framework 的优势

✅ **无需手动编写**：
- API 路由和端点
- 数据模型（Conversation, Message）
- 仓储层（CRUD 操作）
- 对话状态管理

✅ **框架自动处理**：
- LLM 调用和响应流式传输
- 对话历史持久化
- 多轮对话上下文管理
- 工具（Tools）调用和结果处理

✅ **代码更简洁**：
- 少 ~300 行模板代码
- 更专注于业务逻辑（Agent 指令、工具定义）
- 更易维护和扩展

---

---

## 如果需要添加传统 REST API

虽然当前项目使用 AG-UI 架构，但某些场景下可能需要额外的 REST API（如管理后台、数据分析）。

### 场景示例

#### 场景 1: 管理后台查看所有对话

```python
# src/api/conversations.py

from fastapi import APIRouter, HTTPException
from azure.cosmos import ContainerProxy
from ..db import get_container

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.get("/{session_id}")
async def get_conversations(session_id: str):
    """获取某个会话的所有对话记录"""
    container = get_container()

    # 查询该 session_id 的所有文档
    query = "SELECT * FROM c WHERE c.session_id = @session_id ORDER BY c.updated_at DESC"
    items = container.query_items(
        query=query,
        parameters=[{"name": "@session_id", "value": session_id}],
        partition_key=session_id
    )

    return list(items)

@router.delete("/{session_id}/{thread_id}")
async def delete_conversation(session_id: str, thread_id: str):
    """删除特定对话"""
    container = get_container()
    container.delete_item(item=thread_id, partition_key=session_id)
    return {"deleted": True}
```

#### 场景 2: 数据统计和分析

```python
# src/api/analytics.py

from fastapi import APIRouter
from ..db import get_container

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/stats")
async def get_stats():
    """获取对话统计数据"""
    container = get_container()

    # 统计总对话数
    query = "SELECT COUNT(1) as total FROM c"
    result = list(container.query_items(query=query))

    return {
        "total_conversations": result[0]["total"] if result else 0,
        # 更多统计数据...
    }
```

### 集成到主应用

```python
# main.py

from src.api.conversations import router as conversations_router
from src.api.analytics import router as analytics_router

# 注册路由
app.include_router(conversations_router)
app.include_router(analytics_router)
```

### 何时需要定义 Models 和 Repositories

如果你需要更复杂的业务逻辑（如验证、转换、多表关联），建议定义：

#### 1. 数据模型（Models）

```python
# src/models/conversation.py

from pydantic import BaseModel
from datetime import datetime

class ConversationSummary(BaseModel):
    """对话摘要模型"""
    thread_id: str
    session_id: str
    message_count: int
    first_message: str
    last_updated: datetime

class ConversationAnalytics(BaseModel):
    """对话分析模型"""
    avg_messages_per_conversation: float
    most_active_sessions: list[str]
```

#### 2. 仓储层（Repositories）

```python
# src/repositories/conversation_repo.py

from azure.cosmos import ContainerProxy
from ..db import get_container
from ..models import ConversationSummary

class ConversationRepository:
    """对话数据访问层"""

    def __init__(self):
        self.container = get_container()

    def get_summary(self, session_id: str) -> list[ConversationSummary]:
        """获取对话摘要列表"""
        query = """
        SELECT
            c.thread_id,
            c.session_id,
            ARRAY_LENGTH(c.messages) as message_count,
            c.messages[0].content as first_message,
            c.updated_at as last_updated
        FROM c
        WHERE c.session_id = @session_id
        """
        items = self.container.query_items(
            query=query,
            parameters=[{"name": "@session_id", "value": session_id}],
            partition_key=session_id
        )
        return [ConversationSummary(**item) for item in items]

    def get_analytics(self) -> dict:
        """获取分析数据（跨分区查询）"""
        # 实现复杂的分析逻辑
        pass
```

---

## 当前目录结构

```
src/
├── api/                    # 保留用于将来扩展 REST API
│   └── README.md          # 本文档
├── db/                    # 数据库连接和存储
│   ├── cosmos.py          # Cosmos DB 连接
│   └── cosmos_chat_store.py  # Agent Framework 持久化
├── schemas/               # Pydantic 数据验证模型
│   └── flight.py
├── services/              # 业务逻辑层
│   ├── agent.py           # AI Agent 定义
│   ├── tools.py           # Agent 工具
│   └── workflow.py        # 工作流定义
└── exceptions.py          # 异常处理
```

**说明**：
- `api/` 目录**保留**但暂时为空，方便将来添加管理 API
- 当前对话功能通过 `/copilotkit` 端点（AG-UI 协议）实现
- 如需管理功能（查询、删除、统计），在此目录添加 REST API

---

## 参考文档

- [Microsoft Agent Framework 官方文档](https://learn.microsoft.com/en-us/agent-framework/)
- [Agent Memory & Persistence](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-memory)
- [CopilotKit 文档](https://docs.copilotkit.ai/)
