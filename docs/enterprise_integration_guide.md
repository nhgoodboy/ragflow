# RAGFlow 企业系统集成指南

## 概述

本指南详细介绍如何将 RAGFlow 知识库系统集成到企业现有系统中，实现单点登录（SSO）和基于角色的权限控制。

## 集成架构

```
企业主系统 → JWT Token → RAGFlow → 权限验证 → 功能访问
     ↓                      ↓              ↓
  用户登录              自动登录        角色映射
     ↓                      ↓              ↓  
  生成Token            创建用户        权限分配
```

## 配置说明

### 1. 后端配置

#### 1.1 修改配置文件

在 RAGFlow 的配置文件中添加企业认证配置：

```yaml
# conf/service_conf.yaml
enterprise_auth:
  enabled: true
  jwt_secret: "your-jwt-secret-key"  # 与企业系统共享的密钥
  role_mapping:
    enterprise_admin: "admin"         # 企业管理员 → RAGFlow 管理员
    enterprise_user: "normal"         # 企业用户 → RAGFlow 普通用户
  token_expiry: 3600                 # Token 有效期（秒）
  allowed_domains:                   # 允许的IP/域名白名单（可选）
    - "192.168.1.0/24"
    - "10.0.0.0/8"
  auto_create_user: true             # 是否自动创建用户
```

#### 1.2 环境变量

```bash
# 启用企业认证
export ENTERPRISE_AUTH_ENABLED=true
export ENTERPRISE_JWT_SECRET="your-jwt-secret-key"
```

### 2. 前端配置

#### 2.1 企业Token处理

前端需要处理企业系统传递的Token：

```typescript
// 在企业系统中跳转到RAGFlow
const redirectToRAGFlow = (token: string) => {
  const ragflowUrl = `https://ragflow.company.com?enterprise_token=${token}`;
  window.open(ragflowUrl, '_blank');
};
```

## JWT Token规范

### Token结构

企业系统生成的JWT Token必须包含以下字段：

```json
{
  "user_id": "enterprise_user_123",      // 企业系统用户ID（必需）
  "email": "user@company.com",           // 用户邮箱（必需）
  "nickname": "张三",                     // 用户昵称（必需）
  "role": "enterprise_admin",            // 企业角色（必需）
  "tenant_id": "company_tenant_001",     // 租户ID（必需）
  "iat": 1640995200,                     // 签发时间
  "exp": 1640998800,                     // 过期时间
  "jti": "unique_token_id"               // Token唯一标识（可选，用于防重放）
}
```

### 生成Token示例

#### Python示例

```python
import jwt
import time

def generate_enterprise_token(user_id, email, nickname, role, tenant_id, secret_key):
    """生成企业认证Token"""
    current_time = int(time.time())
    
    payload = {
        "user_id": user_id,
        "email": email,
        "nickname": nickname,
        "role": role,
        "tenant_id": tenant_id,
        "iat": current_time,
        "exp": current_time + 3600,  # 1小时后过期
        "jti": f"{user_id}_{current_time}"  # 防重放攻击
    }
    
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

# 使用示例
token = generate_enterprise_token(
    user_id="emp_001",
    email="admin@company.com", 
    nickname="管理员",
    role="enterprise_admin",
    tenant_id="company_001",
    secret_key="your-shared-secret"
)
```

#### Java示例

```java
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

public class EnterpriseTokenGenerator {
    
    public static String generateToken(String userId, String email, 
                                     String nickname, String role, 
                                     String tenantId, String secretKey) {
        
        long currentTimeMillis = System.currentTimeMillis();
        Date now = new Date(currentTimeMillis);
        Date expiration = new Date(currentTimeMillis + 3600000); // 1小时
        
        Map<String, Object> claims = new HashMap<>();
        claims.put("user_id", userId);
        claims.put("email", email);
        claims.put("nickname", nickname);
        claims.put("role", role);
        claims.put("tenant_id", tenantId);
        claims.put("jti", userId + "_" + (currentTimeMillis / 1000));
        
        return Jwts.builder()
                .setClaims(claims)
                .setIssuedAt(now)
                .setExpiration(expiration)
                .signWith(SignatureAlgorithm.HS256, secretKey)
                .compact();
    }
}
```

#### JavaScript示例

```javascript
const jwt = require('jsonwebtoken');

function generateEnterpriseToken(userId, email, nickname, role, tenantId, secretKey) {
    const currentTime = Math.floor(Date.now() / 1000);
    
    const payload = {
        user_id: userId,
        email: email,
        nickname: nickname,
        role: role,
        tenant_id: tenantId,
        iat: currentTime,
        exp: currentTime + 3600, // 1小时后过期
        jti: `${userId}_${currentTime}`
    };
    
    return jwt.sign(payload, secretKey, { algorithm: 'HS256' });
}

// 使用示例
const token = generateEnterpriseToken(
    'emp_001',
    'admin@company.com',
    '管理员', 
    'enterprise_admin',
    'company_001',
    'your-shared-secret'
);
```

## API接口

### 1. 企业登录

**接口地址**: `POST /v1/user/enterprise/login`

**请求参数**:
```json
{
  "enterprise_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "id": "user_uuid",
    "nickname": "张三",
    "email": "user@company.com",
    "access_token": "ragflow_access_token",
    "permissions": {
      "can_manage_knowledge": true,
      "can_chat": true,
      "can_manage_users": false,
      "can_access_system": false
    },
    "login_channel": "enterprise"
  },
  "message": "Enterprise login successful"
}
```

### 2. 验证企业用户

**接口地址**: `GET /v1/user/enterprise/verify`

**请求头**:
```
Authorization: Bearer <ragflow_access_token>
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "user_id": "user_uuid",
    "enterprise_user_id": "enterprise_user_123",
    "email": "user@company.com",
    "permissions": {
      "can_manage_knowledge": true,
      "can_chat": true,
      "can_manage_users": false,
      "can_access_system": false
    },
    "is_enterprise_user": true
  }
}
```

### 3. 获取用户权限

**接口地址**: `GET /v1/user/enterprise/permissions`

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "can_manage_knowledge": true,
    "can_chat": true,
    "can_manage_users": false,
    "can_access_system": false
  }
}
```

## 权限说明

### 权限类型

| 权限 | 说明 | 对应功能 |
|------|------|----------|
| `can_manage_knowledge` | 知识库管理权限 | 创建、编辑、删除知识库和文档 |
| `can_chat` | 聊天权限 | 使用问答功能 |
| `can_manage_users` | 用户管理权限 | 管理团队成员 |
| `can_access_system` | 系统权限 | 访问系统设置和高级功能 |

### 角色映射

| 企业角色 | RAGFlow角色 | 权限 |
|----------|-------------|------|
| `enterprise_admin` | ADMIN | 知识库管理 + 聊天 |
| `enterprise_user` | NORMAL | 仅聊天 |

可根据需要在配置文件中自定义角色映射。

## 前端集成示例

### 1. 权限保护组件

```tsx
import { PermissionGuard } from '@/components/enterprise-permission-guard';

// 使用权限保护
<PermissionGuard permission="can_manage_knowledge">
  <KnowledgeManagementPanel />
</PermissionGuard>

// 多权限保护
<MultiPermissionGuard 
  permissions={['can_manage_knowledge', 'can_access_system']}
  requireAll={false}
>
  <FileManagerPanel />
</MultiPermissionGuard>
```

### 2. 菜单权限过滤

```tsx
import { useEnterprisePermissions } from '@/hooks/enterprise-hooks';
import { filterAccessibleMenus } from '@/utils/permission-routes';

const Navigation = () => {
  const { permissions } = useEnterprisePermissions();
  
  const filteredMenus = filterAccessibleMenus(originalMenus, permissions);
  
  return <Menu items={filteredMenus} />;
};
```

## 安全特性

### 1. Token安全验证

- **时效性验证**: 检查Token是否过期
- **防重放攻击**: 通过JTI字段防止Token重复使用
- **IP白名单**: 限制来源IP地址
- **速率限制**: 防止暴力破解

### 2. 审计日志

系统自动记录以下安全事件：

- 用户登录/登录失败
- Token验证成功/失败
- 权限检查
- 可疑活动检测

### 3. 监控告警

可通过以下API获取安全摘要：

```bash
# 获取安全事件统计
curl -X GET "http://ragflow-api/v1/enterprise/security/summary?days=7"
```

## 故障排除

### 1. Token验证失败

**问题**: `Invalid enterprise token`

**可能原因**:
- JWT密钥不匹配
- Token格式错误
- 必需字段缺失

**解决方案**:
```bash
# 检查JWT密钥配置
grep "jwt_secret" conf/service_conf.yaml

# 验证Token内容
python -c "
import jwt
token = 'your_token_here'
secret = 'your_secret_here'
print(jwt.decode(token, secret, algorithms=['HS256']))
"
```

### 2. 权限不足

**问题**: 用户无法访问某些功能

**排查步骤**:
1. 检查用户角色映射
2. 验证权限配置
3. 查看审计日志

```bash
# 查看用户权限
curl -H "Authorization: Bearer <token>" \
     "http://ragflow-api/v1/user/enterprise/permissions"
```

### 3. 自动登录失败

**问题**: 企业Token无法自动登录

**检查项目**:
- Token是否正确传递到URL参数
- 前端是否正确处理Token
- 网络连接是否正常

### 4. 数据库迁移问题

**问题**: 企业用户字段不存在

**解决方案**:
```bash
# 手动执行迁移
python -c "
from api.db.migrations.enterprise_auth_migration import migrate_enterprise_auth_fields
result = migrate_enterprise_auth_fields()
print(result)
"
```

## 部署建议

### 1. 生产环境配置

```yaml
enterprise_auth:
  enabled: true
  jwt_secret: "complex-random-secret-key-256-bits"
  token_expiry: 1800  # 30分钟，生产环境建议较短
  allowed_domains:
    - "10.0.0.0/8"    # 内网IP段
  auto_create_user: true
```

### 2. 安全建议

- 使用强随机密钥（至少256位）
- 定期轮换JWT密钥
- 配置IP白名单
- 启用HTTPS
- 定期检查审计日志

### 3. 性能优化

- 配置Redis用于Token缓存
- 设置合理的Token过期时间
- 使用数据库索引优化查询

## 示例集成代码

### 企业系统端完整示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>企业系统集成示例</title>
</head>
<body>
    <h1>企业管理系统</h1>
    
    <div id="user-info">
        <p>当前用户: <span id="username"></span></p>
        <p>角色: <span id="user-role"></span></p>
    </div>
    
    <button onclick="openRAGFlow()">打开知识库系统</button>
    
    <script>
        // 模拟用户登录后的信息
        const currentUser = {
            userId: 'emp_001',
            email: 'admin@company.com',
            nickname: '管理员',
            role: 'enterprise_admin'
        };
        
        // 显示用户信息
        document.getElementById('username').textContent = currentUser.nickname;
        document.getElementById('user-role').textContent = currentUser.role;
        
        // 生成企业Token并打开RAGFlow
        async function openRAGFlow() {
            try {
                // 调用后端API生成Token
                const response = await fetch('/api/generate-ragflow-token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(currentUser)
                });
                
                const { token } = await response.json();
                
                // 打开RAGFlow系统
                const ragflowUrl = `https://ragflow.company.com?enterprise_token=${token}`;
                window.open(ragflowUrl, '_blank');
                
            } catch (error) {
                console.error('打开知识库系统失败:', error);
                alert('打开知识库系统失败，请稍后重试');
            }
        }
    </script>
</body>
</html>
```

## 总结

通过本指南，您应该能够成功将RAGFlow集成到企业系统中，实现：

1. **单点登录**: 用户无需重复登录
2. **权限控制**: 基于角色的功能访问控制  
3. **安全保障**: 完善的安全验证和审计机制
4. **无缝体验**: 流畅的用户体验

如有问题，请参考故障排除部分或联系技术支持。 