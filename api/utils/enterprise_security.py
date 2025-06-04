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

import time
import hashlib
import logging
import ipaddress
from typing import Dict, List, Optional, Tuple
from flask import request
from datetime import datetime, timedelta

from api import settings
from api.utils import current_timestamp
from rag.utils.redis_conn import REDIS_CONN


class EnterpriseSecurityManager:
    """企业认证安全管理器
    
    提供token安全验证、防重放攻击、审计日志等安全功能
    """
    
    # Redis key前缀
    TOKEN_NONCE_PREFIX = "enterprise_token_nonce:"
    RATE_LIMIT_PREFIX = "enterprise_rate_limit:"
    AUDIT_LOG_PREFIX = "enterprise_audit:"
    
    @staticmethod
    def validate_token_security(token_payload: Dict, client_ip: str = None) -> Tuple[bool, str]:
        """验证token安全性
        
        Args:
            token_payload: JWT token解析后的payload
            client_ip: 客户端IP地址
            
        Returns:
            (是否通过验证, 错误消息)
        """
        try:
            # 1. 验证token时效性
            if not EnterpriseSecurityManager._validate_token_expiry(token_payload):
                return False, "Token has expired"
            
            # 2. 验证来源域名/IP白名单
            if not EnterpriseSecurityManager._validate_allowed_domains(client_ip):
                return False, "Request from unauthorized domain/IP"
            
            # 3. 验证防重放攻击
            if not EnterpriseSecurityManager._validate_anti_replay(token_payload):
                return False, "Token replay attack detected"
            
            # 4. 验证速率限制
            if not EnterpriseSecurityManager._validate_rate_limit(token_payload.get('user_id', ''), client_ip):
                return False, "Rate limit exceeded"
            
            return True, "Token validation passed"
            
        except Exception as e:
            logging.error(f"Token security validation error: {str(e)}")
            return False, "Token security validation failed"
    
    @staticmethod
    def _validate_token_expiry(token_payload: Dict) -> bool:
        """验证token过期时间"""
        try:
            exp = token_payload.get('exp')
            if not exp:
                return False
            
            current_time = int(time.time())
            
            # 检查是否过期
            if current_time >= exp:
                return False
            
            # 检查是否在合理的时间窗口内（防止时间过长的token）
            max_token_age = settings.ENTERPRISE_AUTH.get('token_expiry', 3600)  # 默认1小时
            iat = token_payload.get('iat', current_time)
            
            if (current_time - iat) > max_token_age:
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Token expiry validation error: {str(e)}")
            return False
    
    @staticmethod
    def _validate_allowed_domains(client_ip: str = None) -> bool:
        """验证来源域名/IP白名单"""
        try:
            allowed_domains = settings.ENTERPRISE_AUTH.get('allowed_domains', [])
            
            # 如果白名单为空，表示允许所有域名
            if not allowed_domains:
                return True
            
            # 获取客户端IP
            if not client_ip:
                client_ip = EnterpriseSecurityManager._get_client_ip()
            
            if not client_ip:
                return False
            
            # 检查IP是否在白名单中
            for allowed in allowed_domains:
                try:
                    # 支持IP地址和CIDR格式
                    if '/' in allowed:
                        # CIDR格式
                        network = ipaddress.ip_network(allowed, strict=False)
                        if ipaddress.ip_address(client_ip) in network:
                            return True
                    else:
                        # 单个IP地址
                        if client_ip == allowed:
                            return True
                except ValueError:
                    # 域名格式，需要额外的域名解析逻辑
                    logging.warning(f"Domain validation not implemented for: {allowed}")
                    continue
            
            return False
            
        except Exception as e:
            logging.error(f"Domain validation error: {str(e)}")
            return False
    
    @staticmethod
    def _get_client_ip() -> str:
        """获取客户端真实IP地址"""
        try:
            # 优先从X-Forwarded-For获取
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                # 取第一个IP（原始客户端IP）
                return forwarded_for.split(',')[0].strip()
            
            # 从X-Real-IP获取
            real_ip = request.headers.get('X-Real-IP')
            if real_ip:
                return real_ip.strip()
            
            # 最后使用remote_addr
            return request.remote_addr
            
        except Exception:
            return ""
    
    @staticmethod
    def _validate_anti_replay(token_payload: Dict) -> bool:
        """防重放攻击验证"""
        try:
            if not REDIS_CONN:
                # 如果没有Redis，跳过防重放检查
                logging.warning("Redis not available, skipping anti-replay check")
                return True
            
            # 使用jti（JWT ID）或者iat+user_id生成唯一标识
            jti = token_payload.get('jti')
            if not jti:
                # 如果没有jti，使用iat和user_id生成
                iat = token_payload.get('iat')
                user_id = token_payload.get('user_id')
                if not iat or not user_id:
                    return False
                jti = hashlib.md5(f"{iat}_{user_id}".encode()).hexdigest()
            
            nonce_key = f"{EnterpriseSecurityManager.TOKEN_NONCE_PREFIX}{jti}"
            
            # 检查是否已经使用过
            if REDIS_CONN.get(nonce_key):
                return False
            
            # 标记为已使用，设置过期时间为token的有效期
            exp = token_payload.get('exp', int(time.time()) + 3600)
            ttl = max(exp - int(time.time()), 0)
            
            if ttl > 0:
                REDIS_CONN.setex(nonce_key, ttl, "used")
            
            return True
            
        except Exception as e:
            logging.error(f"Anti-replay validation error: {str(e)}")
            return False
    
    @staticmethod
    def _validate_rate_limit(user_id: str, client_ip: str = None, limit: int = 10, window: int = 60) -> bool:
        """速率限制验证
        
        Args:
            user_id: 用户ID
            client_ip: 客户端IP
            limit: 限制次数，默认10次
            window: 时间窗口，默认60秒
        """
        try:
            if not REDIS_CONN:
                # 如果没有Redis，跳过速率限制检查
                logging.warning("Redis not available, skipping rate limit check")
                return True
            
            # 为用户和IP分别设置速率限制
            keys = []
            if user_id:
                keys.append(f"{EnterpriseSecurityManager.RATE_LIMIT_PREFIX}user:{user_id}")
            if client_ip:
                keys.append(f"{EnterpriseSecurityManager.RATE_LIMIT_PREFIX}ip:{client_ip}")
            
            current_time = int(time.time())
            
            for key in keys:
                # 使用滑动窗口计数
                pipe = REDIS_CONN.pipeline()
                pipe.zremrangebyscore(key, 0, current_time - window)  # 清除过期记录
                pipe.zcard(key)  # 获取当前计数
                pipe.zadd(key, {str(current_time): current_time})  # 添加新记录
                pipe.expire(key, window)  # 设置key过期时间
                
                results = pipe.execute()
                current_count = results[1]
                
                if current_count >= limit:
                    logging.warning(f"Rate limit exceeded for key: {key}")
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"Rate limit validation error: {str(e)}")
            return True  # 出错时允许通过，避免阻塞正常用户
    
    @staticmethod
    def log_security_event(event_type: str, user_id: str = None, details: Dict = None, 
                          success: bool = True, client_ip: str = None):
        """记录安全审计日志
        
        Args:
            event_type: 事件类型（login, token_validation, etc.）
            user_id: 用户ID
            details: 事件详情
            success: 是否成功
            client_ip: 客户端IP
        """
        try:
            if not client_ip:
                client_ip = EnterpriseSecurityManager._get_client_ip()
            
            log_entry = {
                'timestamp': current_timestamp(),
                'datetime': datetime.now().isoformat(),
                'event_type': event_type,
                'user_id': user_id,
                'client_ip': client_ip,
                'success': success,
                'details': details or {},
                'user_agent': request.headers.get('User-Agent', ''),
                'request_id': request.headers.get('X-Request-ID', '')
            }
            
            # 记录到应用日志
            log_level = logging.INFO if success else logging.WARNING
            logging.log(log_level, f"Enterprise security event: {event_type} - {log_entry}")
            
            # 如果有Redis，也保存到Redis中用于实时监控
            if REDIS_CONN:
                audit_key = f"{EnterpriseSecurityManager.AUDIT_LOG_PREFIX}{datetime.now().strftime('%Y%m%d')}"
                log_data = f"{current_timestamp()}|{event_type}|{user_id or 'unknown'}|{client_ip}|{success}"
                
                # 使用列表存储，保留最近1000条记录
                pipe = REDIS_CONN.pipeline()
                pipe.lpush(audit_key, log_data)
                pipe.ltrim(audit_key, 0, 999)  # 只保留最近1000条
                pipe.expire(audit_key, 86400 * 7)  # 保留7天
                pipe.execute()
            
        except Exception as e:
            logging.error(f"Security event logging error: {str(e)}")
    
    @staticmethod
    def get_security_summary(days: int = 7) -> Dict:
        """获取安全事件摘要
        
        Args:
            days: 查询天数
            
        Returns:
            安全事件统计摘要
        """
        try:
            if not REDIS_CONN:
                return {"error": "Redis not available"}
            
            summary = {
                "total_events": 0,
                "successful_logins": 0,
                "failed_logins": 0,
                "blocked_ips": [],
                "active_users": set(),
                "event_types": {}
            }
            
            # 查询最近几天的审计日志
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
                audit_key = f"{EnterpriseSecurityManager.AUDIT_LOG_PREFIX}{date}"
                
                logs = REDIS_CONN.lrange(audit_key, 0, -1)
                for log_data in logs:
                    try:
                        parts = log_data.decode().split('|')
                        if len(parts) >= 5:
                            timestamp, event_type, user_id, client_ip, success = parts
                            
                            summary["total_events"] += 1
                            
                            if event_type == "enterprise_login":
                                if success == "True":
                                    summary["successful_logins"] += 1
                                    if user_id != "unknown":
                                        summary["active_users"].add(user_id)
                                else:
                                    summary["failed_logins"] += 1
                            
                            # 统计事件类型
                            summary["event_types"][event_type] = summary["event_types"].get(event_type, 0) + 1
                            
                    except Exception:
                        continue
            
            summary["active_users"] = len(summary["active_users"])
            
            return summary
            
        except Exception as e:
            logging.error(f"Get security summary error: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def is_suspicious_activity(user_id: str, client_ip: str = None) -> bool:
        """检测可疑活动
        
        Args:
            user_id: 用户ID
            client_ip: 客户端IP
            
        Returns:
            是否存在可疑活动
        """
        try:
            if not REDIS_CONN:
                return False
            
            # 检查短时间内多次失败登录
            current_time = int(time.time())
            window = 300  # 5分钟窗口
            max_failures = 5  # 最多5次失败
            
            # 检查用户级别的失败次数
            if user_id:
                failure_key = f"enterprise_failures:user:{user_id}"
                failure_count = REDIS_CONN.zcount(failure_key, current_time - window, current_time)
                if failure_count >= max_failures:
                    return True
            
            # 检查IP级别的失败次数
            if client_ip:
                failure_key = f"enterprise_failures:ip:{client_ip}"
                failure_count = REDIS_CONN.zcount(failure_key, current_time - window, current_time)
                if failure_count >= max_failures:
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Suspicious activity detection error: {str(e)}")
            return False
    
    @staticmethod
    def record_login_failure(user_id: str, client_ip: str = None):
        """记录登录失败
        
        Args:
            user_id: 用户ID
            client_ip: 客户端IP
        """
        try:
            if not REDIS_CONN:
                return
            
            current_time = int(time.time())
            
            # 记录用户级别失败
            if user_id:
                failure_key = f"enterprise_failures:user:{user_id}"
                pipe = REDIS_CONN.pipeline()
                pipe.zadd(failure_key, {str(current_time): current_time})
                pipe.zremrangebyscore(failure_key, 0, current_time - 3600)  # 清除1小时前的记录
                pipe.expire(failure_key, 3600)  # 1小时过期
                pipe.execute()
            
            # 记录IP级别失败
            if client_ip:
                failure_key = f"enterprise_failures:ip:{client_ip}"
                pipe = REDIS_CONN.pipeline()
                pipe.zadd(failure_key, {str(current_time): current_time})
                pipe.zremrangebyscore(failure_key, 0, current_time - 3600)  # 清除1小时前的记录
                pipe.expire(failure_key, 3600)  # 1小时过期
                pipe.execute()
            
        except Exception as e:
            logging.error(f"Record login failure error: {str(e)}")
    
    @staticmethod
    def clear_login_failures(user_id: str, client_ip: str = None):
        """清除登录失败记录（成功登录后调用）
        
        Args:
            user_id: 用户ID
            client_ip: 客户端IP
        """
        try:
            if not REDIS_CONN:
                return
            
            # 清除用户级别失败记录
            if user_id:
                failure_key = f"enterprise_failures:user:{user_id}"
                REDIS_CONN.delete(failure_key)
            
            # 清除IP级别失败记录
            if client_ip:
                failure_key = f"enterprise_failures:ip:{client_ip}"
                REDIS_CONN.delete(failure_key)
            
        except Exception as e:
            logging.error(f"Clear login failures error: {str(e)}") 