import io
import os
import time
from urllib.parse import urljoin

import aiohttp
from sycommon.logging.kafka_log import SYLogger
from sycommon.synacos.nacos_service import NacosService

"""
支持异步Feign客户端
    方式一: 使用 @feign_client 和 @feign_request 装饰器
    方式二: 使用 feign 函数
"""

# 示例Feign客户端接口
# @feign_client(service_name="user-service", path_prefix="/api/v1")
# class UserServiceClient:
#
#     @feign_request("GET", "/users/{user_id}")
#     async def get_user(self, user_id):
#         """获取用户信息"""
#         pass
#
#     @feign_request("POST", "/users", headers={"Content-Type": "application/json"})
#     async def create_user(self, user_data):
#         """创建用户"""
#         pass
#
#     @feign_upload("avatar")
#     @feign_request("POST", "/users/{user_id}/avatar")
#     async def upload_avatar(self, user_id, file_path):
#         """上传用户头像"""
#         pass

# # 使用示例
# async def get_user_info(user_id: int, request=None):
#     """获取用户信息"""
#     try:
#         user_service = UserServiceClient()
#         # 设置请求头中的版本信息
#         user_service.get_user._feign_meta['headers']['s-y-version'] = "1.0.0"
#         return await user_service.get_user(user_id=user_id, request=request)
#     except Exception as e:
#         SYLogger.error(f"获取用户信息失败: {str(e)}", TraceId(request))
#         return None


def feign_client(service_name: str, path_prefix: str = "", default_timeout: float | None = None):
    def decorator(cls):
        class FeignWrapper:
            def __init__(self):
                self.service_name = service_name
                self.nacos_manager = NacosService(None)
                self.path_prefix = path_prefix
                self.session = aiohttp.ClientSession()
                self.default_timeout = default_timeout

            def __getattr__(self, name):
                func = getattr(cls, name)

                async def wrapper(*args, **kwargs):
                    # 获取请求元数据
                    request_meta = getattr(func, "_feign_meta", {})
                    method = request_meta.get("method", "GET")
                    path = request_meta.get("path", "")
                    headers = request_meta.get(
                        "headers", {}).copy()  # 复制 headers 避免修改原对象

                    timeout = kwargs.pop('timeout', self.default_timeout)

                    # 处理JSON请求的Content-Type
                    is_json_request = method.upper() in [
                        "POST", "PUT", "PATCH"] and not request_meta.get("files")
                    if is_json_request and "Content-Type" not in headers:
                        headers["Content-Type"] = "application/json"

                    # 获取版本信息
                    version = headers.get('s-y-version')

                    # 构建完整URL
                    full_path = f"{self.path_prefix}{path}"
                    for k, v in kwargs.items():
                        full_path = full_path.replace(f"{{{k}}}", str(v))

                    # 服务发现与负载均衡
                    instances = self.nacos_manager.get_service_instances(
                        self.service_name, version=version)
                    if not instances:
                        SYLogger.error(
                            f"nacos:未找到 {self.service_name} 的健康实例")
                        raise RuntimeError(
                            f"No instances available for {self.service_name}")

                    # 简单轮询负载均衡
                    instance = instances[int(time.time()) % len(instances)]
                    base_url = f"http://{instance['ip']}:{instance['port']}"
                    url = urljoin(base_url, full_path)

                    SYLogger.info(
                        f"nacos:调用服务: {self.service_name} -> {url}")
                    SYLogger.info(f"nacos:请求头: {headers}")

                    # 构建请求
                    params = request_meta.get("params", {})
                    body = request_meta.get("body", {})
                    files = request_meta.get("files", None)
                    form_data = request_meta.get("form_data", None)

                    # 发送请求
                    try:
                        # 处理文件上传
                        if files or form_data:
                            # 创建表单数据
                            data = aiohttp.FormData()
                            if form_data:
                                for key, value in form_data.items():
                                    data.add_field(key, value)
                            if files:
                                for field_name, (filename, content) in files.items():
                                    data.add_field(
                                        field_name, content, filename=filename)
                            # 移除 Content-Type 头，让 aiohttp 自动设置 boundary
                            headers.pop('Content-Type', None)
                            # 发送表单数据
                            async with self.session.request(
                                method=method,
                                url=url,
                                headers=headers,
                                params=params,
                                data=data,
                                timeout=timeout
                            ) as response:
                                return await self._handle_response(response)
                        else:
                            # 普通请求（JSON）
                            async with self.session.request(
                                method=method,
                                url=url,
                                headers=headers,
                                params=params,
                                json=body,
                                timeout=timeout
                            ) as response:
                                return await self._handle_response(response)
                    except Exception as e:
                        SYLogger.error(f"nacos:服务调用失败: {str(e)}")
                        raise RuntimeError(f"Feign call failed: {str(e)}")

                return wrapper

            async def _handle_response(self, response):
                # 处理响应
                if 200 <= response.status < 300:
                    content_type = response.headers.get('Content-Type', '')
                    if 'application/json' in content_type:
                        return await response.json()
                    else:
                        return await response.read()
                raise RuntimeError(
                    f"请求失败: {response.status} - {await response.text()}")

            async def close(self):
                """关闭 aiohttp 会话"""
                await self.session.close()

        return FeignWrapper()
    return decorator


def feign_request(method: str, path: str, headers: dict = None):
    def decorator(func):
        # 初始化请求元数据，确保headers是可修改的字典
        func._feign_meta = {
            "method": method.upper(),
            "path": path,
            "headers": headers.copy() if headers else {}
        }
        return func
    return decorator


def feign_upload(field_name: str = "file"):
    # 文件上传装饰器
    def decorator(func):
        async def wrapper(*args, **kwargs):
            file_path = kwargs.get('file_path')
            if not file_path:
                raise ValueError("file_path is required for upload")

            with open(file_path, 'rb') as f:
                files = {field_name: (os.path.basename(file_path), f.read())}
                kwargs['files'] = files
                return await func(*args, **kwargs)
        return wrapper
    return decorator


async def feign(service_name, api_path, method='GET', params=None, headers=None, file_path=None,
                path_params=None, body=None, files=None, form_data=None, timeout=None):
    """
    feign 函数，显式设置JSON请求的Content-Type头
    """
    session = aiohttp.ClientSession()
    try:
        # 初始化headers，确保是可修改的字典
        headers = headers.copy() if headers else {}

        # 处理JSON请求的Content-Type
        is_json_request = method.upper() in ["POST", "PUT", "PATCH"] and not (
            files or form_data or file_path)
        if is_json_request and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        nacos_service = NacosService(None)
        version = headers.get('s-y-version')

        # 获取服务实例
        instances = nacos_service.get_service_instances(
            service_name, version=version)
        if not instances:
            SYLogger.error(f"nacos:未找到 {service_name} 的健康实例")
            return None

        # 简单轮询负载均衡
        instance = instances[int(time.time()) % len(instances)]

        SYLogger.info(f"nacos:开始调用服务: {service_name}")
        SYLogger.info(f"nacos:请求头: {headers}")

        ip = instance.get('ip')
        port = instance.get('port')

        # 处理path参数
        if path_params:
            for key, value in path_params.items():
                api_path = api_path.replace(f"{{{key}}}", str(value))

        url = f"http://{ip}:{port}{api_path}"
        SYLogger.info(f"nacos:请求地址: {url}")

        try:
            # 处理文件上传
            if files or form_data or file_path:
                data = aiohttp.FormData()
                if form_data:
                    for key, value in form_data.items():
                        data.add_field(key, value)
                if files:
                    for field_name, (filename, content) in files.items():
                        data.add_field(field_name, content, filename=filename)
                if file_path:
                    filename = os.path.basename(file_path)
                    with open(file_path, 'rb') as f:
                        data.add_field('file', f, filename=filename)
                # 移除Content-Type，让aiohttp自动处理
                headers.pop('Content-Type', None)
                async with session.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=params,
                    data=data,
                    timeout=timeout
                ) as response:
                    return await _handle_feign_response(response)
            else:
                # 普通JSON请求
                async with session.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=params,
                    json=body,
                    timeout=timeout
                ) as response:
                    return await _handle_feign_response(response)
        except aiohttp.ClientError as e:
            SYLogger.error(f"nacos:请求服务接口时出错ClientError: {e}")
            return None
    except Exception as e:
        import traceback
        SYLogger.error(f"nacos:请求服务接口时出错: {traceback.format_exc()}")
        return None
    finally:
        await session.close()


async def _handle_feign_response(response):
    """处理Feign请求的响应"""
    if response.status == 200:
        content_type = response.headers.get('Content-Type')
        if 'application/json' in content_type:
            return await response.json()
        else:
            content = await response.read()
            return io.BytesIO(content)
    else:
        error_msg = await response.text()
        SYLogger.error(f"nacos:请求失败，状态码: {response.status}，响应内容: {error_msg}")
        return None
