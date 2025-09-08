import threading
import time
from random import randint
from typing import Callable, Any, Optional, Dict, List


class DebounceTimer:
    """
    高性能防抖计时器，适用于高频触发场景的延迟执行

    特性：
    1. 线程安全的触发与状态管理
    2. 自动资源回收机制
    3. 最后一次触发保证执行
    4. 异常处理与统计监控
    5. 支持参数传递与合并策略
    """

    def __init__(
            self,
            delay_seconds: float,
            callback: Callable[..., Any],
            merge_handler: Optional[Callable[[List[Any]], Any]] = None,
            exception_handler: Optional[Callable[[Exception, Any], None]] = None,
            max_queue_size: int = 10_000
    ):
        """
        初始化防抖计时器

        :param delay_seconds: 防抖延迟时间（秒）
        :param callback: 最终执行的回调函数
        :param merge_handler: 参数合并处理器，默认为取最后一次参数
        :param exception_handler: 自定义异常处理器
        :param max_queue_size: 最大事件队列容量（防内存溢出）
        """
        self.delay = delay_seconds
        self.callback = callback
        self.merge_handler = merge_handler or (lambda args: args[-1] if args else None)
        self.exception_handler = exception_handler
        self._max_queue_size = max_queue_size

        # 线程安全组件
        self._lock = threading.RLock()
        self._timer: Optional[threading.Timer] = None
        self._event_queue: List[Any] = []

        # 运行统计
        self._stats = {
            'active': False,
            'total_triggers': 0,
            'success': 0,
            'failures': 0,
            'last_exec_time': 0.0
        }

    def trigger(self, *args) -> bool:
        """
        触发防抖事件（线程安全）

        :param args: 传递给回调函数的参数,tuple
        :return: 是否成功加入队列（队列满时返回False）
        """
        with self._lock:
            # 队列容量保护
            if len(self._event_queue) >= self._max_queue_size:
                return False

            self._event_queue.append(args)
            self._stats.update({
                'total_triggers': self._stats['total_triggers'] + 1,
                'active': True
            })

            # 重置已有计时器
            if self._timer is not None:
                self._timer.cancel()

            # 启动新计时器
            self._timer = threading.Timer(
                self.delay,
                self._execute
            )
            self._timer.daemon = True  # 守护线程防止阻塞主程序退出
            self._timer.start()
            return True

    def _execute(self) -> None:
        """执行回调（带异常处理和状态更新）"""
        with self._lock:
            # 复制并清空当前队列（减少锁占用时间）
            event_queue = self._event_queue.copy()
            self._event_queue.clear()

        # 合并参数
        merged_args = self.merge_handler(event_queue)
        start_time = time.monotonic()

        try:
            self.callback(merged_args)
            self._stats['success'] += 1
        except Exception as e:
            self._stats['failures'] += 1
            if self.exception_handler:
                self.exception_handler(e, merged_args)
            else:
                raise  # 无自定义处理器时抛出原始异常
        finally:
            self._stats.update({
                'last_exec_time': time.monotonic() - start_time,
                'active': False
            })

    def stop(self) -> None:
        """立即停止计时器并清空队列"""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None  # 释放定时器引用
            self._event_queue.clear()
            self._stats['active'] = False

    @property
    def stats(self) -> Dict[str, Any]:
        """获取当前统计指标快照"""
        return self._stats.copy()

    def __del__(self):
        """析构时自动停止防止资源泄露"""
        self.stop()

    def __enter__(self):
        """支持上下文管理协议"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动清理资源"""
        self.stop()


if __name__ == '__main__':

    # 场景1：搜索框输入防抖
    def search(keywords):
        print(f"正在搜索: {keywords}")

    # 初始化防抖器（500ms延迟）
    search_debouncer = DebounceTimer(0.5, search)

    # 模拟输入事件
    for char in 'python':
        search_debouncer.trigger(char)
        time.sleep(0.1)

    time.sleep(0.6)
    print(search_debouncer.stats)


    # 场景2：IoT设备事件聚合
    def sensor_callback(data):
        print(f"接收传感器数据: {data}")
        print(f"Average: {sum(data)/len(data):.1f}℃")

    # 带合并策略的防抖器
    sensor_timer = DebounceTimer(
        delay_seconds=1.0,
        callback=sensor_callback,
        merge_handler=lambda args: [x[0] for x in args]
    )

    # 模拟高频传感器事件
    for _ in range(100):
        sensor_timer.trigger(randint(20,30))

    time.sleep(2)
    print(sensor_timer.stats)

    # 异常处理
    def error_handler(e, data):
        print(f"Error processing {data}: {str(e)}")

    exception_debouncer = DebounceTimer(
        delay_seconds=0.5,
        callback=lambda x: 1/0,  # 会抛出异常
        exception_handler=error_handler
    )

    exception_debouncer.trigger("test")
    time.sleep(1)
    print(exception_debouncer.stats)  # 查看执行统计
