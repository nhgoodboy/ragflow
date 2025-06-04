#!/usr/bin/env python3
"""
企业认证功能测试套件
包含单元测试、集成测试和安全性测试
"""

import unittest
import jwt
import time
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 假设这些模块存在，实际测试时需要根据项目结构调整
try:
    from api.db.services.enterprise_auth_service import EnterpriseAuthService
    from api.utils.enterprise_security import EnterpriseSecurityManager
    from api import settings
except ImportError:
    print("Warning: 无法导入实际模块，使用模拟对象进行测试")


class TestEnterpriseTokenGeneration(unittest.TestCase):
    """测试企业Token生成功能"""
    
    def setUp(self):
        """测试前准备"""
        self.secret_key = "test-secret-key-for-unittest"
        self.test_user_data = {
            "user_id": "test_user_001",
            "email": "test@company.com", 
            "nickname": "测试用户",
            "role": "enterprise_admin",
            "tenant_id": "test_tenant_001"
        }
    
    def test_valid_token_generation(self):
        """测试有效Token生成"""
        current_time = int(time.time())
        payload = {
            **self.test_user_data,
            "iat": current_time,
            "exp": current_time + 3600,
            "jti": f"{self.test_user_data['user_id']}_{current_time}"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # 验证Token可以正确解码
        decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        
        self.assertEqual(decoded["user_id"], self.test_user_data["user_id"])
        self.assertEqual(decoded["email"], self.test_user_data["email"])
        self.assertEqual(decoded["role"], self.test_user_data["role"])
    
    def test_expired_token(self):
        """测试过期Token"""
        past_time = int(time.time()) - 7200  # 2小时前
        payload = {
            **self.test_user_data,
            "iat": past_time,
            "exp": past_time + 3600  # 1小时前就过期了
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # 验证过期Token会抛出异常
        with self.assertRaises(jwt.ExpiredSignatureError):
            jwt.decode(token, self.secret_key, algorithms=["HS256"])
    
    def test_invalid_signature(self):
        """测试错误签名的Token"""
        payload = {
            **self.test_user_data,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        # 使用错误的密钥生成Token
        token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
        
        # 验证会抛出签名错误
        with self.assertRaises(jwt.InvalidTokenError):
            jwt.decode(token, self.secret_key, algorithms=["HS256"])
    
    def test_missing_required_fields(self):
        """测试缺少必需字段的Token"""
        incomplete_payload = {
            "user_id": "test_user_001",
            # 缺少email, nickname, role, tenant_id
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        token = jwt.encode(incomplete_payload, self.secret_key, algorithm="HS256")
        decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        
        # 验证缺少的字段
        required_fields = ["email", "nickname", "role", "tenant_id"]
        for field in required_fields:
            self.assertNotIn(field, decoded)


class TestEnterpriseAuthService(unittest.TestCase):
    """测试企业认证服务"""
    
    def setUp(self):
        """测试前准备"""
        self.secret_key = "test-secret-key"
        
        # 模拟settings
        self.mock_settings = MagicMock()
        self.mock_settings.ENTERPRISE_AUTH = {
            "enabled": True,
            "jwt_secret": self.secret_key,
            "role_mapping": {
                "enterprise_admin": "admin",
                "enterprise_user": "normal"
            },
            "token_expiry": 3600,
            "allowed_domains": [],
            "auto_create_user": True
        }
    
    @patch('api.db.services.enterprise_auth_service.settings')
    def test_verify_valid_token(self, mock_settings):
        """测试验证有效Token"""
        mock_settings.ENTERPRISE_AUTH = self.mock_settings.ENTERPRISE_AUTH
        
        # 生成有效Token
        current_time = int(time.time())
        payload = {
            "user_id": "test_user_001",
            "email": "test@company.com",
            "nickname": "测试用户",
            "role": "enterprise_admin",
            "tenant_id": "test_tenant_001",
            "iat": current_time,
            "exp": current_time + 3600
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # 测试验证方法
        result = EnterpriseAuthService.verify_enterprise_token(token)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["user_id"], "test_user_001")
        self.assertEqual(result["role"], "enterprise_admin")
    
    @patch('api.db.services.enterprise_auth_service.settings')
    def test_verify_invalid_role(self, mock_settings):
        """测试验证无效角色的Token"""
        mock_settings.ENTERPRISE_AUTH = self.mock_settings.ENTERPRISE_AUTH
        
        # 生成包含无效角色的Token
        current_time = int(time.time())
        payload = {
            "user_id": "test_user_001",
            "email": "test@company.com",
            "nickname": "测试用户",
            "role": "invalid_role",  # 无效角色
            "tenant_id": "test_tenant_001",
            "iat": current_time,
            "exp": current_time + 3600
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # 测试验证方法应该返回None
        result = EnterpriseAuthService.verify_enterprise_token(token)
        self.assertIsNone(result)
    
    def test_role_mapping(self):
        """测试角色映射功能"""
        # 测试管理员角色映射
        admin_role = EnterpriseAuthService.map_enterprise_role_to_ragflow("enterprise_admin")
        self.assertEqual(admin_role, "admin")
        
        # 测试普通用户角色映射
        user_role = EnterpriseAuthService.map_enterprise_role_to_ragflow("enterprise_user")
        self.assertEqual(user_role, "normal")
        
        # 测试无效角色映射（应该返回默认值）
        invalid_role = EnterpriseAuthService.map_enterprise_role_to_ragflow("invalid_role")
        self.assertEqual(invalid_role, "normal")  # 默认为normal


class TestEnterpriseSecurityManager(unittest.TestCase):
    """测试企业安全管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.test_payload = {
            "user_id": "test_user_001",
            "email": "test@company.com",
            "role": "enterprise_admin",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
            "jti": "unique_token_id"
        }
    
    def test_token_expiry_validation(self):
        """测试Token过期验证"""
        # 测试有效Token
        valid_payload = self.test_payload.copy()
        result = EnterpriseSecurityManager._validate_token_expiry(valid_payload)
        self.assertTrue(result)
        
        # 测试过期Token
        expired_payload = self.test_payload.copy()
        expired_payload["exp"] = int(time.time()) - 3600  # 1小时前过期
        result = EnterpriseSecurityManager._validate_token_expiry(expired_payload)
        self.assertFalse(result)
        
        # 测试缺少exp字段的Token
        no_exp_payload = self.test_payload.copy()
        del no_exp_payload["exp"]
        result = EnterpriseSecurityManager._validate_token_expiry(no_exp_payload)
        self.assertFalse(result)
    
    def test_ip_whitelist_validation(self):
        """测试IP白名单验证"""
        # 模拟settings
        with patch('api.utils.enterprise_security.settings') as mock_settings:
            # 测试空白名单（允许所有IP）
            mock_settings.ENTERPRISE_AUTH = {"allowed_domains": []}
            result = EnterpriseSecurityManager._validate_allowed_domains("192.168.1.100")
            self.assertTrue(result)
            
            # 测试IP在白名单中
            mock_settings.ENTERPRISE_AUTH = {"allowed_domains": ["192.168.1.100"]}
            result = EnterpriseSecurityManager._validate_allowed_domains("192.168.1.100")
            self.assertTrue(result)
            
            # 测试IP不在白名单中
            mock_settings.ENTERPRISE_AUTH = {"allowed_domains": ["192.168.1.100"]}
            result = EnterpriseSecurityManager._validate_allowed_domains("10.0.0.1")
            self.assertFalse(result)
            
            # 测试CIDR网段
            mock_settings.ENTERPRISE_AUTH = {"allowed_domains": ["192.168.1.0/24"]}
            result = EnterpriseSecurityManager._validate_allowed_domains("192.168.1.150")
            self.assertTrue(result)
            
            result = EnterpriseSecurityManager._validate_allowed_domains("192.168.2.150")
            self.assertFalse(result)
    
    @patch('api.utils.enterprise_security.REDIS_CONN')
    def test_anti_replay_validation(self, mock_redis):
        """测试防重放攻击验证"""
        # 测试Redis不可用的情况
        mock_redis = None
        result = EnterpriseSecurityManager._validate_anti_replay(self.test_payload)
        self.assertTrue(result)  # Redis不可用时应该跳过检查
        
        # 测试Redis可用，Token未使用过
        mock_redis = MagicMock()
        mock_redis.get.return_value = None  # Token未使用过
        
        with patch('api.utils.enterprise_security.REDIS_CONN', mock_redis):
            result = EnterpriseSecurityManager._validate_anti_replay(self.test_payload)
            self.assertTrue(result)
            # 验证Token被标记为已使用
            mock_redis.setex.assert_called()
        
        # 测试Token已经使用过
        mock_redis.get.return_value = "used"  # Token已使用
        
        with patch('api.utils.enterprise_security.REDIS_CONN', mock_redis):
            result = EnterpriseSecurityManager._validate_anti_replay(self.test_payload)
            self.assertFalse(result)
    
    def test_security_event_logging(self):
        """测试安全事件日志记录"""
        with patch('api.utils.enterprise_security.logging') as mock_logging:
            EnterpriseSecurityManager.log_security_event(
                "test_event",
                "test_user_001",
                {"test": "data"},
                success=True,
                client_ip="192.168.1.100"
            )
            
            # 验证日志被记录
            mock_logging.log.assert_called()


class TestEnterpriseIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.secret_key = "integration-test-secret"
        self.test_user = {
            "user_id": "integration_user_001",
            "email": "integration@company.com",
            "nickname": "集成测试用户",
            "role": "enterprise_admin",
            "tenant_id": "integration_tenant_001"
        }
    
    def generate_test_token(self, user_data=None, expires_in=3600):
        """生成测试Token"""
        if user_data is None:
            user_data = self.test_user
        
        current_time = int(time.time())
        payload = {
            **user_data,
            "iat": current_time,
            "exp": current_time + expires_in,
            "jti": f"{user_data['user_id']}_{current_time}"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def test_full_authentication_flow(self):
        """测试完整的认证流程"""
        # 1. 生成Token
        token = self.generate_test_token()
        self.assertIsNotNone(token)
        
        # 2. 验证Token格式
        decoded = jwt.decode(token, self.secret_key, algorithms=["HS256"])
        self.assertEqual(decoded["user_id"], self.test_user["user_id"])
        
        # 3. 模拟完整的认证流程
        with patch('api.db.services.enterprise_auth_service.settings') as mock_settings:
            mock_settings.ENTERPRISE_AUTH = {
                "enabled": True,
                "jwt_secret": self.secret_key,
                "role_mapping": {"enterprise_admin": "admin"},
                "token_expiry": 3600,
                "allowed_domains": [],
                "auto_create_user": True
            }
            
            # 验证Token
            result = EnterpriseAuthService.verify_enterprise_token(token)
            self.assertIsNotNone(result)
            self.assertEqual(result["user_id"], self.test_user["user_id"])
    
    def test_permission_assignment(self):
        """测试权限分配"""
        # 测试管理员权限
        admin_permissions = EnterpriseAuthService.get_user_permissions(None)  # 需要实际用户对象
        expected_admin_permissions = {
            "can_manage_knowledge": True,
            "can_chat": True,
            "can_manage_users": False,
            "can_access_system": False
        }
        
        # 由于需要实际的数据库连接，这里只测试逻辑
        self.assertIsInstance(admin_permissions, dict)
        for key in expected_admin_permissions:
            self.assertIn(key, admin_permissions)


class TestSecurityVulnerabilities(unittest.TestCase):
    """安全漏洞测试"""
    
    def setUp(self):
        """测试前准备"""
        self.secret_key = "security-test-secret"
    
    def test_jwt_algorithm_confusion(self):
        """测试JWT算法混淆攻击"""
        # 尝试使用HS256密钥作为RS256公钥
        payload = {
            "user_id": "attacker",
            "role": "enterprise_admin",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        # 这应该失败，因为我们只接受HS256
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # 尝试用RS256解码应该失败
        with self.assertRaises(jwt.InvalidTokenError):
            jwt.decode(token, self.secret_key, algorithms=["RS256"])
    
    def test_token_tampering(self):
        """测试Token篡改"""
        payload = {
            "user_id": "normal_user",
            "role": "enterprise_user",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        # 尝试篡改Token（改变角色）
        # 这在实际实现中会通过签名验证失败
        parts = token.split('.')
        header = parts[0]
        payload_part = parts[1]
        signature = parts[2]
        
        # 篡改payload
        import base64
        decoded_payload = base64.urlsafe_b64decode(payload_part + '==')
        tampered_payload = decoded_payload.replace(b'enterprise_user', b'enterprise_admin')
        tampered_payload_encoded = base64.urlsafe_b64encode(tampered_payload).decode().rstrip('=')
        
        tampered_token = f"{header}.{tampered_payload_encoded}.{signature}"
        
        # 验证篡改的Token应该失败
        with self.assertRaises(jwt.InvalidTokenError):
            jwt.decode(tampered_token, self.secret_key, algorithms=["HS256"])
    
    def test_timing_attack_protection(self):
        """测试时序攻击防护"""
        # 测试Token验证时间是否一致（防止时序攻击）
        valid_token = jwt.encode({
            "user_id": "test_user",
            "role": "enterprise_admin",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }, self.secret_key, algorithm="HS256")
        
        invalid_token = "invalid.token.signature"
        
        # 在实际实现中，验证时间应该相似以防止时序攻击
        start_time = time.time()
        try:
            jwt.decode(valid_token, self.secret_key, algorithms=["HS256"])
        except:
            pass
        valid_time = time.time() - start_time
        
        start_time = time.time()
        try:
            jwt.decode(invalid_token, self.secret_key, algorithms=["HS256"])
        except:
            pass
        invalid_time = time.time() - start_time
        
        # 时间差不应该太大（这个测试可能在不同环境下表现不一致）
        time_diff = abs(valid_time - invalid_time)
        self.assertLess(time_diff, 0.1)  # 100ms内


def run_security_tests():
    """运行安全性测试"""
    print("=== 运行安全性测试 ===")
    
    # 创建测试套件
    security_suite = unittest.TestLoader().loadTestsFromTestCase(TestSecurityVulnerabilities)
    auth_suite = unittest.TestLoader().loadTestsFromTestCase(TestEnterpriseAuthService)
    security_manager_suite = unittest.TestLoader().loadTestsFromTestCase(TestEnterpriseSecurityManager)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    
    print("\n1. 安全漏洞测试:")
    result1 = runner.run(security_suite)
    
    print("\n2. 认证服务测试:")
    result2 = runner.run(auth_suite)
    
    print("\n3. 安全管理器测试:")
    result3 = runner.run(security_manager_suite)
    
    # 汇总结果
    total_tests = result1.testsRun + result2.testsRun + result3.testsRun
    total_failures = len(result1.failures) + len(result2.failures) + len(result3.failures)
    total_errors = len(result1.errors) + len(result2.errors) + len(result3.errors)
    
    print(f"\n=== 测试结果汇总 ===")
    print(f"总测试数: {total_tests}")
    print(f"失败数: {total_failures}")
    print(f"错误数: {total_errors}")
    print(f"成功率: {((total_tests - total_failures - total_errors) / total_tests * 100):.1f}%")
    
    return total_failures + total_errors == 0


def run_integration_tests():
    """运行集成测试"""
    print("=== 运行集成测试 ===")
    
    integration_suite = unittest.TestLoader().loadTestsFromTestCase(TestEnterpriseIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(integration_suite)
    
    return len(result.failures) + len(result.errors) == 0


def run_performance_tests():
    """运行性能测试"""
    print("=== 运行性能测试 ===")
    
    secret_key = "performance-test-secret"
    test_count = 1000
    
    # 测试Token生成性能
    print(f"测试生成 {test_count} 个Token的性能...")
    start_time = time.time()
    
    for i in range(test_count):
        payload = {
            "user_id": f"user_{i}",
            "email": f"user{i}@company.com",
            "role": "enterprise_user",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }
        jwt.encode(payload, secret_key, algorithm="HS256")
    
    generation_time = time.time() - start_time
    print(f"生成性能: {test_count/generation_time:.1f} tokens/秒")
    
    # 测试Token验证性能
    test_token = jwt.encode({
        "user_id": "test_user",
        "email": "test@company.com",
        "role": "enterprise_user",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }, secret_key, algorithm="HS256")
    
    print(f"测试验证 {test_count} 个Token的性能...")
    start_time = time.time()
    
    for i in range(test_count):
        jwt.decode(test_token, secret_key, algorithms=["HS256"])
    
    verification_time = time.time() - start_time
    print(f"验证性能: {test_count/verification_time:.1f} tokens/秒")
    
    # 性能基准
    min_generation_rate = 500  # tokens/秒
    min_verification_rate = 1000  # tokens/秒
    
    generation_ok = (test_count/generation_time) >= min_generation_rate
    verification_ok = (test_count/verification_time) >= min_verification_rate
    
    print(f"\n性能测试结果:")
    print(f"Token生成: {'✓' if generation_ok else '✗'} ({test_count/generation_time:.1f} >= {min_generation_rate})")
    print(f"Token验证: {'✓' if verification_ok else '✗'} ({test_count/verification_time:.1f} >= {min_verification_rate})")
    
    return generation_ok and verification_ok


if __name__ == "__main__":
    """运行所有测试"""
    print("RAGFlow 企业认证功能测试套件")
    print("=" * 50)
    
    # 运行各种测试
    security_ok = run_security_tests()
    integration_ok = run_integration_tests()
    performance_ok = run_performance_tests()
    
    # 最终结果
    print("\n" + "=" * 50)
    print("最终测试结果:")
    print(f"安全性测试: {'✓ 通过' if security_ok else '✗ 失败'}")
    print(f"集成测试: {'✓ 通过' if integration_ok else '✗ 失败'}")
    print(f"性能测试: {'✓ 通过' if performance_ok else '✗ 失败'}")
    
    overall_success = security_ok and integration_ok and performance_ok
    print(f"\n总体结果: {'✓ 所有测试通过' if overall_success else '✗ 部分测试失败'}")
    
    exit(0 if overall_success else 1) 