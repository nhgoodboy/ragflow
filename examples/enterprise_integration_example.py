#!/usr/bin/env python3
"""
RAGFlow 企业集成示例代码
演示如何在企业系统中生成和使用JWT Token进行集成
"""

import jwt
import time
import requests
import json
from datetime import datetime, timedelta


class EnterpriseRAGFlowIntegration:
    """企业RAGFlow集成示例类"""
    
    def __init__(self, ragflow_url: str, jwt_secret: str):
        """
        初始化集成类
        
        Args:
            ragflow_url: RAGFlow系统的URL
            jwt_secret: 与RAGFlow共享的JWT密钥
        """
        self.ragflow_url = ragflow_url.rstrip('/')
        self.jwt_secret = jwt_secret
        
    def generate_enterprise_token(self, user_id: str, email: str, nickname: str, 
                                role: str, tenant_id: str, expires_in: int = 3600) -> str:
        """
        生成企业认证Token
        
        Args:
            user_id: 企业系统用户ID
            email: 用户邮箱
            nickname: 用户昵称
            role: 企业角色 (enterprise_admin 或 enterprise_user)
            tenant_id: 租户ID
            expires_in: Token有效期（秒），默认1小时
            
        Returns:
            JWT Token字符串
        """
        current_time = int(time.time())
        
        payload = {
            "user_id": user_id,
            "email": email,
            "nickname": nickname,
            "role": role,
            "tenant_id": tenant_id,
            "iat": current_time,
            "exp": current_time + expires_in,
            "jti": f"{user_id}_{current_time}"  # 防重放攻击
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        return token
    
    def verify_token(self, token: str) -> dict:
        """
        验证Token（用于调试）
        
        Args:
            token: JWT Token
            
        Returns:
            解码后的Token内容
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return {"valid": True, "payload": payload}
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token已过期"}
        except jwt.InvalidTokenError as e:
            return {"valid": False, "error": f"Token无效: {str(e)}"}
    
    def enterprise_login(self, token: str) -> dict:
        """
        使用企业Token登录RAGFlow
        
        Args:
            token: 企业JWT Token
            
        Returns:
            登录结果
        """
        url = f"{self.ragflow_url}/v1/user/enterprise/login"
        
        payload = {
            "enterprise_token": token
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            return response.json()
        except requests.RequestException as e:
            return {"code": 1, "message": f"请求失败: {str(e)}"}
    
    def get_user_permissions(self, access_token: str) -> dict:
        """
        获取用户权限
        
        Args:
            access_token: RAGFlow访问令牌
            
        Returns:
            用户权限信息
        """
        url = f"{self.ragflow_url}/v1/user/enterprise/permissions"
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            return response.json()
        except requests.RequestException as e:
            return {"code": 1, "message": f"请求失败: {str(e)}"}
    
    def generate_ragflow_url(self, user_id: str, email: str, nickname: str, 
                           role: str, tenant_id: str) -> str:
        """
        生成带有企业Token的RAGFlow访问URL
        
        Args:
            user_id: 企业用户ID
            email: 用户邮箱
            nickname: 用户昵称
            role: 企业角色
            tenant_id: 租户ID
            
        Returns:
            完整的RAGFlow访问URL
        """
        token = self.generate_enterprise_token(user_id, email, nickname, role, tenant_id)
        return f"{self.ragflow_url}?enterprise_token={token}"


def test_enterprise_integration():
    """测试企业集成功能"""
    
    # 配置参数 - 请根据实际环境修改
    RAGFLOW_URL = "http://localhost:9380"  # RAGFlow系统URL
    JWT_SECRET = "your-shared-secret-key"   # 与RAGFlow配置文件中相同的密钥
    
    # 创建集成实例
    integration = EnterpriseRAGFlowIntegration(RAGFLOW_URL, JWT_SECRET)
    
    # 测试用户数据
    test_users = [
        {
            "user_id": "admin_001",
            "email": "admin@company.com",
            "nickname": "系统管理员",
            "role": "enterprise_admin",
            "tenant_id": "company_001"
        },
        {
            "user_id": "user_001", 
            "email": "user@company.com",
            "nickname": "普通用户",
            "role": "enterprise_user",
            "tenant_id": "company_001"
        }
    ]
    
    print("=== RAGFlow 企业集成测试 ===\n")
    
    for user in test_users:
        print(f"测试用户: {user['nickname']} ({user['role']})")
        print("-" * 50)
        
        # 1. 生成Token
        print("1. 生成企业Token...")
        token = integration.generate_enterprise_token(**user)
        print(f"Token: {token[:50]}...")
        
        # 2. 验证Token格式
        print("\n2. 验证Token格式...")
        verification = integration.verify_token(token)
        if verification["valid"]:
            print("✓ Token格式有效")
            print(f"  用户ID: {verification['payload']['user_id']}")
            print(f"  角色: {verification['payload']['role']}")
            print(f"  过期时间: {datetime.fromtimestamp(verification['payload']['exp'])}")
        else:
            print(f"✗ Token验证失败: {verification['error']}")
            continue
        
        # 3. 尝试登录
        print("\n3. 尝试企业登录...")
        login_result = integration.enterprise_login(token)
        if login_result.get("code") == 0:
            print("✓ 企业登录成功")
            user_data = login_result["data"]
            print(f"  用户ID: {user_data['id']}")
            print(f"  昵称: {user_data['nickname']}")
            print(f"  邮箱: {user_data['email']}")
            
            # 4. 获取权限信息
            print("\n4. 获取用户权限...")
            access_token = user_data["access_token"]
            permissions_result = integration.get_user_permissions(access_token)
            if permissions_result.get("code") == 0:
                print("✓ 权限获取成功")
                permissions = permissions_result["data"]
                for perm, value in permissions.items():
                    status = "✓" if value else "✗"
                    print(f"  {status} {perm}: {value}")
            else:
                print(f"✗ 权限获取失败: {permissions_result.get('message')}")
        else:
            print(f"✗ 企业登录失败: {login_result.get('message')}")
        
        # 5. 生成访问URL
        print("\n5. 生成RAGFlow访问URL...")
        ragflow_url = integration.generate_ragflow_url(**user)
        print(f"访问URL: {ragflow_url[:100]}...")
        
        print("\n" + "=" * 80 + "\n")


def create_enterprise_user_management_demo():
    """演示企业用户管理功能"""
    
    class EnterpriseUserManager:
        """企业用户管理示例类"""
        
        def __init__(self, integration: EnterpriseRAGFlowIntegration):
            self.integration = integration
            self.users_db = {}  # 模拟用户数据库
        
        def add_user(self, user_id: str, email: str, nickname: str, role: str, tenant_id: str):
            """添加企业用户"""
            self.users_db[user_id] = {
                "user_id": user_id,
                "email": email,
                "nickname": nickname,
                "role": role,
                "tenant_id": tenant_id,
                "created_at": datetime.now(),
                "last_login": None
            }
            print(f"用户 {nickname} 已添加到企业系统")
        
        def get_ragflow_access_url(self, user_id: str) -> str:
            """为指定用户生成RAGFlow访问URL"""
            if user_id not in self.users_db:
                raise ValueError(f"用户 {user_id} 不存在")
            
            user = self.users_db[user_id]
            url = self.integration.generate_ragflow_url(**user)
            
            # 更新最后登录时间
            self.users_db[user_id]["last_login"] = datetime.now()
            
            return url
        
        def list_users(self):
            """列出所有用户"""
            print("企业用户列表:")
            print("-" * 60)
            for user_id, user in self.users_db.items():
                last_login = user["last_login"].strftime("%Y-%m-%d %H:%M:%S") if user["last_login"] else "从未登录"
                print(f"ID: {user_id}, 姓名: {user['nickname']}, 角色: {user['role']}, 最后登录: {last_login}")
    
    # 使用示例
    print("=== 企业用户管理演示 ===\n")
    
    integration = EnterpriseRAGFlowIntegration("http://localhost:9380", "demo-secret-key")
    user_manager = EnterpriseUserManager(integration)
    
    # 添加用户
    user_manager.add_user("mgr_001", "manager@company.com", "部门经理", "enterprise_admin", "dept_001")
    user_manager.add_user("emp_001", "employee@company.com", "员工", "enterprise_user", "dept_001")
    user_manager.add_user("emp_002", "employee2@company.com", "员工2", "enterprise_user", "dept_001")
    
    print()
    user_manager.list_users()
    
    # 生成访问URL
    print(f"\n为部门经理生成RAGFlow访问URL:")
    manager_url = user_manager.get_ragflow_access_url("mgr_001")
    print(f"URL: {manager_url[:80]}...")
    
    print()
    user_manager.list_users()


if __name__ == "__main__":
    """运行测试和演示"""
    
    print("RAGFlow 企业集成示例\n")
    print("请确保:")
    print("1. RAGFlow系统正在运行")
    print("2. 企业认证功能已启用")
    print("3. JWT密钥配置正确")
    print("\n" + "=" * 60 + "\n")
    
    # 运行集成测试
    test_enterprise_integration()
    
    # 运行用户管理演示
    create_enterprise_user_management_demo()
    
    print("演示完成！")
    print("\n集成步骤总结:")
    print("1. 在企业系统中生成JWT Token")
    print("2. 将Token作为URL参数传递给RAGFlow")
    print("3. RAGFlow自动验证Token并创建/登录用户")
    print("4. 根据角色分配相应权限")
    print("5. 用户可以使用RAGFlow功能") 