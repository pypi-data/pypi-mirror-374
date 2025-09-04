#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ultra Pass Python Sidecar

一个简洁的Python微服务sidecar，支持自动注册到Nacos和Feign风格调用。

功能特性:
- 自动服务注册到Nacos
- Feign风格的HTTP客户端调用
- 异构服务支持（Java、Python、Go等）
- 配置中心支持
- 权限拦截器
- 心跳保活机制
- 优雅关闭

@author: lzg
@created: 2025-07-01 14:23:45
@version: 1.0.0
"""

import asyncio
import threading
import yaml
import aiohttp
import json
import re
import inspect
import sys
import os
from typing import Dict, Any, Optional, Callable
from functools import wraps

# 全局配置
_config = None
_nacos_client = None
_service_name = None
_service_port = None
_config_center = None
_web_framework = None
_auth_interceptor = None

# 请求上下文管理
import threading
_request_context = threading.local()

def init_sidecar(app=None):
    """
    初始化sidecar，自动注册服务到Nacos
    服务端启动时调用此函数即可
    
    Args:
        app: Web应用实例（Flask、FastAPI等），可选
    """
    global _config, _nacos_client, _service_name, _service_port, _config_center, _web_framework, _auth_interceptor
    
    # 加载配置
    with open('bootstrap.yml', 'r', encoding='utf-8') as f:
        _config = yaml.safe_load(f)
    
    _service_name = _config['application']['name']
    _service_port = _config['server']['port']
    nacos_discovery = _config['cloud']['nacos']['discovery']
    nacos_config = _config['cloud']['nacos']['config']
    nacos_addr = nacos_discovery['server-addr']
    # 新增命名空间、用户名、密码读取
    nacos_namespace = nacos_discovery.get('namespace', "")
    nacos_username = nacos_discovery.get('username', "")
    nacos_password = nacos_discovery.get('password', "")
    config_namespace = nacos_config.get('namespace', "")
    config_username = nacos_config.get('username', "")
    config_password = nacos_config.get('password', "")
    # 从配置文件读取IP地址
    service_ip = nacos_discovery.get('ip', '127.0.0.1')
    # 检测Web框架
    if app is not None:
        if app.__class__.__module__.startswith("flask"):
            _web_framework = 'flask'
        elif app.__class__.__module__.startswith("fastapi"):
            _web_framework = 'fastapi'
        elif app.__class__.__module__.startswith("django"):
            _web_framework = 'django'
        else:
            _web_framework = detect_web_framework()
    else:
        _web_framework = detect_web_framework()
    print(f"🔍 检测到Web框架: {_web_framework}")
    # 启动Nacos客户端，传递namespace、用户名、密码
    _nacos_client = NacosClient(
        nacos_addr, _service_name, _service_port, service_ip,
        namespace=nacos_namespace, username=nacos_username, password=nacos_password
    )
    # 启动配置中心，传递namespace、用户名、密码
    _config_center = ConfigCenter(
        nacos_config['server-addr'], _service_name, _config,
        namespace=config_namespace, username=config_username, password=config_password
    )
    
    # 初始化权限拦截器
    _auth_interceptor = AuthInterceptor()
    
    # 如果传入了app实例，自动设置权限拦截器
    if app is not None:
        setup_auth_interceptor_internal(app)
    
    # 预加载权限微服务接口
    _load_auth_service()
    

    

    
    def _run():
        async def start_all():
            await _nacos_client.start()
            await _config_center.start()
            # 启动心跳任务
            await _nacos_client.start_heartbeat()
            # 保持心跳任务运行
            while _nacos_client.running:
                await asyncio.sleep(1)
        
        asyncio.run(start_all())
    
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    
    # 注册信号处理器，优雅关闭
    import signal
    def signal_handler(signum, frame):
        print(f"\n🛑 收到信号 {signum}，正在优雅关闭...")
        asyncio.run(stop_sidecar())
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"🚀 Sidecar启动成功 - 服务名: {_service_name}, 端口: {_service_port}")

def setup_auth_interceptor_internal(app):
    """内部函数：设置权限拦截器"""
    global _auth_interceptor, _web_framework
    
    if _auth_interceptor is None:
        print("⚠️ Sidecar未初始化，请先调用init_sidecar()")
        return
    
    # 优先根据app实例类型动态切换
    if app.__class__.__module__.startswith("flask"):
        _web_framework = 'flask'
        _auth_interceptor.setup_flask_interceptor(app)
    elif app.__class__.__module__.startswith("fastapi"):
        _web_framework = 'fastapi'
        _auth_interceptor.setup_fastapi_interceptor(app)
    elif app.__class__.__module__.startswith("django"):
        _web_framework = 'django'
        _auth_interceptor.setup_django_interceptor(app)
    else:
        print(f"⚠️ 不支持的Web框架: {type(app)}")

def setup_auth_interceptor(app):
    """设置权限拦截器（向后兼容）"""
    setup_auth_interceptor_internal(app)

def set_request_context(request):
    """设置当前请求上下文"""
    global _request_context
    _request_context.current_request = request

def get_request_context():
    """获取当前请求上下文"""
    global _request_context
    return getattr(_request_context, 'current_request', None)

def get_current_token():
    """从当前请求上下文中获取token"""
    request = get_request_context()
    if not request:
        return None
    
    # 1. 优先从Authorization头获取token
    if hasattr(request, 'headers'):
        # 获取Authorization头
        auth_header = request.headers.get('Authorization', '')
        if auth_header:
            # 清洗Bearer前缀
            if auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '').strip()
                if token:
                    return token
            else:
                # 直接是token的情况
                token = auth_header.strip()
                if token:
                    return token
    
    # 2. 从cookie中获取access_token
    if hasattr(request, 'cookies'):
        # Flask请求
        return request.cookies.get('access_token')
    elif hasattr(request, 'cookies'):
        # FastAPI请求
        return request.cookies.get('access_token')
    
    return None

def detect_web_framework():
    """检测当前使用的Web框架"""
    # 检查Flask
    try:
        import flask
        if 'flask' in sys.modules:
            return 'flask'
    except ImportError:
        pass
    
    # 检查FastAPI
    try:
        import fastapi
        if 'fastapi' in sys.modules:
            return 'fastapi'
    except ImportError:
        pass
    
    # 检查Django
    try:
        import django
        if 'django' in sys.modules:
            return 'django'
    except ImportError:
        pass
    
    # 检查Gunicorn
    try:
        import gunicorn
        if 'gunicorn' in sys.modules:
            return 'gunicorn'
    except ImportError:
        pass
    
    # 检查Uvicorn
    try:
        import uvicorn
        if 'uvicorn' in sys.modules:
            return 'uvicorn'
    except ImportError:
        pass
    
    return 'unknown'

async def stop_sidecar():
    """停止sidecar"""
    global _nacos_client, _config_center
    
    if _nacos_client:
        await _nacos_client.stop()
    
    if _config_center and _config_center.session:
        await _config_center.session.close()

class ConfigValue:
    """配置值类，类似Java @Value注解"""
    
    def __init__(self, config_key: str, default: Any = None):
        self.config_key = config_key
        self.default = default
    
    def __get__(self, obj, objtype=None):
        return get_config_value(self.config_key, self.default)

def config_remote(config_key: str, default: Any = None):
    """
    从Nacos配置中心获取配置
    用法: 
    server_port = config_remote('server.port', 9201)
    redis_host = config_remote('spring.data.redis.host', 'localhost')
    """
    return get_config_value(config_key, default)

def config_local(config_key: str, default: Any = None) -> Any:
    """
    从本地bootstrap.yml获取配置
    用法:
    port = config_local('server.port', 9202)
    service_name = config_local('application.name', 'unknown')
    """
    global _config
    if _config is None:
        return default
    
    keys = config_key.split('.')
    current = _config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def get_config_value(config_key: str, default: Any = None) -> Any:
    """
    获取远程配置值
    支持点分隔的配置路径，如: spring.data.redis.host
    """
    global _config_center
    if _config_center is None:
        return default
    
    return _config_center.get_value(config_key, default)

# 为了向后兼容，保留别名
def remote_config(config_key: str, default: Any = None):
    """别名: config_remote"""
    return config_remote(config_key, default)

def local_config(config_key: str, default: Any = None) -> Any:
    """别名: config_local"""
    return config_local(config_key, default)

class AuthService:
    """权限服务"""
    
    def __init__(self):
        self.auth_client = AuthClient()
    
    async def check_permission(self, url: str, method: str, headers: dict, cookies: dict = None, params: dict = None) -> dict:
        """检查权限"""
        try:
            # 从多个地方获取token
            token = self._extract_token(headers, cookies, params)
            if not token:
                return {
                    'has_permission': False,
                    'message': 'token不能为空，请从cookie、header或parameter中提供token'
                }
            
            # 获取应用代码
            app_code = config_local('application.code')
            if not app_code:
                return {
                    'has_permission': False,
                    'message': '应用代码未配置，请在bootstrap.yml中配置application.code'
                }
            app_code = str(app_code)
            
            # 调用权限微服务
            result = await self.auth_client.check_permission(url, app_code)
            return result
            
        except Exception as e:
            print(f"权限检查失败: {e}")
            return {
                'has_permission': False,
                'message': f'权限检查失败: {str(e)}'
            }
    
    def _extract_token(self, headers: dict, cookies: dict = None, params: dict = None) -> str:
        """从多个地方提取token"""
        # 1. 从Authorization头获取
        auth_header = headers.get('Authorization', '')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '')
                if token:
                    return token
            else:
                # 直接是token的情况
                return auth_header
        
        # 2. 从cookie获取
        if cookies:
            # 常见的token cookie名称
            token_cookies = ['token', 'access_token', 'auth_token', 'jwt_token', 'session_token']
            for cookie_name in token_cookies:
                token = cookies.get(cookie_name)
                if token:
                    return token
        
        # 3. 从URL参数获取
        if params:
            # 常见的token参数名称
            token_params = ['token', 'access_token', 'auth_token', 'jwt_token']
            for param_name in token_params:
                token = params.get(param_name)
                if token:
                    return token
        
        # 4. 从自定义头获取
        custom_headers = ['X-Auth-Token', 'X-Token', 'X-Access-Token']
        for header_name in custom_headers:
            token = headers.get(header_name)
            if token:
                return token
        
        return ''

class AuthClient:
    """权限微服务客户端"""
    
    def __init__(self):
        self.auth_service = AuthPermissionService()
    
    async def check_permission(self, url: str, code: str) -> dict:
        """检查权限"""
        try:
            # 检查code是否为空
            if not code:
                return {
                    'has_permission': False,
                    'message': '应用代码不能为空'
                }
            
            # 调用权限微服务
            result = await self.auth_service.check_permission(url=url, code=code)
            
            # 解析返回结果
            if result and result.get('code') == 200:
                return {
                    'has_permission': True,
                    'message': '权限验证通过'
                }
            else:
                return {
                    'has_permission': False,
                    'message': result.get('msg', '权限不足') if result else '权限验证失败'
                }
                
        except Exception as e:
            print(f"调用权限服务失败: {e}")
            # 根据配置决定失败时的行为
            if config_local('auth.fail_open', True):
                return {
                    'has_permission': True,
                    'message': '权限服务不可用，默认放行'
                }
            else:
                return {
                    'has_permission': False,
                    'message': f'权限服务调用失败: {str(e)}'
                }

# 权限微服务接口定义 - 动态加载
_auth_service_module = None

def _load_auth_service():
    """动态加载权限微服务接口"""
    global _auth_service_module
    if _auth_service_module is None:
        try:
            from . import auth_service
            _auth_service_module = auth_service
            print("✅ 权限微服务接口加载成功")
        except Exception as e:
            print(f"⚠️ 权限微服务接口加载失败: {e}")
            return None
    return _auth_service_module

class AuthPermissionService:
    """权限微服务接口代理"""
    
    def __init__(self):
        self._service = None
    
    def _get_service(self):
        """获取权限服务实例"""
        if self._service is None:
            module = _load_auth_service()
            if module:
                self._service = module.AuthPermissionService()
            else:
                raise Exception("权限微服务接口未加载")
        return self._service
    
    async def check_permission(self, url: str, code: str = None):
        """权限校验接口"""
        service = self._get_service()
        return await service.check_permission(url=url, code=code)
    
    async def get_menu_resources(self, code: str, token: str = None):
        """获取菜单资源"""
        service = self._get_service()
        return await service.get_menu_resources(code=code)
    
    async def get_user_info(self, token: str = None):
        """获取用户信息"""
        service = self._get_service()
        return await service.get_user_info()

class AuthInterceptor:
    """权限拦截器"""
    
    def __init__(self):
        self.auth_service = AuthService()
    
    def setup_flask_interceptor(self, app):
        """设置Flask权限拦截器"""
        from flask import request, jsonify
        
        @app.before_request
        def before_request():
            # 设置请求上下文
            set_request_context(request)
            
            # 跳过OPTIONS请求
            if request.method == 'OPTIONS':
                return None
            
            # 检查权限是否启用
            if not config_local('auth.enabled', True):
                return None
            
            # 检查排除路径
            exclude_paths = config_local('auth.exclude_paths', [])
            for exclude_path in exclude_paths:
                if request.path.startswith(exclude_path):
                    return None
            
            # 跳过静态文件
            if request.path.startswith('/static/'):
                return None
            
            # 跳过健康检查
            if request.path in ['/health', '/healthz', '/ping']:
                return None
            
            # 权限检查
            try:
                result = asyncio.run(self.auth_service.check_permission(
                    url=request.path,
                    method=request.method,
                    headers=dict(request.headers),
                    cookies=dict(request.cookies),
                    params=dict(request.args)
                ))
                
                if not result.get('has_permission', False):
                    return jsonify({
                        'code': 401,
                        'message': result.get('message', '权限不足')
                    }), 401
                    
            except Exception as e:
                print(f"权限检查异常: {e}")
                # 权限检查失败时，根据配置决定是否放行
                if config_local('auth.fail_open', True):
                    return None
                else:
                    return jsonify({
                        'code': 500,
                        'message': '权限检查失败'
                    }), 500
    
    def setup_fastapi_interceptor(self, app):
        """设置FastAPI权限拦截器"""
        from fastapi import Request, HTTPException
        from fastapi.responses import JSONResponse
        
        @app.middleware("http")
        async def auth_middleware(request: Request, call_next):
            # 设置请求上下文
            set_request_context(request)
            
            # 跳过OPTIONS请求
            if request.method == "OPTIONS":
                return await call_next(request)
            
            # 检查权限是否启用
            if not config_local('auth.enabled', True):
                return await call_next(request)
            
            # 检查排除路径
            exclude_paths = config_local('auth.exclude_paths', [])
            for exclude_path in exclude_paths:
                if request.url.path.startswith(exclude_path):
                    return await call_next(request)
            
            # 跳过静态文件
            if request.url.path.startswith('/static/'):
                return await call_next(request)
            
            # 跳过健康检查
            if request.url.path in ['/health', '/healthz', '/ping']:
                return await call_next(request)
            
            # 权限检查
            try:
                result = await self.auth_service.check_permission(
                    url=str(request.url.path),
                    method=request.method,
                    headers=dict(request.headers),
                    cookies=dict(request.cookies),
                    params=dict(request.query_params)
                )
                
                if not result.get('has_permission', False):
                    return JSONResponse(
                        status_code=401,
                        content={
                            'code': 401,
                            'message': result.get('message', '权限不足')
                        }
                    )
                    
            except Exception as e:
                print(f"权限检查异常: {e}")
                # 权限检查失败时，根据配置决定是否放行
                if config_local('auth.fail_open', True):
                    return await call_next(request)
                else:
                    return JSONResponse(
                        status_code=500,
                        content={
                            'code': 500,
                            'message': '权限检查失败'
                        }
                    )
            
            return await call_next(request)
    
    def setup_django_interceptor(self, app):
        """设置Django权限拦截器"""
        # Django中间件实现
        pass

class ConfigCenter:
    """Nacos配置中心客户端"""
    
    def __init__(self, server_addr: str, service_name: str, bootstrap_config: dict, namespace: str = "", username: str = "", password: str = ""):
        self.server_addr = server_addr
        self.service_name = service_name
        self.bootstrap_config = bootstrap_config
        self.namespace = namespace or ""
        self.username = username or ""
        self.password = password or ""
        self.session = None
        self.configs = {}
        self.listeners = {}
        
    async def start(self):
        """启动配置中心"""
        self.session = aiohttp.ClientSession()
        await self.load_configs()
        print(f"📋 配置中心启动成功: {self.service_name}")
        
    async def load_configs(self):
        """加载所有配置"""
        # 加载主配置
        await self.load_config(self.service_name, "DEFAULT_GROUP")
        
        # 加载共享配置
        shared_configs = self.bootstrap_config.get('cloud', {}).get('nacos', {}).get('config', {}).get('shared-configs', [])
        for shared_config in shared_configs:
            # 解析配置名称，如: application-${spring.profiles.active}.${spring.cloud.nacos.config.file-extension}
            config_name = self._resolve_config_name(shared_config)
            await self.load_config(config_name, "DEFAULT_GROUP")
    
    def _resolve_config_name(self, config_template: str) -> str:
        """解析配置名称模板"""
        # 简化实现，实际应该支持更复杂的变量替换
        profiles = self.bootstrap_config.get('profiles', {}).get('active', 'dev')
        file_ext = self.bootstrap_config.get('cloud', {}).get('nacos', {}).get('config', {}).get('file-extension', 'yml')
        
        config_name = config_template.replace('${spring.profiles.active}', profiles)
        config_name = config_name.replace('${spring.cloud.nacos.config.file-extension}', file_ext)
        return config_name
    
    async def load_config(self, data_id: str, group: str):
        """加载指定配置"""
        url = f"http://{self.server_addr}/nacos/v1/cs/configs"
        params = {
            'dataId': data_id,
            'group': group,
            'tenant': self.namespace  # 命名空间
        }
        headers = {}
        if self.username and self.password:
            from base64 import b64encode
            basic_auth = b64encode(f"{self.username}:{self.password}".encode()).decode()
            headers['Authorization'] = f"Basic {basic_auth}"
        try:
            async with self.session.get(url, params=params, headers=headers) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    # 解析YAML配置
                    config_data = yaml.safe_load(content) if content else {}
                    self.configs[data_id] = config_data
                    print(f"✅ 配置加载成功: {data_id}")
                else:
                    print(f"⚠️ 配置加载失败: {data_id}, 状态码: {resp.status}")
        except Exception as e:
            print(f"❌ 配置加载异常: {data_id}, 错误: {e}")
    
    def get_value(self, config_key: str, default: Any = None) -> Any:
        """
        获取配置值
        支持点分隔的配置路径，如: spring.data.redis.host
        """
        keys = config_key.split('.')
        
        # 遍历所有配置源
        for config_data in self.configs.values():
            value = self._get_nested_value(config_data, keys)
            if value is not None:
                return value
        
        return default
    
    def _get_nested_value(self, data: dict, keys: list) -> Any:
        """递归获取嵌套配置值"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current

def feign(service_name: str):
    """
    定义Feign客户端的装饰器
    """
    def decorator(cls):
        cls._service_name = service_name
        # 为每个方法创建代理
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if hasattr(attr, '_http_method'):
                # 创建代理方法
                setattr(cls, attr_name, create_proxy_method(service_name, attr))
        return cls
    return decorator

def create_proxy_method(service_name: str, original_method):
    """创建代理方法"""
    async def proxy_method(self, *args, **kwargs):
        # 获取HTTP方法和路径
        method = original_method._http_method
        path_template = original_method._path
        
        # 处理路径参数
        path = path_template
        path_param_count = path_template.count('{')
        path_args = args[:path_param_count]
        other_args = args[path_param_count:]
        for i, arg in enumerate(path_args):
            path = re.sub(r'\{[^}]+\}', str(arg), path, count=1)
        
        # 处理查询参数
        params = {}
        for key, value in kwargs.items():
            if key not in ['data', 'json', 'headers']:
                # 过滤掉None值
                if value is not None:
                    if isinstance(value, bool):
                        params[key] = str(value).lower()
                    else:
                        params[key] = value
        
        # 处理POST请求体自动组装
        data = kwargs.get('data')
        json_data = kwargs.get('json')
        headers = kwargs.get('headers', {})
        
        # 添加 from-source: inner 请求头
        headers = {**headers, "from-source": "inner"}
        
        # 自动处理token：优先从参数获取，其次从当前请求上下文获取
        token = kwargs.get('token')
        if not token:
            # 从当前请求上下文中获取token
            token = get_current_token()
        
        # 确保token不为空且不为None
        if token and token.strip() != '':
            headers['Authorization'] = f"Bearer {token}"
            # 从参数中移除token，避免重复传递
            if 'token' in params:
                del params['token']
        
        # 打印调试信息
        print(f"🔍 微服务调用调试信息:")
        print(f"   服务名: {service_name}")
        print(f"   请求方法: {method}")
        print(f"   请求路径: {path}")
        print(f"   请求头: {headers}")
        print(f"   请求参数: {params}")
        print(f"   请求体: {json_data if json_data else data}")
        print(f"   Token: {token}")
        print(f"   Token长度: {len(token) if token else 0}")
        
        if method == 'POST' and json_data is None and data is None:
            # 自动组装json体（去除path参数和headers参数）
            sig = inspect.signature(original_method)
            param_names = list(sig.parameters.keys())[1:]  # 跳过self
            # 跳过path参数
            param_names = param_names[path_param_count:]
            json_data = {}
            # 先处理多余的位置参数
            for i, v in enumerate(other_args):
                if i < len(param_names):
                    json_data[param_names[i]] = v
            # 再处理kwargs
            for k, v in kwargs.items():
                if k not in ['data', 'json', 'headers'] and k in param_names:
                    json_data[k] = v
            headers = {**headers, "Content-Type": "application/json"}
        elif json_data is not None:
            headers = {**headers, "Content-Type": "application/json"}
        
        # 调用远程服务
        async with FeignProxy(service_name) as proxy:
            return await proxy.call(method, path, params=params, data=data, json=json_data, headers=headers)
    
    return proxy_method

def get(path: str):
    """GET请求装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 这个方法会被feign_client装饰器替换
            pass
        wrapper._http_method = 'GET'
        wrapper._path = path
        return wrapper
    return decorator

def post(path: str):
    """POST请求装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 这个方法会被feign_client装饰器替换
            pass
        wrapper._http_method = 'POST'
        wrapper._path = path
        return wrapper
    return decorator

class NacosClient:
    """Nacos客户端，使用Nacos SDK"""
    
    def __init__(self, server_addr: str, service_name: str, port: int, ip: str = None, namespace: str = "", username: str = "", password: str = ""):
        self.server_addr = server_addr
        self.service_name = service_name
        self.port = port
        self.ip = ip or '127.0.0.1'
        self.namespace = namespace or ""
        self.username = username or ""
        self.password = password or ""
        self.naming_client = None
        self.running = False
        self.heartbeat_task = None
        self.heartbeat_interval = 10  # 心跳间隔（秒）
        
    async def start(self):
        """启动Nacos客户端"""
        try:
            from nacos import NacosClient as NacosSDKClient
            
            # 创建Nacos SDK客户端（兼容Nacos 2.0.3）
            self.naming_client = NacosSDKClient(
                server_addresses=self.server_addr,
                namespace=self.namespace,  # 支持命名空间
                username=self.username,   # 支持用户名
                password=self.password    # 支持密码
            )
            
            # 注册服务
            await self.register_service()
            print(f"✅ 服务注册成功: {self.service_name} -> {self.server_addr}")
            
            self.running = True
            
        except Exception as e:
            print(f"❌ Nacos客户端启动失败: {e}")
            raise
    
    async def start_heartbeat(self):
        """启动心跳任务"""
        if self.heartbeat_task is None:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            print(f"💓 心跳任务启动成功，间隔: {self.heartbeat_interval}秒")
    
    async def _heartbeat_loop(self):
        """心跳循环任务"""
        while self.running:
            try:
                await self._send_heartbeat()
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                print(f"⚠️ 心跳发送失败: {e}")
                await asyncio.sleep(self.heartbeat_interval)
    
    async def _send_heartbeat(self):
        """发送心跳到Nacos"""
        try:
            if self.naming_client:
                # 使用Nacos SDK发送心跳（兼容Nacos 2.0.3）
                # 注意：Nacos SDK会自动处理心跳，这里主要是保持连接
                # 我们可以通过重新注册实例来模拟心跳
                self.naming_client.add_naming_instance(
                    service_name=self.service_name,
                    ip=self.ip,
                    port=self.port,
                    weight=1.0,
                    metadata={'version': '1.0.0'},
                    ephemeral=True,  # 临时实例，支持心跳
                    heartbeat_interval=self.heartbeat_interval * 1000  # 毫秒
                )
                print(f"💓 心跳保持成功: {self.service_name}")
        except Exception as e:
            print(f"❌ 心跳保持失败: {self.service_name}, 错误: {e}")
            raise
    
    async def register_service(self):
        """注册服务到Nacos"""
        try:
            # 使用Nacos SDK注册服务（兼容Nacos 2.0.3）
            self.naming_client.add_naming_instance(
                service_name=self.service_name,
                ip=self.ip,
                port=self.port,
                weight=1.0,
                metadata={'version': '1.0.0'},
                ephemeral=True,  # 临时实例，支持心跳
                heartbeat_interval=self.heartbeat_interval * 1000  # 毫秒
            )
            print(f"🎯 服务注册成功: {self.service_name}")
        except Exception as e:
            print(f"❌ 服务注册失败: {self.service_name}, 错误: {e}")
            raise
    
    async def get_service_instance(self, service_name: str):
        """获取服务实例（带负载均衡，兼容Nacos 2.0.3）"""
        try:
            # 获取所有健康的服务实例
            instances_data = self.naming_client.list_naming_instance(service_name)
            if not instances_data or 'hosts' not in instances_data:
                print(f"⚠️ 服务 {service_name} 没有可用实例")
                return None
            
            # 过滤健康的实例
            healthy_instances = []
            for inst in instances_data['hosts']:
                # 检查实例是否健康
                if inst.get('healthy', False) or inst.get('enabled', False):
                    healthy_instances.append(inst)
            
            if not healthy_instances:
                print(f"⚠️ 服务 {service_name} 没有健康实例")
                return None
            
            # 简单的随机负载均衡
            import random
            selected_instance = random.choice(healthy_instances)
            print(f"🎯 选择服务实例: {service_name} -> {selected_instance['ip']}:{selected_instance['port']}")
            
            # 创建一个简单的对象来模拟实例
            class ServiceInstance:
                def __init__(self, ip, port):
                    self.ip = ip
                    self.port = port
            
            return ServiceInstance(selected_instance['ip'], selected_instance['port'])
        except Exception as e:
            print(f"❌ 获取服务实例失败: {service_name}, 错误: {e}")
            return None
    
    async def stop(self):
        """停止Nacos客户端"""
        self.running = False
        
        # 停止心跳任务
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
            self.heartbeat_task = None
            print(f"💓 心跳任务已停止: {self.service_name}")
        
        if self.naming_client:
            try:
                # 注销服务
                self.naming_client.remove_naming_instance(
                    service_name=self.service_name,
                    ip=self.ip,
                    port=self.port
                )
                print(f"🔚 服务注销成功: {self.service_name}")
            except Exception as e:
                print(f"⚠️ 服务注销失败: {self.service_name}, 错误: {e}")

class FeignProxy:
    """Feign代理，使用Nacos SDK进行服务发现"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.session = None
        self.nacos_client = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        # 获取全局Nacos客户端
        global _nacos_client
        if _nacos_client:
            self.nacos_client = _nacos_client
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def call(self, method: str, path: str, **kwargs):
        """调用远程服务"""
        if not self.nacos_client:
            raise Exception("Nacos客户端未初始化")
        
        # 使用Nacos SDK获取服务实例
        try:
            # 获取服务实例（Nacos SDK会自动处理负载均衡）
            service_instance = await self.nacos_client.get_service_instance(self.service_name)
            if not service_instance:
                raise Exception(f"服务 {self.service_name} 不可用")
            
            base_url = f"http://{service_instance.ip}:{service_instance.port}"
            url = f"{base_url}{path}"
            
            # 打印实际HTTP请求信息
            print(f"🌐 实际HTTP请求:")
            print(f"   完整URL: {url}")
            print(f"   请求方法: {method}")
            print(f"   请求头: {kwargs.get('headers', {})}")
            print(f"   请求参数: {kwargs.get('params', {})}")
            print(f"   请求体: {kwargs.get('json', kwargs.get('data', None))}")
            
            async with self.session.request(method, url, **kwargs) as resp:
                print(f"📡 响应状态码: {resp.status}")
                response_text = await resp.text()
                print(f"📡 响应内容: {response_text[:200]}...")  # 只打印前200个字符
                return await resp.json()
                
        except Exception as e:
            print(f"调用服务 {self.service_name} 失败: {e}")
            raise

def config_var(config_key: str, default: Any = None):
    """
    配置变量装饰器，类似Java @Value
    用法: redis_host = config_var("spring.data.redis.host", "localhost")
    """
    return get_config_value(config_key, default)

def create_config_vars():
    """
    创建配置变量，在init_sidecar后调用
    用法: 
    redis_host, redis_port, db_url = create_config_vars(
        "spring.data.redis.host",
        "spring.data.redis.port", 
        "spring.datasource.url"
    )
    """
    def _create_vars(*config_keys):
        return [get_config_value(key) for key in config_keys]
    return _create_vars

# 导出主要接口
__all__ = [
    'init_sidecar',
    'feign', 
    'get',
    'post',
    'config',
    'get_config_value',
    'local_config'
] 