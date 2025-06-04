# RAGFlow 企业认证功能

<div align="center">
  <img src="https://github.com/infiniflow/ragflow/assets/12318111/b083548b-bb83-4f55-9c5c-8b2cd7e8f72f" width="200">
  <h3>企业级单点登录(SSO)与权限管理</h3>
  
  [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
  [![Version](https://img.shields.io/badge/version-v0.14.0-green.svg)](https://github.com/infiniflow/ragflow/releases)
  [![Security](https://img.shields.io/badge/security-JWT%20%2B%20RBAC-orange.svg)](#安全特性)
</div>

## 📋 目录

- [功能概述](#功能概述)
- [快速开始](#快速开始)
- [配置指南](#配置指南)
- [API文档](#api文档)
- [集成示例](#集成示例)
- [权限说明](#权限说明)
- [安全特性](#安全特性)
- [故障排除](#故障排除)
- [贡献指南](#贡献指南)

## 🚀 功能概述

RAGFlow企业认证功能提供了完整的企业级单点登录(SSO)解决方案，让企业能够将RAGFlow无缝集成到现有的用户管理系统中。

### ✨ 核心特性

- 🔐 **JWT Token认证** - 基于标准JWT的安全认证机制
- 🎯 **单点登录(SSO)** - 用户无需重复登录，一键访问RAGFlow
- 👥 **基于角色的权限控制(RBAC)** - 灵活的权限管理体系
- 🛡️ **多层安全防护** - 防重放攻击、IP白名单、速率限制
- 📊 **完整审计日志** - 详细的安全事件记录和监控
- 🔄 **自动用户管理** - 基于Token自动创建和同步用户信息

### 🎪 支持场景

- 企业内部知识库系统集成
- 多系统统一身份认证
- 细粒度权限控制
- 合规性审计要求

## ⚡ 快速开始

### 1. 环境准备

确保您的RAGFlow实例版本 >= v0.14.0，并已启用企业认证功能。

### 2. 基础配置

在RAGFlow配置文件中添加企业认证配置：

```yaml
# conf/service_conf.yaml
enterprise_auth:
  enabled: true
  jwt_secret: "your-super-secret-key-256-bits"
  role_mapping:
    enterprise_admin: "admin"
    enterprise_user: "normal"
  token_expiry: 3600
  auto_create_user: true
```

### 3. 生成企业Token

```python
import jwt
import time

def generate_enterprise_token():
    payload = {
        "user_id": "emp_001",
        "email": "admin@company.com",
        "nickname": "管理员",
        "role": "enterprise_admin",
        "tenant_id": "company_001",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    
    return jwt.encode(payload, "your-super-secret-key-256-bits", algorithm="HS256")
```

### 4. 集成访问

```javascript
// 企业系统中跳转到RAGFlow
const token = generateEnterpriseToken();
const ragflowUrl = `https://ragflow.company.com?enterprise_token=${token}`;
window.open(ragflowUrl, '_blank');
```

## ⚙️ 配置指南

### 完整配置选项

```yaml
enterprise_auth:
  # 基础配置
  enabled: true                           # 是否启用企业认证
  jwt_secret: "your-jwt-secret-key"       # JWT签名密钥
  token_expiry: 3600                      # Token有效期（秒）
  auto_create_user: true                  # 是否自动创建用户
  
  # 角色映射
  role_mapping:
    enterprise_admin: "admin"             # 企业管理员 → RAGFlow管理员
    enterprise_user: "normal"             # 企业用户 → RAGFlow普通用户
    enterprise_viewer: "normal"           # 企业查看者 → RAGFlow普通用户
  
  # 安全配置
  allowed_domains:                        # IP/域名白名单
    - "192.168.1.0/24"                   # 内网IP段
    - "10.0.0.0/8"                       # 企业网段
    - "company.example.com"               # 企业域名
  
  # 高级安全选项
  enable_anti_replay: true                # 启用防重放攻击
  enable_rate_limiting: true              # 启用速率限制
  max_login_attempts: 5                   # 最大登录尝试次数
  rate_limit_window: 300                  # 速率限制时间窗口（秒）
```

### 环境变量配置

```bash
# 基础配置
export ENTERPRISE_AUTH_ENABLED=true
export ENTERPRISE_JWT_SECRET="your-jwt-secret-key"
export ENTERPRISE_TOKEN_EXPIRY=3600

# 安全配置
export ENTERPRISE_ALLOWED_DOMAINS="192.168.1.0/24,10.0.0.0/8"
export ENTERPRISE_ANTI_REPLAY_ENABLED=true
export ENTERPRISE_RATE_LIMITING_ENABLED=true
```

## 📚 API文档

### 企业登录API

#### `POST /v1/user/enterprise/login`

使用企业Token登录RAGFlow系统。

**请求参数:**
```json
{
  "enterprise_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应示例:**
```json
{
  "code": 0,
  "data": {
    "id": "user_uuid",
    "nickname": "张三",
    "email": "zhangsan@company.com",
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

### 用户验证API

#### `GET /v1/user/enterprise/verify`

验证当前用户的企业身份。

**请求头:**
```
Authorization: Bearer <ragflow_access_token>
```

**响应示例:**
```json
{
  "code": 0,
  "data": {
    "user_id": "user_uuid",
    "enterprise_user_id": "emp_001",
    "email": "zhangsan@company.com",
    "is_enterprise_user": true,
    "permissions": {
      "can_manage_knowledge": true,
      "can_chat": true,
      "can_manage_users": false,
      "can_access_system": false
    }
  }
}
```

### 权限查询API

#### `GET /v1/user/enterprise/permissions`

获取当前用户的详细权限信息。

**响应示例:**
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

### 安全监控API

#### `GET /v1/enterprise/security/summary`

获取安全事件统计摘要（需要管理员权限）。

**查询参数:**
- `days`: 查询天数，默认7天

**响应示例:**
```json
{
  "code": 0,
  "data": {
    "total_events": 1250,
    "successful_logins": 1180,
    "failed_logins": 70,
    "active_users": 45,
    "event_types": {
      "enterprise_login": 1180,
      "token_validation": 2340,
      "permission_check": 5670
    }
  }
}
```

## 🔧 集成示例

### Python集成示例

```python
import jwt
import time
import requests

class EnterpriseRAGFlowClient:
    def __init__(self, ragflow_url, jwt_secret):
        self.ragflow_url = ragflow_url
        self.jwt_secret = jwt_secret
    
    def generate_token(self, user_id, email, nickname, role, tenant_id):
        """生成企业认证Token"""
        current_time = int(time.time())
        payload = {
            "user_id": user_id,
            "email": email,
            "nickname": nickname,
            "role": role,
            "tenant_id": tenant_id,
            "iat": current_time,
            "exp": current_time + 3600,
            "jti": f"{user_id}_{current_time}"
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    def login_user(self, user_id, email, nickname, role, tenant_id):
        """用户登录"""
        token = self.generate_token(user_id, email, nickname, role, tenant_id)
        
        response = requests.post(
            f"{self.ragflow_url}/v1/user/enterprise/login",
            json={"enterprise_token": token}
        )
        
        return response.json()

# 使用示例
client = EnterpriseRAGFlowClient(
    ragflow_url="https://ragflow.company.com",
    jwt_secret="your-shared-secret"
)

result = client.login_user(
    user_id="emp_001",
    email="admin@company.com",
    nickname="管理员",
    role="enterprise_admin",
    tenant_id="company_001"
)

print(f"登录结果: {result}")
```

### Java集成示例

```java
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

public class EnterpriseRAGFlowClient {
    private String ragflowUrl;
    private String jwtSecret;
    
    public EnterpriseRAGFlowClient(String ragflowUrl, String jwtSecret) {
        this.ragflowUrl = ragflowUrl;
        this.jwtSecret = jwtSecret;
    }
    
    public String generateToken(String userId, String email, String nickname, 
                               String role, String tenantId) {
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
                .signWith(SignatureAlgorithm.HS256, jwtSecret)
                .compact();
    }
    
    public String generateAccessUrl(String userId, String email, String nickname,
                                   String role, String tenantId) {
        String token = generateToken(userId, email, nickname, role, tenantId);
        return ragflowUrl + "?enterprise_token=" + token;
    }
}
```

### JavaScript/Node.js集成示例

```javascript
const jwt = require('jsonwebtoken');
const axios = require('axios');

class EnterpriseRAGFlowClient {
    constructor(ragflowUrl, jwtSecret) {
        this.ragflowUrl = ragflowUrl;
        this.jwtSecret = jwtSecret;
    }
    
    generateToken(userId, email, nickname, role, tenantId) {
        const currentTime = Math.floor(Date.now() / 1000);
        
        const payload = {
            user_id: userId,
            email: email,
            nickname: nickname,
            role: role,
            tenant_id: tenantId,
            iat: currentTime,
            exp: currentTime + 3600,
            jti: `${userId}_${currentTime}`
        };
        
        return jwt.sign(payload, this.jwtSecret, { algorithm: 'HS256' });
    }
    
    async loginUser(userId, email, nickname, role, tenantId) {
        const token = this.generateToken(userId, email, nickname, role, tenantId);
        
        try {
            const response = await axios.post(
                `${this.ragflowUrl}/v1/user/enterprise/login`,
                { enterprise_token: token }
            );
            return response.data;
        } catch (error) {
            throw new Error(`登录失败: ${error.response?.data?.message || error.message}`);
        }
    }
    
    generateAccessUrl(userId, email, nickname, role, tenantId) {
        const token = this.generateToken(userId, email, nickname, role, tenantId);
        return `${this.ragflowUrl}?enterprise_token=${token}`;
    }
}

// 使用示例
const client = new EnterpriseRAGFlowClient(
    'https://ragflow.company.com',
    'your-shared-secret'
);

// 生成访问URL
const accessUrl = client.generateAccessUrl(
    'emp_001',
    'admin@company.com',
    '管理员',
    'enterprise_admin',
    'company_001'
);

console.log('RAGFlow访问URL:', accessUrl);
```

### 前端React集成示例

```tsx
import React, { useEffect, useState } from 'react';
import { Button, Space, Card, Tag } from 'antd';

interface User {
    userId: string;
    email: string;
    nickname: string;
    role: string;
    tenantId: string;
}

const EnterprisePortal: React.FC = () => {
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    
    useEffect(() => {
        // 从企业系统获取当前用户信息
        fetchCurrentUser();
    }, []);
    
    const fetchCurrentUser = async () => {
        // 模拟获取当前用户信息
        const user: User = {
            userId: 'emp_001',
            email: 'admin@company.com',
            nickname: '管理员',
            role: 'enterprise_admin',
            tenantId: 'company_001'
        };
        setCurrentUser(user);
    };
    
    const openRAGFlow = async () => {
        if (!currentUser) return;
        
        try {
            // 调用后端API生成Token
            const response = await fetch('/api/generate-ragflow-token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(currentUser)
            });
            
            const { token } = await response.json();
            
            // 打开RAGFlow
            const ragflowUrl = `https://ragflow.company.com?enterprise_token=${token}`;
            window.open(ragflowUrl, '_blank');
            
        } catch (error) {
            console.error('打开RAGFlow失败:', error);
        }
    };
    
    const getRoleColor = (role: string) => {
        return role === 'enterprise_admin' ? 'red' : 'blue';
    };
    
    const getRoleText = (role: string) => {
        return role === 'enterprise_admin' ? '管理员' : '普通用户';
    };
    
    if (!currentUser) {
        return <div>加载中...</div>;
    }
    
    return (
        <Card title="企业知识库系统" style={{ maxWidth: 600, margin: '50px auto' }}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <div>
                    <h3>当前用户信息</h3>
                    <p><strong>姓名:</strong> {currentUser.nickname}</p>
                    <p><strong>邮箱:</strong> {currentUser.email}</p>
                    <p><strong>角色:</strong> <Tag color={getRoleColor(currentUser.role)}>
                        {getRoleText(currentUser.role)}
                    </Tag></p>
                </div>
                
                <Button 
                    type="primary" 
                    size="large" 
                    onClick={openRAGFlow}
                    style={{ width: '100%' }}
                >
                    🚀 打开知识库系统 (RAGFlow)
                </Button>
                
                <div style={{ fontSize: '12px', color: '#666' }}>
                    <p>点击上方按钮将使用单点登录方式打开RAGFlow知识库系统</p>
                    <p>您的访问权限由企业角色自动确定</p>
                </div>
            </Space>
        </Card>
    );
};

export default EnterprisePortal;
```

## 👥 权限说明

### 权限类型

| 权限标识 | 权限名称 | 功能描述 |
|----------|----------|----------|
| `can_manage_knowledge` | 知识库管理 | 创建、编辑、删除知识库和文档 |
| `can_chat` | 聊天功能 | 使用AI问答功能 |
| `can_manage_users` | 用户管理 | 管理团队成员和权限 |
| `can_access_system` | 系统管理 | 访问系统设置和高级功能 |

### 角色权限矩阵

| 企业角色 | RAGFlow角色 | 知识库管理 | 聊天功能 | 用户管理 | 系统管理 |
|----------|-------------|------------|----------|----------|----------|
| `enterprise_admin` | ADMIN | ✅ | ✅ | ❌ | ❌ |
| `enterprise_user` | NORMAL | ❌ | ✅ | ❌ | ❌ |
| `enterprise_viewer` | NORMAL | ❌ | ✅ | ❌ | ❌ |

### 自定义角色映射

可以在配置文件中自定义角色映射关系：

```yaml
enterprise_auth:
  role_mapping:
    # 企业角色 → RAGFlow角色
    enterprise_super_admin: "owner"      # 超级管理员
    enterprise_admin: "admin"            # 管理员
    enterprise_manager: "admin"          # 部门经理
    enterprise_user: "normal"            # 普通员工
    enterprise_guest: "normal"           # 访客用户
```

## 🛡️ 安全特性

### JWT Token安全

- **HMAC SHA256签名**: 使用HMAC SHA256算法确保Token完整性
- **时效性控制**: 可配置的Token过期时间
- **防篡改机制**: 任何Token内容修改都会导致验证失败

### 防重放攻击

```yaml
enterprise_auth:
  enable_anti_replay: true              # 启用防重放攻击
```

- 使用JTI(JWT ID)确保每个Token只能使用一次
- Redis缓存已使用Token，防止重复使用
- 自动清理过期Token记录

### IP白名单

```yaml
enterprise_auth:
  allowed_domains:
    - "192.168.1.0/24"                 # 支持CIDR格式
    - "10.0.0.0/8"                     # 企业内网
    - "specific.ip.address"            # 特定IP地址
```

### 速率限制

```yaml
enterprise_auth:
  enable_rate_limiting: true
  max_login_attempts: 5                 # 5分钟内最多5次尝试
  rate_limit_window: 300               # 5分钟时间窗口
```

### 审计日志

系统自动记录以下安全事件：

- ✅ **成功登录**: 用户成功通过企业认证
- ❌ **登录失败**: Token验证失败或其他错误
- 🔍 **权限检查**: 用户访问功能时的权限验证
- ⚠️ **可疑活动**: 检测到的异常登录行为
- 🚫 **访问拒绝**: IP白名单或速率限制触发

### 安全最佳实践

1. **强密钥管理**
   ```bash
   # 使用256位随机密钥
   openssl rand -base64 32
   ```

2. **合理的Token过期时间**
   ```yaml
   # 生产环境建议30分钟
   token_expiry: 1800
   ```

3. **网络安全**
   ```yaml
   # 严格的IP白名单
   allowed_domains:
     - "internal.company.network/24"
   ```

4. **监控告警**
   ```bash
   # 定期检查安全事件
   curl -H "Authorization: Bearer <admin_token>" \
        "https://ragflow.company.com/v1/enterprise/security/summary?days=1"
   ```

## 🔧 故障排除

### 常见问题

#### ❌ 问题1: "Invalid enterprise token"

**可能原因:**
- JWT密钥不匹配
- Token格式错误
- 必需字段缺失

**解决方案:**
```bash
# 1. 检查JWT密钥配置
grep "jwt_secret" conf/service_conf.yaml

# 2. 验证Token内容
python3 -c "
import jwt
token = 'your_token_here'
secret = 'your_secret_here'
print(jwt.decode(token, secret, algorithms=['HS256']))
"

# 3. 检查Token字段完整性
python3 -c "
import jwt
token = 'your_token_here'
secret = 'your_secret_here'
payload = jwt.decode(token, secret, algorithms=['HS256'])
required = ['user_id', 'email', 'nickname', 'role', 'tenant_id']
missing = [f for f in required if f not in payload]
print(f'缺失字段: {missing}' if missing else '字段完整')
"
```

#### ❌ 问题2: "Token has expired"

**解决方案:**
```python
# 检查Token过期时间
import jwt
from datetime import datetime

token = "your_token_here"
secret = "your_secret_here"

try:
    payload = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_exp": False})
    exp_time = datetime.fromtimestamp(payload['exp'])
    current_time = datetime.now()
    
    print(f"Token过期时间: {exp_time}")
    print(f"当前时间: {current_time}")
    print(f"是否过期: {current_time > exp_time}")
    
except Exception as e:
    print(f"Token解析错误: {e}")
```

#### ❌ 问题3: "Request from unauthorized domain/IP"

**解决方案:**
```yaml
# 检查IP白名单配置
enterprise_auth:
  allowed_domains:
    - "0.0.0.0/0"  # 临时允许所有IP（仅用于调试）
```

```bash
# 获取客户端真实IP
curl -H "X-Forwarded-For: your_ip" \
     -H "X-Real-IP: your_ip" \
     "https://ragflow.company.com/v1/user/enterprise/login"
```

#### ❌ 问题4: "Rate limit exceeded"

**解决方案:**
```bash
# 清除速率限制记录（需要Redis访问权限）
redis-cli DEL enterprise_rate_limit:user:your_user_id
redis-cli DEL enterprise_rate_limit:ip:your_ip_address

# 或者调整速率限制配置
```

```yaml
enterprise_auth:
  max_login_attempts: 10               # 增加允许尝试次数
  rate_limit_window: 60               # 缩短时间窗口
```

### 调试工具

#### Token验证工具

```python
#!/usr/bin/env python3
"""
Enterprise Token验证工具
"""
import jwt
import sys
from datetime import datetime

def verify_token(token, secret):
    try:
        # 解码Token（不验证过期时间）
        payload = jwt.decode(token, secret, algorithms=["HS256"], options={"verify_exp": False})
        
        print("✅ Token格式有效")
        print(f"用户ID: {payload.get('user_id')}")
        print(f"邮箱: {payload.get('email')}")
        print(f"角色: {payload.get('role')}")
        print(f"签发时间: {datetime.fromtimestamp(payload.get('iat', 0))}")
        print(f"过期时间: {datetime.fromtimestamp(payload.get('exp', 0))}")
        
        # 检查是否过期
        if payload.get('exp', 0) < datetime.now().timestamp():
            print("⚠️ Token已过期")
        else:
            print("✅ Token未过期")
            
        # 检查必需字段
        required_fields = ['user_id', 'email', 'nickname', 'role', 'tenant_id']
        missing_fields = [f for f in required_fields if f not in payload]
        
        if missing_fields:
            print(f"❌ 缺失必需字段: {missing_fields}")
        else:
            print("✅ 所有必需字段存在")
            
        return True
        
    except jwt.ExpiredSignatureError:
        print("❌ Token已过期")
        return False
    except jwt.InvalidTokenError as e:
        print(f"❌ Token无效: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python verify_token.py <token> <secret>")
        sys.exit(1)
    
    token = sys.argv[1]
    secret = sys.argv[2]
    
    verify_token(token, secret)
```

#### 网络连接测试

```bash
#!/bin/bash
# 网络连接测试脚本

RAGFLOW_URL="https://ragflow.company.com"
TOKEN="your_test_token"

echo "=== RAGFlow企业认证连接测试 ==="

# 1. 基础连接测试
echo "1. 测试基础连接..."
curl -s -o /dev/null -w "HTTP状态码: %{http_code}, 响应时间: %{time_total}s\n" $RAGFLOW_URL

# 2. 企业登录API测试
echo "2. 测试企业登录API..."
curl -X POST "$RAGFLOW_URL/v1/user/enterprise/login" \
     -H "Content-Type: application/json" \
     -d "{\"enterprise_token\": \"$TOKEN\"}" \
     -w "HTTP状态码: %{http_code}, 响应时间: %{time_total}s\n"

# 3. DNS解析测试
echo "3. 测试DNS解析..."
nslookup ragflow.company.com

# 4. SSL证书测试
echo "4. 测试SSL证书..."
echo | openssl s_client -connect ragflow.company.com:443 -servername ragflow.company.com 2>/dev/null | openssl x509 -noout -dates
```

### 日志分析

```bash
# 查看企业认证相关日志
tail -f /path/to/ragflow/logs/application.log | grep -i "enterprise"

# 统计登录成功/失败次数
grep "enterprise_login" /path/to/ragflow/logs/application.log | \
awk '{if($0 ~ /success/) success++; else failed++} END {print "成功:", success, "失败:", failed}'

# 查看最近的安全事件
grep "security_event" /path/to/ragflow/logs/application.log | tail -20
```

## 🤝 贡献指南

### 开发环境搭建

1. **克隆仓库**
   ```bash
   git clone https://github.com/infiniflow/ragflow.git
   cd ragflow
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   npm install  # 前端依赖
   ```

3. **配置开发环境**
   ```yaml
   # conf/service_conf.yaml
   enterprise_auth:
     enabled: true
     jwt_secret: "dev-secret-key-do-not-use-in-production"
     role_mapping:
       enterprise_admin: "admin"
       enterprise_user: "normal"
     token_expiry: 86400  # 开发环境24小时
   ```

4. **运行测试**
   ```bash
   python tests/enterprise_auth_test.py
   ```

### 代码贡献流程

1. **Fork仓库**并创建特性分支
   ```bash
   git checkout -b feature/enterprise-auth-improvement
   ```

2. **编写代码**并确保通过测试
   ```bash
   # 运行单元测试
   python -m pytest tests/enterprise_auth_test.py -v
   
   # 运行安全测试
   python tests/enterprise_auth_test.py
   
   # 代码格式检查
   flake8 api/db/services/enterprise_auth_service.py
   flake8 api/utils/enterprise_security.py
   ```

3. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 改进企业认证功能安全性"
   git push origin feature/enterprise-auth-improvement
   ```

4. **创建Pull Request**

### 代码规范

- **Python代码**: 遵循PEP 8规范
- **JavaScript/TypeScript**: 使用ESLint和Prettier
- **文档**: 使用中文注释，英文变量名
- **测试**: 新功能必须包含相应测试用例

### 安全审查清单

提交企业认证相关代码时，请确保：

- ✅ 敏感信息（密钥、密码）不包含在代码中
- ✅ 输入验证和数据清理已实现
- ✅ 错误处理不会泄露敏感信息
- ✅ 日志记录不包含敏感数据
- ✅ 安全测试用例已通过
- ✅ 代码注释清晰，安全考虑已说明

## 📞 支持与反馈

### 获取帮助

- 📖 **文档**: [完整集成指南](docs/enterprise_integration_guide.md)
- 💬 **社区讨论**: [GitHub Discussions](https://github.com/infiniflow/ragflow/discussions)
- 🐛 **问题报告**: [GitHub Issues](https://github.com/infiniflow/ragflow/issues)
- 📧 **商业支持**: enterprise@infiniflow.io

### 反馈渠道

如果您在使用企业认证功能时遇到问题或有改进建议，欢迎通过以下方式联系我们：

1. **技术问题**: 在GitHub Issues中创建问题报告
2. **功能建议**: 在GitHub Discussions中发起讨论
3. **安全漏洞**: 发送邮件至security@infiniflow.io
4. **商业合作**: 联系enterprise@infiniflow.io

---

<div align="center">
  <h3>🚀 让企业知识管理更简单高效</h3>
  <p>RAGFlow企业认证功能 - 安全、可靠、易集成</p>
  
  [![GitHub Stars](https://img.shields.io/github/stars/infiniflow/ragflow?style=social)](https://github.com/infiniflow/ragflow)
  [![GitHub Forks](https://img.shields.io/github/forks/infiniflow/ragflow?style=social)](https://github.com/infiniflow/ragflow)
</div> 