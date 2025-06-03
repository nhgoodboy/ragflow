# 企业系统集成RAGFlow聊天窗口方案

本项目提供了在企业系统中为不同用户集成独立RAGFlow聊天窗口的完整解决方案。

## 核心概念

每个`shared_id`对应一个独立的聊天会话（session/conversation），不同用户需要使用不同的`shared_id`来实现独立的聊天环境。

## 方案架构

### 方案一：API动态创建会话（推荐）
- 为每个用户动态创建专属的聊天会话
- 通过RAGFlow API管理会话生命周期
- 支持会话持久化和历史记录

### 方案二：预创建会话池
- 预先为用户创建会话，按需分配
- 适合用户数量固定的场景

## 文件说明

### 前端文件
- `enterprise-chat-demo.html` - 完整的企业系统集成演示页面
- `user-chat-integration.js` - JavaScript集成工具类
- `embed-demo.html` - 原始的嵌入演示文件

### 后端文件
- `user_session_manager.py` - Python Flask后端会话管理服务
- `requirements.txt` - Python依赖包

## 快速开始

### 1. 准备工作

首先，您需要获取以下信息：
- **API密钥** (`apiKey`): 从RAGFlow控制台获取
- **聊天助手ID** (`chatId`): 您要使用的聊天助手的ID
- **认证令牌** (`auth`): 用于嵌入式聊天的认证令牌

### 2. 后端部署（可选）

如果您需要会话管理功能，可以部署后端服务：

```bash
# 安装依赖
pip install -r requirements.txt

# 配置RAGFlow连接信息
# 编辑 user_session_manager.py 中的 RAGFLOW_CONFIG

# 启动服务
python user_session_manager.py
```

### 3. 前端集成

#### 3.1 简单集成（直接HTML）

```html
<!DOCTYPE html>
<html>
<head>
    <title>用户聊天窗口</title>
</head>
<body>
    <div id="chat-container" style="width: 100%; height: 600px;"></div>
    
    <script src="user-chat-integration.js"></script>
    <script>
        const chatIntegration = new RAGFlowChatIntegration({
            baseURL: 'http://sz.safewaychina.cn:7080',
            apiKey: 'YOUR_API_KEY',
            chatId: 'YOUR_CHAT_ID',
            auth: 'YOUR_AUTH_TOKEN'
        });

        // 为当前用户嵌入聊天窗口
        async function initChat() {
            const userId = getCurrentUserId(); // 获取当前用户ID
            const userName = getCurrentUserName(); // 获取当前用户名
            
            await chatIntegration.embedUserChat('chat-container', userId, userName);
        }

        initChat();
    </script>
</body>
</html>
```

#### 3.2 与现有系统集成

```javascript
// 在您的企业系统中集成
class EnterpriseChatSystem {
    constructor(ragflowConfig) {
        this.chatIntegration = new RAGFlowChatIntegration(ragflowConfig);
        this.currentUser = null;
    }

    // 用户登录时初始化聊天
    async onUserLogin(user) {
        this.currentUser = user;
        try {
            await this.chatIntegration.embedUserChat(
                'chat-container', 
                user.id, 
                user.name
            );
            console.log(`用户 ${user.name} 聊天窗口已初始化`);
        } catch (error) {
            console.error('初始化聊天失败:', error);
        }
    }

    // 用户切换时更新聊天窗口
    async switchUser(newUser) {
        if (this.currentUser?.id !== newUser.id) {
            await this.onUserLogin(newUser);
        }
    }
}
```

## API接口说明

如果使用后端会话管理服务，可以调用以下API：

### 获取用户会话
```http
GET /api/users/{user_id}/session?user_name={user_name}
```

### 创建新会话
```http
POST /api/users/{user_id}/session
Content-Type: application/json

{
    "user_name": "用户名称"
}
```

### 获取用户列表
```http
GET /api/users
```

### 注册用户
```http
POST /api/users
Content-Type: application/json

{
    "user_id": "用户ID",
    "user_name": "用户名称",
    "department": "部门",
    "email": "邮箱"
}
```

## 实现策略

### 1. 用户会话隔离
每个用户都有独立的`shared_id`，确保：
- 聊天历史记录隔离
- 用户上下文独立
- 个性化体验

### 2. 会话管理
- **创建**: 用户首次访问时创建会话
- **复用**: 后续访问使用现有会话
- **清理**: 定期清理过期会话

### 3. 错误处理
- API调用失败时的降级策略
- 网络异常的重试机制
- 用户友好的错误提示

## 部署注意事项

### 1. 安全考虑
- API密钥不要在前端暴露
- 使用HTTPS传输
- 实施适当的认证和授权

### 2. 性能优化
- 会话复用减少API调用
- 合理的缓存策略
- 异步加载避免阻塞

### 3. 监控和日志
- 记录会话创建和使用情况
- 监控API调用成功率
- 跟踪用户使用模式

## 故障排除

### 常见问题

1. **会话创建失败**
   - 检查API密钥是否正确
   - 确认聊天助手ID有效
   - 验证网络连接

2. **聊天窗口无法加载**
   - 检查iframe src URL
   - 确认认证令牌有效
   - 查看浏览器控制台错误

3. **用户会话混乱**
   - 确保每个用户使用独立的shared_id
   - 检查用户ID的唯一性
   - 验证会话管理逻辑

### 调试工具

1. **健康检查**: `GET /api/health`
2. **配置验证**: `GET /api/config`
3. **浏览器开发者工具**: 查看网络请求和控制台日志

## 扩展功能

### 1. 多租户支持
为不同企业/组织提供隔离的聊天环境

### 2. 权限控制
基于用户角色限制聊天功能

### 3. 聊天记录导出
提供聊天历史的导出功能

### 4. 自定义主题
支持企业品牌定制

## 技术支持

如有问题，请检查：
1. RAGFlow服务是否正常运行
2. 网络连接是否正常
3. API密钥和权限是否正确
4. 浏览器是否支持iframe嵌入

## 更新日志

- v1.0.0: 初始版本，支持基本的用户会话管理
- 后续版本将增加更多企业级功能