# RAGFlow 项目架构图

## 1. 系统概览架构

```mermaid
graph TB
    %% 用户界面层
    subgraph "前端层 Frontend Layer"
        WebUI[Web界面<br/>React + Umi + Ant Design]
        API_Gateway[API网关<br/>Nginx反向代理]
    end
    
    %% 应用服务层
    subgraph "应用服务层 Application Layer"
        RagFlow_Server[RAGFlow主服务<br/>Flask + Python]
        Agent_Service[AI Agent服务<br/>多模态AI助手]
        MCP_Server[MCP服务器<br/>模型控制协议]
        Sandbox[代码执行沙箱<br/>安全代码执行环境]
    end
    
    %% 核心业务层
    subgraph "核心业务层 Core Business Layer"
        RAG_Engine[RAG引擎<br/>检索增强生成]
        DeepDoc[DeepDoc<br/>深度文档理解]
        GraphRAG[GraphRAG<br/>图谱RAG]
        LLM_Integration[LLM集成层<br/>多模型支持]
        NLP_Engine[NLP处理引擎<br/>自然语言处理]
    end
    
    %% 数据存储层
    subgraph "数据存储层 Data Layer"
        MySQL[(MySQL数据库<br/>结构化数据)]
        VectorDB[(向量数据库<br/>Elasticsearch/OpenSearch)]
        Infinity[(Infinity向量引擎<br/>高性能向量搜索)]
        MinIO[(MinIO对象存储<br/>文件存储)]
        Redis[(Redis缓存<br/>会话和缓存)]
    end
    
    %% 外部集成
    subgraph "外部集成 External Integrations"
        LLM_Providers[LLM提供商<br/>OpenAI/Anthropic/阿里云等]
        Internet_Search[互联网搜索<br/>Tavily/DuckDuckGo]
        Cloud_Storage[云存储<br/>Azure/AWS S3]
    end
    
    %% 连接关系
    WebUI --> API_Gateway
    API_Gateway --> RagFlow_Server
    RagFlow_Server --> Agent_Service
    RagFlow_Server --> MCP_Server
    Agent_Service --> Sandbox
    
    RagFlow_Server --> RAG_Engine
    RagFlow_Server --> DeepDoc
    RAG_Engine --> GraphRAG
    RAG_Engine --> LLM_Integration
    DeepDoc --> NLP_Engine
    
    RAG_Engine --> VectorDB
    RAG_Engine --> Infinity
    RagFlow_Server --> MySQL
    RagFlow_Server --> MinIO
    RagFlow_Server --> Redis
    
    LLM_Integration --> LLM_Providers
    Agent_Service --> Internet_Search
    MinIO --> Cloud_Storage
    
    %% 样式定义
    classDef frontend fill:#e1f5fe
    classDef application fill:#f3e5f5
    classDef business fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef external fill:#fce4ec
    
    class WebUI,API_Gateway frontend
    class RagFlow_Server,Agent_Service,MCP_Server,Sandbox application
    class RAG_Engine,DeepDoc,GraphRAG,LLM_Integration,NLP_Engine business
    class MySQL,VectorDB,Infinity,MinIO,Redis data
    class LLM_Providers,Internet_Search,Cloud_Storage external
```

## 2. 核心模块架构

```mermaid
graph TD
    %% RAG核心模块
    subgraph "RAG核心模块"
        RAG_SVR[RAG服务器<br/>rag/svr/]
        RAG_App[RAG应用<br/>rag/app/]
        RAG_Utils[RAG工具<br/>rag/utils/]
        LLM_Module[LLM模块<br/>rag/llm/]
        NLP_Module[NLP模块<br/>rag/nlp/]
        Prompts[提示词管理<br/>rag/prompts.py]
        Raptor[Raptor算法<br/>rag/raptor.py]
    end
    
    %% API服务模块
    subgraph "API服务模块"
        API_Apps[API应用<br/>api/apps/]
        API_Utils[API工具<br/>api/utils/]
        API_DB[数据库层<br/>api/db/]
        Server[RAGFlow服务器<br/>api/ragflow_server.py]
        Validation[数据验证<br/>api/validation.py]
    end
    
    %% 文档处理模块
    subgraph "文档处理模块"
        Doc_Parser[文档解析器<br/>deepdoc/parser/]
        Doc_Vision[视觉处理<br/>deepdoc/vision/]
    end
    
    %% Agent模块
    subgraph "Agent模块"
        Agent_Component[Agent组件<br/>agent/component/]
        Agent_Canvas[Agent画布<br/>agent/canvas.py]
        Agent_Templates[Agent模板<br/>agent/templates/]
    end
    
    %% 前端模块
    subgraph "前端模块"
        Web_Src[源码<br/>web/src/]
        Web_Public[静态资源<br/>web/public/]
        Web_Config[配置<br/>web配置文件]
    end
    
    %% 模块间关系
    RAG_SVR --> API_Apps
    API_Apps --> API_DB
    Server --> RAG_App
    Agent_Component --> RAG_Utils
    Doc_Parser --> NLP_Module
    Web_Src --> Server
```

## 3. 技术栈架构

```mermaid
graph LR
    %% 前端技术栈
    subgraph "前端技术栈"
        React[React 18]
        Umi[Umi 4]
        AntD[Ant Design]
        TypeScript[TypeScript]
        TailwindCSS[Tailwind CSS]
        Monaco[Monaco Editor]
        G6[AntV G6图形]
    end
    
    %% 后端技术栈
    subgraph "后端技术栈"
        Python[Python 3.10+]
        Flask[Flask Web框架]
        Peewee[Peewee ORM]
        NLTK[NLTK自然语言处理]
        OpenCV[OpenCV计算机视觉]
        NumPy[NumPy科学计算]
        Pandas[Pandas数据处理]
    end
    
    %% AI/ML技术栈
    subgraph "AI/ML技术栈"
        Transformers[Hugging Face Transformers]
        ONNX[ONNX Runtime]
        Infinity_SDK[Infinity SDK]
        LangChain[LangChain集成]
        MultiModal[多模态模型]
    end
    
    %% 数据库技术栈
    subgraph "数据存储技术栈"
        MySQL_8[MySQL 8.0]
        ES[Elasticsearch 8.x]
        OpenSearch[OpenSearch]
        Redis_Cache[Redis/Valkey]
        MinIO_Storage[MinIO对象存储]
        Infinity_Vector[Infinity向量数据库]
    end
    
    %% 部署技术栈
    subgraph "部署技术栈"
        Docker[Docker容器]
        DockerCompose[Docker Compose]
        Nginx[Nginx反向代理]
        gVisor[gVisor安全沙箱]
        Helm[Helm Charts]
    end
    
    %% 技术栈关系
    React --> TypeScript
    Umi --> AntD
    Python --> Flask
    Flask --> Peewee
    Transformers --> ONNX
    Docker --> DockerCompose
    Nginx --> gVisor
```

## 4. 部署架构图

```mermaid
graph TB
    %% 负载均衡层
    subgraph "负载均衡层"
        LB[负载均衡器<br/>Nginx]
    end
    
    %% 容器编排层
    subgraph "Docker容器集群"
        subgraph "主应用容器"
            RagFlow_Container[ragflow-server<br/>端口:9380,80,443]
            Executor_Container[ragflow-executor<br/>任务执行器]
        end
        
        subgraph "数据库容器"
            MySQL_Container[ragflow-mysql<br/>端口:3306]
            Redis_Container[ragflow-redis<br/>端口:6379]
        end
        
        subgraph "存储容器"
            MinIO_Container[ragflow-minio<br/>端口:9000,9001]
        end
        
        subgraph "搜索引擎容器"
            ES_Container[ragflow-es-01<br/>端口:9200]
            OS_Container[ragflow-opensearch-01<br/>端口:9201]
            Infinity_Container[ragflow-infinity<br/>端口:23817,23820]
        end
        
        subgraph "安全沙箱"
            Sandbox_Container[ragflow-sandbox-executor-manager<br/>端口:9385]
        end
    end
    
    %% 持久化存储
    subgraph "数据持久化"
        MySQL_Volume[(mysql_data)]
        Redis_Volume[(redis_data)]
        MinIO_Volume[(minio_data)]
        ES_Volume[(esdata01)]
        OS_Volume[(osdata01)]
        Infinity_Volume[(infinity_data)]
        Logs_Volume[(ragflow-logs)]
    end
    
    %% 网络
    subgraph "Docker网络"
        RagFlow_Network[ragflow bridge network]
    end
    
    %% 连接关系
    LB --> RagFlow_Container
    RagFlow_Container --> MySQL_Container
    RagFlow_Container --> Redis_Container
    RagFlow_Container --> MinIO_Container
    RagFlow_Container --> ES_Container
    RagFlow_Container --> OS_Container
    RagFlow_Container --> Infinity_Container
    RagFlow_Container --> Sandbox_Container
    
    %% 数据持久化连接
    MySQL_Container --> MySQL_Volume
    Redis_Container --> Redis_Volume
    MinIO_Container --> MinIO_Volume
    ES_Container --> ES_Volume
    OS_Container --> OS_Volume
    Infinity_Container --> Infinity_Volume
    RagFlow_Container --> Logs_Volume
    
    %% 网络连接
    RagFlow_Container -.-> RagFlow_Network
    MySQL_Container -.-> RagFlow_Network
    Redis_Container -.-> RagFlow_Network
    MinIO_Container -.-> RagFlow_Network
    ES_Container -.-> RagFlow_Network
    OS_Container -.-> RagFlow_Network
    Infinity_Container -.-> RagFlow_Network
    Sandbox_Container -.-> RagFlow_Network
```

## 5. 数据流架构

```mermaid
sequenceDiagram
    participant User as 用户
    participant WebUI as Web界面
    participant API as API网关
    participant RAG as RAG引擎
    participant DeepDoc as 文档处理
    participant Vector as 向量数据库
    participant LLM as 大语言模型
    participant DB as 数据库
    
    User->>WebUI: 上传文档/提问
    WebUI->>API: HTTP请求
    API->>RAG: 处理请求
    
    alt 文档上传流程
        RAG->>DeepDoc: 文档解析
        DeepDoc->>DeepDoc: 文档分块
        DeepDoc->>Vector: 向量化存储
        Vector->>DB: 元数据存储
    else 问答流程
        RAG->>Vector: 相似性搜索
        Vector->>RAG: 相关文档片段
        RAG->>LLM: 增强提示词
        LLM->>RAG: 生成回答
        RAG->>DB: 记录对话历史
    end
    
    RAG->>API: 返回结果
    API->>WebUI: 响应数据
    WebUI->>User: 显示结果
```

## 6. 安全架构

```mermaid
graph TD
    %% 安全边界
    subgraph "安全边界"
        WAF[Web应用防火墙]
        SSL[SSL/TLS加密]
        Auth[身份认证]
        RBAC[角色权限控制]
    end
    
    %% 容器安全
    subgraph "容器安全"
        gVisor_Sandbox[gVisor沙箱]
        Docker_Security[Docker安全配置]
        Network_Isolation[网络隔离]
        Resource_Limit[资源限制]
    end
    
    %% 数据安全
    subgraph "数据安全"
        Data_Encryption[数据加密]
        Access_Control[访问控制]
        Audit_Log[审计日志]
        Backup[数据备份]
    end
    
    %% AI安全
    subgraph "AI安全"
        Prompt_Injection_Defense[提示词注入防护]
        Content_Filter[内容过滤]
        Model_Security[模型安全]
        Privacy_Protection[隐私保护]
    end
    
    %% 安全流程
    WAF --> SSL
    SSL --> Auth
    Auth --> RBAC
    RBAC --> gVisor_Sandbox
    gVisor_Sandbox --> Data_Encryption
    Data_Encryption --> Prompt_Injection_Defense
```

## 7. 系统特性说明

### 核心特性
- **深度文档理解**: 基于DeepDoc的文档解析和理解能力
- **多模态RAG**: 支持文本、图像、表格等多种数据类型
- **AI Agent**: 智能助手功能，支持推理和代码执行
- **GraphRAG**: 图谱增强的检索生成
- **多模型支持**: 集成多种LLM提供商

### 技术特色
- **高性能向量搜索**: 基于Infinity向量引擎
- **安全代码执行**: gVisor沙箱环境
- **云原生部署**: Docker容器化部署
- **水平扩展**: 微服务架构支持
- **多语言支持**: 国际化界面

### 部署选项
- **单机部署**: Docker Compose一键部署
- **集群部署**: Kubernetes + Helm Charts
- **云部署**: 支持各大云平台
- **GPU加速**: 可选GPU支持加速推理

---

*此架构图基于RAGFlow v0.19.0版本分析生成，展示了完整的系统架构、技术栈、部署方式和数据流程。* 