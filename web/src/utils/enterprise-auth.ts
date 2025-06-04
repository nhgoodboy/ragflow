import { message } from 'antd';
import authorizationUtil from './authorization-util';
import userService from '@/services/user-service';
import { Authorization } from '@/constants/authorization';

export interface EnterpriseUser {
  id: string;
  nickname: string;
  email: string;
  access_token: string;
  permissions: {
    can_manage_knowledge: boolean;
    can_chat: boolean;
    can_manage_users: boolean;
    can_access_system: boolean;
  };
  login_channel: string;
}

export interface EnterpriseAuthResponse {
  code: number;
  data: EnterpriseUser | boolean;
  message: string;
  response?: Response;
}

class EnterpriseAuth {
  private static instance: EnterpriseAuth;
  private enterpriseToken: string | null = null;

  constructor() {
    if (EnterpriseAuth.instance) {
      return EnterpriseAuth.instance;
    }
    EnterpriseAuth.instance = this;
  }

  /**
   * 从URL参数或localStorage获取企业token
   */
  getEnterpriseToken(): string | null {
    // 优先从URL参数获取
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('enterprise_token');
    
    if (tokenFromUrl) {
      this.enterpriseToken = tokenFromUrl;
      // 清除URL中的token参数，避免在浏览器历史中暴露
      this.clearTokenFromUrl();
      // 保存到localStorage
      this.saveTokenToStorage(tokenFromUrl);
      return tokenFromUrl;
    }

    // 从localStorage获取
    const tokenFromStorage = this.getTokenFromStorage();
    if (tokenFromStorage) {
      this.enterpriseToken = tokenFromStorage;
      return tokenFromStorage;
    }

    return null;
  }

  /**
   * 清除URL中的enterprise_token参数
   */
  private clearTokenFromUrl(): void {
    const url = new URL(window.location.href);
    url.searchParams.delete('enterprise_token');
    
    // 使用replaceState避免在浏览器历史中留下包含token的URL
    window.history.replaceState({}, document.title, url.toString());
  }

  /**
   * 保存token到localStorage
   */
  private saveTokenToStorage(token: string): void {
    try {
      localStorage.setItem('enterprise_token', token);
    } catch (error) {
      console.warn('Failed to save enterprise token to localStorage:', error);
    }
  }

  /**
   * 从localStorage获取token
   */
  private getTokenFromStorage(): string | null {
    try {
      return localStorage.getItem('enterprise_token');
    } catch (error) {
      console.warn('Failed to get enterprise token from localStorage:', error);
      return null;
    }
  }

  /**
   * 清除保存的token
   */
  clearToken(): void {
    this.enterpriseToken = null;
    try {
      localStorage.removeItem('enterprise_token');
    } catch (error) {
      console.warn('Failed to remove enterprise token from localStorage:', error);
    }
  }

  /**
   * 检查是否有企业token
   */
  hasEnterpriseToken(): boolean {
    return !!this.getEnterpriseToken();
  }

  /**
   * 使用企业token登录
   */
  async loginWithEnterpriseToken(token?: string): Promise<EnterpriseAuthResponse> {
    const enterpriseToken = token || this.getEnterpriseToken();
    
    if (!enterpriseToken) {
      return {
        code: 1,
        data: false,
        message: 'No enterprise token available'
      };
    }

    try {
      const response = await fetch('/v1/user/enterprise/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          enterprise_token: enterpriseToken
        })
      });

      const result = await response.json();

      if (result.code === 0 && result.data) {
        // 保存认证信息
        const userData = result.data as EnterpriseUser;
        const authorization = response.headers.get(Authorization);
        
        if (authorization) {
          authorizationUtil.setItems({
            Authorization: authorization,
            userInfo: JSON.stringify({
              avatar: userData.avatar || '',
              name: userData.nickname,
              email: userData.email,
            }),
            Token: userData.access_token,
          });
        }

        message.success('企业登录成功');
        return {
          code: 0,
          data: userData,
          message: result.message,
          response
        };
      } else {
        message.error(result.message || '企业登录失败');
        return {
          code: result.code || 1,
          data: false,
          message: result.message || '企业登录失败'
        };
      }
    } catch (error) {
      console.error('Enterprise login error:', error);
      message.error('企业登录请求失败');
      return {
        code: 1,
        data: false,
        message: '企业登录请求失败'
      };
    }
  }

  /**
   * 验证企业用户状态
   */
  async verifyEnterpriseUser(): Promise<any> {
    try {
      const authorization = authorizationUtil.getAuthorization();
      if (!authorization) {
        return { code: 1, message: 'No authorization' };
      }

      const response = await fetch('/v1/user/enterprise/verify', {
        method: 'GET',
        headers: {
          'Authorization': authorization,
          'Content-Type': 'application/json',
        }
      });

      return await response.json();
    } catch (error) {
      console.error('Enterprise user verification error:', error);
      return { code: 1, message: 'Verification failed' };
    }
  }

  /**
   * 刷新企业token
   */
  async refreshEnterpriseToken(newToken: string): Promise<any> {
    try {
      const response = await fetch('/v1/user/enterprise/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          enterprise_token: newToken
        })
      });

      const result = await response.json();
      
      if (result.code === 0) {
        // 更新保存的token
        this.saveTokenToStorage(newToken);
        this.enterpriseToken = newToken;
      }

      return result;
    } catch (error) {
      console.error('Enterprise token refresh error:', error);
      return { code: 1, message: 'Token refresh failed' };
    }
  }

  /**
   * 获取企业用户权限
   */
  async getEnterprisePermissions(): Promise<any> {
    try {
      const authorization = authorizationUtil.getAuthorization();
      if (!authorization) {
        return { code: 1, message: 'No authorization' };
      }

      const response = await fetch('/v1/user/enterprise/permissions', {
        method: 'GET',
        headers: {
          'Authorization': authorization,
          'Content-Type': 'application/json',
        }
      });

      return await response.json();
    } catch (error) {
      console.error('Get enterprise permissions error:', error);
      return { code: 1, message: 'Get permissions failed' };
    }
  }

  /**
   * 自动企业登录流程
   * 在应用启动时调用，检查并处理企业token
   */
  async autoEnterpriseLogin(): Promise<boolean> {
    const token = this.getEnterpriseToken();
    
    if (!token) {
      return false;
    }

    // 检查当前是否已经登录
    const currentAuth = authorizationUtil.getAuthorization();
    if (currentAuth) {
      // 如果已经登录，验证是否为企业用户
      const verification = await this.verifyEnterpriseUser();
      if (verification.code === 0 && verification.data?.is_enterprise_user) {
        return true;
      }
    }

    // 尝试企业登录
    const loginResult = await this.loginWithEnterpriseToken(token);
    return loginResult.code === 0;
  }

  /**
   * 退出企业登录
   */
  async logoutEnterprise(): Promise<void> {
    this.clearToken();
    authorizationUtil.removeAll();
    
    // 可以选择重定向到企业系统或显示登录页面
    window.location.href = '/login';
  }

  /**
   * 检查用户权限
   */
  async checkPermission(permission: keyof EnterpriseUser['permissions']): Promise<boolean> {
    try {
      const permissionsResult = await this.getEnterprisePermissions();
      if (permissionsResult.code === 0) {
        return permissionsResult.data[permission] || false;
      }
      return false;
    } catch (error) {
      console.error('Check permission error:', error);
      return false;
    }
  }
}

export default new EnterpriseAuth(); 