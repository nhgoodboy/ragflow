import React, { useEffect, useState } from 'react';
import { Alert, Spin } from 'antd';
import { useEnterprisePermissions, usePermissionCheck } from '@/hooks/enterprise-hooks';
import type { EnterprisePermissions } from '@/hooks/enterprise-hooks';

interface PermissionGuardProps {
  permission: keyof EnterprisePermissions;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showError?: boolean;
  errorMessage?: string;
}

/**
 * 权限保护组件
 * 根据企业用户权限控制子组件的渲染
 */
export const PermissionGuard: React.FC<PermissionGuardProps> = ({
  permission,
  children,
  fallback,
  showError = true,
  errorMessage = '您没有权限访问此功能'
}) => {
  const { hasPermission, checking } = usePermissionCheck(permission);

  if (checking) {
    return <Spin size="small" />;
  }

  if (!hasPermission) {
    if (fallback) {
      return <>{fallback}</>;
    }
    
    if (showError) {
      return (
        <Alert
          message="权限不足"
          description={errorMessage}
          type="warning"
          showIcon
          style={{ margin: '16px 0' }}
        />
      );
    }
    
    return null;
  }

  return <>{children}</>;
};

interface MultiPermissionGuardProps {
  permissions: Array<keyof EnterprisePermissions>;
  requireAll?: boolean; // true: 需要所有权限, false: 需要任一权限
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showError?: boolean;
  errorMessage?: string;
}

/**
 * 多权限保护组件
 */
export const MultiPermissionGuard: React.FC<MultiPermissionGuardProps> = ({
  permissions,
  requireAll = true,
  children,
  fallback,
  showError = true,
  errorMessage = '您没有权限访问此功能'
}) => {
  const { permissions: userPermissions, loading } = useEnterprisePermissions();

  if (loading) {
    return <Spin size="small" />;
  }

  const hasPermission = requireAll
    ? permissions.every(perm => userPermissions[perm])
    : permissions.some(perm => userPermissions[perm]);

  if (!hasPermission) {
    if (fallback) {
      return <>{fallback}</>;
    }
    
    if (showError) {
      return (
        <Alert
          message="权限不足"
          description={errorMessage}
          type="warning"
          showIcon
          style={{ margin: '16px 0' }}
        />
      );
    }
    
    return null;
  }

  return <>{children}</>;
};

interface RoleBasedGuardProps {
  allowedRoles: Array<'admin' | 'normal'>;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showError?: boolean;
  errorMessage?: string;
}

/**
 * 基于角色的权限保护组件
 */
export const RoleBasedGuard: React.FC<RoleBasedGuardProps> = ({
  allowedRoles,
  children,
  fallback,
  showError = true,
  errorMessage = '您的角色无权访问此功能'
}) => {
  const [userRole, setUserRole] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 从用户信息中获取角色
    const getUserRole = async () => {
      try {
        // 这里应该调用API获取用户角色信息
        // 暂时从localStorage获取
        const userInfo = localStorage.getItem('userInfo');
        if (userInfo) {
          const parsed = JSON.parse(userInfo);
          setUserRole(parsed.role || 'normal');
        }
      } catch (error) {
        console.error('获取用户角色失败:', error);
        setUserRole('normal');
      } finally {
        setLoading(false);
      }
    };

    getUserRole();
  }, []);

  if (loading) {
    return <Spin size="small" />;
  }

  const hasPermission = userRole && allowedRoles.includes(userRole as any);

  if (!hasPermission) {
    if (fallback) {
      return <>{fallback}</>;
    }
    
    if (showError) {
      return (
        <Alert
          message="角色权限不足"
          description={errorMessage}
          type="warning"
          showIcon
          style={{ margin: '16px 0' }}
        />
      );
    }
    
    return null;
  }

  return <>{children}</>;
};

/**
 * 权限Hook，用于在组件中检查权限
 */
export const usePermissionGuard = () => {
  const { permissions, loading, error } = useEnterprisePermissions();

  return {
    permissions,
    loading,
    error,
    hasPermission: (permission: keyof EnterprisePermissions) => permissions[permission],
    hasAnyPermission: (permissionList: Array<keyof EnterprisePermissions>) => 
      permissionList.some(perm => permissions[perm]),
    hasAllPermissions: (permissionList: Array<keyof EnterprisePermissions>) => 
      permissionList.every(perm => permissions[perm]),
  };
};

export default PermissionGuard; 