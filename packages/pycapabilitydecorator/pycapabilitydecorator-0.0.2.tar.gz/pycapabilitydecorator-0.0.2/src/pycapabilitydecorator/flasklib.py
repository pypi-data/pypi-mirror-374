# flasklib.py
# -*- coding: utf-8 -*-

"""
Flask 服务器相关功能模块
用于处理基于 CapabilityDecorator 的 Web 服务
"""

from email.policy import default
import json
import base64
import os
import sys
import shutil
import time
from timeit import default_timer
from tkinter import N
from flask import Flask, jsonify, render_template, request , send_from_directory , render_template_string
from . import tools



class printLogger:

    def info(self, message):
        print(message)

    def error(self, message):
        print(message)

    def debug(self, message):
        print(message)

    def warning(self, message):
        print(message)

INDEX_HTML = 'index.html'
class FlaskServer:
    """Flask 服务器封装类"""

    default_templates_path = "assets/pages"
    default_static_path = "assets/static"
    page_404 = ""
    page_500 = ""
    page_404_content = None
    page_500_content = None

    def __init__(self, capabilities,  server_params=None , log =printLogger()):
        """
        初始化 Flask 服务器

        Args:
            capabilities (dict): 能力元数据字典
            server_params (dict): 服务器配置参数
        """
        self.capabilities = capabilities
        self.server_params = server_params or {}
        self.log = log
        # 获取服务器配置参数
        self.host = self.server_params.get('host', '0.0.0.0')
        self.port = self.server_params.get('port', 5000)


        # 获取能力所在路径
        self.capability_dir = self.server_params.get('capability_dir')

        #self.log.debug(f"self.server_params: {self.server_params}")

        self.routes_type = self.server_params.get('routes_type', "html")

        # 智能查找模板目录
        self.templates = self._find_templates_path()
        self.static = self._find_static_path()

        self.log.info(f"模板目录.templates: {self.templates}")
        self.log.info(f"模板目录.static: {self.static}")


        self._set_404_500_page()

        # 创建 Flask 应用
        self.app = Flask(__name__,
                        template_folder=self.templates,
                        static_folder=self.static,
                        static_url_path='/static')

        # 设置路由
        self._setup_routes()

        # 创建页面处理器缓存
        self._page_handler_cache = {}

        # 创建页面处理器缓存，限制最大缓存数量
        self._page_handler_cache = {}
        self._max_cache_size = 50  # 限制缓存最大条目数

    def _find_templates_path(self):
        """智能查找模板目录"""
        # 优先使用传入的参数
        if self.server_params.get('templates'):
            return self.server_params.get('templates')

        # 获取从 CapabilityDecorator 传递的目录信息
        current_dir = self.server_params.get('current_working_dir', os.getcwd())
        script_dir = self.server_params.get('script_dir', current_dir)
        caller_dir = self.server_params.get('caller_dir', current_dir)

        # 尝试常见的模板目录路径
        possible_paths = [
            "assets/pages",  # 相对于当前工作目录
            os.path.join(current_dir, "assets/pages"),
            os.path.join(current_dir, "assets/pages"),
            os.path.join(script_dir, "assets/pages"),
            os.path.join(caller_dir, "assets/pages") if caller_dir else None,
        ]

        # 移除 None 值
        possible_paths = [p for p in possible_paths if p is not None]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found templates directory: {path}")
                # 返回绝对路径
                return os.path.abspath(path)

        # 如果都找不到，返回默认值的绝对路径
        default_path = "assets/pages"
        print(f"Using default templates directory: {default_path}")
        return os.path.abspath(default_path)

    def _find_static_path(self):
        """智能查找静态文件目录"""
        # 优先使用传入的参数
        if self.server_params.get('static'):
            return self.server_params.get('static')

        # 获取从 CapabilityDecorator 传递的目录信息
        current_dir = self.server_params.get('current_working_dir', os.getcwd())
        script_dir = self.server_params.get('script_dir', current_dir)
        caller_dir = self.server_params.get('caller_dir', current_dir)
        

        # 尝试常见的静态文件目录路径
        possible_paths = [
            "assets/static",  # 相对于当前工作目录
            os.path.join(current_dir, "assets/static"),
            os.path.join(script_dir, "assets/static"),
            os.path.join(caller_dir, "assets/static") if caller_dir else None,
        ]

        # 移除 None 值
        possible_paths = [p for p in possible_paths if p is not None]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found static directory: {path}")
                # 返回绝对路径
                return os.path.abspath(path)

        # 如果都找不到，返回默认值的绝对路径
        default_path = "assets/static"
        print(f"Using default static directory: {default_path}")
        return os.path.abspath(default_path)

    def _set_404_500_page(self):
        """设置 404 和 500 页面"""

        default_assets_pages = ''
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_assets_dir = os.path.join(current_dir, 'default_assets' )
        _pages_dir = os.path.join(default_assets_dir, 'pages' )


        self.page_404 = self.server_params.get('page_404', '404.html')
        self.page_500 = self.server_params.get('page_500', '500.html')

        if os.path.exists(_pages_dir):
            default_assets_pages = _pages_dir

        # 特殊需求,使用default 模板 读取
        if self.page_404 == "default":
            default_404 = os.path.join(default_assets_pages, '404.html')
            if os.path.isfile(default_404):
                with open(default_404, 'r', encoding='utf-8') as file:
                    self.page_404_content = file.read()

        if self.page_500 == "default":
            default_500 = os.path.join(default_assets_pages, '500.html')
            if os.path.isfile(default_500):
                with open(default_500, 'r', encoding='utf-8') as file:
                    self.page_500_content = file.read()

    def _handle_methods(self,params):
        """处理方法调用的统一入口"""
        # 查找自定义方法处理器
        custom_methods_handler = None
        for capability in self.capabilities.values():
            methods = capability.get('methods', [])
            for method in methods:
                method_name = method.get('name', '')
                if method_name == 'server_methods':
                    custom_methods_handler = method.get('func')
                    break
            if custom_methods_handler:
                break

        # 收集所有参数
        # 检查 request.args 是否是 ImmutableMultiDict（Flask 的默认类型）或者普通 dict
        # if hasattr(request.args, 'to_dict'):
        #     params = request.args.to_dict()
        # else:
        #     params = dict(request.args)

        # 尝试从 JSON body 中获取参数
        try:
            if request.is_json:
                json_data = request.get_json()
                if isinstance(json_data, dict):
                    params.update(json_data)
        except Exception as e:
            self.log.warning(f"Failed to parse JSON data: {e}")

        # 尝试从 form 中获取参数
        try:
            if request.form:
                params.update(request.form.to_dict())
        except Exception as e:
            self.log.warning(f"Failed to parse form data: {e}")

        # 获取 capability_name 和 method_name
        capability_name = params.get('capability_name')
        method_name = params.get('method_name')

        # 如果没有通过参数传递，则尝试从路径参数中获取
        if not capability_name:
            capability_name = request.view_args.get('capability_name') if request.view_args else None
        if not method_name:
            method_name = request.view_args.get('method_name') if request.view_args else None

        if not capability_name:
            return jsonify({"error": "Missing capability_name"}), 400
        if not method_name:
            return jsonify({"error": "Missing method_name"}), 400

        # 检查 capability 是否存在
        if capability_name not in self.capabilities:
            return jsonify({"error": f"Capability '{capability_name}' not found"}), 404

        # 获取 capability 信息
        capability = self.capabilities[capability_name]

        # 查找对应的方法
        method_func = None
        func_params = []
        for method in capability.get('methods', []):
            if method.get('name') == method_name:
                method_func = method.get('func')
                # 获取函数签名以了解它接受哪些参数
                import inspect
                sig = inspect.signature(method_func)
                func_params = list(sig.parameters.keys())
                break

        if not method_func:
            return jsonify({"error": f"Method '{method_name}' not found in capability '{capability_name}'"}), 404

        try:
            # 记录即将调用的方法信息
            self.log.info(f"Calling method: {method_name} from capability: {capability_name}")
            self.log.info(f"Method function name: {method_func.__name__}")
            self.log.info(f"Method function reference: {method_func}")
            self.log.info(f"Parameters: {params}")

            if params and len(func_params) > 0:
                result = method_func(params)
            elif len(func_params) == 0:
                result = method_func()
            else:
                result = method_func({})

            return jsonify(result) if isinstance(result, dict) else str(result)
        except Exception as e:
            self.log.error(f"Error executing method: {str(e)}")
            return jsonify({"error": f"Error executing method: {str(e)}"}), 500

    def _handle_special_commands(self, command_name, capability_name, params):
        """处理特殊命令"""
        try:
            # 对于 register 命令，返回 capability 元数据
            if command_name == 'register':
                capabilities_meta =	tools.clean_capabilities_meta(self.capabilities)

                # 如果指定了 capability_name，则只返回该 capability 的信息
                if capability_name and capability_name in self.capabilities:
                    # 找到指定的 capability
                    target_capability = None
                    for cap_meta in capabilities_meta:
                        if cap_meta.get('name') == capability_name:
                            target_capability = cap_meta
                            break
                    if target_capability:
                        return jsonify(target_capability)

                return jsonify(capabilities_meta)
            # 对于其他特殊命令，返回通用的成功响应
            elif command_name in ['start', 'stop', 'destroy']:
                result = {
                    'code': 0,
                    'msg': f'{command_name} command executed successfully'
                }
                return jsonify(result)

        except Exception as e:
            self.log.error(f"Error handling special command '{command_name}': {str(e)}")
            return jsonify({"error": f"Error handling special command: {str(e)}"}), 500


    def render_page(self, page_path, option):
        self.log.debug(f"Rendering page '{page_path}' for option '{option}'")
        return render_template( page_path, **option)

    def _setup_routes(self):
        """设置 Flask 路由"""
        # 默认页面处理器 - 显示 register JSON
        @self.app.route('/')
        def index():
            try:
                return render_template(INDEX_HTML)
            except Exception as e:
                self.log.info(f"Index template not found: {e}")
                # 如果没有找到模板，则显示 register JSON
                try:
                    capabilities_meta = tools.clean_capabilities_meta(self.capabilities)
                    self.log.info(f"===capabilities_meta= {capabilities_meta}")
                    return jsonify(capabilities_meta)
                except Exception as json_error:
                    self.log.error(f"Error serializing capabilities: {json_error}")
                    # 返回一个简单的默认响应
                    return jsonify({"message": "Welcome to Capability Decorator Server",
                                   "capabilities": list(self.capabilities.keys())})


        # 页面路由处理器 - 支持/capability/<项目名>/pages/<页面地址> 格式
        @self.app.route('/capability/<capability_name>/pages/<path:page_path>')
        def pages(capability_name, page_path):
            return self._pages_to_routes_handle(capability_name, page_path)


        # 方法路由处理器 - 支持/capability/<项目名>/methods/<方法名> 格式
        @self.app.route('/capability/<capability_name>/methods/<method_name>', methods=['GET', 'POST'])
        def methods_with_capability(capability_name, method_name):
            # 将路径参数添加到请求参数中
            # params = request.args.to_dict()
            # # 保存原始参数以便后续处理
            # request.args = params
            params = {}
            params["capability_name"] = capability_name
            params["method_name"] = method_name
            return self._handle_methods(params)

        if self.routes_type == 'vue':
            # SPA 的兜底路由：所有非 API 路径都返回 index.html
            @self.app.route('/', defaults={'path': ''})
            @self.app.route('/<path:path>')
            def serve_vue(path):
                # 如果是 API 请求，不要兜底
                if path.startswith('api/'):
                    return {'error': 'Not Found'}, 404  # 或者你应该有真正的 API 路由

                # 如果请求的是静态文件（如 .js, .css, .png），尝试从静态目录提供
                if path != "" and os.path.exists(os.path.join(self.app.static_folder, path)):
                    return send_from_directory(self.app.static_folder, path)

                # 其他所有请求，返回 index.html
                if os.path.exists(INDEX_HTML):
                    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    return "index.html not found!", 500


        # 404 处理
        @self.app.errorhandler(404)
        def page_404(error):
            try:
                return render_template(self.page_404)
            except Exception as e:
                try:
                    if self.page_404_content :
                        return render_template_string(self.page_404_content)
                except Exception as e:
                    pass
            # 最后的备选方案
            return "404 Not Found", 404

        # 500 处理
        @self.app.errorhandler(500)
        def page_500(error):
            try:
                return render_template( self.page_500,error=error)
            except Exception as e:
                try:
                    if self.page_500_content :
                        return render_template_string(self.page_500_content,error=error)
                except Exception as e:
                    pass
            # 最后的备选方案
            return "500 Internal Server Error", 500


    def _pages_to_routes_handle(self,capability_name, page_path):
        """ 页面路径处理 """
        start_time = time.time()
        try:
            # 处理页面路径
            actual_page_path = page_path.strip('/')

            # 检查缓存
            cache_key = f"{capability_name}:{actual_page_path}"
            if cache_key in self._page_handler_cache:
                page_handler = self._page_handler_cache[cache_key]
                # 调用缓存的页面处理器
                if page_handler:
                    try:
                        # 创建参数字典
                        params = {
                            'capability_name': capability_name,
                            'page_path': actual_page_path,
                            'url_params': request.args.to_dict()
                        }
                        result = page_handler(params)
                        # 如果返回的是字典，转换为JSON；否则作为HTML内容返回
                        response = jsonify(result) if isinstance(result, dict) else str(result)
                        elapsed_time = time.time() - start_time
                        self.log.info(f"Page {capability_name}/{actual_page_path} served from cache in {elapsed_time:.3f}s")
                        return response
                    except Exception as e:
                        self.log.error(f"Error executing page handler: {str(e)}")
                        # 出错时继续尝试模板方式
                        pass

            # 如果没有指定 capability，尝试从路径中解析或者使用默认处理方式
            if not capability_name:
                # 尝试从路径中解析 capability_name（如果路径格式为 capability_name/...）
                path_parts = actual_page_path.split('/', 1)
                if len(path_parts) > 1 and path_parts[0] in self.capabilities:
                    capability_name = path_parts[0]
                    actual_page_path = path_parts[1]
                else:
                    # 没有指定 capability，显示 index 页面或 JSON
                    try:
                        return render_template(INDEX_HTML)
                    except:
                        # 如果没有找到模板，则显示 register JSON
                        capabilities_meta = tools.clean_capabilities_meta(self.capabilities)
                        return jsonify(capabilities_meta)

            # 检查指定的 capability 是否存在
            if capability_name not in self.capabilities:
                return jsonify({
                    "error": f"Capability '{capability_name}' not found",
                    "available_capabilities": list(self.capabilities.keys())
                }), 404

            # 如果没有指定具体页面路径，尝试获取该 capability 的默认页面
            if not actual_page_path:
                actual_page_path = "index.html"

            # 查找自定义页面处理器
            custom_pages_handler = None
            capability_info = self.capabilities[capability_name]
            methods = capability_info.get('methods', [])
            page_handler = None

            # 查找匹配的页面处理器
            for method in methods:
                method_pages = method.get('pages', [])
                # 检查该方法是否注册了请求的页面路径
                for page in method_pages:
                    if isinstance(page, str) and page.lstrip('/') == actual_page_path:
                        page_handler = method.get('func')
                        break
                    elif isinstance(page, dict) and page.get('url', '').lstrip('/') == actual_page_path:
                        page_handler = method.get('func')
                        break
                if page_handler:
                    break

            # 管理缓存大小，如果超过限制则清除最旧的条目
            if len(self._page_handler_cache) >= self._max_cache_size:
                # 删除第一个条目（最旧的）
                first_key = next(iter(self._page_handler_cache))
                del self._page_handler_cache[first_key]

            # 缓存页面处理器
            self._page_handler_cache[cache_key] = page_handler

            # 如果找到了页面处理器，调用它来生成页面内容
            if page_handler:
                try:
                    # 创建参数字典
                    params = {
                        'capability_name': capability_name,
                        'page_path': actual_page_path,
                        'url_params': request.args.to_dict()
                    }
                    result = page_handler(params)
                    # 如果返回的是字典，转换为JSON；否则作为HTML内容返回
                    if isinstance(result, dict):
                        response = jsonify(result)
                    else:
                        # 获取 MIME 类型，默认为 text/html
                        mime_type = 'text/html'
                        # 查找对应的方法并获取其页面类型
                        for method in methods:
                            if method.get('func') == page_handler:
                                self.log.info(f"Found matching method: {method.get('name')}")
                                if 'pages_type' in method:
                                    mime_type = method['pages_type']
                                    self.log.info(f"Using MIME type from method: {mime_type}")
                                break

                        self.log.info(f"Returning content with MIME type: {mime_type}")
                        response = str(result), 200, {'Content-Type': mime_type}

                    elapsed_time = time.time() - start_time
                    self.log.info(f"Page {capability_name}/{actual_page_path} generated in {elapsed_time:.3f}s")
                    return response
                except Exception as e:
                    self.log.error(f"Error executing page handler: {str(e)}")
                    # 出错时继续尝试模板方式
                    pass

            # 如果有自定义页面处理器，使用它
            if custom_pages_handler:
                params = {
                    'capability_name': capability_name,
                    'page_path': actual_page_path,
                    'url_params': request.args.to_dict()
                }
                response = custom_pages_handler(params)
                elapsed_time = time.time() - start_time
                self.log.info(f"Page {capability_name}/{actual_page_path} served by custom handler in {elapsed_time:.3f}s")
                return response

            # 否则使用默认处理逻辑 - 渲染模板
            try:
                # 构造完整的模板路径: {capability_name}/{actual_page_path}
                full_template_path = f"{capability_name}/{actual_page_path}"
                response = render_template(full_template_path)
                elapsed_time = time.time() - start_time
                self.log.info(f"Page {capability_name}/{actual_page_path} rendered from template in {elapsed_time:.3f}s")
                return response
            except:
                # 如果模板不存在，尝试添加.html后缀
                try:
                    full_template_path = f"{capability_name}/{actual_page_path}.html"
                    response = render_template(full_template_path)
                    elapsed_time = time.time() - start_time
                    self.log.info(f"Page {capability_name}/{actual_page_path} rendered from template (.html) in {elapsed_time:.3f}s")
                    return response
                except:
                    # 尝试不带 capability_name 的路径
                    try:
                        response = render_template(actual_page_path)
                        elapsed_time = time.time() - start_time
                        self.log.info(f"Page {capability_name}/{actual_page_path} rendered from template (no capability) in {elapsed_time:.3f}s")
                        return response
                    except:
                        # 最后尝试不带 capability_name 但添加 .html 后缀
                        try:
                            response = render_template(f"{actual_page_path}.html")
                            elapsed_time = time.time() - start_time
                            self.log.info(f"Page {capability_name}/{actual_page_path} rendered from template (no capability, .html) in {elapsed_time:.3f}s")
                            return response
                        except:
                            # 如果还是找不到，返回错误信息
                            elapsed_time = time.time() - start_time
                            self.log.info(f"Page {capability_name}/{actual_page_path} not found after {elapsed_time:.3f}s")
                            return jsonify({
                                "error": f"Page '{actual_page_path}' not found in capability '{capability_name}'",
                                "suggestion": f"Make sure the template exists in {self.templates}/{capability_name}/ directory"
                            }), 404
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.log.error(f"Error handling page request after {elapsed_time:.3f}s: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500

    def run(self, debug=False):
        """
        启动 Flask 服务器

        Args:
            debug (bool): 是否启用调试模式
        """
        # 添加性能优化配置
        self.app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        self.app.config['TEMPLATES_AUTO_RELOAD'] = False

        self.log.info(f"仅用于能力服务测试:")
        self.log.info(f"Starting Flask server for capabilities: {list(self.capabilities.keys())}")
        self.log.info(f"Host: {self.host}, Port: {self.port}")
        self.log.info(f"Templates directory: {self.templates}")
        self.log.info(f"Static directory: {self.static}")
        self.log.info(f"Static URL path: {self.app.static_url_path}")
        self.app.run(host=self.host, port=self.port, debug=debug, threaded=True)