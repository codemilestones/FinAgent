"""
速率限制器和重试装饰器

用于控制 API 请求频率和自动重试。
"""

import functools
import time
import threading
from typing import Callable, TypeVar

T = TypeVar("T")


class RateLimiter:
    """
    简单的速率限制器

    控制函数调用频率，确保两次调用之间的最小时间间隔。
    """

    def __init__(self, rate: float = 1.0):
        """
        初始化速率限制器

        Args:
            rate: 最小调用间隔（秒），默认 1 秒
        """
        self.rate = rate
        self.last_call = 0.0
        self._lock = threading.Lock()

    def acquire(self) -> float:
        """
        获取许可，计算需要等待的时间

        Returns:
            需要等待的秒数
        """
        with self._lock:
            current = time.time()
            elapsed = current - self.last_call
            wait_time = max(0, self.rate - elapsed)

            if wait_time > 0:
                time.sleep(wait_time)

            self.last_call = time.time()
            return wait_time

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        装饰器模式，将函数限制速率

        Args:
            func: 要限速的函数

        Returns:
            包装后的函数
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            self.acquire()
            return func(*args, **kwargs)

        return wrapper


def retry_on_exception(
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    initial_delay: float = 1.0,
    exceptions: tuple = (Exception,),
):
    """
    重试装饰器

    Args:
        max_retries: 最大重试次数
        backoff_factor: 退避因子，每次重试延迟时间乘以该因子
        initial_delay: 初始延迟时间（秒）
        exceptions: 需要重试的异常类型

    Returns:
        装饰器函数
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        # 最后一次尝试失败，抛出异常
                        raise last_exception

        return wrapper

    return decorator
