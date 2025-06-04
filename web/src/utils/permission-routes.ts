import type { EnterprisePermissions } from '@/hooks/enterprise-hooks';

// 路由权限映射配置
export interface RoutePermission {
  path: string;
  requiredPermissions?: Array<keyof EnterprisePermissions>;
  requireAll?: boolean; // 是否需要所有权限，默认false（任一权限即可）
  roles?: Array<'admin' | 'normal'>; // 允许的角色
  fallbackPath?: string; // 无权限时的重定向路径
  description?: string; // 权限描述
}

/**
 * 路由权限配置
 */
export const ROUTE_PERMISSIONS: RoutePermission[] = [
  // 知识库管理相关路由
  {
    path: '/knowledge',
    requiredPermissions: ['can_manage_knowledge'],
    description: '知识库管理权限'
  },
  {
    path: '/knowledge/dataset',
    requiredPermissions: ['can_manage_knowledge'],
    description: '数据集管理权限'
  },
  {
    path: '/knowledge/chunk',
    requiredPermissions: ['can_manage_knowledge'],
    description: '文档分块管理权限'
  },
  
  // 聊天相关路由
  {
    path: '/chat',
    requiredPermissions: ['can_chat'],
    description: '聊天功能权限'
  },
  {
    path: '/conversation',
    requiredPermissions: ['can_chat'],
    description: '对话管理权限'
  },
  
  // 用户管理相关路由
  {
    path: '/user-setting',
    requiredPermissions: ['can_manage_users'],
    description: '用户管理权限'
  },
  {
    path: '/team',
    requiredPermissions: ['can_manage_users'],
    description: '团队管理权限'
  },
  
  // 系统设置相关路由  
  {
    path: '/setting',
    requiredPermissions: ['can_access_system'],
    description: '系统设置权限'
  },
  {
    path: '/flow',
    requiredPermissions: ['can_access_system'],
    description: '工作流管理权限'
  },
  {
    path: '/file-manager',
    requiredPermissions: ['can_manage_knowledge', 'can_access_system'],
    requireAll: false, // 知识库管理或系统权限任一即可
    description: '文件管理权限'
  },
  
  // 仅管理员角色可访问的路由
  {
    path: '/admin',
    roles: ['admin'],
    description: '管理员专用功能'
  }
];

/**
 * 检查用户是否有访问指定路由的权限
 */
export const checkRoutePermission = (
  path: string, 
  userPermissions: EnterprisePermissions,
  userRole?: string
): boolean => {
  // 查找匹配的路由配置
  const routeConfig = ROUTE_PERMISSIONS.find(config => {
    // 精确匹配或前缀匹配
    return path === config.path || path.startsWith(config.path + '/');
  });

  // 如果没有配置，默认允许访问
  if (!routeConfig) {
    return true;
  }

  // 检查角色权限
  if (routeConfig.roles && routeConfig.roles.length > 0) {
    if (!userRole || !routeConfig.roles.includes(userRole as any)) {
      return false;
    }
  }

  // 检查功能权限
  if (routeConfig.requiredPermissions && routeConfig.requiredPermissions.length > 0) {
    const hasPermission = routeConfig.requireAll
      ? routeConfig.requiredPermissions.every(perm => userPermissions[perm])
      : routeConfig.requiredPermissions.some(perm => userPermissions[perm]);
    
    if (!hasPermission) {
      return false;
    }
  }

  return true;
};

/**
 * 获取用户可访问的路由列表
 */
export const getAccessibleRoutes = (
  userPermissions: EnterprisePermissions,
  userRole?: string
): string[] => {
  return ROUTE_PERMISSIONS
    .filter(config => checkRoutePermission(config.path, userPermissions, userRole))
    .map(config => config.path);
};

/**
 * 获取路由的权限描述
 */
export const getRoutePermissionDescription = (path: string): string => {
  const routeConfig = ROUTE_PERMISSIONS.find(config => 
    path === config.path || path.startsWith(config.path + '/')
  );
  
  return routeConfig?.description || '需要相应权限才能访问此功能';
};

/**
 * 菜单项权限配置
 */
export interface MenuPermission {
  key: string;
  requiredPermissions?: Array<keyof EnterprisePermissions>;
  requireAll?: boolean;
  roles?: Array<'admin' | 'normal'>;
  children?: MenuPermission[];
}

/**
 * 侧边栏菜单权限配置
 */
export const MENU_PERMISSIONS: MenuPermission[] = [
  {
    key: 'knowledge',
    requiredPermissions: ['can_manage_knowledge'],
    children: [
      {
        key: 'dataset',
        requiredPermissions: ['can_manage_knowledge']
      },
      {
        key: 'chunk',
        requiredPermissions: ['can_manage_knowledge']
      }
    ]
  },
  {
    key: 'chat',
    requiredPermissions: ['can_chat']
  },
  {
    key: 'conversation',
    requiredPermissions: ['can_chat']
  },
  {
    key: 'flow',
    requiredPermissions: ['can_access_system']
  },
  {
    key: 'file-manager',
    requiredPermissions: ['can_manage_knowledge', 'can_access_system'],
    requireAll: false
  },
  {
    key: 'user-setting',
    requiredPermissions: ['can_manage_users']
  },
  {
    key: 'team',
    requiredPermissions: ['can_manage_users']
  },
  {
    key: 'setting',
    requiredPermissions: ['can_access_system']
  }
];

/**
 * 检查菜单项是否应该显示
 */
export const checkMenuPermission = (
  menuKey: string,
  userPermissions: EnterprisePermissions,
  userRole?: string
): boolean => {
  const findMenuConfig = (configs: MenuPermission[], key: string): MenuPermission | null => {
    for (const config of configs) {
      if (config.key === key) {
        return config;
      }
      if (config.children) {
        const found = findMenuConfig(config.children, key);
        if (found) return found;
      }
    }
    return null;
  };

  const menuConfig = findMenuConfig(MENU_PERMISSIONS, menuKey);
  
  if (!menuConfig) {
    return true; // 没有配置的菜单默认显示
  }

  // 检查角色权限
  if (menuConfig.roles && menuConfig.roles.length > 0) {
    if (!userRole || !menuConfig.roles.includes(userRole as any)) {
      return false;
    }
  }

  // 检查功能权限
  if (menuConfig.requiredPermissions && menuConfig.requiredPermissions.length > 0) {
    const hasPermission = menuConfig.requireAll
      ? menuConfig.requiredPermissions.every(perm => userPermissions[perm])
      : menuConfig.requiredPermissions.some(perm => userPermissions[perm]);
    
    if (!hasPermission) {
      return false;
    }
  }

  return true;
};

/**
 * 过滤用户可见的菜单项
 */
export const filterAccessibleMenus = (
  menus: any[],
  userPermissions: EnterprisePermissions,
  userRole?: string
): any[] => {
  return menus.filter(menu => {
    const hasPermission = checkMenuPermission(menu.key, userPermissions, userRole);
    
    if (!hasPermission) {
      return false;
    }

    // 递归过滤子菜单
    if (menu.children) {
      menu.children = filterAccessibleMenus(menu.children, userPermissions, userRole);
    }

    return true;
  });
}; 