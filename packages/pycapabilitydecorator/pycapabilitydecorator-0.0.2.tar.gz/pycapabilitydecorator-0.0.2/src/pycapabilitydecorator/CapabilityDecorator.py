# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "click>=8.1.8",
#     "Flask>=2.3.3",
# ]
# ///

'''
@File    :   CapabilityDecorator.py
@Time    :   2025/07/29 20:50:32
@Author  :   LX
@Version :   1.0.0
@Desc    :   Capability 元数据与 CLI 命令自动注册系统
'''

import traceback
from xmlrpc.client import boolean
import click
import json
import base64
import inspect
import os
from functools import wraps
from typing import Any, Dict, List, Optional, Callable
from io import StringIO
import sys
import atexit
from . import tools
from .flasklib import FlaskServer



class CapabilityDecorator:
    """Capability 元数据与 CLI 命令自动注册系统管理类"""

    _instance = None
    _initialized = False
    _server = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CapabilityDecorator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # --- 全局存储 ---
        # 存储所有 capability 的元数据，key 为 capability name
        self._CAPABILITIES: Dict[str, Dict[str, Any]] = {}
        # 存储所有待注册的 Option (顶级命令)
        self._PENDING_OPTIONS: List[Dict[str, Any]] = []
        # 顶级 CLI Group - 在第一个 @init wrapper 中初始化
        self._CLI_GROUP: Optional[click.Group] = None
        # 存储 capability name 到其初始化函数的映射
        self._CAPABILITY_INIT_FUNCS: Dict[str, Callable] = {}
        # 标记是否已显式定义了 capability
        self._EXPLICIT_CAPABILITY_DEFINED: bool = False
        # 标记是否已经注册了退出处理函数
        self._EXIT_HANDLER_REGISTERED: bool = False
        # 特殊命令列表
        self._SPECIAL_COMMANDS = ['register', 'start', 'stop', 'destroy' , 'server']

        self._OK_RETURNS = {
            'code': 0,
            'msg': 'OK',
        }
        self.debug = False
        self._initialized = True

    class CapabilityError(Exception):
        """Capability 模块自定义异常。"""
        pass

    def _get_default_capability_name(self):
        """获取默认的 capability 名称（基于文件名）。"""
        # 获取调用栈中的文件名
        frame = inspect.currentframe()
        while frame:
            filename = frame.f_code.co_filename
            if filename != __file__:
                # 获取文件名（不含扩展名）作为 capability 名称
                return os.path.splitext(os.path.basename(filename))[0]
            frame = frame.f_back
        # 如果无法获取文件名，使用默认名称
        return "default_capability"

    def _ensure_default_capability(self):
        """确保至少有一个默认的 capability。"""
        if not self._CAPABILITIES and not self._EXPLICIT_CAPABILITY_DEFINED:
            # 创建默认的 capability
            name = self._get_default_capability_name()
            meta = {
                'name': name,
                'version': "0.1.0",
                'status': 1,
                'pages': [],
                'author':'',
                'author_email':'',
                'license':'',
                'methods': [],
                'init_params': {},
                'language_type': "Python",
                'static_dir':'',
                'templates_dir':'',
            }
            self._CAPABILITIES[name] = meta
            # 添加一个空的初始化函数
            self._CAPABILITY_INIT_FUNCS[name] = lambda x: None

    def _output_all_capability_meta(self, ctx: click.Context, param: click.Parameter, value: bool):
        """处理顶级 --capability 选项的回调：输出所有 capability 元数据。"""
        if not value or ctx.resilient_parsing:
            return
        self._ensure_default_capability()
        json_output = json.dumps(list(self._CAPABILITIES.values()), indent=2, ensure_ascii=False)
        click.echo(json_output)
        ctx.exit(0)

    def _run_cli_if_needed(self):
        """在程序退出前检查是否需要运行 CLI"""
        # 只有在有注册的命令但没有运行过 CLI 的情况下才运行
        if self._PENDING_OPTIONS and self._CLI_GROUP is None:
            self._CLI_GROUP = click.Group()
            self.register_pending_options()
            self.add_top_level_capability_option()
            self.add_init_command()
            self.add_special_commands()  # 添加特殊命令
            self._CLI_GROUP(standalone_mode=True, prog_name=os.path.basename(sys.argv[0]))

    def _clean_capabilities_meta(self):
        """清理 capabilities 元数据，移除不可序列化的函数对象"""
        return tools.clean_capabilities_meta(self._CAPABILITIES)


    def _get_caller_file(self):
        """获取调用文件的路径"""
        try:
            # 首先尝试通过命令行参数获取主脚本
            if len(sys.argv) > 0 and not sys.argv[0].startswith('-'):
                caller_script = sys.argv[0]
                if os.path.isfile(caller_script):
                    return os.path.abspath(caller_script)

            # 如果通过命令行参数无法获取，则使用调用栈
            frame = inspect.currentframe()
            # 向上追溯调用栈，找到用户脚本文件
            while frame:
                filename = frame.f_code.co_filename
                # 排除当前文件和标准库文件以及框架文件
                if (filename != __file__ and
                    not filename.startswith('<') and
                    'site-packages' not in filename and
                    os.path.basename(filename) != 'click' and
                    os.path.basename(filename) != 'cmd' and
                    os.path.basename(filename) != 'runpy.py' and
                    os.path.basename(filename) != 'threading.py' and
                    filename != inspect.getfile(type(self))):  # 排除装饰器类文件
                    return filename
                frame = frame.f_back
            return None
        except:
            # 最后的备选方案
            if len(sys.argv) > 0 and os.path.isfile(sys.argv[0]):
                return os.path.abspath(sys.argv[0])
            return None

    def add_special_commands(self):
        """添加特殊命令（register, start, stop, destroy, server）"""
        assert self._CLI_GROUP is not None

        # 添加 register 命令
        if 'register' not in self._CLI_GROUP.commands:
            @click.command(name='register')
            @click.option('--params', 'parameters_str', type=str, default='',
                        help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            def register_command(ctx, parameters_str):
                """注册 capability 元数据"""
                try:
                    params_dict = {}
                    json_dict = {}
                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        json_dict = json.loads(json_str)

                    # 直接使用清理后的元数据
                    result = self._clean_capabilities_meta()
                    click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing 'register': {e}", err=True)
                    ctx.exit(1)

            self._CLI_GROUP.add_command(register_command)

        # 添加 start 命令
        if 'start' not in self._CLI_GROUP.commands:
            @click.command(name='start')
            @click.option('--params', 'parameters_str', type=str, default='',
                          help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            def start_command(ctx, parameters_str):
                """启动能力"""
                try:
                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        json_dict = json.loads(json_str)
                    else:
                        json_dict = {}

                    result = self._OK_RETURNS
                    click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing 'start': {e}", err=True)
                    ctx.exit(1)

            self._CLI_GROUP.add_command(start_command)

        # 添加 stop 命令
        if 'stop' not in self._CLI_GROUP.commands:
            @click.command(name='stop')
            @click.option('--params', 'parameters_str', type=str, default='',
                          help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            def stop_command(ctx, parameters_str):
                """停止能力"""
                try:
                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        json_dict = json.loads(json_str)
                    else:
                        json_dict = {}

                    result = self._OK_RETURNS
                    click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing 'stop': {e}", err=True)
                    ctx.exit(1)

            self._CLI_GROUP.add_command(stop_command)

        # 添加 destroy 命令
        if 'destroy' not in self._CLI_GROUP.commands:
            @click.command(name='destroy')
            @click.option('--params', 'parameters_str', type=str, default='',
                          help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            def destroy_command(ctx, parameters_str):
                """销毁能力"""
                try:
                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        json_dict = json.loads(json_str)
                    else:
                        json_dict = {}

                    result = self._OK_RETURNS
                    click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing 'destroy': {e}", err=True)
                    ctx.exit(1)

            self._CLI_GROUP.add_command(destroy_command)


        # 添加 server 命令
        if 'server' not in self._CLI_GROUP.commands:

            @click.command(name='server')
            @click.option('--params', 'parameters_str', type=str, default='',
                        help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            def server_command(ctx, parameters_str):
                """启动服务器"""
                try:
                    if FlaskServer is None:
                        click.echo("flasklib is not available. Please make sure flasklib.py is in the same directory.")
                        ctx.exit(1)

                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        server_params = json.loads(json_str)
                    else:
                        server_params = {}
                    # 获取调用文件的路径信息
                    caller_file = self._get_caller_file()
                    if caller_file:
                        server_params['caller_file'] = caller_file
                        server_params['caller_dir'] = os.path.dirname(caller_file)

                    # 添加当前工作目录信息到 server_params
                    server_params['current_working_dir'] = os.getcwd()
                    server_params['script_dir'] = os.path.dirname(os.path.abspath(sys.argv[0])) if len(sys.argv) > 0 else os.getcwd()

                    # 从 capabilities 中获取 static_dir 和 templates_dir 参数
                    for cap_name, cap_meta in self._CAPABILITIES.items():
                        if 'static_dir' in cap_meta and cap_meta['static_dir']:
                            server_params['static'] = cap_meta['static_dir']
                        if 'templates_dir' in cap_meta and cap_meta['templates_dir']:
                            server_params['templates'] = cap_meta['templates_dir']
                        # 只处理第一个找到的 capability 的目录设置
                        if 'static' in server_params and 'templates' in server_params:
                            break

                    # 创建 Flask 服务器实例
                    self._server = FlaskServer(self._CAPABILITIES, server_params , )

                    click.echo(f"server调试模式debug={self.debug}" )
                    # click.echo(f"Starting Flask server for capabilities: {list(self._CAPABILITIES.keys())}")
                    self._server.run(debug=self.debug)

                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing 'server': {e}", err=True)
                    ctx.exit(1)


            self._CLI_GROUP.add_command(server_command)



    def register_pending_options(self):
        """注册所有暂存的 Option 作为顶级命令。"""
        # 确保 _CLI_GROUP 已经存在
        if self._CLI_GROUP is None:
            self._CLI_GROUP = click.Group()

        self._ensure_default_capability()

        for option_meta in self._PENDING_OPTIONS:
            cmd_name = option_meta['name']
            # 使用 alias 作为命令名，如果提供了 alias，否则使用 name
            command_name = option_meta.get('alias') or cmd_name
            description = option_meta['description']
            params = option_meta['params']
            func = option_meta['func']
            capability_name = option_meta['capability_name']
            # 获取 option_meta 中的 returns (如果存在)
            returns = option_meta.get('returns', {})

            # 创建顶级命令
            @click.command(name=command_name, help=description)
            @click.option('--params', 'parameters_str', type=str, default='',
                          help='Base64 encoded JSON string of parameters.')
            @click.pass_context
            # 在 register_pending_options 方法中完全重写 command_wrapper 函数
            def command_wrapper(ctx, parameters_str, func=func, params=params, returns=returns, cmd_name=command_name):
                try:
                    params_dict = {}
                    json_dict = {}
                    if parameters_str.strip():
                        # Base64 解码并解析 JSON 这边设置参数默认是 json base64 字符串
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        json_dict = json.loads(json_str)

                    # 对于 register 和 destroy 命令特殊处理，始终添加 capability 数据
                    if cmd_name in self._SPECIAL_COMMANDS:
                        params_dict['params'] = json_dict
                        params_dict['capability'] = self._clean_capabilities_meta()
                    else:
                        params_dict = json_dict
                    sig = inspect.signature(func)
                    func_params = list(sig.parameters.keys())

                    # 捕获函数的打印输出
                    old_stdout = sys.stdout
                    sys.stdout = captured_output = StringIO()

                    try:
                        if len(func_params) == 0:
                            result = func()
                        else:
                            result = func(params_dict)
                    finally:
                        # 恢复标准输出
                        sys.stdout = old_stdout

                    # 获取捕获的输出
                    output = captured_output.getvalue()

                    # 特殊处理 register 和 destroy 方法
                    if cmd_name == 'register':
                        # 确保 register 命令总是返回清理后的元数据
                        if result is None or not isinstance(result, list):
                            result = self._clean_capabilities_meta()
                        click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                    elif cmd_name in [ 'start' , 'stop' , 'destroy' ] :
                        if result is None:
                            result = self._OK_RETURNS
                        click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                    else:
                        # 先输出函数的打印内容（如果有的话）
                        if output.strip():
                            # 如果有打印输出，就输出打印内容
                            click.echo(output.strip())

                        # 其它 命令的标准处理
                        if result is not None:
                            if isinstance(result, dict):
                                click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                            else:
                                click.echo(result)
                        else:
                            # 如果没有返回值且没有打印输出，输出默认值
                            # if not output.strip():
                            click.echo(json.dumps(self._OK_RETURNS, ensure_ascii=False, indent=4))

                except (base64.binascii.Error, UnicodeDecodeError) as e:
                    click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                    ctx.exit(1)
                except json.JSONDecodeError as e:
                    click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                    ctx.exit(1)
                except Exception as e:
                    click.echo(f"Error executing '{cmd_name}': {e}", err=True)
                    ctx.exit(1)


            # 将命令添加到顶级 Group
            self._CLI_GROUP.add_command(command_wrapper)

            # --- 更新 capability 的 methods 列表中的 name ---
            # 确保我们使用正确的 capability_name
            actual_capability_name = capability_name
            if actual_capability_name is None and self._CAPABILITIES:
                # 如果没有显式指定 capability_name，则使用默认的 capability
                actual_capability_name = next(iter(self._CAPABILITIES))

            cap_methods = self._CAPABILITIES[actual_capability_name]['methods']
            # 使用更精确的方式匹配方法，通过函数引用匹配而不是通过描述等信息
            for method in cap_methods:
                if method.get('func') == func:
                    method['name'] = command_name
                    if 'alias' in option_meta:
                        method['alias'] = option_meta['alias']
                    break


    def add_top_level_capability_option(self):
        """为顶级 CLI Group 添加 --capability 选项。"""
        assert self._CLI_GROUP is not None
        # 检查是否已添加，避免重复
        if not any(isinstance(p, click.Option) and '--capability' in p.opts for p in self._CLI_GROUP.params):
            self._CLI_GROUP.params.append(
                click.Option(
                    ['--capability'],
                    is_flag=True,
                    is_eager=True,
                    expose_value=False,
                    help='Output metadata for all capabilities (JSON) and exit.',
                    callback=self._output_all_capability_meta
                )
            )

    # 修改 add_init_command 函数
    def add_init_command(self):
        """添加顶级 init 命令，用于执行所有 capability 的初始化逻辑。"""
        assert self._CLI_GROUP is not None

        if 'init' not in self._CLI_GROUP.commands:
            @click.command(name='init')
            @click.option('--params', 'parameters_str', type=str, default='',
                        help='Base64 encoded JSON string of parameters for the init command. (Optional)')
            @click.option('--capability', is_flag=True, is_eager=True, expose_value=False,
                        help='Output metadata for all capabilities (JSON) and exit.',
                        callback=self._output_all_capability_meta)
            @click.pass_context
            def init_command(ctx, parameters_str):
                """执行所有 capability 的初始化逻辑。"""
                init_params = {}
                if parameters_str.strip():
                    try:
                        json_str = base64.b64decode(parameters_str).decode('utf-8')
                        init_params = json.loads(json_str)
                    except (base64.binascii.Error, UnicodeDecodeError) as e:
                        click.echo(f"Invalid base64 encoding in --params: {e}", err=True)
                        ctx.exit(1)
                    except json.JSONDecodeError as e:
                        click.echo(f"Invalid JSON in decoded parameters: {e}", err=True)
                        ctx.exit(1)

                self._ensure_default_capability()

                if not self._CAPABILITY_INIT_FUNCS:
                    click.echo("No capabilities to initialize.")
                    return self._OK_RETURNS

                for cap_name, init_func in self._CAPABILITY_INIT_FUNCS.items():
                    try:
                        click.echo(f"Initializing capability: {cap_name}")
                        result = init_func(init_params)
                        # 如果初始化函数没有返回值，则输出默认值
                        if result is None:
                            click.echo(json.dumps(self._OK_RETURNS, ensure_ascii=False, indent=4))
                        else:
                            click.echo(json.dumps(result, ensure_ascii=False, indent=4))
                    except Exception as e:
                        click.echo(f"Error initializing capability '{cap_name}': {e}", err=True)

            self._CLI_GROUP.add_command(init_command)
    # --- 装饰器定义 ---
    def init(self, name: str = None,
             version: str = "1.0.0",
             status: int = 1,
             pages: List[Dict[str, str]] = None,
             init_params: Optional[Dict[str, Dict[str, str]]] = None,
             language_type: str = "Python",
             static_dir: str = None,
             templates_dir: str = None,
             templates_dir: str = None,
             page_404: str = None,
             page_500: str = None,
             debug:boolean = False) -> Callable[[Callable], Callable]:
        """
        装饰器：初始化一个 capability 的元数据
        name (可选): 能力名称，默认为文件名
        version (可选): 版本
        status (可选): 状态默认块状态，默认为 1
        pages (可选): 描述能力文档的页面列表，支持多种格式：
                    1. 字符串列表: ["/page1", "/page2"]
                    2. 字典列表: [{"url": "/page1", "description": "页面1"}, ...]
        `init_params` (可选): 描述初始化函数可能接收的参数元数据
        `language_type` (可选): 描述能力实现使用的编程语言，默认为 "Python"
        `static_dir` (可选): 静态文件目录路径
        `templates_dir` (可选): 模板文件目录路径
        `debug` (可选): 调试模式,默认值 False
        """
        self._EXPLICIT_CAPABILITY_DEFINED = True

        pages = pages or []
        init_params = init_params or {} # 如果没提供 init_params，用空字典
        self.debug = debug
        def decorator(func: Callable) -> Callable:
            # 如果没有提供 name，则使用文件名
            capability_name = name if name else self._get_default_capability_name()

            # 处理 pages 参数，统一转换为标准格式
            processed_pages = []
            if pages:
                # 获取调用函数的文件名和行号
                frame = inspect.currentframe()
                try:
                    caller_frame = frame.f_back
                    filename = caller_frame.f_code.co_filename
                    lineno = caller_frame.f_lineno
                    # 获取文件名（不含路径）和行号
                    basename = os.path.basename(filename)
                finally:
                    del frame

                # 处理 pages 参数，支持两种格式
                for page in pages:
                    if isinstance(page, str):
                        # 格式1: 字符串列表
                        page_info = {
                            'path': page,
                            'description': "",  # 没有描述则为空字符串
                            'source': f"#{basename} {lineno}-{lineno}"  # 记录来源
                        }
                        processed_pages.append(page_info)
                    elif isinstance(page, dict):
                        # 格式2: 字典列表
                        url = page.get('url', '')
                        if url:
                            page_info = {
                                'path': url,
                                'description': page.get('description', ""),  # 没有描述则为空字符串
                                'handler': page.get('handler'),  # 如果有处理函数也一并保存
                                'source': f"#{basename} {lineno}-{lineno}"  # 记录来源
                            }
                            processed_pages.append(page_info)

            # 如果 capability 已经存在，更新它的元数据而不是抛出异常
            if capability_name in self._CAPABILITIES:
                # 更新已存在的 capability 元数据
                self._CAPABILITIES[capability_name].update({
                    'version': version,
                    'status': status,
                    'pages': processed_pages,
                    'init_params': init_params,
                    'language_type': language_type,
                    'static_dir': static_dir or '',
                    'templates_dir': templates_dir or '',
                    'debug': debug
                })
            else:
                meta = {
                    'name': capability_name,
                    'version': version,
                    'status': status,
                    'pages': processed_pages,
                    'methods': [],
                    'init_params': init_params,
                    'language_type': language_type,
                    'static_dir': static_dir or '',
                    'templates_dir': templates_dir or '',
                    'debug' : debug
                }
                self._CAPABILITIES[capability_name] = meta

            self._CAPABILITY_INIT_FUNCS[capability_name] = func

            @wraps(func)
            def wrapper(*args, **kwargs):
                if self._CLI_GROUP is None:
                    self._CLI_GROUP = click.Group()

                self.register_pending_options()
                self.add_top_level_capability_option()
                self.add_init_command()
                self.add_special_commands()  # 添加特殊命令
                self._CLI_GROUP(standalone_mode=True, prog_name="capability_test")

            return wrapper

        return decorator


    def render_page(self,page_path,option):
        """
        加载页面数据
        """
        if self._server:
            return self._server.render_page(page_path,option)
        else:
            self.log.error("请先启动server服务!!!")


    def option(self, name: Optional[str] = None, description: str = "",
               params: Dict[str, Dict[str, str]] = None,
               returns: Dict[str, Dict[str, str]] = None,
               capability_name: Optional[str] = None,
               alias: Optional[str] = None,
               pages: Optional[List] = None,
               pages_type: Optional[str] = None) -> Callable[[Callable], Callable]:
        """
        装饰器：注册一个顶级 CLI 命令。
        name (可选): 命令的名称。如果未提供，则使用被装饰函数的名称 (func.__name__)。
        `capability_name (可选)` 指定该命令属于哪个 capability (通过 @init 定义的 name)。
                    如果不指定，则尝试关联到最近定义的 capability。
        `params (可选)` 是 `parameters` 的简化别名。
        alias (可选): 为该命令指定一个别名作为 CLI 命令名。如果未提供，则使用 name（或函数名）。
        pages (可选): 页面列表，支持两种格式：
                    1. 字符串列表: ["/page1", "/page2"]
                    2. 字典列表: [{"url": "/page1", "description": "页面1"}, ...]
        pages_type (可选): 页面 MIME 类型，默认为 "text/html"。
                    例如: "text/html", "application/javascript", "text/css"
        """
        # 注册退出处理函数，确保在没有 @init 装饰器的情况下也能运行 CLI
        if not self._EXIT_HANDLER_REGISTERED:
            atexit.register(self._run_cli_if_needed)
            self._EXIT_HANDLER_REGISTERED = True

        params = params or {}
        returns = returns or {}
        pages = pages or []
        # 默认 MIME 类型为 text/html
        pages_type = pages_type or "text/html"

        def decorator(func: Callable) -> Callable:
            cap_name = capability_name
            if cap_name is None and self._CAPABILITIES:
                # 如果没有显式指定 capability_name，但已存在定义的 capability，则使用第一个
                cap_name = next(iter(self._CAPABILITIES))
            elif cap_name is None and not self._CAPABILITIES:
                # 如果没有定义任何 capability，则创建一个默认的
                self._ensure_default_capability()
                if self._CAPABILITIES:
                    cap_name = next(iter(self._CAPABILITIES))
                else:
                    # 如果仍然没有 capabilities，则创建一个临时的默认 capability
                    default_name = self._get_default_capability_name()
                    self._CAPABILITIES[default_name] = {
                        'name': default_name,
                        'version': "0.1.0",
                        'status': 1,
                        'pages': [],
                        'methods': [],
                        'init_params': {},
                        'language_type': "Python",
                        'static_dir': '',
                        'templates_dir': '',
                    }
                    cap_name = default_name

            if cap_name not in self._CAPABILITIES:
                raise self.CapabilityError(f"Cannot assign option to capability '{cap_name}': capability not defined.")

            final_name = name
            if not final_name:
                final_name = func.__name__
            if not final_name:
                raise self.CapabilityError(f"Cannot determine name for option from function '{func.__name__}'. Function name is empty.")

            option_meta = {
                'name': final_name,
                'description': description,
                'params': params,
                'returns': returns,
                'func': func,
                'capability_name': cap_name
            }
            if alias is not None:
                option_meta['alias'] = alias

            self._PENDING_OPTIONS.append(option_meta)

            method_entry = {
                'name': final_name,
                'description': description,
                'params': params,
                'returns': returns,
                'func': func
            }

            if alias is not None:
                method_entry['alias'] = alias

            # 添加页面信息到方法条目中
            if pages:
                method_entry['pages'] = pages

            # 添加页面类型信息到方法条目中
            method_entry['pages_type'] = pages_type

            self._CAPABILITIES[cap_name]['methods'].append(method_entry)

            # 处理 pages 参数并添加到 capability 的 pages 列表中
            if pages:
                capability_pages = self._CAPABILITIES[cap_name]['pages']
                # 获取调用函数的文件名和行号
                frame = inspect.currentframe()
                try:
                    caller_frame = frame.f_back
                    filename = caller_frame.f_code.co_filename
                    lineno = caller_frame.f_lineno
                    # 获取文件名（不含路径）和行号
                    basename = os.path.basename(filename)
                finally:
                    del frame

                # 处理 pages 参数，支持两种格式
                for page in pages:
                    if isinstance(page, str):
                        # 格式1: 字符串列表
                        page_info = {
                            'path': page,
                            'description': f"Page {page}",
                            'source': f"#{basename} {lineno}-{lineno}"  # 记录来源
                        }
                        capability_pages.append(page_info)
                    elif isinstance(page, dict):
                        # 格式2: 字典列表
                        url = page.get('url', '')
                        if url:
                            page_info = {
                                'path': url,
                                'description': page.get('description', f"Page {url}"),
                                'handler': page.get('handler'),  # 如果有处理函数也一并保存
                                'source': f"#{basename} {lineno}-{lineno}"  # 记录来源
                            }
                            capability_pages.append(page_info)

            return func

        return decorator



# 创建全局实例
capability = CapabilityDecorator()

# 为了向后兼容，创建装饰器函数
init = capability.init
option = capability.option
CapabilityError = CapabilityDecorator.CapabilityError