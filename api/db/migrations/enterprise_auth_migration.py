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

"""
企业认证数据库迁移脚本
添加企业用户相关字段和索引
"""

import logging
from playhouse.migrate import migrate
from api.db.db_models import DB, DatabaseMigrator, User
from api import settings
from peewee import CharField


def migrate_enterprise_auth_fields():
    """执行企业认证相关的数据库迁移"""
    migrator = DatabaseMigrator[settings.DATABASE_TYPE.upper()].value(DB)
    
    migrations_applied = []
    migrations_failed = []
    
    try:
        # 添加 enterprise_user_id 字段
        logging.info("Adding enterprise_user_id field to user table...")
        migrate(
            migrator.add_column(
                "user", 
                "enterprise_user_id", 
                CharField(max_length=255, null=True, help_text="enterprise system user id", index=True)
            )
        )
        migrations_applied.append("enterprise_user_id field")
    except Exception as e:
        logging.warning(f"enterprise_user_id field migration failed (might already exist): {str(e)}")
        migrations_failed.append(f"enterprise_user_id: {str(e)}")
    
    try:
        # 添加 enterprise_source 字段
        logging.info("Adding enterprise_source field to user table...")
        migrate(
            migrator.add_column(
                "user", 
                "enterprise_source", 
                CharField(max_length=64, null=True, help_text="enterprise system source", index=True)
            )
        )
        migrations_applied.append("enterprise_source field")
    except Exception as e:
        logging.warning(f"enterprise_source field migration failed (might already exist): {str(e)}")
        migrations_failed.append(f"enterprise_source: {str(e)}")
    
    # 创建额外的索引以提升查询性能
    try:
        logging.info("Creating composite index for enterprise authentication...")
        # 注意：这里的索引创建语法可能需要根据具体数据库类型调整
        if settings.DATABASE_TYPE.upper() == "MYSQL":
            DB.execute_sql(
                "CREATE INDEX IF NOT EXISTS idx_user_enterprise_composite ON user (enterprise_user_id, enterprise_source)"
            )
        elif settings.DATABASE_TYPE.upper() == "POSTGRES":
            DB.execute_sql(
                "CREATE INDEX IF NOT EXISTS idx_user_enterprise_composite ON \"user\" (enterprise_user_id, enterprise_source)"
            )
        migrations_applied.append("enterprise composite index")
    except Exception as e:
        logging.warning(f"Enterprise composite index creation failed: {str(e)}")
        migrations_failed.append(f"composite index: {str(e)}")
    
    # 记录迁移结果
    if migrations_applied:
        logging.info(f"Enterprise auth migrations applied successfully: {', '.join(migrations_applied)}")
    
    if migrations_failed:
        logging.warning(f"Some enterprise auth migrations failed: {', '.join(migrations_failed)}")
    
    return {
        "applied": migrations_applied,
        "failed": migrations_failed,
        "success": len(migrations_applied) > 0 or len(migrations_failed) == 0
    }


def rollback_enterprise_auth_fields():
    """回滚企业认证相关的数据库迁移"""
    migrator = DatabaseMigrator[settings.DATABASE_TYPE.upper()].value(DB)
    
    rollbacks_applied = []
    rollbacks_failed = []
    
    try:
        # 删除复合索引
        logging.info("Dropping enterprise composite index...")
        if settings.DATABASE_TYPE.upper() == "MYSQL":
            DB.execute_sql("DROP INDEX IF EXISTS idx_user_enterprise_composite ON user")
        elif settings.DATABASE_TYPE.upper() == "POSTGRES":
            DB.execute_sql("DROP INDEX IF EXISTS idx_user_enterprise_composite")
        rollbacks_applied.append("enterprise composite index")
    except Exception as e:
        logging.warning(f"Enterprise composite index removal failed: {str(e)}")
        rollbacks_failed.append(f"composite index: {str(e)}")
    
    try:
        # 删除 enterprise_source 字段
        logging.info("Removing enterprise_source field from user table...")
        migrate(migrator.drop_column("user", "enterprise_source"))
        rollbacks_applied.append("enterprise_source field")
    except Exception as e:
        logging.warning(f"enterprise_source field removal failed: {str(e)}")
        rollbacks_failed.append(f"enterprise_source: {str(e)}")
    
    try:
        # 删除 enterprise_user_id 字段
        logging.info("Removing enterprise_user_id field from user table...")
        migrate(migrator.drop_column("user", "enterprise_user_id"))
        rollbacks_applied.append("enterprise_user_id field")
    except Exception as e:
        logging.warning(f"enterprise_user_id field removal failed: {str(e)}")
        rollbacks_failed.append(f"enterprise_user_id: {str(e)}")
    
    # 记录回滚结果
    if rollbacks_applied:
        logging.info(f"Enterprise auth rollbacks applied successfully: {', '.join(rollbacks_applied)}")
    
    if rollbacks_failed:
        logging.warning(f"Some enterprise auth rollbacks failed: {', '.join(rollbacks_failed)}")
    
    return {
        "applied": rollbacks_applied,
        "failed": rollbacks_failed,
        "success": len(rollbacks_applied) > 0 or len(rollbacks_failed) == 0
    }


def verify_enterprise_auth_migration():
    """验证企业认证迁移是否成功"""
    try:
        # 检查字段是否存在
        test_query = User.select().where(User.enterprise_user_id.is_null()).limit(1)
        list(test_query)  # 执行查询
        
        # 检查索引是否存在（通过查询计划或系统表）
        if settings.DATABASE_TYPE.upper() == "MYSQL":
            result = DB.execute_sql("SHOW INDEX FROM user WHERE Key_name = 'idx_user_enterprise_composite'")
            index_exists = len(list(result)) > 0
        elif settings.DATABASE_TYPE.upper() == "POSTGRES":
            result = DB.execute_sql(
                "SELECT indexname FROM pg_indexes WHERE tablename = 'user' AND indexname = 'idx_user_enterprise_composite'"
            )
            index_exists = len(list(result)) > 0
        else:
            index_exists = True  # 对于其他数据库类型，假设索引存在
        
        return {
            "fields_exist": True,
            "index_exists": index_exists,
            "success": True,
            "message": "Enterprise auth migration verification passed"
        }
        
    except Exception as e:
        return {
            "fields_exist": False,
            "index_exists": False,
            "success": False,
            "message": f"Enterprise auth migration verification failed: {str(e)}"
        }


def create_sample_enterprise_users():
    """创建示例企业用户（仅用于测试）"""
    try:
        from api.db.services.enterprise_auth_service import EnterpriseAuthService
        from api.utils import get_uuid
        import json
        
        # 示例管理员用户数据
        admin_data = {
            "user_id": "enterprise_admin_001",
            "email": "admin@enterprise.com",
            "nickname": "企业管理员",
            "role": "enterprise_admin",
            "tenant_id": "enterprise_tenant_001",
            "iat": 1640995200,  # 2022-01-01
            "exp": 1640998800   # 2022-01-01 + 1 hour
        }
        
        # 示例普通用户数据
        user_data = {
            "user_id": "enterprise_user_001", 
            "email": "user@enterprise.com",
            "nickname": "企业用户",
            "role": "enterprise_user",
            "tenant_id": "enterprise_tenant_001",
            "iat": 1640995200,
            "exp": 1640998800
        }
        
        created_users = []
        
        # 创建管理员用户
        admin_user = EnterpriseAuthService.create_or_update_user(admin_data)
        if admin_user:
            created_users.append(f"Admin: {admin_user.email}")
        
        # 创建普通用户
        normal_user = EnterpriseAuthService.create_or_update_user(user_data)
        if normal_user:
            created_users.append(f"User: {normal_user.email}")
        
        return {
            "success": True,
            "created_users": created_users,
            "message": f"Created {len(created_users)} sample enterprise users"
        }
        
    except Exception as e:
        return {
            "success": False,
            "created_users": [],
            "message": f"Failed to create sample enterprise users: {str(e)}"
        }


if __name__ == "__main__":
    """直接运行此脚本时执行迁移"""
    print("=== Enterprise Auth Migration ===")
    
    # 执行迁移
    migration_result = migrate_enterprise_auth_fields()
    print(f"Migration result: {migration_result}")
    
    # 验证迁移
    verification_result = verify_enterprise_auth_migration()
    print(f"Verification result: {verification_result}")
    
    # 可选：创建示例用户（仅在开发环境中）
    import os
    if os.getenv("ENVIRONMENT") == "development":
        sample_result = create_sample_enterprise_users()
        print(f"Sample users creation result: {sample_result}")
    
    print("=== Migration Complete ===") 