import { useAuth } from '@/hooks/auth-hooks';
import { redirectToLogin } from '@/utils/authorization-util';
import enterpriseAuth from '@/utils/enterprise-auth';
import { useEffect, useState } from 'react';
import { Outlet } from 'umi';

export default () => {
  const { isLogin } = useAuth();
  const [isEnterpriseLoginChecked, setIsEnterpriseLoginChecked] = useState(false);
  const [isEnterpriseLogin, setIsEnterpriseLogin] = useState(false);

  // 检查企业登录
  useEffect(() => {
    const checkEnterpriseLogin = async () => {
      try {
        // 如果已经登录，跳过企业登录检查
        if (isLogin === true) {
          setIsEnterpriseLoginChecked(true);
          return;
        }

        // 检查是否有企业token
        if (enterpriseAuth.hasEnterpriseToken()) {
          console.log('Found enterprise token, attempting auto login...');
          const loginSuccess = await enterpriseAuth.autoEnterpriseLogin();
          if (loginSuccess) {
            setIsEnterpriseLogin(true);
            console.log('Enterprise auto login successful');
          } else {
            console.log('Enterprise auto login failed');
            // 清除无效的token
            enterpriseAuth.clearToken();
          }
        }
      } catch (error) {
        console.error('Enterprise login check error:', error);
        enterpriseAuth.clearToken();
      } finally {
        setIsEnterpriseLoginChecked(true);
      }
    };

    // 只有在非登录状态下才检查企业登录
    if (isLogin !== true && !isEnterpriseLoginChecked) {
      checkEnterpriseLogin();
    } else if (isLogin === true) {
      setIsEnterpriseLoginChecked(true);
    }
  }, [isLogin, isEnterpriseLoginChecked]);

  // 等待检查完成
  if (!isEnterpriseLoginChecked) {
    return <div>Loading...</div>;
  }

  // 判断登录状态
  const shouldAllowAccess = isLogin === true || isEnterpriseLogin;
  const shouldRedirectToLogin = isLogin === false && !isEnterpriseLogin;

  if (shouldAllowAccess) {
    return <Outlet />;
  } else if (shouldRedirectToLogin) {
    redirectToLogin();
    return <></>;
  }

  return <></>;
};
