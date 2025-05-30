# RAGFlow 项目说明文档

<div align="center">
<img src="web/src/assets/logo-with-text.png" width="400" alt="RAGFlow Logo">

[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://github.com/infiniflow/ragflow/blob/main/LICENSE)
[![Version](https://img.shields.io/github/v/release/infiniflow/ragflow?color=blue&label=Latest%20Release)](https://github.com/infiniflow/ragflow/releases/latest)
[![Docker Pulls](https://img.shields.io/docker/pulls/infiniflow/ragflow?label=Docker%20Pulls&color=0db7ed&logo=docker&logoColor=white)](https://hub.docker.com/r/infiniflow/ragflow)
[![Demo](https://img.shields.io/badge/Online-Demo-4e6b99)](https://demo.ragflow.io)

</div>

## 📋 目录

- [项目概述](#项目概述)
- [核心功能](#核心功能)
- [技术架构](#技术架构)
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [安装部署](#安装部署)
- [使用指南](#使用指南)
- [开发指南](#开发指南)
- [API文档](#api文档)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 🚀 项目概述

### 什么是RAGFlow？

RAGFlow是一个基于深度文档理解的开源RAG（检索增强生成）引擎。它为各种规模的企业提供了简化的RAG工作流程，结合大语言模型（LLM）提供真实可靠的问答能力，并基于来自各种复杂格式数据的充分引用支持。

### 项目定位

- **🎯 企业级RAG解决方案**: 面向企业级应用的完整RAG系统
- **📚 深度文档理解**: 基于先进的文档解析和理解技术
- **🤖 多模态AI助手**: 集成AI Agent，支持代码执行和推理
- **🔧 开箱即用**: 提供完整的部署和使用方案
- **🌐 云原生架构**: 支持容器化部署和水平扩展

### 版本信息

- **当前版本**: v0.19.0
- **开发语言**: Python 3.10+
- **许可证**: Apache 2.0
- **维护状态**: 活跃开发中

## ✨ 核心功能

### 🔍 RAG核心功能

#### 智能文档处理
- **多格式支持**: PDF、DOCX、PPTX、TXT、Markdown等
- **深度解析**: 基于DeepDoc的文档布局分析和内容提取
- **智能分块**: 自动文档分段和结构化处理
- **多模态理解**: 支持文本、图像、表格混合内容

#### 高级检索能力
- **向量搜索**: 基于Infinity向量引擎的高性能相似性搜索
- **混合检索**: 结合关键词和语义检索
- **GraphRAG**: 图谱增强的检索生成
- **跨语言查询**: 支持多语言文档检索

#### 生成增强
- **多模型支持**: 集成OpenAI、Anthropic、阿里云等LLM提供商
- **上下文增强**: 基于检索结果的智能提示词构建
- **引用溯源**: 生成结果附带准确的文档引用
- **流式输出**: 实时生成和展示

### 🤖 AI Agent功能

#### 智能助手
- **多轮对话**: 支持上下文感知的连续对话
- **推理能力**: 结合互联网搜索的深度推理
- **代码执行**: 安全的Python/JavaScript代码执行环境
- **工具调用**: 支持多种外部工具和API集成

#### 工作流管理
- **可视化编排**: 基于画布的工作流设计
- **模板系统**: 预定义的Agent模板和组件
- **事件驱动**: 支持异步任务和事件处理

### 🌐 Web界面

#### 现代化UI
- **响应式设计**: 适配PC和移动端
- **直观操作**: 拖拽式文档上传和管理
- **实时预览**: 文档解析结果即时展示
- **可视化图表**: 支持知识图谱和数据可视化

#### 管理功能
- **用户管理**: 多用户支持和权限控制
- **项目管理**: 知识库和对话历史管理
- **监控仪表板**: 系统状态和性能监控

## 🏗️ 技术架构

### 整体架构

RAGFlow采用分层的微服务架构：

```
┌─────────────────────────────────────────────┐
│                前端层                        │
│  React + Umi + Ant Design + TypeScript     │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│                API网关                       │
│          Nginx反向代理                       │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│              应用服务层                       │
│ RAGFlow服务 │ Agent服务 │ MCP服务 │ 沙箱    │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│              核心业务层                       │
│ RAG引擎 │ DeepDoc │ GraphRAG │ LLM集成      │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│              数据存储层                       │
│ MySQL │ 向量DB │ Infinity │ MinIO │ Redis  │
└─────────────────────────────────────────────┘
```

### 核心组件

#### 后端服务
- **Flask Web框架**: 轻量级Web服务
- **Peewee ORM**: 数据库对象关系映射
- **NLTK**: 自然语言处理
- **OpenCV**: 计算机视觉处理
- **ONNX Runtime**: 模型推理引擎

#### 前端技术
- **React 18**: 现代化前端框架
- **Umi 4**: 企业级前端应用框架
- **Ant Design**: 企业级UI设计语言
- **Monaco Editor**: 代码编辑器
- **AntV G6**: 图形可视化

#### 数据存储
- **MySQL 8.0**: 关系型数据库
- **Elasticsearch/OpenSearch**: 全文搜索和向量存储
- **Infinity**: 高性能向量数据库
- **MinIO**: 对象存储服务
- **Redis/Valkey**: 缓存和会话存储

## 💻 系统要求

### 硬件要求

#### 最低配置
- **CPU**: 4核心
- **内存**: 16 GB RAM
- **存储**: 50 GB可用空间
- **网络**: 稳定的互联网连接

#### 推荐配置
- **CPU**: 8核心或更多
- **内存**: 32 GB RAM或更多
- **存储**: 100 GB SSD
- **GPU**: 可选，用于模型推理加速

### 软件要求

#### 必需软件
- **Docker**: >= 24.0.0
- **Docker Compose**: >= v2.26.1
- **操作系统**: Linux、macOS或Windows

#### 可选软件
- **gVisor**: 用于代码执行沙箱功能
- **Kubernetes**: 用于集群部署
- **Helm**: 用于Kubernetes包管理

## 🚀 快速开始

### 在线体验

访问 [https://demo.ragflow.io](https://demo.ragflow.io) 体验RAGFlow的功能。

### 一键部署

1. **克隆仓库**
```bash
git clone https://github.com/infiniflow/ragflow.git
cd ragflow
```

2. **启动服务**
```bash
docker compose up -d
```

3. **访问应用**
- 打开浏览器访问 `http://localhost`
- 默认管理员账户：admin / infiniflow

### Docker部署

```bash
# 设置系统参数
sudo sysctl -w vm.max_map_count=262144

# 拉取镜像
docker pull infiniflow/ragflow:v0.19.0

# 启动服务
docker compose up -d
```

## 📦 安装部署

### Docker Compose部署（推荐）

#### 1. 环境准备

```bash
# 检查Docker版本
docker --version
docker compose version

# 设置系统参数
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

#### 2. 下载项目

```bash
git clone https://github.com/infiniflow/ragflow.git
cd ragflow
```

#### 3. 配置环境

复制并编辑环境配置文件：

```bash
cp docker/.env.example docker/.env
```

编辑关键配置：

```env
# 基础配置
RAGFLOW_IMAGE=infiniflow/ragflow:v0.19.0
SVR_HTTP_PORT=80
TIMEZONE=Asia/Shanghai

# 数据库配置
MYSQL_PASSWORD=infiniflow
REDIS_PASSWORD=infiniflow

# 存储配置
MINIO_USER=infiniflow
MINIO_PASSWORD=infiniflow

# 向量数据库配置（三选一）
# Elasticsearch
ELASTIC_PASSWORD=infiniflow

# OpenSearch
OPENSEARCH_PASSWORD=infiniflow

# Infinity
INFINITY_THRIFT_PORT=23817
INFINITY_HTTP_PORT=23820
```

#### 4. 启动服务

```bash
cd docker

# 启动完整服务（包括Elasticsearch）
docker compose --profile elasticsearch up -d

# 或使用OpenSearch
docker compose --profile opensearch up -d

# 或使用Infinity（推荐）
docker compose --profile infinity up -d
```

#### 5. 验证部署

```bash
# 检查服务状态
docker compose ps

# 查看日志
docker compose logs ragflow-server

# 健康检查
curl http://localhost/health
```

### Kubernetes部署

#### 1. 使用Helm Chart

```bash
# 添加Helm仓库
helm repo add ragflow https://infiniflow.github.io/ragflow-helm

# 安装RAGFlow
helm install ragflow ragflow/ragflow \
  --namespace ragflow \
  --create-namespace \
  --values values.yaml
```

#### 2. 自定义配置

创建`values.yaml`文件：

```yaml
# 镜像配置
image:
  repository: infiniflow/ragflow
  tag: v0.19.0
  pullPolicy: IfNotPresent

# 服务配置
service:
  type: LoadBalancer
  port: 80

# 持久化存储
persistence:
  enabled: true
  storageClass: "standard"
  size: 100Gi

# 资源限制
resources:
  limits:
    cpu: 4
    memory: 8Gi
  requests:
    cpu: 2
    memory: 4Gi

# 数据库配置
mysql:
  enabled: true
  persistence:
    size: 50Gi

# 向量数据库
elasticsearch:
  enabled: true
  persistence:
    size: 100Gi
```

### 源码部署

#### 1. 环境准备

```bash
# 安装Python 3.10+
python3 --version

# 安装Node.js（用于前端构建）
node --version
npm --version
```

#### 2. 后端部署

```bash
# 安装依赖
pip install -r requirements.txt

# 或使用uv（推荐）
uv sync

# 配置环境变量
export RAGFLOW_ENV=development
export DATABASE_URL=mysql://user:password@localhost:3306/ragflow

# 启动后端服务
python api/ragflow_server.py
```

#### 3. 前端部署

```bash
cd web

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
```

#### 4. 数据库初始化

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE ragflow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行迁移
python api/db/migrations/init_db.py
```

## 📖 使用指南

### 创建知识库

#### 1. 登录系统

1. 访问RAGFlow Web界面
2. 使用管理员账户登录
3. 进入主控制台

#### 2. 创建知识库

1. 点击"新建知识库"
2. 输入知识库名称和描述
3. 选择解析模式：
   - **智能模式**: 自动识别文档类型和结构
   - **简单模式**: 基础文本提取
   - **手动模式**: 自定义解析规则

#### 3. 上传文档

```bash
# 支持的格式
- PDF文件
- Word文档（.docx）
- PowerPoint（.pptx）
- 文本文件（.txt）
- Markdown文件（.md）
- Excel文件（.xlsx）
```

#### 4. 配置解析参数

```json
{
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "enable_ocr": true,
  "enable_table_extraction": true,
  "language": "zh-CN"
}
```

### 配置问答机器人

#### 1. 创建机器人

1. 进入"机器人"页面
2. 点击"新建机器人"
3. 选择关联的知识库
4. 配置基础参数

#### 2. 高级配置

```yaml
# 模型配置
llm_model: "gpt-4"
temperature: 0.7
max_tokens: 2000

# 检索配置
retrieval_mode: "hybrid"  # keyword, semantic, hybrid
top_k: 10
similarity_threshold: 0.7

# 生成配置
include_citations: true
response_format: "detailed"  # brief, detailed, structured
```

#### 3. 系统提示词

```
你是一个专业的AI助手，基于提供的文档内容回答用户问题。

回答要求：
1. 准确性：只基于文档内容回答，不添加主观推测
2. 完整性：尽可能提供全面的信息
3. 引用：标注信息来源的文档和页码
4. 清晰性：使用结构化的格式组织答案

如果文档中没有相关信息，请明确说明。
```

### API使用示例

#### 文档上传API

```python
import requests
import json

# 上传文档
def upload_document(file_path, kb_id):
    url = "http://localhost/api/v1/document/upload"
    
    files = {'file': open(file_path, 'rb')}
    data = {
        'kb_id': kb_id,
        'parser_config': json.dumps({
            'chunk_size': 1000,
            'chunk_overlap': 200
        })
    }
    
    response = requests.post(url, files=files, data=data)
    return response.json()

# 使用示例
result = upload_document('/path/to/document.pdf', 'kb_123')
print(result)
```

#### 问答API

```python
# 发送问题
def ask_question(question, kb_id):
    url = "http://localhost/api/v1/chat/completion"
    
    payload = {
        'question': question,
        'kb_id': kb_id,
        'stream': False,
        'retrieval_config': {
            'top_k': 5,
            'similarity_threshold': 0.7
        }
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# 使用示例
answer = ask_question("什么是RAGFlow？", "kb_123")
print(answer['answer'])
print(answer['citations'])
```

#### 流式问答

```python
import json

def stream_chat(question, kb_id):
    url = "http://localhost/api/v1/chat/completion"
    
    payload = {
        'question': question,
        'kb_id': kb_id,
        'stream': True
    }
    
    response = requests.post(url, json=payload, stream=True)
    
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode('utf-8'))
            if 'delta' in data:
                print(data['delta'], end='', flush=True)
```

## 🛠️ 开发指南

### 开发环境搭建

#### 1. 克隆项目

```bash
git clone https://github.com/infiniflow/ragflow.git
cd ragflow
```

#### 2. 后端开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 设置环境变量
export FLASK_ENV=development
export FLASK_DEBUG=1
```

#### 3. 前端开发环境

```bash
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 数据库设置

```bash
# 启动开发数据库
docker run -d \
  --name ragflow-mysql-dev \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=ragflow_dev \
  -p 3306:3306 \
  mysql:8.0

# 运行数据库迁移
python api/db/migrations/init_db.py
```

### 项目结构

```
ragflow/
├── api/                    # 后端API服务
│   ├── apps/              # 应用模块
│   ├── db/                # 数据库层
│   ├── utils/             # 工具函数
│   └── ragflow_server.py  # 主服务器
├── rag/                   # RAG核心引擎
│   ├── app/               # RAG应用逻辑
│   ├── llm/               # LLM集成
│   ├── nlp/               # NLP处理
│   └── svr/               # RAG服务器
├── deepdoc/               # 文档处理模块
│   ├── parser/            # 文档解析器
│   └── vision/            # 视觉处理
├── agent/                 # AI Agent模块
│   ├── component/         # Agent组件
│   ├── templates/         # 模板系统
│   └── canvas.py          # 画布实现
├── web/                   # 前端应用
│   ├── src/               # 源代码
│   ├── public/            # 静态资源
│   └── package.json       # 依赖配置
├── docker/                # 容器化配置
│   ├── docker-compose.yml # 编排文件
│   └── .env.example       # 环境变量模板
└── docs/                  # 文档
```

### 核心模块开发

#### RAG引擎扩展

创建自定义检索器：

```python
# rag/retrieval/custom_retriever.py
from rag.retrieval.base import BaseRetriever

class CustomRetriever(BaseRetriever):
    def __init__(self, config):
        super().__init__(config)
        self.index_name = config.get('index_name')
    
    def retrieve(self, query, top_k=10):
        # 实现自定义检索逻辑
        results = self._search_index(query, top_k)
        return self._format_results(results)
    
    def _search_index(self, query, top_k):
        # 具体的搜索实现
        pass
    
    def _format_results(self, results):
        # 格式化搜索结果
        pass
```

#### 文档解析器扩展

创建自定义解析器：

```python
# deepdoc/parser/custom_parser.py
from deepdoc.parser.base import BaseParser

class CustomParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.supported_formats = ['.custom']
    
    def parse(self, file_path, **kwargs):
        # 实现自定义解析逻辑
        chunks = self._extract_content(file_path)
        return self._format_chunks(chunks)
    
    def _extract_content(self, file_path):
        # 内容提取逻辑
        pass
    
    def _format_chunks(self, chunks):
        # 格式化输出
        pass
```

#### Agent组件开发

创建自定义Agent组件：

```python
# agent/component/custom_component.py
from agent.component.base import BaseComponent

class CustomComponent(BaseComponent):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.component_type = "custom"
    
    async def execute(self, inputs):
        # 组件执行逻辑
        result = await self._process_inputs(inputs)
        return self._format_output(result)
    
    async def _process_inputs(self, inputs):
        # 处理输入数据
        pass
    
    def _format_output(self, result):
        # 格式化输出
        pass
```

### 前端组件开发

#### 创建新页面

```typescript
// web/src/pages/CustomPage/index.tsx
import React from 'react';
import { PageContainer } from '@ant-design/pro-components';
import { Card, Button } from 'antd';

const CustomPage: React.FC = () => {
  return (
    <PageContainer>
      <Card title="自定义页面">
        <Button type="primary">
          Hello RAGFlow
        </Button>
      </Card>
    </PageContainer>
  );
};

export default CustomPage;
```

#### 添加路由配置

```typescript
// web/.umirc.ts
export default {
  routes: [
    {
      path: '/custom',
      name: '自定义页面',
      component: './CustomPage',
    },
  ],
};
```

### 测试指南

#### 单元测试

```python
# tests/test_rag_engine.py
import pytest
from rag.engine import RAGEngine

class TestRAGEngine:
    def setup_method(self):
        self.engine = RAGEngine()
    
    def test_document_processing(self):
        # 测试文档处理
        result = self.engine.process_document('test.pdf')
        assert result is not None
        assert len(result.chunks) > 0
    
    def test_question_answering(self):
        # 测试问答功能
        answer = self.engine.answer_question('测试问题')
        assert answer.text is not None
        assert len(answer.citations) > 0
```

#### 集成测试

```python
# tests/test_api.py
import pytest
from api import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_upload_document(client):
    # 测试文档上传接口
    with open('test.pdf', 'rb') as f:
        response = client.post('/api/v1/document/upload', 
                             data={'file': f, 'kb_id': 'test'})
    assert response.status_code == 200

def test_chat_completion(client):
    # 测试聊天接口
    response = client.post('/api/v1/chat/completion',
                          json={'question': '测试问题', 'kb_id': 'test'})
    assert response.status_code == 200
```

#### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_rag_engine.py

# 生成覆盖率报告
pytest --cov=rag --cov-report=html
```

## 📚 API文档

### 认证

RAGFlow API使用Bearer Token认证：

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -X GET http://localhost/api/v1/user/info
```

### 核心API端点

#### 知识库管理

**创建知识库**
```http
POST /api/v1/knowledge-base

{
  "name": "我的知识库",
  "description": "知识库描述",
  "language": "zh-CN"
}
```

**获取知识库列表**
```http
GET /api/v1/knowledge-base?page=1&size=10
```

**更新知识库**
```http
PUT /api/v1/knowledge-base/{kb_id}

{
  "name": "更新后的名称",
  "description": "更新后的描述"
}
```

**删除知识库**
```http
DELETE /api/v1/knowledge-base/{kb_id}
```

#### 文档管理

**上传文档**
```http
POST /api/v1/document/upload
Content-Type: multipart/form-data

file: [文件]
kb_id: 知识库ID
parser_config: {
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "enable_ocr": true
}
```

**获取文档列表**
```http
GET /api/v1/document?kb_id={kb_id}&page=1&size=10
```

**获取文档详情**
```http
GET /api/v1/document/{doc_id}
```

**删除文档**
```http
DELETE /api/v1/document/{doc_id}
```

#### 聊天对话

**发送消息**
```http
POST /api/v1/chat/completion

{
  "question": "你的问题",
  "kb_id": "知识库ID",
  "stream": false,
  "retrieval_config": {
    "top_k": 5,
    "similarity_threshold": 0.7
  },
  "generation_config": {
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

**流式聊天**
```http
POST /api/v1/chat/completion
Content-Type: application/json

{
  "question": "你的问题",
  "kb_id": "知识库ID",
  "stream": true
}
```

**获取聊天历史**
```http
GET /api/v1/chat/history?conversation_id={conv_id}&page=1&size=20
```

#### Agent接口

**创建Agent**
```http
POST /api/v1/agent

{
  "name": "我的Agent",
  "description": "Agent描述",
  "canvas_config": {
    "components": [...],
    "connections": [...]
  }
}
```

**执行Agent**
```http
POST /api/v1/agent/{agent_id}/execute

{
  "inputs": {
    "query": "用户输入",
    "context": {...}
  }
}
```

### 错误处理

API使用标准HTTP状态码，错误响应格式：

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": {
      "field": "kb_id",
      "reason": "知识库ID不能为空"
    }
  }
}
```

常见错误码：

- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未授权访问
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `429 Too Many Requests`: 请求频率超限
- `500 Internal Server Error`: 服务器内部错误

## ❓ 常见问题

### 安装部署

**Q: Docker容器启动失败怎么办？**

A: 检查以下几个方面：
1. 确认Docker版本 >= 24.0.0
2. 检查系统内存是否充足（至少16GB）
3. 确认vm.max_map_count设置正确
4. 查看容器日志：`docker compose logs`

**Q: 如何配置GPU支持？**

A: 使用GPU版本的Docker Compose文件：
```bash
docker compose -f docker-compose-gpu.yml up -d
```

**Q: 数据库连接失败怎么解决？**

A: 检查数据库配置：
1. 确认MySQL容器正常运行
2. 检查环境变量中的数据库密码
3. 验证网络连通性

### 使用问题

**Q: 文档上传后无法检索到内容？**

A: 可能的原因和解决方案：
1. 等待文档处理完成（检查处理状态）
2. 检查文档格式是否支持
3. 调整检索参数（降低相似度阈值）
4. 查看文档解析日志

**Q: 回答质量不佳怎么优化？**

A: 尝试以下优化方法：
1. 调整文档分块大小
2. 优化系统提示词
3. 增加检索的文档数量
4. 使用更强的语言模型
5. 提高文档质量和相关性

**Q: 如何支持私有模型？**

A: 配置自定义模型端点：
```python
from rag.llm import LLMConfig

config = LLMConfig(
    provider="custom",
    base_url="http://your-model-server",
    api_key="your-api-key",
    model_name="your-model"
)
```

### 性能优化

**Q: 系统响应速度慢怎么优化？**

A: 性能优化建议：
1. **硬件优化**：增加内存和CPU核心数
2. **缓存优化**：配置Redis缓存
3. **索引优化**：调整向量数据库参数
4. **并发优化**：增加工作进程数
5. **网络优化**：使用CDN加速静态资源

**Q: 如何水平扩展系统？**

A: 扩展策略：
1. 使用Kubernetes部署
2. 配置负载均衡器
3. 分离读写数据库
4. 使用分布式缓存
5. 微服务拆分

### 开发相关

**Q: 如何添加新的文档格式支持？**

A: 实现自定义解析器：
1. 继承`BaseParser`类
2. 实现`parse`方法
3. 注册解析器到系统
4. 添加格式检测逻辑

**Q: 如何集成新的语言模型？**

A: 扩展LLM集成：
1. 实现`BaseLLM`接口
2. 添加模型配置
3. 实现API调用逻辑
4. 注册到模型工厂

## 🤝 贡献指南

### 贡献方式

我们欢迎各种形式的贡献：

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🧪 添加测试用例

### 开发流程

#### 1. 准备工作

```bash
# Fork项目到你的GitHub账户
# 克隆Fork的仓库
git clone https://github.com/YOUR_USERNAME/ragflow.git
cd ragflow

# 添加上游仓库
git remote add upstream https://github.com/infiniflow/ragflow.git

# 创建开发分支
git checkout -b feature/your-feature-name
```

#### 2. 开发规范

**代码风格**
- Python: 遵循PEP 8规范
- TypeScript: 使用Prettier格式化
- 提交信息: 使用约定式提交规范

**提交消息格式**
```
type(scope): description

[optional body]

[optional footer]
```

类型说明：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

#### 3. 提交Pull Request

```bash
# 确保代码最新
git fetch upstream
git rebase upstream/main

# 运行测试
pytest
npm test

# 提交更改
git add .
git commit -m "feat(rag): add custom retriever support"

# 推送到Fork仓库
git push origin feature/your-feature-name
```

然后在GitHub上创建Pull Request。

### 代码审查

所有提交都需要经过代码审查：

1. **自动检查**：CI/CD流水线验证
2. **人工审查**：维护者代码审查
3. **测试验证**：确保测试通过
4. **文档更新**：必要时更新文档

### 问题反馈

#### 报告Bug

使用Bug报告模板：

```markdown
## Bug描述
简要描述遇到的问题

## 复现步骤
1. 执行操作A
2. 执行操作B
3. 观察到错误

## 期望行为
描述期望的正确行为

## 环境信息
- 操作系统：
- Docker版本：
- RAGFlow版本：

## 附加信息
相关日志、截图等
```

#### 功能建议

使用功能请求模板：

```markdown
## 功能描述
描述希望添加的功能

## 使用场景
说明为什么需要这个功能

## 期望实现
描述理想的实现方式

## 替代方案
描述考虑过的其他解决方案
```

## 📄 许可证

本项目基于 [Apache License 2.0](https://github.com/infiniflow/ragflow/blob/main/LICENSE) 开源协议。

### 许可证要点

- ✅ 商业使用
- ✅ 分发
- ✅ 修改
- ✅ 专利使用
- ✅ 私人使用

### 限制条件

- ⚠️ 需要包含许可证和版权声明
- ⚠️ 需要声明对原始代码的更改
- ❌ 不提供责任担保
- ❌ 不提供商标权

### 贡献协议

通过向本项目提交贡献，您同意：

1. 您的贡献将在Apache 2.0许可证下发布
2. 您拥有贡献内容的知识产权
3. 您的贡献不侵犯第三方权利

---

## 📞 联系我们

- **官方网站**: [https://ragflow.io](https://ragflow.io)
- **在线演示**: [https://demo.ragflow.io](https://demo.ragflow.io)
- **GitHub**: [https://github.com/infiniflow/ragflow](https://github.com/infiniflow/ragflow)
- **Discord**: [加入社区讨论](https://discord.gg/NjYzJD3GM3)
- **Twitter**: [@infiniflowai](https://twitter.com/infiniflowai)

### 技术支持

- **文档中心**: [https://ragflow.io/docs](https://ragflow.io/docs)
- **GitHub Issues**: 报告问题和功能请求
- **社区论坛**: 技术讨论和经验分享

---

*感谢您对RAGFlow项目的关注和支持！我们期待您的参与和贡献。* 