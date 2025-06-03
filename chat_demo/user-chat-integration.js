/**
 * 企业系统集成RAGFlow聊天窗口示例
 * 为不同用户创建独立的聊天会话
 */

class RAGFlowChatIntegration {
    constructor(config) {
        this.baseURL = config.baseURL; // RAGFlow服务地址
        this.apiKey = config.apiKey;   // API密钥
        this.chatId = config.chatId;   // 聊天助手ID
        this.auth = config.auth;       // 认证token
    }

    /**
     * 为用户创建新的聊天会话
     * @param {string} userId - 用户ID
     * @param {string} userName - 用户名称
     * @returns {Promise<Object>} 会话信息
     */
    async createUserSession(userId, userName = null) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/chats/${this.chatId}/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify({
                    name: userName ? `${userName}的聊天会话` : `用户${userId}的会话`,
                    user_id: userId
                })
            });

            const result = await response.json();
            
            if (result.code === 0) {
                return {
                    success: true,
                    sessionId: result.data.id,
                    sessionName: result.data.name,
                    userId: userId
                };
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('创建会话失败:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 获取用户现有的会话列表
     * @param {string} userId - 用户ID
     * @returns {Promise<Array>} 会话列表
     */
    async getUserSessions(userId) {
        try {
            const response = await fetch(
                `${this.baseURL}/api/v1/chats/${this.chatId}/sessions?user_id=${userId}&page=1&page_size=50`, 
                {
                    headers: {
                        'Authorization': `Bearer ${this.apiKey}`
                    }
                }
            );

            const result = await response.json();
            
            if (result.code === 0) {
                return result.data;
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('获取用户会话失败:', error);
            return [];
        }
    }

    /**
     * 为用户获取或创建聊天会话
     * @param {string} userId - 用户ID
     * @param {string} userName - 用户名称
     * @returns {Promise<string>} 会话ID
     */
    async getOrCreateUserSession(userId, userName = null) {
        // 首先查看用户是否已有会话
        const existingSessions = await this.getUserSessions(userId);
        
        if (existingSessions.length > 0) {
            // 使用最新的会话
            return existingSessions[0].id;
        }
        
        // 如果没有现有会话，创建新会话
        const newSession = await this.createUserSession(userId, userName);
        
        if (newSession.success) {
            return newSession.sessionId;
        } else {
            throw new Error('无法创建用户会话: ' + newSession.error);
        }
    }

    /**
     * 生成用户专属的聊天窗口URL
     * @param {string} userId - 用户ID
     * @param {string} userName - 用户名称
     * @returns {Promise<string>} 聊天窗口URL
     */
    async generateUserChatURL(userId, userName = null) {
        try {
            const sessionId = await this.getOrCreateUserSession(userId, userName);
            
            return `${this.baseURL}/chat/share?shared_id=${sessionId}&from=chat&auth=${this.auth}`;
        } catch (error) {
            console.error('生成聊天URL失败:', error);
            throw error;
        }
    }

    /**
     * 在页面中嵌入用户专属聊天窗口
     * @param {string} containerId - 容器元素ID
     * @param {string} userId - 用户ID
     * @param {string} userName - 用户名称
     */
    async embedUserChat(containerId, userId, userName = null) {
        try {
            const chatURL = await this.generateUserChatURL(userId, userName);
            
            const container = document.getElementById(containerId);
            if (!container) {
                throw new Error(`找不到容器元素: ${containerId}`);
            }

            container.innerHTML = `
                <iframe
                    src="${chatURL}"
                    style="width: 100%; height: 100%; min-height: 600px; border: none; border-radius: 6px;"
                    frameborder="0"
                    title="用户聊天窗口"
                ></iframe>
            `;
            
            return chatURL;
        } catch (error) {
            console.error('嵌入聊天窗口失败:', error);
            
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = `
                    <div style="padding: 20px; text-align: center; color: #999;">
                        聊天窗口加载失败: ${error.message}
                    </div>
                `;
            }
            throw error;
        }
    }
}

// 使用示例
const chatIntegration = new RAGFlowChatIntegration({
    baseURL: 'http://sz.safewaychina.cn:7080',
    apiKey: 'YOUR_API_KEY',
    chatId: 'YOUR_CHAT_ID',
    auth: 'UzOTkwZmEyM2NmYzExZjA4MDE1ZmFjYT'
});

// 示例：当用户登录后，为其嵌入专属聊天窗口
async function initUserChat(userId, userName) {
    try {
        await chatIntegration.embedUserChat('chat-container', userId, userName);
        console.log(`用户 ${userName} 的聊天窗口已加载`);
    } catch (error) {
        console.error('初始化用户聊天失败:', error);
    }
}

// 示例：在用户信息变更时更新聊天窗口
async function updateUserChat(oldUserId, newUserId, userName) {
    try {
        // 为新用户创建会话
        const newChatURL = await chatIntegration.generateUserChatURL(newUserId, userName);
        
        // 更新iframe源
        const iframe = document.querySelector('#chat-container iframe');
        if (iframe) {
            iframe.src = newChatURL;
        }
        
        console.log(`聊天窗口已切换到用户 ${userName}`);
    } catch (error) {
        console.error('更新用户聊天失败:', error);
    }
} 