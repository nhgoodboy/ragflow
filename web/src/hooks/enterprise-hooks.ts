import { useEffect, useState } from 'react';
import enterpriseAuth, { EnterpriseUser } from '@/utils/enterprise-auth';

export interface EnterprisePermissions {
  can_manage_knowledge: boolean;
  can_chat: boolean;
  can_manage_users: boolean;
  can_access_system: boolean;
}

/**
 * 企业用户权限检查hook
 */
export const useEnterprisePermissions = () => {
  const [permissions, setPermissions] = useState<EnterprisePermissions>({
    can_manage_knowledge: false,
    can_chat: false,
    can_manage_users: false,
    can_access_system: false,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPermissions = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const result = await enterpriseAuth.getEnterprisePermissions();
        if (result.code === 0) {
          setPermissions(result.data);
        } else {
          setError(result.message || 'Failed to fetch permissions');
        }
      } catch (err) {
        setError('Failed to fetch permissions');
        console.error('Error fetching enterprise permissions:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPermissions();
  }, []);

  return { permissions, loading, error, refetch: () => setLoading(true) };
};

/**
 * 检查特定权限的hook
 */
export const usePermissionCheck = (permission: keyof EnterprisePermissions) => {
  const [hasPermission, setHasPermission] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const checkPermission = async () => {
      try {
        setChecking(true);
        const result = await enterpriseAuth.checkPermission(permission);
        setHasPermission(result);
      } catch (error) {
        console.error(`Error checking permission ${permission}:`, error);
        setHasPermission(false);
      } finally {
        setChecking(false);
      }
    };

    checkPermission();
  }, [permission]);

  return { hasPermission, checking };
};

/**
 * 企业用户验证hook
 */
export const useEnterpriseVerification = () => {
  const [isEnterpriseUser, setIsEnterpriseUser] = useState(false);
  const [userInfo, setUserInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifyUser = async () => {
      try {
        setLoading(true);
        const result = await enterpriseAuth.verifyEnterpriseUser();
        
        if (result.code === 0) {
          setIsEnterpriseUser(result.data?.is_enterprise_user || false);
          setUserInfo(result.data);
        } else {
          setIsEnterpriseUser(false);
          setUserInfo(null);
        }
      } catch (error) {
        console.error('Error verifying enterprise user:', error);
        setIsEnterpriseUser(false);
        setUserInfo(null);
      } finally {
        setLoading(false);
      }
    };

    verifyUser();
  }, []);

  return { isEnterpriseUser, userInfo, loading };
};

/**
 * 权限保护组件hook
 */
export const usePermissionGuard = (requiredPermission: keyof EnterprisePermissions) => {
  const { hasPermission, checking } = usePermissionCheck(requiredPermission);
  
  return {
    canAccess: hasPermission,
    loading: checking,
    PermissionGuard: ({ children, fallback }: { 
      children: React.ReactNode; 
      fallback?: React.ReactNode; 
    }) => {
      if (checking) {
        return <div>Checking permissions...</div>;
      }
      
      if (!hasPermission) {
        return fallback || <div>You don't have permission to access this resource.</div>;
      }
      
      return <>{children}</>;
    }
  };
}; 