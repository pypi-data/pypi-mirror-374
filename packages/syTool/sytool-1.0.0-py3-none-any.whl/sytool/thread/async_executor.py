import asyncio
import concurrent.futures
import inspect
import uuid
from dataclasses import dataclass
from enum import Enum
from functools import partial
from threading import Lock
from typing import (
    Any, Callable, Coroutine, Dict, List, Optional, Union,
    Awaitable, Iterable, TypeVar, Generic
)


class ExecutionMode(Enum):
    """任务执行模式"""
    ASYNC = "async"  # 协程模式
    THREAD = "thread"  # 线程模式
    AUTO = "auto"  # 自动选择模式


@dataclass
class TaskConfig:
    """任务配置参数"""
    mode: ExecutionMode = ExecutionMode.AUTO  # 执行模式
    timeout: Optional[float] = None  # 超时时间（秒）
    max_retries: int = 0  # 最大重试次数
    retry_delay: float = 0.5  # 重试间隔（秒）
    priority: int = 0  # 任务优先级（数值越大优先级越高）


class TaskState(Enum):
    """任务状态"""
    PENDING = "pending"  # 等待中
    RUNNING = "running"  # 执行中
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消
    TIMEOUT = "timeout"  # 超时


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str  # 任务ID
    state: TaskState  # 任务状态
    result: Optional[Any] = None  # 返回结果
    error: Optional[Exception] = None  # 异常信息
    create_time: Optional[float] = None  # 开始时间
    execution_time: Optional[float] = None  # 执行时间（秒）


T = TypeVar('T')  # 泛型参数


# =================== 任务处理器 ===================

class TaskHandler(Generic[T]):
    """任务处理器（支持链式操作）"""

    def __init__(self, manager: 'AsyncTaskExecutor', task_id: str):
        self._manager = manager
        self.task_id = task_id

    def then(
            self,
            callback: Union[Callable[[T], Any], Callable[[T], Awaitable[Any]]]
    ) -> 'TaskHandler[T]':
        """添加成功回调（支持同步/异步函数）

        Args:
            callback: 回调函数，接收任务结果作为参数

        Returns:
            当前任务处理器（支持链式调用）
        """
        self._manager._add_callback(self.task_id, 'success', callback)
        return self

    def catch(
            self,
            callback: Union[Callable[[Exception], Any], Callable[[Exception], Awaitable[Any]]]
    ) -> 'TaskHandler[T]':
        """添加异常回调

        Args:
            callback: 异常处理函数，接收异常对象作为参数

        Returns:
            当前任务处理器（支持链式调用）
        """
        self._manager._add_callback(self.task_id, 'error', callback)
        return self

    def finally_(
            self,
            callback: Union[Callable[[], Any], Callable[[], Awaitable[Any]]]
    ) -> 'TaskHandler[T]':
        """添加最终回调（无论成功或失败都会执行）

        Args:
            callback: 最终回调函数

        Returns:
            当前任务处理器（支持链式调用）
        """
        self._manager._add_callback(self.task_id, 'finally', callback)
        return self


class AsyncTaskExecutor:
    """高性能异步任务执行器（支持协程/线程混合模式和优先级调度）

    特点：
    - 支持协程和线程混合执行
    - 支持任务优先级调度
    - 提供链式回调机制
    - 支持任务重试和超时控制
    """

    def __init__(
            self,
            *,
            max_async_workers: int = 100,
            max_thread_workers: int = 10,
            max_queue_size: int = 1000,
            loop: Optional[asyncio.AbstractEventLoop] = None,
            enable_priority: bool = False
    ):
        """
        初始化执行器

        Args:
            max_async_workers: 最大协程并发数（信号量控制）
            max_thread_workers: 线程池最大工作线程数
            loop: 自定义事件循环
            enable_priority: 是否启用优先级队列
        """
        # 使用asyncio.get_running_loop()替代get_event_loop()避免跨循环问题
        self.loop = loop or asyncio.get_running_loop()
        self.thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_thread_workers, thread_name_prefix="AsyncTaskExecutor"
        )
        self.async_semaphore = asyncio.Semaphore(max_async_workers)
        self.enable_priority = enable_priority

        # 任务存储结构
        self._data_lock = Lock()  # 共享数据锁
        self._pending_tasks: Dict[str, asyncio.Task] = {}
        self._completed_tasks: Dict[str, TaskResult] = {}
        self._callbacks: Dict[str, Dict[str, list]] = {}
        self._task_events: Dict[str, asyncio.Event] = {}

        # 优先级队列（负优先级实现升序排序）
        self._task_queue: Optional[asyncio.PriorityQueue] = None
        if enable_priority:
            self._task_queue = asyncio.PriorityQueue(maxsize=max_queue_size)
            self._queue_consumer_task = self.loop.create_task(self._process_task_queue())

        self._submitted_order: List[str] = []  # 提交顺序记录
        self._completed_order: List[str] = []  # 完成顺序记录
        self._shutdown_event = asyncio.Event()  # 关闭信号
        self._is_shutting_down = False  # 关闭状态标志

    def _generate_task_id(self) -> str:
        """生成唯一任务ID"""
        return str(uuid.uuid4())

    def _add_callback(self, task_id: str, cb_type: str, callback: Callable):
        """注册回调函数

        Args:
            task_id: 任务ID
            cb_type: 回调类型（success/error/finally）
            callback: 回调函数
        """
        if task_id not in self._callbacks:
            self._callbacks[task_id] = {'success': [], 'error': [], 'finally': []}
        self._callbacks[task_id][cb_type].append(callback)

    async def _execute_async(
            self,
            coro: Coroutine,
            config: TaskConfig
    ) -> Any:
        """协程任务执行器（带并发控制）

        Args:
            coro: 协程对象
            config: 任务配置

        Returns:
            任务执行结果

        Raises:
            Exception: 如果所有重试都失败则抛出异常
        """
        for attempt in range(config.max_retries + 1):
            try:
                # 使用asyncio.wait_for处理超时
                return await asyncio.wait_for(coro, timeout=config.timeout)
            except asyncio.CancelledError:
                raise
            except asyncio.TimeoutError as e:
                if attempt == config.max_retries:
                    raise
                print(f"任务超时，尝试重试 ({attempt + 1}/{config.max_retries})")
                await asyncio.sleep(config.retry_delay)
            except Exception as e:
                if attempt == config.max_retries:
                    raise
                print((f"任务异常，尝试重试 ({attempt + 1}/{config.max_retries}): {e}"))
                await asyncio.sleep(config.retry_delay)

    async def _execute_thread(
            self,
            func: Callable,
            *args,
            config: TaskConfig,
            **kwargs
    ) -> Any:
        """线程任务执行器

        Args:
            func: 可调用对象
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            任务执行结果
        """
        for attempt in range(config.max_retries + 1):
            try:
                return await self.loop.run_in_executor(
                    self.thread_executor, partial(func, *args, **kwargs)
                )
            except Exception as e:
                if attempt == config.max_retries or isinstance(e, (KeyboardInterrupt, SystemExit)):
                    raise
                print(f"线程任务异常，重试 ({attempt + 1}/{config.max_retries}): {e}")
                await asyncio.sleep(config.retry_delay)

    async def _task_wrapper(
            self,
            task_id: str,
            func: Union[Callable, Coroutine],
            args: Iterable,
            kwargs: Dict,
            config: TaskConfig
    ) -> TaskResult:
        """统一任务包装器

        Args:
            task_id: 任务ID
            func: 任务函数（协程或普通函数）
            args: 位置参数
            kwargs: 关键字参数
            config: 任务配置

        Returns:
            任务结果对象
        """
        start_time = self.loop.time()
        try:
            # 更新任务状态为运行中
            self._update_task_state(task_id, TaskState.RUNNING)

            # 确定执行模式
            if config.mode == ExecutionMode.ASYNC:
                executor = self._execute_async(func(*args, **kwargs), config)
            elif config.mode == ExecutionMode.THREAD:
                executor = self._execute_thread(func, *args, **kwargs)
            else:  # AUTO模式
                if inspect.iscoroutinefunction(func):
                    executor = self._execute_async(func(*args, **kwargs), config)
                else:
                    executor = self._execute_thread(func, *args, **kwargs)

            result = await executor
            exec_time = self.loop.time() - start_time
            return self._complete_task(task_id, result, start_time, exec_time)
        except asyncio.CancelledError as e:
            exec_time = self.loop.time() - start_time
            return self._fail_task(task_id, TaskState.CANCELLED, e, start_time, exec_time)
        except asyncio.TimeoutError as e:
            exec_time = self.loop.time() - start_time
            return self._fail_task(task_id, TaskState.TIMEOUT, e, start_time, exec_time)
        except Exception as e:
            exec_time = self.loop.time() - start_time
            return self._fail_task(task_id, TaskState.FAILED, e, start_time, exec_time)
        finally:
            self._cleanup_task(task_id)

    def _update_task_state(self, task_id: str, state: TaskState):
        """更新任务状态

        Args:
            task_id: 任务ID
            state: 新状态
        """
        with self._data_lock:
            if task_id in self._completed_tasks:
                self._completed_tasks[task_id].state = state

    def _complete_task(self, task_id: str, result: Any, create_time: float, exec_time: float) -> TaskResult:
        """标记任务完成

        Args:
            task_id: 任务ID
            result: 任务结果
        """
        with self._data_lock:
            self._completed_order.append(task_id)
            task_result = TaskResult(
                task_id=task_id,
                state=TaskState.SUCCESS,
                result=result,
                create_time=create_time,
                execution_time=exec_time
            )
            self._completed_tasks[task_id] = task_result
            # 触发任务事件
            if event := self._task_events.pop(task_id, None):
                event.set()
            self._run_callbacks(task_id, 'success', result)
            return task_result

    def _fail_task(self, task_id: str, state: TaskState, error: Exception, create_time: float=None, exec_time: float = None) -> TaskResult:
        """标记任务失败

        Args:
            task_id: 任务ID
            error: 异常对象
        """
        with self._data_lock:
            self._completed_order.append(task_id)
            task_result = TaskResult(
                task_id=task_id,
                state=state,
                error=error,
                create_time=create_time,
                execution_time=exec_time
            )
            self._completed_tasks[task_id] = task_result
            # 触发任务事件
            if event := self._task_events.pop(task_id, None):
                event.set()
            self._run_callbacks(task_id, 'error', error)
            return task_result

    def _cleanup_task(self, task_id: str):
        """清理任务资源"""
        with self._data_lock:
            self._pending_tasks.pop(task_id, None)
            self._task_events.pop(task_id, None)
            # 保留回调直到执行完毕
            # self._callbacks.pop(task_id, None)

    def _run_callbacks(self, task_id: str, cb_type: str, arg: Any = None):
        """执行回调函数链"""
        if self._is_shutting_down:
            return
        try:
            callbacks = self._callbacks.get(task_id, {}).get(cb_type, [])
            for cb in callbacks:
                try:
                    if inspect.iscoroutinefunction(cb):
                        if cb_type == 'finally':
                            self.loop.create_task(cb())
                        else:
                            self.loop.create_task(cb(arg))
                    else:
                        if cb_type == 'finally':
                            self.loop.call_soon_threadsafe(cb)
                        else:
                            self.loop.call_soon_threadsafe(cb, arg)
                except Exception as e:
                    print(f"Callback error: {e!r}")

            # 执行最终回调
            if cb_type in ('success', 'error'):
                self._run_callbacks(task_id, 'finally')  # 不传递参数
        except Exception as e:
            print(f"{cb_type} 回调错误: {e}")

    async def _process_task_queue(self):
        """优先级队列消费者"""
        while not self._shutdown_event.is_set() or not self._task_queue.empty():
            async with self.async_semaphore:
                try:
                    # 带超时的队列获取（防止关闭时卡死）
                    _, task_id, task_info = await asyncio.wait_for(
                        self._task_queue.get(),
                        timeout=0.5
                    )

                    # 检查是否正在关闭
                    if self._shutdown_event.is_set():
                        self._fail_task(task_id, TaskState.CANCELLED, asyncio.CancelledError("Executor shutting down"))
                        self._task_queue.task_done()
                        continue

                    # 解析任务参数
                    func = task_info["func"]
                    args = task_info.get("args", ())
                    kwargs = task_info.get("kwargs", {})
                    config = task_info["config"]

                    # 创建并执行任务
                    task_coro = self._task_wrapper(task_id, func, args, kwargs, config)
                    task = self.loop.create_task(task_coro)
                    self._pending_tasks[task_id] = task

                    # 绑定队列完成标记
                    task.add_done_callback(lambda _: self._task_queue.task_done())

                except asyncio.TimeoutError:
                    # 超时正常，继续检查关闭条件
                    continue
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"队列处理错误: {e!r}")
                    self._fail_task(task_id, TaskState.FAILED, e)
                    self._task_queue.task_done()

    def submit(
            self,
            func: Union[Callable, Coroutine],
            *args,
            config: Optional[TaskConfig] = None,
            **kwargs
    ) -> TaskHandler[Any]:
        """
        提交任务（支持优先级调度）

        Args:
            func: 可调用对象或协程
            *args: 位置参数
            config: 任务配置
            **kwargs: 关键字参数

        Returns:
            任务处理器
        """
        if self._is_shutting_down:
            raise RuntimeError("执行器正在关闭，无法提交新任务")

        config = config or TaskConfig()
        task_id = self._generate_task_id()

        # 初始化任务状态和事件
        self._completed_tasks[task_id] = TaskResult(task_id, TaskState.PENDING)
        self._task_events[task_id] = asyncio.Event()
        self._submitted_order.append(task_id)

        if self.enable_priority:
            # 将任务描述信息放入优先级队列（而不是直接创建任务）
            task_info = {
                'task_id': task_id,
                'func': func,
                'args': args,
                'kwargs': kwargs,
                'config': config
            }

            # 负优先级实现升序排序
            self._task_queue.put_nowait((-config.priority, task_id, task_info))
        else:
            # 直接调度任务
            task_coro = self._task_wrapper(task_id, func, args, kwargs, config)
            task = self.loop.create_task(task_coro)
            self._pending_tasks[task_id] = task

        return TaskHandler(self, task_id)

    async def gather(self, ordered: bool = True, return_exceptions: bool = False) -> List[TaskResult]:
        """
        获取所有任务结果，等待所有任务完成后再返回。

        Args:
            ordered: 是否按提交顺序返回
            return_exceptions: 是否包含异常结果

        Returns:
            任务结果列表
        """
        await self.wait_all()

        # 检查未完成的任务
        for task_id in self._submitted_order:
            if self._completed_tasks[task_id].state == TaskState.PENDING:
                self._fail_task(task_id, TaskState.CANCELLED, asyncio.CancelledError("Task cancelled during shutdown"))

        if ordered:
            # 按提交顺序返回
            return [self._completed_tasks[task_id] for task_id in self._submitted_order]
        else:
            # 按完成顺序返回
            return [self._completed_tasks[task_id] for task_id in self._completed_order]

    async def wait_all(self, timeout: Optional[float] = None):
        """等待所有任务完成，包括队列中的任务"""
        if self._task_queue:
            await self._task_queue.join()  # 等待队列消费者处理完所有任务
            self._shutdown_event.set()

        if pending := [t for t in self._pending_tasks.values() if not t.done()]:
            await asyncio.shield(asyncio.gather(*pending, return_exceptions=True))

        if pending:
            done, pending = await asyncio.wait(
                pending,
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED
            )
            for task in pending:
                task.cancel()

    async def get_result(self, task_id: str) -> Optional[TaskResult]:
        """获取单个任务结果

        Args:
            task_id: 任务ID

        Returns:
            任务结果对象或None
        """
        await self.wait_for(task_id)
        return self._completed_tasks.get(task_id)

    async def wait_for(
            self,
            *task_ids: str,
            timeout: Optional[float] = None,
            callback: Optional[Callable[[List[TaskResult]], None]] = None
    ) -> List[TaskResult]:
        """等待指定任务完成

        Args:
            *task_ids: 要等待的任务ID列表
            callback: 完成回调函数

        Returns:
            任务结果列表
        """
        # 预检查任务状态
        pending_set = set(task_ids)
        results = []

        # 立即获取已完成任务
        for tid in list(pending_set):
            if self._completed_tasks[tid].state not in (TaskState.PENDING, TaskState.RUNNING):
                results.append(self._completed_tasks[tid])
                pending_set.remove(tid)

        # 处理剩余未完成任务
        if pending_set:
            events = [self._task_events[tid] for tid in pending_set]
            wait_coro = asyncio.gather(*[e.wait() for e in events])

            try:
                await asyncio.wait_for(wait_coro, timeout=timeout)
            except asyncio.TimeoutError:
                # 标记超时任务
                for tid in pending_set:
                    if not self._task_events[tid].is_set():
                        self._fail_task(tid, TaskState.TIMEOUT, asyncio.TimeoutError())
                raise
            finally:
                results.extend(self._completed_tasks[tid] for tid in pending_set)

        # 排序结果保持原始顺序
        ordered_results = [r for tid in task_ids for r in results if r.task_id == tid]

        if callback:
            if asyncio.iscoroutinefunction(callback):
                await callback(ordered_results)
            else:
                self.loop.call_soon_threadsafe(callback, ordered_results)

        return ordered_results

    async def shutdown(self, timeout: float = 30):
        """优雅关闭执行器

        Args:
            timeout: 等待任务完成的超时时间
        """
        # 停止接受新任务
        self._is_shutting_down = True
        print("开始关闭执行器...")

        # 取消队列消费者
        if hasattr(self, '_queue_consumer_task'):
            self._queue_consumer_task.cancel()
            try:
                await self._queue_consumer_task
            except asyncio.CancelledError:
                pass

        # 清空优先级队列并标记任务为取消
        if self._task_queue:
            while not self._task_queue.empty():
                try:
                    _, task_id, _ = self._task_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                else:
                    self._fail_task(task_id, TaskState.CANCELLED, asyncio.CancelledError("Executor shutting down"))
                    self._task_queue.task_done()
            self._shutdown_event.set()

        # 取消所有待处理任务
        for task_id, task in list(self._pending_tasks.items()):
            if not task.done():
                task.cancel()
                self._fail_task(task_id, TaskState.CANCELLED, asyncio.CancelledError("Task cancelled during shutdown"))

        # 使用更可靠的等待方式
        if pending := [t for t in self._pending_tasks.values() if not t.done()]:
            done, pending = await asyncio.wait(
                pending,
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED
            )
            for task in pending:
                task.cancel()

        # 关闭线程池
        self.thread_executor.shutdown(wait=True, cancel_futures=True)

        # 清理资源
        self._pending_tasks.clear()
        self._task_events.clear()
        self._callbacks.clear()

        self._completed_tasks.clear()
        self._submitted_order.clear()
        self._completed_order.clear()

        print("执行器已关闭")


async def demo_usage():
    # 示例协程任务
    async def async_task(n: int):
        await asyncio.sleep(0.5)
        return f"AsyncTask-{n}"

    # 示例阻塞任务
    def blocking_task(n: int):
        import time
        time.sleep(0.5)
        return f"BlockingTask-{n}"

    # 初始化执行器
    executor = AsyncTaskExecutor(
        max_async_workers=5,
        max_thread_workers=3,
        enable_priority=True
    )

    # 场景1：混合提交+链式处理
    task1 = executor.submit(async_task, 1, config=TaskConfig(priority=2)) \
        .then(lambda r: print(f"async_task链式处理结果: {r}")) \
        .catch(lambda e: print(f"async_task链式处理异常: {e}")) \
        .finally_(lambda: print("async_task Task1 执行finally方法"))

    task2 = executor.submit(
        blocking_task, 2,
        config=TaskConfig(mode=ExecutionMode.THREAD, max_retries=1)
    ).then(lambda r: print(f"Thread 链式处理结果: {r}")) \
        .finally_(lambda: print("Thread Task2 执行finally方法"))

    # 场景2：批量提交任务
    for i in range(3, 10):
        if i == 9:
            def blocking_exception_task(n: int):
                import time
                time.sleep(0.5)
                raise ValueError(f"BlockingExceptionTask-{n}")

            executor.submit(blocking_exception_task, i, config=TaskConfig(priority=100))
        elif i == 7:
            def async_exception_task(n: int):
                import time
                time.sleep(0.5)
                raise RuntimeError(f"AsyncExceptionTask-{n}")

            executor.submit(async_exception_task, i)
        else:
            executor.submit(async_task, i)

    # 场景3：等待特定任务完成
    await executor.wait_for(task1.task_id, callback=lambda rs: print("等待特定任务完成:First task completed", rs))

    # 场景4：按完成顺序获取结果
    unordered_results = await executor.gather(ordered=False)
    unordered_results = [task.result for task in unordered_results]
    print("按完成顺序获取结果:", unordered_results)

    # 场景5：按提交顺序获取结果
    ordered_results = await executor.gather(ordered=True)
    ordered_results = [task.result for task in ordered_results]
    print("按提交顺序获取结果:", ordered_results)

    # 场景6：获取单个任务结果
    print("Task2 执行结果:", await executor.get_result(task2.task_id))

    # 场景7：带优先级的任务
    high_pri_task = executor.submit(
        async_task, 99,
        config=TaskConfig(priority=5)
    )

    # 场景8：异常处理任务
    def faulty_task():
        raise ValueError("Intentional error")

    exception_task = executor.submit(faulty_task) \
        .catch(lambda e: print(f"异常任务测试结果: {e}")) \
        .finally_(lambda: print("异常任务结束后清理资源"))

    print("获取高优先级任务结果:", await executor.get_result(high_pri_task.task_id))
    print("获取异常任务结果:", await executor.get_result(exception_task.task_id))
    print("队列状态:",
          "运行中" if not executor._shutdown_event.is_set() else "已关闭",
          "剩余任务:", executor._task_queue.qsize() if executor._task_queue else 0)
    print("未完成任务:", [t.task_id for t in executor._pending_tasks.values() if not t.done()])

    ordered_results = await executor.gather(ordered=True)
    ordered_results = [task.result for task in ordered_results]
    print("最终获取所有结果:", ordered_results)

    # 关闭执行器
    await executor.shutdown()


# 运行示例
if __name__ == "__main__":
    asyncio.run(demo_usage())

    import queue

    # 创建优先队列
    task_queue = queue.PriorityQueue()

    # 放入任务（优先级取反）
    task_queue.put((-5, "低优先级任务"))
    task_queue.put((-10, "高优先级任务"))

    # 获取任务（优先级高的先出队）
    while not task_queue.empty():
        priority, task = task_queue.get()
        print(f"处理任务: {task}, 原始优先级: {priority}")
