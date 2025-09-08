import sys
from functools import wraps
from pathlib import Path
from typing import Callable, Any

from loguru import logger
from ..file import get_root_path

# 模块级全局变量存储敏感信息标记键
_SENSITIVE_EXTRA_KEY = "sensitive"


def configure_logging(
        console_level: str = "DEBUG",
        log_dir: Path = get_root_path() / "logs",
        rotation_size: str = "100 MB",
        retention_days: str = "30 days",
        error_retention: str = "90 days",
        log_format: str = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<cyan>Thread-{thread}</cyan> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>.<cyan>{function}</cyan>:"
                "<cyan>{line}</cyan> | "
                "<level>{message}</level>"
        ),
        compression: str = "gz",
        enqueue: bool = True,
        sensitive_key: str = "sensitive"
) -> None:
    """动态配置日志系统

    Args:
        console_level: 控制台日志级别（默认DEBUG）
        log_dir: 日志存储目录（默认当前目录/logs）
        rotation_size: 日志轮转大小（默认100MB）
        retention_days: 普通日志保留天数（默认30天）
        error_retention: 错误日志保留天数（默认90天）
        log_format: 日志格式模板
        compression: 日志压缩格式（默认gz）
        enqueue: 启用异步队列（默认True）
        sensitive_key: 敏感信息标记字段（默认sensitive）
    """
    global _SENSITIVE_EXTRA_KEY
    _SENSITIVE_EXTRA_KEY = sensitive_key

    # 参数有效性校验
    valid_levels = {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}
    if console_level not in valid_levels:
        raise ValueError(f"无效的日志级别: {console_level}，可选值: {valid_levels}")

    # 路径类型转换和目录创建
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 移除默认handler避免重复记录
    logger.remove()

    # 控制台输出（过滤敏感信息）
    logger.add(
        sys.stdout,
        level=console_level,
        format=log_format,
        colorize=True,  # 启用彩色输出
        backtrace=True,  # 启用异常回溯跟踪
        diagnose=False,  # 生产环境需关闭敏感信息
        enqueue=enqueue,  # 启用异步安全队列
        filter=lambda r: _SENSITIVE_EXTRA_KEY not in r["extra"],
        catch=True
    )

    # 普通文件日志（按大小轮转）
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        rotation=rotation_size,
        retention=retention_days,
        compression=compression,
        format=log_format,
        level="INFO",
        enqueue=enqueue,
        encoding="utf-8",
        filter=lambda r: _SENSITIVE_EXTRA_KEY not in r["extra"],
        catch=True
    )

    # 错误日志（按天轮转+敏感过滤）
    logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention=error_retention,
        compression=compression,
        format=log_format,
        level="ERROR",
        enqueue=enqueue,
        encoding="utf-8",
        filter=lambda r: _SENSITIVE_EXTRA_KEY not in r["extra"],
        catch=True
    )


def log_exceptions(func: Callable) -> Callable:
    """自动记录异常信息的装饰器

    功能：
    1. 自动捕获未处理异常
    2. 记录完整堆栈跟踪
    3. 标记敏感操作上下文
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.opt(exception=True).error(
                "函数 {} 执行异常",
                func.__name__,
                extra={_SENSITIVE_EXTRA_KEY: True}
            )
            raise e

    return wrapper


class AppLogger:
    """应用日志操作封装"""

    @staticmethod
    @log_exceptions
    def process_sensitive_data(data: dict) -> None:
        """处理敏感数据（示例方法）"""
        logger.info(
            "开始处理敏感数据",
            extra={_SENSITIVE_EXTRA_KEY: True}
        )
        if "required" not in data:
            raise ValueError("缺少必填字段")

    @staticmethod
    def log_business_event(user_id: int, event_type: str) -> None:
        """记录结构化业务事件"""
        logger.info(
            "业务事件发生",
            extra={
                "event": {
                    "type": event_type,
                    "user_id": user_id,
                    "result": "success"
                }
            }
        )

    @classmethod
    def log_api_request(cls) -> None:
        """记录API请求上下文"""
        context_logger = logger.bind(request_id="REQ-123", service="payment")
        context_logger.info("请求开始")
        try:
            # 模拟业务处理
            context_logger.debug("处理支付逻辑...")
            1 / 0
        except Exception:
            context_logger.error("请求处理失败")
            raise
        finally:
            context_logger.info("请求结束")


if __name__ == "__main__":
    # 初始化日志配置
    configure_logging(
        console_level="DEBUG",
        log_dir="./app_logs",
        sensitive_key="confidential"
    )

    # 常规日志示例
    logger.debug("调试信息")
    logger.info("系统启动完成")
    logger.warning("磁盘空间不足20%")

    # 异常日志示例
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("发生除零错误")

    # 敏感操作示例
    try:
        AppLogger.process_sensitive_data({"key": "value"})
    except ValueError:
        logger.warning("捕获到数据处理异常")

    # 结构化日志示例
    AppLogger.log_business_event(12345, "purchase")

    # 上下文日志示例
    try:
        AppLogger.log_api_request()
    except Exception:
        logger.error("API请求处理异常")