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

import logging
from flask import request
from flask_login import login_user, current_user, login_required

from api.db.services.enterprise_auth_service import EnterpriseAuthService
from api.utils.api_utils import (
    get_json_result,
    server_error_response,
    validate_request,
    construct_response
)
from api import settings


@manager.route("/enterprise/login", methods=["POST"])  # noqa: F821
@validate_request("enterprise_token")
def enterprise_login():
    """
    企业用户登录接口
    ---
    tags:
      - Enterprise Auth
    parameters:
      - in: body
        name: body
        description: 企业登录凭据
        required: true
        schema:
          type: object
          properties:
            enterprise_token:
              type: string
              description: 企业系统生成的JWT token
    responses:
      200:
        description: 登录成功
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                id:
                  type: string
                  description: 用户ID
                nickname:
                  type: string
                  description: 用户昵称
                email:
                  type: string
                  description: 用户邮箱
                permissions:
                  type: object
                  description: 用户权限
            message:
              type: string
              description: 响应消息
      401:
        description: 认证失败
        schema:
          type: object
          properties:
            code:
              type: integer
              description: 错误代码
            message:
              type: string
              description: 错误消息
    """
    try:
        enterprise_token = request.json.get("enterprise_token")
        
        # 验证企业token
        user_data = EnterpriseAuthService.verify_enterprise_token(enterprise_token)
        if not user_data:
            return get_json_result(
                data=False,
                code=settings.RetCode.AUTHENTICATION_ERROR,
                message="Invalid enterprise token"
            )
        
        # 创建或更新用户
        user = EnterpriseAuthService.create_or_update_user(user_data)
        if not user:
            return get_json_result(
                data=False,
                code=settings.RetCode.SERVER_ERROR,
                message="Failed to create or update user"
            )
        
        # 登录用户
        login_user(user)
        
        # 获取用户权限
        permissions = EnterpriseAuthService.get_user_permissions(user)
        
        # 构造响应数据
        response_data = {
            "id": user.id,
            "nickname": user.nickname,
            "email": user.email,
            "access_token": user.access_token,
            "permissions": permissions,
            "login_channel": "enterprise"
        }
        
        return construct_response(
            data=response_data,
            auth=user.get_id(),
            message="Enterprise login successful"
        )
        
    except Exception as e:
        logging.error(f"Enterprise login error: {str(e)}")
        return server_error_response(e)


@manager.route("/enterprise/verify", methods=["GET"])  # noqa: F821
@login_required
def verify_enterprise_user():
    """
    验证企业用户状态
    ---
    tags:
      - Enterprise Auth
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: 验证成功
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                user_id:
                  type: string
                  description: 用户ID
                enterprise_user_id:
                  type: string
                  description: 企业用户ID
                permissions:
                  type: object
                  description: 用户权限
                is_enterprise_user:
                  type: boolean
                  description: 是否为企业用户
            message:
              type: string
              description: 响应消息
      401:
        description: 未授权访问
    """
    try:
        # 检查是否为企业用户
        is_enterprise_user = bool(current_user.enterprise_user_id)
        
        # 获取用户权限
        permissions = EnterpriseAuthService.get_user_permissions(current_user)
        
        response_data = {
            "user_id": current_user.id,
            "enterprise_user_id": current_user.enterprise_user_id,
            "email": current_user.email,
            "nickname": current_user.nickname,
            "permissions": permissions,
            "is_enterprise_user": is_enterprise_user,
            "enterprise_source": current_user.enterprise_source
        }
        
        return get_json_result(data=response_data, message="User verification successful")
        
    except Exception as e:
        logging.error(f"Enterprise user verification error: {str(e)}")
        return server_error_response(e)


@manager.route("/enterprise/refresh", methods=["POST"])  # noqa: F821
@validate_request("enterprise_token")
def refresh_enterprise_token():
    """
    刷新企业用户token
    ---
    tags:
      - Enterprise Auth
    parameters:
      - in: body
        name: body
        description: 新的企业token
        required: true
        schema:
          type: object
          properties:
            enterprise_token:
              type: string
              description: 新的企业系统JWT token
    responses:
      200:
        description: 刷新成功
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                user_id:
                  type: string
                  description: 用户ID
                access_token:
                  type: string
                  description: 新的访问token
                permissions:
                  type: object
                  description: 更新后的权限
            message:
              type: string
              description: 响应消息
      401:
        description: token验证失败
    """
    try:
        enterprise_token = request.json.get("enterprise_token")
        
        # 验证新的企业token
        user_data = EnterpriseAuthService.verify_enterprise_token(enterprise_token)
        if not user_data:
            return get_json_result(
                data=False,
                code=settings.RetCode.AUTHENTICATION_ERROR,
                message="Invalid enterprise token for refresh"
            )
        
        # 更新用户信息
        user = EnterpriseAuthService.create_or_update_user(user_data)
        if not user:
            return get_json_result(
                data=False,
                code=settings.RetCode.SERVER_ERROR,
                message="Failed to refresh user data"
            )
        
        # 获取更新后的权限
        permissions = EnterpriseAuthService.get_user_permissions(user)
        
        response_data = {
            "user_id": user.id,
            "access_token": user.access_token,
            "permissions": permissions,
            "enterprise_user_id": user.enterprise_user_id
        }
        
        return get_json_result(data=response_data, message="Enterprise token refreshed successfully")
        
    except Exception as e:
        logging.error(f"Enterprise token refresh error: {str(e)}")
        return server_error_response(e)


@manager.route("/enterprise/permissions", methods=["GET"])  # noqa: F821
@login_required
def get_enterprise_permissions():
    """
    获取企业用户权限列表
    ---
    tags:
      - Enterprise Auth
    security:
      - ApiKeyAuth: []
    responses:
      200:
        description: 权限获取成功
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                can_manage_knowledge:
                  type: boolean
                  description: 是否可以管理知识库
                can_chat:
                  type: boolean
                  description: 是否可以聊天
                can_manage_users:
                  type: boolean
                  description: 是否可以管理用户
                can_access_system:
                  type: boolean
                  description: 是否可以访问系统设置
            message:
              type: string
              description: 响应消息
      401:
        description: 未授权访问
    """
    try:
        permissions = EnterpriseAuthService.get_user_permissions(current_user)
        
        return get_json_result(data=permissions, message="Permissions retrieved successfully")
        
    except Exception as e:
        logging.error(f"Get enterprise permissions error: {str(e)}")
        return server_error_response(e)


@manager.route("/enterprise/config", methods=["GET"])  # noqa: F821
def get_enterprise_config():
    """
    获取企业认证配置信息
    ---
    tags:
      - Enterprise Auth
    responses:
      200:
        description: 配置获取成功
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                enabled:
                  type: boolean
                  description: 企业认证是否启用
                supported_roles:
                  type: array
                  items:
                    type: string
                  description: 支持的企业角色列表
            message:
              type: string
              description: 响应消息
    """
    try:
        config_data = {
            "enabled": getattr(settings, 'ENTERPRISE_AUTH', {}).get('enabled', False),
            "supported_roles": list(getattr(settings, 'ENTERPRISE_AUTH', {}).get('role_mapping', {}).keys())
        }
        
        return get_json_result(data=config_data, message="Enterprise config retrieved successfully")
        
    except Exception as e:
        logging.error(f"Get enterprise config error: {str(e)}")
        return server_error_response(e) 