from __future__ import annotations

import asyncio
import multiprocessing
import os
import ssl
from abc import ABC, abstractmethod
from datetime import datetime
from http.cookiejar import DefaultCookiePolicy, CookieJar
from pathlib import Path
from typing import Any, Optional, Union, Iterator, AsyncIterator, TypeVar, cast, Callable, Dict

import httpx
import orjson
from httpx import (
    Response,
    Request,
    HTTPError,
    ConnectError,
    ReadError,
    TimeoutException,
    ProxyError,
    ResponseNotRead,
    HTTPStatusError,
    RequestError,
)
from loguru import logger

T = TypeVar("T", bytes, str, dict, Iterator[bytes], AsyncIterator[bytes])


class SessionError(Exception):
    """自定义会话异常基类"""
    pass


class NetworkError(SessionError):
    """网络层异常"""
    pass


class SecurityError(SessionError):
    """安全策略异常"""
    pass

class RateLimitError(SessionError):
    """API限流异常"""
    def __init__(self, message: str, retry_after: Union[int, datetime] = None):
        super().__init__(message)
        self.retry_after = retry_after  # 支持秒数或具体时间

class RetryableError(SessionError):
    """可重试异常基类"""
    def __init__(self, message: str, retry_after: Union[int, datetime] = None):
        super().__init__(message)
        self.retry_after = retry_after


class BaseSession(ABC):
    """HTTP客户端抽象基类（支持同步/异步双模式）"""

    RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(self, client: Union[httpx.Client, httpx.AsyncClient]):
        self._client = client

    @abstractmethod
    def request(self, method: str, url: str, **kwargs: Any) -> Optional[T]:
        """统一请求入口"""
        raise NotImplementedError

    @staticmethod
    def _common_headers(random_ua: bool = False) -> Dict[str, str]:
        """公共请求头配置"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY"
        }

        if random_ua:
            try:
                from fake_useragent import UserAgent
                headers["User-Agent"] = UserAgent().random
            except ImportError:
                logger.warning("fake_useragent not installed, using default User-Agent")

        return headers

    @staticmethod
    def _secure_cookie_jar(allowed_domains: Optional[list] = None) -> CookieJar:
        """
        安全Cookie策略配置

        Args:
            allowed_domains: 允许的域名列表，None表示允许所有
        """
        if allowed_domains and not isinstance(allowed_domains, list):
            raise TypeError("allowed_domains必须是列表类型")

        blocked_domains = [
            ".onion", ".exe", ".zip", ".app", ".dmg",  # 高危扩展名
            ".local",  # 本地域名
        ]

        jar = CookieJar()
        jar.set_policy(
            DefaultCookiePolicy(
                blocked_domains=blocked_domains,  # 阻止可疑域名
                strict_ns_domain=0,
                allowed_domains=allowed_domains,
                netscape=False,
                hide_cookie2=True,
                strict_rfc2965_unverifiable=True,
            )
        )
        return jar

    @staticmethod
    def _resolve_verify(verify: Union[bool, str, ssl.SSLContext]) -> Union[bool, str, ssl.SSLContext]:
        """SSL证书校验"""
        if isinstance(verify, str):
            verify_path = Path(verify)
            if not verify_path.exists():
                raise SecurityError(f"SSL CA bundle路径不存在: {verify}")
            if not verify_path.is_file():
                raise SecurityError(f"SSL CA bundle不是有效文件: {verify}")
            return str(verify_path)
        return verify

    def _process_json_response(self, response: Response) -> dict:
        """处理JSON类型响应"""
        try:
            return orjson.loads(response.content)
        except orjson.JSONDecodeError as e:
            raise httpx.JSONDecodeError(e.msg, e.doc, e.pos)

    def _process_text_response(self, response: Response, encoding: str) -> str:
        """处理文本类型响应"""
        return response.content.decode(encoding, errors="replace")

    def _process_binary_response(self, response: Response) -> bytes:
        """处理二进制类型响应"""
        return response.content

    def process_response(
            self,
            response: Response,
            response_encoding: Optional[str] = None,
            stream: bool = False
    ) -> Optional[T]:
        """
        统一响应处理管道

        Args:
            response: 原始响应对象
            response_encoding: 指定解码字符集
            stream: 是否为流式响应

        Returns:
            处理后的响应内容，类型根据stream参数决定
        """
        try:
            if stream:
                return cast(T, self.stream_response(response))

            content_type = response.headers.get("Content-Type", "").split(";")[0]
            encoding = response_encoding or response.encoding or "utf-8"

            if content_type == "application/json":
                return cast(T, self._process_json_response(response))
            elif content_type.startswith("text/"):
                return cast(T, self._process_text_response(response, encoding))
            else:
                return cast(T, self._process_binary_response(response))
        except UnicodeDecodeError:
            logger.warning(f"响应解码失败 URL={response.url}")
            return cast(T, response.content)
        except ResponseNotRead as e:
            logger.error(f"响应内容未读取: {str(e)}")
            return None

    @abstractmethod
    def stream_response(self, response: Response) -> Union[Iterator[bytes], AsyncIterator[bytes]]:
        """流式响应处理"""
        raise NotImplementedError

    def validate_request_params(self, url: str, method: str) -> None:
        """请求参数验证"""
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise ValueError(f"无效URL格式: {url}")
        if method.upper() not in {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"}:
            raise ValueError(f"不支持的HTTP方法: {method}")

    def pre_request_hook(self, request: Request) -> None:
        """请求预处理钩子（子类可扩展）"""
        logger.debug(f"请求开始: {request.method} {request.url}")

    def post_response_hook(self, response: Response) -> None:
        """响应后处理钩子（子类可扩展）"""
        logger.debug(f"请求完成: {response.status_code} {response.url}")

    def handle_response_error(self, error: HTTPError) -> None:
        """统一错误处理"""
        if isinstance(error, HTTPStatusError):
            status_code = error.response.status_code
            if status_code == 429:
                retry_after = error.response.headers.get("Retry-After")
                raise RateLimitError(f"API rate limit exceeded: {error}", retry_after=int(retry_after) if retry_after else None)
            elif status_code in self.RETRY_STATUS_CODES:
                raise RetryableError(f"Server error: {status_code}")
            else:
                raise NetworkError(f"HTTP error {status_code}: {error}")
        elif isinstance(error, (ConnectError, ReadError, TimeoutException, ProxyError)):
            raise RetryableError(f"Network error: {error}")
        else:
            raise NetworkError(f"Request failed: {error}")

    # 快捷方法定义
    def get(self, url: str, **kwargs: Any) -> Optional[T]:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Optional[T]:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Optional[T]:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Optional[T]:
        return self.request("DELETE", url, **kwargs)


class SyncSession(BaseSession):
    """同步生产级HTTP客户端（支持HTTP/2）"""

    def __init__(
            self,
            max_connections: Optional[int] = None,
            timeout: Union[httpx.Timeout, float, None] = None,
            retries: int = 3,
            proxies: Optional[Dict] = None,
            verify: Union[ssl.SSLContext, str, bool] = True,
            allowed_cookie_domains: Optional[list] = None,
            random_ua: bool = False
    ):
        """
        Args:
            max_connections: 最大连接数（默认根据CPU核心计算）
            timeout: 超时配置（默认连接3.05s，读取30s）
            retries: 请求重试次数
            proxies: 代理配置（如{'http://': 'http://proxy.example.com'}）
            verify: SSL证书验证开关
            allowed_cookie_domains: 允许的Cookie域名白名单
        """
        client = self._build_client(
            max_connections=max_connections,
            timeout=timeout,
            retries=retries,
            proxies=proxies,
            verify=verify,
            allowed_cookie_domains=allowed_cookie_domains,
            random_ua=random_ua
        )
        super().__init__(client)

    def _build_client(
            self,
            max_connections: Optional[int],
            timeout: Union[httpx.Timeout, float, None],
            retries: int,
            proxies: Optional[Dict],
            verify: Union[ssl.SSLContext, str, bool],
            allowed_cookie_domains: Optional[list],
            random_ua: bool
    ) -> httpx.Client:
        """构建同步客户端"""
        cpu_cores = multiprocessing.cpu_count()
        max_connections = max(50, min(100, (cpu_cores * 4))) if max_connections is None else max_connections

        return httpx.Client(
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max(10, int(max_connections * 0.3)),  # 最多保留10个空闲长连接
                keepalive_expiry=300,
            ),
            timeout=timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(
                connect=3.05, read=30.0, write=5.0, pool=5.0
            ),
            transport=httpx.HTTPTransport(
                retries=retries,
                http2=True,
            ),
            headers=self._common_headers(random_ua),
            cookies=self._secure_cookie_jar(allowed_cookie_domains),
            follow_redirects=True,
            max_redirects=5,
            proxy=proxies,
            verify=self._resolve_verify(verify),
        )

    def request(self, method: str, url: str, **kwargs: Any) -> Optional[T]:
        """同步请求核心方法"""
        self.validate_request_params(url, method)
        try:
            # 构建请求对象并执行钩子
            request = self._client.build_request(
                method=method.upper(),
                url=url,
                params=kwargs.get("params"),
                content=kwargs.get("data"),
                json=kwargs.get("json"),
                files=kwargs.get("files"),
                headers=kwargs.get("headers"),
            )
            self.pre_request_hook(request)

            response = self._client.send(request)
            self.post_response_hook(response)

            response.raise_for_status()
            return self.process_response(
                response,
                response_encoding=kwargs.get("response_encoding"),
                stream=kwargs.get("stream", False),
            )
        except (HTTPError, RequestError) as e:
            logger.error(f"请求失败 [{method}] {url} | 异常: {type(e).__name__} | 信息: {str(e)}")
            self.handle_response_error(e)
            return None

    def stream_response(self, response: Response) -> Iterator[bytes]:
        """同步流式响应"""
        try:
            yield from response.iter_bytes(chunk_size=64 * 1024)  # 64KB chunks
        finally:
            response.close()

    def download_file(
            self,
            url: str,
            save_path: str,
            chunk_size: int = 64 * 1024,
            on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> bool:
        """大文件下载（带进度回调）"""
        try:
            save_path = Path(save_path).resolve()
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with self._client.stream("GET", url) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("Content-Length", 0))

                with open(save_path, "wb") as f:
                    downloaded = 0
                    for chunk in response.iter_bytes(chunk_size):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if on_progress:
                            on_progress(downloaded, total_size)
                return True
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            return False

    def close(self):
        """显式关闭客户端"""
        self._client.close()


class AsyncSession(BaseSession):
    """异步生产级HTTP客户端（支持HTTP/2）"""

    def __init__(
            self,
            max_connections: int = 250,
            timeout: Union[httpx.Timeout, float, None] = None,
            retries: int = 3,
            proxies: Optional[Dict] = None,
            verify: Union[ssl.SSLContext, str, bool] = True,
            allowed_cookie_domains: Optional[list] = None,
            random_ua: bool = False
    ):
        """
        Args:
            max_connections: 最大连接数（默认250）
            timeout: 超时配置（默认连接3.05s，读取30s）
            retries: 请求重试次数
            proxies: 代理配置
            verify: SSL证书验证开关
            allowed_cookie_domains: 允许的Cookie域名白名单
        """
        client = self._build_client(
            max_connections=max_connections,
            timeout=timeout,
            retries=retries,
            proxies=proxies,
            verify=verify,
            allowed_cookie_domains=allowed_cookie_domains,
            random_ua=random_ua
        )
        super().__init__(client)

    def _build_client(
            self,
            max_connections: int,
            timeout: Union[httpx.Timeout, float, None],
            retries: int,
            proxies: Optional[Dict],
            verify: Union[ssl.SSLContext, str, bool],
            allowed_cookie_domains: Optional[list],
            random_ua: bool
    ) -> httpx.AsyncClient:
        """构建异步客户端"""
        return httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max(10, int(max_connections * 0.3)),
                keepalive_expiry=300,
            ),
            timeout=timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(
                connect=3.05, read=30.0, write=5.0, pool=5.0
            ),
            transport=httpx.AsyncHTTPTransport(
                retries=retries,
                http2=True
            ),
            headers=self._common_headers(random_ua),
            cookies=self._secure_cookie_jar(allowed_cookie_domains),
            follow_redirects=True,
            max_redirects=5,
            proxy=proxies,
            verify=self._resolve_verify(verify),
        )

    async def request(self, method: str, url: str, **kwargs: Any) -> Optional[T]:
        """异步请求核心方法"""
        self.validate_request_params(url, method)
        try:
            # 构建请求对象并执行钩子
            request = self._client.build_request(
                method=method.upper(),
                url=url,
                params=kwargs.get("params"),
                content=kwargs.get("data"),
                json=kwargs.get("json"),
                files=kwargs.get("files"),
                headers=kwargs.get("headers"),
            )
            self.pre_request_hook(request)

            response = await self._client.send(request)
            self.post_response_hook(response)

            response.raise_for_status()
            return self.process_response(
                response,
                response_encoding=kwargs.get("response_encoding"),
                stream=kwargs.get("stream", False),
            )
        except (HTTPError, RequestError) as e:
            logger.error(f"请求失败 [{method}] {url} | 异常: {type(e).__name__} | 信息: {str(e)}")
            self.handle_response_error(e)
            return None

    async def stream_response(self, response: Response) -> AsyncIterator[bytes]:
        """异步流式响应"""
        try:
            async for chunk in response.aiter_bytes(chunk_size=64 * 1024):
                yield chunk
        finally:
            await response.aclose()

    async def download_file(

            self,
            url: str,
            save_path: Union[str, os.PathLike],
            chunk_size: int = 64 * 1024,
            on_progress: Optional[Callable[[int, int], None]] = None,
            **request_kwargs,
    ) -> bool:
        """异步大文件下载

        Args:
            url: 下载文件URL
            save_path: 保存路径
            chunk_size: 分块大小（字节）
            on_progress: 进度回调函数 (已下载, 总大小)
            **request_kwargs: 其他请求参数

        Returns:
            是否成功
        """
        try:
            import aiofiles
        except ImportError:
            raise ImportError("aiofiles is required for async file downloads")

        try:
            save_path = Path(save_path).resolve()
            save_path.parent.mkdir(parents=True, exist_ok=True)
            async with self._client.stream("GET", url, **request_kwargs) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("Content-Length", 0))

                async with aiofiles.open(save_path, "wb") as f:
                    downloaded = 0
                    async for chunk in response.aiter_bytes(chunk_size):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        if on_progress:
                            on_progress(downloaded, total_size)
                return True
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            return False

    async def close(self):
        """显式关闭客户端"""
        await self._client.aclose()


if __name__ == "__main__":

    def on_progress(downloaded, total_size):
        logger.debug(f"下载进度: {downloaded}/{total_size} bytes")


    # 同步客户端测试集
    def test_sync_client():
        # 常规请求
        session = SyncSession(random_ua=True)
        print("GET测试:", session.get("https://httpbin.org/get"))
        print(
            "POST测试:",
            session.post("https://httpbin.org/post", json={"key": "value"}),
        )

        # 流式响应
        print("\n流式响应测试:")
        stream = session.get("https://httpbin.org/stream/3", stream=True)
        if isinstance(stream, Iterator):
            for chunk in stream:
                print(f"收到数据块: {len(chunk)} bytes")

        # 文件下载
        print("\n文件下载测试:")
        success = session.download_file(
            "https://httpbin.org/bytes/1048576", "sync_download.bin",
            on_progress=on_progress
        )
        print(f"下载结果: {'成功' if success else '失败'}")


    # 异步客户端测试集
    async def test_async_client():
        session = AsyncSession()
        # 常规请求
        print("GET测试:", await session.get("https://httpbin.org/get"))
        print(
            "POST测试:",
            await session.post("https://httpbin.org/post", json={"key": "value"}),
        )

        # 流式响应
        print("\n异步流式响应测试:")
        stream = await session.get("https://httpbin.org/stream/3", stream=True)
        if isinstance(stream, AsyncIterator):
            async for chunk in stream:
                print(f"收到数据块: {len(chunk)} bytes")

        # 并发请求
        print("\n并发请求测试:")

        async def concurrent_request(i: int):
            return await session.post(
                "https://httpbin.org/post", json={"index": i}
            )

        tasks = [concurrent_request(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        print(f"完成{len(results)}个并发请求")

        # 文件下载
        print("\n异步文件下载测试:")
        success = await session.download_file(
            "https://httpbin.org/bytes/1048576", "async_download.bin",
            on_progress=on_progress
        )
        print(f"下载结果: {'成功' if success else '失败'}")


    # 验证代理失效场景
    def test_proxy_failure():
        session = SyncSession(proxies="http://invalid:3128")
        try:
            session.get("http://httpbin.org/ip")
        except ProxyError as e:
            assert "ProxyError" in str(e)


    # 使用pytest-benchmark进行压测
    def test_concurrent_performance(benchmark):
        session = SyncSession()
        urls = ["https://httpbin.org/get"] * 100

        def test_fn():
            return [session.get(url) for url in urls]

        benchmark(test_fn)


    # 执行测试
    print("===== 同步客户端测试 =====")
    test_sync_client()

    print("\n===== 异步客户端测试 =====")
    asyncio.run(test_async_client())

    print("\n===== 代理测试 =====")
    test_proxy_failure()
