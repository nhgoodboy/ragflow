"""
企业系统用户聊天会话管理器
用于管理不同用户的RAGFlow聊天会话
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import sqlite3
import hashlib
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# RAGFlow配置
RAGFLOW_CONFIG = {
    'base_url': 'http://sz.safewaychina.cn:7080',
    'api_key': 'YOUR_API_KEY',        # 需要替换为实际的API密钥
    'chat_id': 'YOUR_CHAT_ID',        # 需要替换为实际的聊天助手ID
    'auth_token': 'UzOTkwZmEyM2NmYzExZjA4MDE1ZmFjYT'  # 现有的auth token
}

class UserSessionManager:
    """用户会话管理器"""
    
    def __init__(self, db_path='user_sessions.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建用户会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_name TEXT,
                session_id TEXT UNIQUE NOT NULL,
                session_name TEXT,
                chat_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # 创建用户信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                user_name TEXT,
                department TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user_session(self, user_id, user_name=None):
        """为用户创建新的聊天会话"""
        try:
            # 调用RAGFlow API创建会话
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {RAGFLOW_CONFIG['api_key']}"
            }
            
            payload = {
                'name': f"{user_name or user_id}的聊天会话",
                'user_id': user_id
            }
            
            response = requests.post(
                f"{RAGFLOW_CONFIG['base_url']}/api/v1/chats/{RAGFLOW_CONFIG['chat_id']}/sessions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    session_data = result['data']
                    session_id = session_data['id']
                    
                    # 生成聊天URL
                    chat_url = self.generate_chat_url(session_id, user_id)
                    
                    # 保存到数据库
                    self.save_user_session(user_id, user_name, session_id, session_data.get('name'), chat_url)
                    
                    return {
                        'success': True,
                        'session_id': session_id,
                        'session_name': session_data.get('name'),
                        'chat_url': chat_url
                    }
                else:
                    return {'success': False, 'error': result.get('message', '创建会话失败')}
            else:
                return {'success': False, 'error': f'API请求失败: {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            # 如果API调用失败，创建模拟会话（用于演示）
            print(f"API调用失败，创建模拟会话: {e}")
            return self.create_mock_session(user_id, user_name)
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_mock_session(self, user_id, user_name=None):
        """创建模拟会话（用于演示）"""
        session_id = str(uuid.uuid4()).replace('-', '')
        session_name = f"{user_name or user_id}的模拟会话"
        
        # 使用现有的shared_id作为演示
        chat_url = self.generate_chat_url('c23776c03cfa11f08a28faca3d0be991', user_id)
        
        # 保存到数据库
        self.save_user_session(user_id, user_name, session_id, session_name, chat_url)
        
        return {
            'success': True,
            'session_id': session_id,
            'session_name': session_name,
            'chat_url': chat_url,
            'is_mock': True
        }
    
    def generate_chat_url(self, session_id, user_id):
        """生成聊天URL"""
        return f"{RAGFLOW_CONFIG['base_url']}/chat/share?shared_id={session_id}&from=chat&auth={RAGFLOW_CONFIG['auth_token']}&user_id={user_id}"
    
    def save_user_session(self, user_id, user_name, session_id, session_name, chat_url):
        """保存用户会话到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_sessions 
            (user_id, user_name, session_id, session_name, chat_url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, user_name, session_id, session_name, chat_url, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_user_sessions(self, user_id):
        """获取用户的所有会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, session_name, chat_url, created_at, updated_at
            FROM user_sessions
            WHERE user_id = ? AND is_active = 1
            ORDER BY updated_at DESC
        ''', (user_id,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'session_id': row[0],
                'session_name': row[1],
                'chat_url': row[2],
                'created_at': row[3],
                'updated_at': row[4]
            })
        
        conn.close()
        return sessions
    
    def get_or_create_user_session(self, user_id, user_name=None):
        """获取或创建用户会话"""
        # 首先查找现有会话
        sessions = self.get_user_sessions(user_id)
        
        if sessions:
            # 返回最新的会话
            return {
                'success': True,
                'existing': True,
                **sessions[0]
            }
        
        # 如果没有现有会话，创建新会话
        return self.create_user_session(user_id, user_name)
    
    def register_user(self, user_id, user_name, department=None, email=None):
        """注册用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, user_name, department, email)
            VALUES (?, ?, ?, ?)
        ''', (user_id, user_name, department, email))
        
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        """获取所有用户"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id, user_name, department, email FROM users ORDER BY user_name')
        
        users = []
        for row in cursor.fetchall():
            users.append({
                'user_id': row[0],
                'user_name': row[1],
                'department': row[2],
                'email': row[3]
            })
        
        conn.close()
        return users

# 创建会话管理器实例
session_manager = UserSessionManager()

# 初始化一些示例用户
sample_users = [
    {'user_id': 'user_001', 'user_name': '张三', 'department': '技术部', 'email': 'zhangsan@company.com'},
    {'user_id': 'user_002', 'user_name': '李四', 'department': '市场部', 'email': 'lisi@company.com'},
    {'user_id': 'user_003', 'user_name': '王五', 'department': '销售部', 'email': 'wangwu@company.com'},
    {'user_id': 'user_004', 'user_name': '赵六', 'department': '人事部', 'email': 'zhaoliu@company.com'},
    {'user_id': 'user_005', 'user_name': '钱七', 'department': '财务部', 'email': 'qianqi@company.com'}
]

for user in sample_users:
    session_manager.register_user(**user)

# API路由
@app.route('/api/users', methods=['GET'])
def get_users():
    """获取所有用户列表"""
    try:
        users = session_manager.get_all_users()
        return jsonify({'success': True, 'data': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<user_id>/session', methods=['GET'])
def get_user_session(user_id):
    """获取或创建用户聊天会话"""
    try:
        user_name = request.args.get('user_name')
        result = session_manager.get_or_create_user_session(user_id, user_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<user_id>/sessions', methods=['GET'])
def get_user_sessions(user_id):
    """获取用户的所有会话"""
    try:
        sessions = session_manager.get_user_sessions(user_id)
        return jsonify({'success': True, 'data': sessions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/<user_id>/session', methods=['POST'])
def create_user_session(user_id):
    """为用户创建新的聊天会话"""
    try:
        data = request.get_json() or {}
        user_name = data.get('user_name')
        result = session_manager.create_user_session(user_id, user_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def register_user():
    """注册新用户"""
    try:
        data = request.get_json()
        if not data or not data.get('user_id') or not data.get('user_name'):
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400
        
        session_manager.register_user(
            data['user_id'],
            data['user_name'],
            data.get('department'),
            data.get('email')
        )
        
        return jsonify({'success': True, 'message': '用户注册成功'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ragflow_config': {
            'base_url': RAGFLOW_CONFIG['base_url'],
            'chat_id': RAGFLOW_CONFIG['chat_id']
        }
    })

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取前端配置"""
    return jsonify({
        'success': True,
        'config': {
            'base_url': RAGFLOW_CONFIG['base_url'],
            'auth_token': RAGFLOW_CONFIG['auth_token']
        }
    })

if __name__ == '__main__':
    print("启动用户会话管理服务...")
    print(f"RAGFlow服务地址: {RAGFLOW_CONFIG['base_url']}")
    print("访问 http://localhost:5000/api/health 检查服务状态")
    print("访问 http://localhost:5000/api/users 查看用户列表")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 