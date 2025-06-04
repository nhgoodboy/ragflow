# RAGFlow 企业认证 API 接口文档

<div align="center">
  <h2>🔐 Enterprise Authentication API Documentation</h2>
  <p>RAGFlow 企业级单点登录与权限管理接口规范</p>
  
  [![Version](https://img.shields.io/badge/API_Version-v1.0-blue.svg)](#版本信息)
  [![Protocol](https://img.shields.io/badge/Protocol-HTTP/HTTPS-green.svg)](#协议说明)
  [![Auth](https://img.shields.io/badge/Auth-JWT_Bearer-orange.svg)](#认证方式)
</div>

---

## 📋 目录

- [版本信息](#版本信息)
- [基础信息](#基础信息)
- [认证流程](#认证流程)
- [核心接口](#核心接口)
- [管理接口](#管理接口)
- [安全接口](#安全接口)
- [错误码说明](#错误码说明)
- [SDK 示例](#sdk-示例)
- [测试工具](#测试工具)

---

## 📊 版本信息

| 版本 | 发布日期 | 变更说明 |
|------|----------|----------|
| v1.0 | 2024-01-15 | 初始版本，支持基础企业认证功能 |
| v1.1 | 2024-02-01 | 新增安全监控接口 |
| v1.2 | 2024-03-01 | 新增批量用户管理接口 |

---

## 🌐 基础信息

### 服务地址
- **生产环境**: `https://api.ragflow.company.com`
- **测试环境**: `https://test-api.ragflow.company.com`
- **开发环境**: `http://localhost:9380`

### 协议说明
- **协议**: HTTP/HTTPS
- **请求方法**: GET, POST, PUT, DELETE
- **数据格式**: JSON
- **字符编码**: UTF-8

### 通用请求头
```http
Content-Type: application/json
Accept: application/json
User-Agent: YourApp/1.0
X-Request-ID: unique-request-id
```

### 通用响应格式
```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "timestamp": 1640995200,
  "request_id": "req_12345678"
}
```

---

## 🔄 认证流程

### 1. 企业Token生成流程

```mermaid
sequenceDiagram
    participant E as 企业系统
    participant R as RAGFlow
    participant U as 用户
    
    U->>E: 点击访问RAGFlow
    E->>E: 生成JWT Token
    E->>U: 跳转到RAGFlow(带Token)
    U->>R: 访问RAGFlow页面
    R->>R: 验证Token并创建用户
    R->>U: 返回RAGFlow访问令牌
    U->>R: 使用功能
```

### 2. JWT Token 规范

**Token结构**:
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "enterprise_user_123",
    "email": "user@company.com",
    "nickname": "张三",
    "role": "enterprise_admin",
    "tenant_id": "company_tenant_001",
    "iat": 1640995200,
    "exp": 1640998800,
    "jti": "unique_token_id"
  }
}
```

**必需字段**:
- `user_id`: 企业系统用户ID
- `email`: 用户邮箱
- `nickname`: 用户昵称
- `role`: 企业角色
- `tenant_id`: 租户ID
- `iat`: 签发时间
- `exp`: 过期时间

**可选字段**:
- `jti`: Token唯一标识（用于防重放攻击）

---

## 🔑 核心接口

### 1. 企业用户登录

#### `POST /v1/user/enterprise/login`

使用企业JWT Token登录RAGFlow系统。

**请求参数**:
```json
{
  "enterprise_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**请求示例**:
```bash
curl -X POST "https://api.ragflow.company.com/v1/user/enterprise/login" \
  -H "Content-Type: application/json" \
  -d '{
    "enterprise_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZW50ZXJwcmlzZV91c2VyXzEyMyIsImVtYWlsIjoidXNlckBjb21wYW55LmNvbSIsIm5pY2tuYW1lIjoi5byg5LiJIiwicm9sZSI6ImVudGVycHJpc2VfYWRtaW4iLCJ0ZW5hbnRfaWQiOiJjb21wYW55X3RlbmFudF8wMDEiLCJpYXQiOjE2NDA5OTUyMDAsImV4cCI6MTY0MDk5ODgwMH0.signature"
  }'
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Enterprise login successful",
  "data": {
    "id": "usr_f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "enterprise_user_id": "enterprise_user_123",
    "nickname": "张三",
    "email": "user@company.com",
    "access_token": "ragflow_access_token_abc123",
    "refresh_token": "ragflow_refresh_token_def456",
    "permissions": {
      "can_manage_knowledge": true,
      "can_chat": true,
      "can_manage_users": false,
      "can_access_system": false
    },
    "role": "admin",
    "login_channel": "enterprise",
    "expires_in": 3600,
    "created_at": "2024-01-15T10:30:00Z",
    "last_login_at": "2024-01-15T10:30:00Z"
  },
  "timestamp": 1640995200
}
```

**错误响应**:
```json
{
  "code": 4001,
  "message": "Invalid enterprise token",
  "data": null,
  "timestamp": 1640995200,
  "error_details": {
    "reason": "token_expired",
    "description": "The provided JWT token has expired"
  }
}
```

---

### 2. 验证企业用户身份

#### `GET /v1/user/enterprise/verify`

验证当前登录用户的企业身份信息。

**请求头**:
```http
Authorization: Bearer <ragflow_access_token>
```

**请求示例**:
```bash
curl -X GET "https://api.ragflow.company.com/v1/user/enterprise/verify" \
  -H "Authorization: Bearer ragflow_access_token_abc123"
```

**响应示例**:
```json
{
  "code": 0,
  "message": "User verification successful",
  "data": {
    "user_id": "usr_f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "enterprise_user_id": "enterprise_user_123",
    "email": "user@company.com",
    "nickname": "张三",
    "role": "admin",
    "enterprise_source": "enterprise_system",
    "is_enterprise_user": true,
    "tenant_id": "company_tenant_001",
    "permissions": {
      "can_manage_knowledge": true,
      "can_chat": true,
      "can_manage_users": false,
      "can_access_system": false
    },
    "last_login_at": "2024-01-15T10:30:00Z",
    "token_expires_at": "2024-01-15T11:30:00Z"
  },
  "timestamp": 1640995200
}
```

---

### 3. 获取用户权限信息

#### `GET /v1/user/enterprise/permissions`

获取当前用户的详细权限信息。

**请求头**:
```http
Authorization: Bearer <ragflow_access_token>
```

**查询参数**:
- `detailed` (可选): 是否返回详细权限说明，默认为 `false`

**请求示例**:
```bash
curl -X GET "https://api.ragflow.company.com/v1/user/enterprise/permissions?detailed=true" \
  -H "Authorization: Bearer ragflow_access_token_abc123"
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Permissions retrieved successfully",
  "data": {
    "permissions": {
      "can_manage_knowledge": true,
      "can_chat": true,
      "can_manage_users": false,
      "can_access_system": false
    },
    "role": "admin",
    "role_description": "知识库管理员",
    "permission_details": {
      "can_manage_knowledge": {
        "enabled": true,
        "description": "可以创建、编辑、删除知识库和文档",
        "scope": ["create", "read", "update", "delete"]
      },
      "can_chat": {
        "enabled": true,
        "description": "可以使用AI聊天问答功能",
        "scope": ["chat", "history"]
      },
      "can_manage_users": {
        "enabled": false,
        "description": "可以管理团队成员和权限",
        "scope": []
      },
      "can_access_system": {
        "enabled": false,
        "description": "可以访问系统设置和高级功能",
        "scope": []
      }
    }
  },
  "timestamp": 1640995200
}
```

---

### 4. 刷新访问令牌

#### `POST /v1/user/enterprise/refresh`

使用刷新令牌获取新的访问令牌。

**请求参数**:
```json
{
  "refresh_token": "ragflow_refresh_token_def456"
}
```

**请求示例**:
```bash
curl -X POST "https://api.ragflow.company.com/v1/user/enterprise/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "ragflow_refresh_token_def456"
  }'
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "ragflow_access_token_new123",
    "refresh_token": "ragflow_refresh_token_new456",
    "expires_in": 3600,
    "token_type": "Bearer"
  },
  "timestamp": 1640995200
}
```

---

### 5. 企业用户注销

#### `POST /v1/user/enterprise/logout`

注销当前企业用户。

**请求头**:
```http
Authorization: Bearer <ragflow_access_token>
```

**请求示例**:
```bash
curl -X POST "https://api.ragflow.company.com/v1/user/enterprise/logout" \
  -H "Authorization: Bearer ragflow_access_token_abc123"
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Logout successful",
  "data": {
    "logout_time": "2024-01-15T11:30:00Z",
    "session_duration": 3600
  },
  "timestamp": 1640995200
}
```

---

## 👨‍💼 管理接口

### 1. 批量创建企业用户

#### `POST /v1/admin/enterprise/users/batch`

批量创建或更新企业用户（需要管理员权限）。

**请求头**:
```http
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

**请求参数**:
```json
{
  "users": [
    {
      "enterprise_user_id": "emp_001",
      "email": "user1@company.com",
      "nickname": "用户1",
      "role": "enterprise_admin",
      "tenant_id": "company_001",
      "department": "技术部",
      "extra_info": {
        "phone": "13800138001",
        "position": "高级工程师"
      }
    },
    {
      "enterprise_user_id": "emp_002",
      "email": "user2@company.com",
      "nickname": "用户2",
      "role": "enterprise_user",
      "tenant_id": "company_001",
      "department": "销售部",
      "extra_info": {
        "phone": "13800138002",
        "position": "销售经理"
      }
    }
  ],
  "operation": "create_or_update"
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Batch user operation completed",
  "data": {
    "total": 2,
    "success": 2,
    "failed": 0,
    "results": [
      {
        "enterprise_user_id": "emp_001",
        "status": "created",
        "user_id": "usr_f47ac10b-58cc-4372-a567-0e02b2c3d479"
      },
      {
        "enterprise_user_id": "emp_002",
        "status": "updated",
        "user_id": "usr_a23bc45d-67ef-4890-b123-456789abcdef"
      }
    ]
  },
  "timestamp": 1640995200
}
```

---

### 2. 查询企业用户列表

#### `GET /v1/admin/enterprise/users`

获取企业用户列表（需要管理员权限）。

**请求头**:
```http
Authorization: Bearer <admin_access_token>
```

**查询参数**:
- `page`: 页码，默认为 1
- `size`: 每页大小，默认为 20，最大 100
- `role`: 过滤角色，可选值：`enterprise_admin`, `enterprise_user`
- `status`: 用户状态，可选值：`active`, `inactive`
- `search`: 搜索关键词（搜索昵称、邮箱）
- `tenant_id`: 租户ID过滤
- `created_after`: 创建时间起始过滤（ISO 8601格式）
- `created_before`: 创建时间结束过滤（ISO 8601格式）

**请求示例**:
```bash
curl -X GET "https://api.ragflow.company.com/v1/admin/enterprise/users?page=1&size=20&role=enterprise_admin&status=active" \
  -H "Authorization: Bearer admin_access_token_xyz789"
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Users retrieved successfully",
  "data": {
    "users": [
      {
        "user_id": "usr_f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "enterprise_user_id": "emp_001",
        "email": "user1@company.com",
        "nickname": "用户1",
        "role": "enterprise_admin",
        "ragflow_role": "admin",
        "tenant_id": "company_001",
        "status": "active",
        "last_login_at": "2024-01-15T10:30:00Z",
        "created_at": "2024-01-10T09:00:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "permissions": {
          "can_manage_knowledge": true,
          "can_chat": true,
          "can_manage_users": false,
          "can_access_system": false
        }
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 150,
      "total_pages": 8
    }
  },
  "timestamp": 1640995200
}
```

---

### 3. 更新企业用户权限

#### `PUT /v1/admin/enterprise/users/{user_id}/permissions`

更新指定企业用户的权限（需要管理员权限）。

**路径参数**:
- `user_id`: 用户ID

**请求头**:
```http
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

**请求参数**:
```json
{
  "role": "enterprise_admin",
  "permissions": {
    "can_manage_knowledge": true,
    "can_chat": true,
    "can_manage_users": false,
    "can_access_system": false
  },
  "reason": "用户角色调整"
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "User permissions updated successfully",
  "data": {
    "user_id": "usr_f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "old_role": "enterprise_user",
    "new_role": "enterprise_admin",
    "old_permissions": {
      "can_manage_knowledge": false,
      "can_chat": true,
      "can_manage_users": false,
      "can_access_system": false
    },
    "new_permissions": {
      "can_manage_knowledge": true,
      "can_chat": true,
      "can_manage_users": false,
      "can_access_system": false
    },
    "updated_at": "2024-01-15T11:00:00Z"
  },
  "timestamp": 1640995200
}
```

---

### 4. 删除企业用户

#### `DELETE /v1/admin/enterprise/users/{user_id}`

删除指定的企业用户（需要管理员权限）。

**路径参数**:
- `user_id`: 用户ID

**请求头**:
```http
Authorization: Bearer <admin_access_token>
```

**查询参数**:
- `force`: 是否强制删除，默认为 `false`
- `reason`: 删除原因

**请求示例**:
```bash
curl -X DELETE "https://api.ragflow.company.com/v1/admin/enterprise/users/usr_f47ac10b-58cc-4372-a567-0e02b2c3d479?force=false&reason=user_left_company" \
  -H "Authorization: Bearer admin_access_token_xyz789"
```

**响应示例**:
```json
{
  "code": 0,
  "message": "User deleted successfully",
  "data": {
    "user_id": "usr_f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "enterprise_user_id": "emp_001",
    "deleted_at": "2024-01-15T11:30:00Z",
    "deletion_reason": "user_left_company"
  },
  "timestamp": 1640995200
}
```

---

## 🛡️ 安全接口

### 1. 获取安全事件摘要

#### `GET /v1/enterprise/security/summary`

获取企业认证相关的安全事件统计摘要（需要管理员权限）。

**请求头**:
```http
Authorization: Bearer <admin_access_token>
```

**查询参数**:
- `days`: 统计天数，默认为 7，最大 30
- `event_types`: 事件类型过滤，逗号分隔
- `format`: 返回格式，可选值：`json`, `csv`

**请求示例**:
```bash
curl -X GET "https://api.ragflow.company.com/v1/enterprise/security/summary?days=7&event_types=login,token_validation" \
  -H "Authorization: Bearer admin_access_token_xyz789"
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Security summary retrieved successfully",
  "data": {
    "summary_period": {
      "start_date": "2024-01-08T00:00:00Z",
      "end_date": "2024-01-15T23:59:59Z",
      "days": 7
    },
    "statistics": {
      "total_events": 1250,
      "successful_logins": 1180,
      "failed_logins": 70,
      "blocked_attempts": 15,
      "active_users": 45,
      "unique_ips": 28
    },
    "event_breakdown": {
      "enterprise_login": 1180,
      "token_validation": 2340,
      "permission_check": 5670,
      "suspicious_activity": 12,
      "rate_limit_exceeded": 8
    },
    "top_failure_reasons": [
      {
        "reason": "token_expired",
        "count": 35,
        "percentage": 50.0
      },
      {
        "reason": "invalid_signature",
        "count": 20,
        "percentage": 28.6
      },
      {
        "reason": "missing_fields",
        "count": 15,
        "percentage": 21.4
      }
    ],
    "security_alerts": [
      {
        "type": "high_failure_rate",
        "description": "IP 192.168.1.100 在过去1小时内失败尝试10次",
        "severity": "medium",
        "timestamp": "2024-01-15T10:30:00Z"
      }
    ]
  },
  "timestamp": 1640995200
}
```

---

### 2. 获取安全事件详情

#### `GET /v1/enterprise/security/events`

获取详细的安全事件列表（需要管理员权限）。

**请求头**:
```http
Authorization: Bearer <admin_access_token>
```

**查询参数**:
- `page`: 页码，默认为 1
- `size`: 每页大小，默认为 50，最大 200
- `event_type`: 事件类型过滤
- `user_id`: 用户ID过滤
- `ip_address`: IP地址过滤
- `success`: 是否成功，可选值：`true`, `false`
- `start_time`: 开始时间（ISO 8601格式）
- `end_time`: 结束时间（ISO 8601格式）
- `severity`: 严重程度，可选值：`low`, `medium`, `high`, `critical`

**请求示例**:
```bash
curl -X GET "https://api.ragflow.company.com/v1/enterprise/security/events?page=1&size=20&event_type=enterprise_login&success=false" \
  -H "Authorization: Bearer admin_access_token_xyz789"
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Security events retrieved successfully",
  "data": {
    "events": [
      {
        "id": "evt_12345678-1234-1234-1234-123456789abc",
        "event_type": "enterprise_login",
        "timestamp": "2024-01-15T10:30:00Z",
        "user_id": "usr_f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "enterprise_user_id": "emp_001",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "success": false,
        "failure_reason": "token_expired",
        "severity": "medium",
        "details": {
          "token_age": 7200,
          "expected_expiry": "2024-01-15T09:30:00Z",
          "client_time": "2024-01-15T10:30:00Z"
        },
        "geo_location": {
          "country": "China",
          "region": "Beijing",
          "city": "Beijing"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 70,
      "total_pages": 4
    }
  },
  "timestamp": 1640995200
}
```

---

### 3. 安全配置管理

#### `GET /v1/enterprise/security/config`

获取当前安全配置（需要管理员权限）。

**请求示例**:
```bash
curl -X GET "https://api.ragflow.company.com/v1/enterprise/security/config" \
  -H "Authorization: Bearer admin_access_token_xyz789"
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Security config retrieved successfully",
  "data": {
    "token_expiry": 3600,
    "max_login_attempts": 5,
    "rate_limit_window": 300,
    "enable_anti_replay": true,
    "enable_rate_limiting": true,
    "allowed_domains": [
      "192.168.1.0/24",
      "10.0.0.0/8"
    ],
    "role_mapping": {
      "enterprise_admin": "admin",
      "enterprise_user": "normal"
    },
    "audit_log_retention": 30,
    "security_alerts_enabled": true
  },
  "timestamp": 1640995200
}
```

#### `PUT /v1/enterprise/security/config`

更新安全配置（需要超级管理员权限）。

**请求参数**:
```json
{
  "token_expiry": 1800,
  "max_login_attempts": 3,
  "rate_limit_window": 600,
  "enable_anti_replay": true,
  "enable_rate_limiting": true,
  "allowed_domains": [
    "192.168.1.0/24"
  ],
  "audit_log_retention": 60,
  "security_alerts_enabled": true
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Security config updated successfully",
  "data": {
    "updated_fields": [
      "token_expiry",
      "max_login_attempts",
      "audit_log_retention"
    ],
    "updated_at": "2024-01-15T11:30:00Z"
  },
  "timestamp": 1640995200
}
```

---

### 4. IP白名单管理

#### `GET /v1/enterprise/security/whitelist/ip`

获取IP白名单。

#### `POST /v1/enterprise/security/whitelist/ip`

添加IP到白名单。

#### `DELETE /v1/enterprise/security/whitelist/ip`

从白名单移除IP。

**添加IP示例**:
```bash
curl -X POST "https://api.ragflow.company.com/v1/enterprise/security/whitelist/ip" \
  -H "Authorization: Bearer admin_access_token_xyz789" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_addresses": ["192.168.2.0/24", "10.1.1.100"],
    "description": "新增办公网段",
    "expires_at": "2024-12-31T23:59:59Z"
  }'
```

---

## ❌ 错误码说明

### 通用错误码

| 错误码 | HTTP状态码 | 错误信息 | 说明 |
|--------|------------|----------|------|
| 0 | 200 | Success | 请求成功 |
| 1001 | 400 | Invalid request parameters | 请求参数无效 |
| 1002 | 401 | Authentication required | 需要身份验证 |
| 1003 | 403 | Permission denied | 权限不足 |
| 1004 | 404 | Resource not found | 资源不存在 |
| 1005 | 429 | Rate limit exceeded | 请求频率超限 |
| 1006 | 500 | Internal server error | 服务器内部错误 |

### 企业认证专用错误码

| 错误码 | HTTP状态码 | 错误信息 | 说明 |
|--------|------------|----------|------|
| 4001 | 400 | Invalid enterprise token | 企业Token无效 |
| 4002 | 400 | Token expired | Token已过期 |
| 4003 | 400 | Missing required fields | 缺少必需字段 |
| 4004 | 400 | Invalid token signature | Token签名无效 |
| 4005 | 403 | Invalid enterprise role | 企业角色无效 |
| 4006 | 403 | IP not in whitelist | IP不在白名单中 |
| 4007 | 429 | Login attempts exceeded | 登录尝试次数过多 |
| 4008 | 409 | Token replay detected | 检测到Token重放攻击 |
| 4009 | 400 | User creation failed | 用户创建失败 |
| 4010 | 403 | Enterprise auth disabled | 企业认证功能未启用 |

### 错误响应格式

```json
{
  "code": 4001,
  "message": "Invalid enterprise token",
  "data": null,
  "timestamp": 1640995200,
  "request_id": "req_12345678",
  "error_details": {
    "error_type": "authentication_error",
    "reason": "token_expired",
    "description": "The provided JWT token has expired",
    "suggestions": [
      "请检查Token的过期时间",
      "重新生成有效的Token",
      "确认系统时间同步"
    ]
  }
}
```

---

## 📱 SDK 示例

### Python SDK

```python
import requests
import jwt
import time
from typing import Dict, Optional

class RAGFlowEnterpriseClient:
    def __init__(self, base_url: str, jwt_secret: str):
        self.base_url = base_url.rstrip('/')
        self.jwt_secret = jwt_secret
        self.access_token = None
    
    def generate_enterprise_token(self, user_id: str, email: str, 
                                nickname: str, role: str, tenant_id: str) -> str:
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
    
    def enterprise_login(self, enterprise_token: str) -> Dict:
        """企业用户登录"""
        url = f"{self.base_url}/v1/user/enterprise/login"
        response = requests.post(url, json={"enterprise_token": enterprise_token})
        result = response.json()
        
        if result["code"] == 0:
            self.access_token = result["data"]["access_token"]
        
        return result
    
    def verify_user(self) -> Dict:
        """验证用户身份"""
        url = f"{self.base_url}/v1/user/enterprise/verify"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()
    
    def get_permissions(self) -> Dict:
        """获取用户权限"""
        url = f"{self.base_url}/v1/user/enterprise/permissions"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()

# 使用示例
client = RAGFlowEnterpriseClient(
    base_url="https://api.ragflow.company.com",
    jwt_secret="your-secret-key"
)

# 生成Token并登录
token = client.generate_enterprise_token(
    user_id="emp_001",
    email="admin@company.com",
    nickname="管理员",
    role="enterprise_admin",
    tenant_id="company_001"
)

login_result = client.enterprise_login(token)
print("登录结果:", login_result)

if login_result["code"] == 0:
    permissions = client.get_permissions()
    print("用户权限:", permissions)
```

### JavaScript SDK

```javascript
class RAGFlowEnterpriseClient {
    constructor(baseUrl, jwtSecret) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.jwtSecret = jwtSecret;
        this.accessToken = null;
    }
    
    generateEnterpriseToken(userId, email, nickname, role, tenantId) {
        const jwt = require('jsonwebtoken');
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
    
    async enterpriseLogin(enterpriseToken) {
        const response = await fetch(`${this.baseUrl}/v1/user/enterprise/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enterprise_token: enterpriseToken })
        });
        
        const result = await response.json();
        
        if (result.code === 0) {
            this.accessToken = result.data.access_token;
        }
        
        return result;
    }
    
    async verifyUser() {
        const response = await fetch(`${this.baseUrl}/v1/user/enterprise/verify`, {
            headers: { 'Authorization': `Bearer ${this.accessToken}` }
        });
        
        return await response.json();
    }
    
    async getPermissions() {
        const response = await fetch(`${this.baseUrl}/v1/user/enterprise/permissions`, {
            headers: { 'Authorization': `Bearer ${this.accessToken}` }
        });
        
        return await response.json();
    }
}

// 使用示例
const client = new RAGFlowEnterpriseClient(
    'https://api.ragflow.company.com',
    'your-secret-key'
);

(async () => {
    try {
        const token = client.generateEnterpriseToken(
            'emp_001',
            'admin@company.com',
            '管理员',
            'enterprise_admin',
            'company_001'
        );
        
        const loginResult = await client.enterpriseLogin(token);
        console.log('登录结果:', loginResult);
        
        if (loginResult.code === 0) {
            const permissions = await client.getPermissions();
            console.log('用户权限:', permissions);
        }
    } catch (error) {
        console.error('操作失败:', error);
    }
})();
```

---

## 🔧 测试工具

### Postman Collection

```json
{
  "info": {
    "name": "RAGFlow Enterprise Auth API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.ragflow.company.com"
    },
    {
      "key": "enterprise_token",
      "value": "{{enterprise_token}}"
    },
    {
      "key": "access_token",
      "value": "{{access_token}}"
    }
  ],
  "item": [
    {
      "name": "Enterprise Login",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/v1/user/enterprise/login",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"enterprise_token\": \"{{enterprise_token}}\"\n}"
        }
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "if (pm.response.code === 200) {",
              "  const jsonData = pm.response.json();",
              "  if (jsonData.code === 0) {",
              "    pm.environment.set('access_token', jsonData.data.access_token);",
              "  }",
              "}"
            ]
          }
        }
      ]
    },
    {
      "name": "Verify User",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/v1/user/enterprise/verify",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ]
      }
    },
    {
      "name": "Get Permissions",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/v1/user/enterprise/permissions",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ]
      }
    }
  ]
}
```

### cURL 测试脚本

```bash
#!/bin/bash
# RAGFlow Enterprise Auth API 测试脚本

BASE_URL="https://api.ragflow.company.com"
JWT_SECRET="your-secret-key"

# 生成测试Token（需要Python和PyJWT）
generate_token() {
    python3 -c "
import jwt
import time

payload = {
    'user_id': 'test_user_001',
    'email': 'test@company.com',
    'nickname': '测试用户',
    'role': 'enterprise_admin',
    'tenant_id': 'test_tenant_001',
    'iat': int(time.time()),
    'exp': int(time.time()) + 3600,
    'jti': f'test_user_001_{int(time.time())}'
}

token = jwt.encode(payload, '$JWT_SECRET', algorithm='HS256')
print(token)
"
}

echo "=== RAGFlow Enterprise Auth API 测试 ==="

# 1. 生成Token
echo "1. 生成企业Token..."
ENTERPRISE_TOKEN=$(generate_token)
echo "Token: ${ENTERPRISE_TOKEN:0:50}..."

# 2. 企业登录
echo -e "\n2. 企业用户登录..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/v1/user/enterprise/login" \
  -H "Content-Type: application/json" \
  -d "{\"enterprise_token\": \"$ENTERPRISE_TOKEN\"}")

echo "登录响应: $LOGIN_RESPONSE"

# 提取access_token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('code') == 0:
        print(data['data']['access_token'])
    else:
        print('LOGIN_FAILED')
except:
    print('PARSE_ERROR')
")

if [ "$ACCESS_TOKEN" = "LOGIN_FAILED" ] || [ "$ACCESS_TOKEN" = "PARSE_ERROR" ]; then
    echo "登录失败，终止测试"
    exit 1
fi

echo "Access Token: ${ACCESS_TOKEN:0:50}..."

# 3. 验证用户
echo -e "\n3. 验证用户身份..."
curl -s -X GET "$BASE_URL/v1/user/enterprise/verify" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# 4. 获取权限
echo -e "\n4. 获取用户权限..."
curl -s -X GET "$BASE_URL/v1/user/enterprise/permissions" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# 5. 注销
echo -e "\n5. 用户注销..."
curl -s -X POST "$BASE_URL/v1/user/enterprise/logout" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

echo -e "\n=== 测试完成 ==="
```

---

## 📋 接口变更日志

### v1.2 (2024-03-01)
- 新增批量用户管理接口
- 新增IP白名单管理接口
- 优化安全事件查询性能
- 新增地理位置信息记录

### v1.1 (2024-02-01)
- 新增安全监控相关接口
- 新增安全配置管理接口
- 优化错误码体系
- 新增请求ID追踪

### v1.0 (2024-01-15)
- 初始版本发布
- 基础企业认证功能
- 用户权限管理
- JWT Token 认证

---

## 📞 技术支持

### 联系方式
- **技术支持邮箱**: api-support@infiniflow.io
- **企业服务**: enterprise@infiniflow.io
- **安全问题**: security@infiniflow.io

### 支持时间
- **工作日**: 9:00 - 18:00 (GMT+8)
- **紧急问题**: 24/7 响应
- **SLA**: 4小时内响应

### 相关文档
- [企业认证集成指南](enterprise_integration_guide.md)
- [安全最佳实践](security_best_practices.md)
- [故障排除指南](troubleshooting_guide.md)

---

<div align="center">
  <p><strong>© 2024 InfiniFlow. All rights reserved.</strong></p>
  <p>本文档内容受版权保护，未经授权不得复制或传播。</p>
</div> 