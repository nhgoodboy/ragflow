#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import jwt
import logging
from datetime import datetime
from typing import Dict, Optional
from werkzeug.security import generate_password_hash

from api.db import UserTenantRole, StatusEnum
from api.db.db_models import User, Tenant, UserTenant
from api.db.services.user_service import UserService, TenantService, UserTenantService
from api.db.services.common_service import CommonService
from api.utils import get_uuid, current_timestamp, datetime_format, get_format_time
from api import settings
from api.utils.enterprise_security import EnterpriseSecurityManager
from flask import request


class EnterpriseAuthService(CommonService):
    """企业认证服务类
    
    提供企业系统JWT token验证、用户管理和权限映射功能
    """
    
    @staticmethod
    def verify_enterprise_token(token: str) -> Optional[Dict]:
        """验证企业JWT token
        
        Args:
            token: 企业系统生成的JWT token
            
        Returns:
            解析后的用户信息字典，验证失败返回None
        """
        try:
            if not hasattr(settings, 'ENTERPRISE_AUTH') or not settings.ENTERPRISE_AUTH.get('enabled', False):
                logging.warning("Enterprise authentication is not enabled")
                return None
                
            jwt_secret = settings.ENTERPRISE_AUTH.get('jwt_secret')
            if not jwt_secret:
                logging.error("Enterprise JWT secret not configured")
                return None
                
            # 解码并验证JWT token
            payload = jwt.decode(
                token, 
                jwt_secret, 
                algorithms=['HS256'],
                options={"verify_exp": True, "verify_iat": True}
            )
            
            # 验证必需字段
            required_fields = ['user_id', 'email', 'nickname', 'role', 'tenant_id']
            for field in required_fields:
                if field not in payload:
                    logging.error(f"Missing required field in enterprise token: {field}")
                    return None
                    
            # 验证角色是否有效
            valid_roles = settings.ENTERPRISE_AUTH.get('role_mapping', {}).keys()
            if payload['role'] not in valid_roles:
                logging.error(f"Invalid enterprise role: {payload['role']}")
                return None
            
            # 安全验证
            client_ip = request.remote_addr if request else None
            security_valid, security_msg = EnterpriseSecurityManager.validate_token_security(payload, client_ip)
            if not security_valid:
                logging.warning(f"Enterprise token security validation failed: {security_msg}")
                # 记录安全事件
                EnterpriseSecurityManager.log_security_event(
                    'token_validation_failed', 
                    payload.get('user_id'), 
                    {'reason': security_msg},
                    success=False,
                    client_ip=client_ip
                )
                return None
            
            # 记录成功的token验证
            EnterpriseSecurityManager.log_security_event(
                'token_validation_success', 
                payload.get('user_id'), 
                success=True,
                client_ip=client_ip
            )
                
            return payload
            
        except jwt.ExpiredSignatureError:
            logging.warning("Enterprise token has expired")
            EnterpriseSecurityManager.log_security_event(
                'token_expired', 
                None, 
                success=False
            )
            return None
        except jwt.InvalidTokenError as e:
            logging.warning(f"Invalid enterprise token: {str(e)}")
            EnterpriseSecurityManager.log_security_event(
                'invalid_token', 
                None, 
                {'error': str(e)},
                success=False
            )
            return None
        except Exception as e:
            logging.error(f"Error verifying enterprise token: {str(e)}")
            return None
    
    @staticmethod
    def create_or_update_user(user_data: Dict) -> Optional[User]:
        """创建或更新企业用户
        
        Args:
            user_data: 从JWT token解析的用户数据
            
        Returns:
            User对象，创建失败返回None
        """
        try:
            enterprise_user_id = user_data['user_id']
            email = user_data['email']
            nickname = user_data['nickname']
            enterprise_role = user_data['role']
            enterprise_tenant_id = user_data['tenant_id']
            
            client_ip = request.remote_addr if request else None
            
            # 检查可疑活动
            if EnterpriseSecurityManager.is_suspicious_activity(enterprise_user_id, client_ip):
                logging.warning(f"Suspicious activity detected for user {enterprise_user_id}")
                EnterpriseSecurityManager.log_security_event(
                    'suspicious_activity', 
                    enterprise_user_id, 
                    success=False,
                    client_ip=client_ip
                )
                return None
            
            # 检查是否已存在企业用户
            existing_users = UserService.query(enterprise_user_id=enterprise_user_id)
            
            if existing_users:
                # 更新现有用户
                user = existing_users[0]
                update_data = {
                    'nickname': nickname,
                    'email': email,
                    'last_login_time': get_format_time(),
                    'update_time': current_timestamp(),
                    'update_date': datetime_format(datetime.now())
                }
                UserService.update_by_id(user.id, update_data)
                user = UserService.filter_by_id(user.id)
                
                # 记录成功的用户更新
                EnterpriseSecurityManager.log_security_event(
                    'enterprise_user_updated', 
                    enterprise_user_id, 
                    {'email': email, 'nickname': nickname},
                    success=True,
                    client_ip=client_ip
                )
                
                # 清除登录失败记录
                EnterpriseSecurityManager.clear_login_failures(enterprise_user_id, client_ip)
                
                logging.info(f"Updated enterprise user: {email}")
                return user
            else:
                # 检查邮箱是否已被其他用户使用
                email_users = UserService.query(email=email)
                if email_users:
                    # 如果邮箱已存在但不是企业用户，更新为企业用户
                    user = email_users[0]
                    update_data = {
                        'enterprise_user_id': enterprise_user_id,
                        'enterprise_source': 'enterprise_system',
                        'nickname': nickname,
                        'last_login_time': get_format_time(),
                        'update_time': current_timestamp(),
                        'update_date': datetime_format(datetime.now())
                    }
                    UserService.update_by_id(user.id, update_data)
                    user = UserService.filter_by_id(user.id)
                else:
                    # 创建新的企业用户
                    user_id = get_uuid()
                    user_info = {
                        'id': user_id,
                        'enterprise_user_id': enterprise_user_id,
                        'enterprise_source': 'enterprise_system',
                        'email': email,
                        'nickname': nickname,
                        'password': generate_password_hash(get_uuid()),  # 随机密码，企业用户不使用
                        'access_token': get_uuid(),
                        'login_channel': 'enterprise',
                        'last_login_time': get_format_time(),
                        'is_superuser': False,
                        'status': StatusEnum.VALID.value
                    }
                    
                    if not UserService.save(**user_info):
                        logging.error(f"Failed to create enterprise user: {email}")
                        EnterpriseSecurityManager.log_security_event(
                            'enterprise_user_creation_failed', 
                            enterprise_user_id, 
                            {'email': email},
                            success=False,
                            client_ip=client_ip
                        )
                        return None
                        
                    user = UserService.filter_by_id(user_id)
                
                # 创建或更新租户关系
                EnterpriseAuthService._ensure_user_tenant_relationship(
                    user, enterprise_role, enterprise_tenant_id
                )
                
                # 记录成功的用户创建
                EnterpriseSecurityManager.log_security_event(
                    'enterprise_user_created', 
                    enterprise_user_id, 
                    {'email': email, 'nickname': nickname, 'role': enterprise_role},
                    success=True,
                    client_ip=client_ip
                )
                
                # 清除登录失败记录
                EnterpriseSecurityManager.clear_login_failures(enterprise_user_id, client_ip)
                
                logging.info(f"Created enterprise user: {email}")
                return user
                
        except Exception as e:
            logging.error(f"Error creating/updating enterprise user: {str(e)}")
            # 记录用户创建/更新失败
            EnterpriseSecurityManager.record_login_failure(
                user_data.get('user_id', ''), 
                request.remote_addr if request else None
            )
            return None
    
    @staticmethod
    def _ensure_user_tenant_relationship(user: User, enterprise_role: str, enterprise_tenant_id: str):
        """确保用户-租户关系存在
        
        Args:
            user: 用户对象
            enterprise_role: 企业角色
            enterprise_tenant_id: 企业租户ID
        """
        try:
            # 映射企业角色到ragflow角色
            ragflow_role = EnterpriseAuthService.map_enterprise_role_to_ragflow(enterprise_role)
            
            # 检查用户是否已有租户关系
            user_tenants = UserTenantService.query(user_id=user.id)
            
            if user_tenants:
                # 更新现有租户关系的角色
                for user_tenant in user_tenants:
                    if user_tenant.role != ragflow_role:
                        UserTenantService.update_by_id(user_tenant.id, {'role': ragflow_role})
                        logging.info(f"Updated user {user.email} role to {ragflow_role}")
            else:
                # 创建新的租户关系
                # 使用用户ID作为租户ID（每个企业用户有自己的租户空间）
                tenant_id = user.id
                
                # 确保租户存在
                tenant = TenantService.query(id=tenant_id)
                if not tenant:
                    tenant_info = {
                        'id': tenant_id,
                        'name': f"{user.nickname}'s Enterprise Space",
                        'llm_id': settings.CHAT_MDL,
                        'embd_id': settings.EMBEDDING_MDL,
                        'asr_id': settings.ASR_MDL,
                        'parser_ids': settings.PARSERS,
                        'img2txt_id': settings.IMAGE2TEXT_MDL
                    }
                    TenantService.insert(**tenant_info)
                
                # 创建用户-租户关系
                user_tenant_info = {
                    'id': get_uuid(),
                    'tenant_id': tenant_id,
                    'user_id': user.id,
                    'role': ragflow_role,
                    'invited_by': user.id,
                    'status': StatusEnum.VALID.value
                }
                UserTenantService.save(**user_tenant_info)
                
                logging.info(f"Created tenant relationship for user {user.email} with role {ragflow_role}")
                
        except Exception as e:
            logging.error(f"Error ensuring user-tenant relationship: {str(e)}")
    
    @staticmethod
    def map_enterprise_role_to_ragflow(enterprise_role: str) -> UserTenantRole:
        """映射企业角色到ragflow角色
        
        Args:
            enterprise_role: 企业系统中的角色
            
        Returns:
            ragflow系统中对应的角色
        """
        role_mapping = settings.ENTERPRISE_AUTH.get('role_mapping', {})
        ragflow_role = role_mapping.get(enterprise_role, UserTenantRole.NORMAL)
        
        # 确保返回有效的ragflow角色
        if ragflow_role not in [UserTenantRole.OWNER, UserTenantRole.ADMIN, UserTenantRole.NORMAL]:
            logging.warning(f"Invalid ragflow role {ragflow_role}, defaulting to NORMAL")
            ragflow_role = UserTenantRole.NORMAL
            
        return ragflow_role
    
    @staticmethod
    def get_user_permissions(user: User) -> Dict[str, bool]:
        """获取用户权限列表
        
        Args:
            user: 用户对象
            
        Returns:
            权限字典
        """
        try:
            user_tenants = UserTenantService.query(user_id=user.id)
            if not user_tenants:
                return {
                    'can_manage_knowledge': False,
                    'can_chat': False,
                    'can_manage_users': False,
                    'can_access_system': False
                }
            
            # 取最高权限
            highest_role = UserTenantRole.NORMAL
            for user_tenant in user_tenants:
                if user_tenant.role == UserTenantRole.OWNER:
                    highest_role = UserTenantRole.OWNER
                    break
                elif user_tenant.role == UserTenantRole.ADMIN and highest_role != UserTenantRole.OWNER:
                    highest_role = UserTenantRole.ADMIN
            
            # 根据角色返回权限
            if highest_role == UserTenantRole.OWNER:
                return {
                    'can_manage_knowledge': True,
                    'can_chat': True,
                    'can_manage_users': True,
                    'can_access_system': True
                }
            elif highest_role == UserTenantRole.ADMIN:
                return {
                    'can_manage_knowledge': True,
                    'can_chat': True,
                    'can_manage_users': False,
                    'can_access_system': False
                }
            else:  # NORMAL
                return {
                    'can_manage_knowledge': False,
                    'can_chat': True,
                    'can_manage_users': False,
                    'can_access_system': False
                }
                
        except Exception as e:
            logging.error(f"Error getting user permissions: {str(e)}")
            return {
                'can_manage_knowledge': False,
                'can_chat': False,
                'can_manage_users': False,
                'can_access_system': False
            } 