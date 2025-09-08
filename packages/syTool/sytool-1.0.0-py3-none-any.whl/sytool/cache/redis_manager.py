"""
Redis通用工具类（支持单节点/集群/哨兵模式）
版本：v1.1 (2025-05-13)
"""
import time
import uuid
from functools import wraps
from threading import Thread, Event, RLock
from typing import Any, List, Callable, Optional, Dict, Tuple

from loguru import logger
from redis import Redis, ConnectionPool
from redis.exceptions import ConnectionError
from redis.sentinel import Sentinel
from rediscluster import RedisCluster
from rediscluster.exceptions import RedisClusterException


# -------------------- 自定义异常类型 --------------------
class RedisConnError(Exception):
    """Redis连接相关异常基类"""


class RedisConfigError(RedisConnError):
    """配置参数错误"""


class RedisOperationError(Exception):
    """Redis操作相关异常基类"""


class RedisLockError(RedisOperationError):
    """分布式锁异常"""


class RedisSerializationError(RedisOperationError):
    """序列化异常"""


# -------------------- 装饰器 --------------------
def retry_connection(retries=3, delay=0.1, backoff=2):
    """
    指数退避 连接重试装饰器
    :param retries: 最大重试次数
    :param delay: 重试间隔(秒)
    :param backoff: 默认为2,表示指数退避重试.比如:0.1*2*2*2
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            current_delay = delay
            for attempt in range(1, retries + 1):
                try:
                    return func(self, *args, **kwargs)
                except (ConnectionError, TimeoutError, RedisClusterException) as e:
                    msg = f"Redis连接异常({attempt}/{retries}): {str(e)}"
                    logger.warning(msg)
                    if attempt < retries:
                        time.sleep(current_delay)
                        current_delay *= backoff  # 指数退避
                        self._reconnect()
            raise RedisConnError(f"操作失败，重试{retries}次后仍无法连接Redis")

        return wrapper

    return decorator


# -------------------- 核心工具类 --------------------
class RedisClient:
    """
    Redis通用客户端工具类

    特性：
    1. 支持单节点、集群、哨兵三种部署模式
    2. 支持自定义序列化策略（默认使用字符串编码）
    3. 线程安全连接池管理
    4. 完善的异常处理和重试机制
    5. 支持分布式锁（含自动续期）
    6. 实现所有主流数据结构操作

    配置示例：
    # 单节点模式
    {
        "mode": "standalone",
        "host": "127.0.0.1",
        "port": 6379,
        "password": "yourpassword",
        "db": 0,
        "max_connections": 20
    }

    # 集群模式
    {
        "mode": "cluster",
        "nodes": [
            {"host": "node1", "port": 7000},
            {"host": "node2", "port": 7001}
        ],
        "password": "yourpassword",
        "max_connections": 50
    }

    # 哨兵模式
    {
        "mode": "sentinel",
        "sentinels": [
            {"host": "sentinel1", "port": 26379},
            {"host": "sentinel2", "port": 26379}
        ],
        "service_name": "mymaster",
        "password": "yourpassword",
        "db": 0,
        "max_connections": 30
    }
    """

    def __init__(self,
                 config: dict,
                 key_serializer: Callable[[str], bytes] = None,
                 key_deserializer: Callable[[bytes], str] = None,
                 value_serializer: Callable[[Any], bytes] = None,
                 value_deserializer: Callable[[bytes], Any] = None):

        """
        初始化Redis客户端
        :param config: 连接配置字典
        :param key_serializer: key序列化方法（默认字符串编码）
        :param value_serializer: value序列化方法（默认字符串转换）
        """
        self.config = self._validate_config(config)
        self._setup_serializers(key_serializer, key_deserializer,
                                value_serializer, value_deserializer)
        self._client = self._init_client()
        self._lock_renewers = {}  # 锁续期线程管理器
        self._lock = RLock()  # 线程操作锁

    def _setup_serializers(self, key_ser, key_deser, val_ser, val_deser):
        """初始化序列化器"""
        # 添加参数类型校验
        if not all(callable(f) for f in [key_ser, key_deser, val_ser, val_deser] if f is not None):
            raise RedisConfigError("序列化方法必须可调用")

        # 设置默认序列化方法
        self.key_serializer = key_ser or (lambda x: x.encode('utf-8'))
        self.key_deserializer = key_deser or (lambda x: x.decode('utf-8'))
        self.value_serializer = val_ser or (lambda x: str(x).encode('utf-8'))
        self.value_deserializer = val_deser or (lambda x: x.decode('utf-8'))

    def _validate_config(self, config: dict) -> dict:
        """配置参数校验"""
        mode = config.get('mode', 'standalone').lower()
        if mode not in {'standalone', 'cluster', 'sentinel'}:
            raise RedisConfigError(f"不支持的Redis模式：{mode}")

        # 模式特定校验
        if mode == 'sentinel':
            if not isinstance(config.get('sentinels'), list) or len(config['sentinels']) == 0:
                raise RedisConfigError("哨兵模式需要至少一个sentinel节点配置")
        elif mode == 'cluster':
            if not isinstance(config.get('nodes'), list) or len(config['nodes']) < 3:
                logger.warning("集群模式建议配置至少3个节点以保证高可用")

        # 设置默认连接数
        config.setdefault('max_connections', 20)
        return config

    def _init_client(self) -> Any:
        """根据配置初始化客户端连接"""
        mode = self.config['mode'].lower()
        try:
            if mode == 'standalone':
                return self._init_standalone_node()
            elif mode == 'cluster':
                return self._init_cluster()
            elif mode == 'sentinel':
                return self._init_sentinel()
        except Exception as e:
            raise RedisConnError(f"无法建立Redis连接: {str(e)}") from e

    def _init_standalone_node(self) -> Redis:
        """初始化单节点连接"""
        pool = ConnectionPool(
            host=self.config['host'],
            port=self.config['port'],
            password=self.config.get('password'),
            db=self.config.get('db', 0),
            decode_responses=False,
            max_connections=self.config['max_connections']
        )
        return Redis(connection_pool=pool)

    def _init_cluster(self) -> RedisCluster:
        """初始化集群连接"""
        return RedisCluster(
            startup_nodes=self.config['nodes'],
            password=self.config.get('password'),
            decode_responses=False,
            max_connections=self.config['max_connections']
        )

    def _init_sentinel(self) -> Redis:
        """初始化哨兵模式连接"""
        sentinel = Sentinel(
            [(s['host'], s['port']) for s in self.config['nodes']],
            password=self.config.get('password'),
            socket_timeout=5,
            decode_responses=False
        )
        return sentinel.master_for(
            self.config['service_name'],
            db=self.config.get('db', 0),
            password=self.config.get('password')
        )

    # -------------------- 基础方法 --------------------
    @retry_connection()
    def set(self, key: str, value: Any, ex: int = None, nx: bool = False, xx: bool = False) -> bool:
        """
        设置键值对
        :param key: 键名
        :param value: 值（自动序列化）
        :param ex: 过期时间(秒)
        :param nx: 仅当键不存在时设置
        :param xx: 仅当键存在时设置
        :return: 是否设置成功
        """
        skey = self._serialize_key(key)
        svalue = self._serialize_value(value)
        return self._client.set(skey, svalue, ex=ex, nx=nx, xx=xx)

    @retry_connection()
    def get(self, key: str) -> Any:
        """获取键值（自动反序列化）"""
        skey = self._serialize_key(key)
        svalue = self._client.get(skey)
        return self._deserialize_value(svalue)

    @retry_connection()
    def delete(self, *keys: str) -> int:
        """删除一个或多个键"""
        skeys = [self._serialize_key(k) for k in keys]
        return self._client.delete(*skeys)

    @retry_connection()
    def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        return self._client.expire(self._serialize_key(key), seconds)

    @retry_connection()
    def exists(self, key: str) -> bool:
        """判断键是否存在"""
        return self._client.exists(self._serialize_key(key)) == 1

    # -------------------- 哈希表操作 --------------------
    @retry_connection()
    def hset(self, name: str, key: str, value: Any) -> int:
        """设置哈希字段"""
        sname = self._serialize_key(name)
        skey = self._serialize_key(key)
        svalue = self._serialize_value(value)
        return self._client.hset(sname, skey, svalue)

    @retry_connection()
    def hget(self, name: str, key: str) -> Any:
        """获取哈希字段值"""
        sname = self._serialize_key(name)
        skey = self._serialize_key(key)
        svalue = self._client.hget(sname, skey)
        return self._deserialize_value(svalue) if svalue is not None else None

    @retry_connection()
    def hexists(self, name: str, key: str) -> bool:
        sname = self._serialize_key(name)
        skey = self._serialize_key(key)
        return self._client.hexists(sname, skey)

    @retry_connection()
    def hgetall(self, name: str) -> Dict[str, Any]:
        """获取整个哈希表"""
        data = self._client.hgetall(self._serialize_key(name))
        return {
            self.key_deserializer(k): self._deserialize_value(v)
            for k, v in data.items()
        }

    # -------------------- 高级方法 --------------------
    def set_if_absent(self, key: str, value: Any, ex: int = None) -> bool:
        """当键不存在时设置值（原子操作）"""
        skey = self._serialize_key(key)
        svalue = self._serialize_value(value)
        return self._client.set(skey, svalue, ex=ex, nx=True)

    def increment(self, key: str, amount: int = 1) -> int:
        """原子递增"""
        skey = self._serialize_key(key)
        return self._client.incrby(skey, amount)

    def decrement(self, key: str, amount: int = 1) -> int:
        """原子递减"""
        skey = self._serialize_key(key)
        return self._client.decrby(skey, amount)

    # -------------------- 分布式锁 --------------------
    def acquire_lock(self,
                     lock_key: str,
                     timeout: int = 10,
                     expire_time: int = 30,
                     renew_interval: int = 10) -> Optional[str]:
        """
        获取分布式锁（支持自动续期）
        :param lock_key: 锁名称
        :param timeout: 获取锁超时时间(秒)
        :param expire_time: 锁过期时间(秒)
        :param renew_interval: 自动续期间隔(秒)
        :return: 锁标识（获取失败返回None）
        """
        identifier = str(uuid.uuid4())
        skey = self._serialize_key(lock_key)
        stop_event = Event()

        # 使用Lua脚本保证原子性:仅当键不存在时设置值（原子性互斥)
        lua_script = """
               if redis.call('set', KEYS[1], ARGV[1], 'NX', 'EX', ARGV[2]) then
                   return 1
               else
                   return 0
               end"""

        with self._lock:
            end_time = time.monotonic() + timeout
            while time.monotonic() < end_time:
                # 尝试获取锁
                result = self._client.eval(lua_script, 1, skey, identifier, expire_time)
                if result:
                    # 启动续期线程
                    renew_thread = Thread(target=self._lock_renewer,
                                          args=(skey, identifier, expire_time, renew_interval, stop_event),
                                          daemon=True)
                    renew_thread.start()
                    self._lock_renewers[identifier] = (renew_thread, stop_event)
                    return identifier
                time.sleep(0.1)
        return None

    def _lock_renewer(self, skey: bytes, identifier: str,
                      expire_time: int, interval: int, stop_event: Event):
        """锁续期线程"""
        while not stop_event.is_set():
            time.sleep(interval)
            try:
                lua = """
                if redis.call("GET", KEYS[1]) == ARGV[1] then
                    return redis.call("EXPIRE", KEYS[1], ARGV[2])
                else
                    return 0
                end"""
                result = self._client.eval(lua, 1, skey, identifier, expire_time)
                if not result:
                    break
            except Exception as e:
                logger.error(f"锁续期失败: {str(e)}")
                break

    @retry_connection()
    def release_lock(self, lock_key: str, identifier: str):
        """释放分布式锁"""
        skey = self._serialize_key(lock_key)
        # 停止续期线程
        if identifier in self._lock_renewers:
            renew_thread, stop_event = self._lock_renewers[identifier]
            stop_event.set()
            # 添加线程移除后的清理检查
            del self._lock_renewers[identifier]
            logger.debug("redis锁续期线程已停止.lock_key:{},identifier:{}", lock_key, identifier)

        lua = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end"""
        self._client.eval(lua, 1, skey, identifier)

    # -------------------- 其他工具方法 --------------------
    @retry_connection()
    def scan_keys(self, pattern: str = "*", count=100) -> List[str]:
        """模糊查询键"""
        if isinstance(self._client, RedisCluster):
            return [
                self._deserialize_key(k)
                for k in self._client.scan_iter(match=pattern, count=count)
            ]
        return self._standalone_scan(pattern, count)

    def _standalone_scan(self, pattern: str, count: int) -> List[str]:
        """单节点/哨兵模式下的SCAN实现"""
        cursor = 0
        keys = []
        while True:
            cursor, partial = self._client.scan(
                cursor=cursor,
                match=self._serialize_key(pattern),
                count=count
            )
            keys.extend([self._deserialize_key(k) for k in partial])
            if cursor == 0:
                break
        return keys

    # -------------------- 集合操作 --------------------
    @retry_connection()
    def sadd(self, name: str, *values: Any) -> int:
        """向集合添加元素"""
        sname = self._serialize_key(name)
        svalues = [self._serialize_value(v) for v in values]
        return self._client.sadd(sname, *svalues)

    @retry_connection()
    def smembers(self, name: str) -> set:
        """获取集合所有元素"""
        sname = self._serialize_key(name)
        return {self._deserialize_value(v) for v in self._client.smembers(sname)}

    # -------------------- 列表操作 --------------------
    @retry_connection()
    def lpush(self, name: str, *values: Any) -> int:
        """列表左端插入元素"""
        return self._client.lpush(
            self._serialize_key(name),
            *[self._serialize_value(v) for v in values]
        )

    @retry_connection()
    def lrange(self, name: str, start: int, end: int) -> List[Any]:
        """获取列表范围元素"""
        return [
            self._deserialize_value(v)
            for v in self._client.lrange(
                self._serialize_key(name), start, end
            )
        ]

    @retry_connection()
    def rpop(self, name: str) -> Any:
        """列表右端弹出"""
        sname = self._serialize_key(name)
        svalue = self._client.rpop(sname)
        return self._deserialize_value(svalue) if svalue else None

    # -------------------- 有序集合操作 --------------------
    @retry_connection()
    def zadd(self, name: str, mapping: Dict[Any, float]) -> int:
        """向有序集合添加元素"""
        return self._client.zadd(
            self._serialize_key(name),
            {self._serialize_value(k): v for k, v in mapping.items()}
        )

    @retry_connection()
    def zrange(self, name: str, min_score: float, max_score: float,
               withscores: bool = False, offset: int = None, count: int = None) -> List[Tuple]:
        """
        有序集合范围查询
        """
        sname = self._serialize_key(name)
        results = self._client.zrangebyscore(sname, min_score, max_score,
                                             withscores=withscores, start=offset, num=count)
        if withscores:
            return [(self._deserialize_value(k), v) for k, v in results]
        return [self._deserialize_value(k) for k in results]

    # -------------------- pipline --------------------
    @retry_connection()
    def pipeline(self):
        """获取Pipeline对象"""
        return self._client.pipeline()

    @retry_connection()
    def pubsub(self):
        """获取PubSub对象"""
        return self._client.pubsub()

    # -------------------- Stream操作 --------------------
    @retry_connection()
    def xadd(self, stream: str, fields: dict, max_len=1000) -> str:
        """添加Stream消息"""
        sstream = self._serialize_key(stream)
        sfields = {k: self._serialize_value(v) for k, v in fields.items()}
        return self._client.xadd(sstream, sfields, maxlen=max_len)

    # -------------------- 序列化方法 --------------------
    def _serialize_key(self, key: str) -> bytes:
        try:
            return self.key_serializer(key)
        except Exception as e:
            raise RedisSerializationError(f"Key序列化失败: {str(e)}") from e

    def _deserialize_key(self, key: bytes) -> str:
        try:
            return self.key_deserializer(key)
        except Exception as e:
            raise RedisSerializationError(f"Key反序列化失败: {str(e)}") from e

    def _serialize_value(self, value: Any) -> bytes:
        try:
            return self.value_serializer(value)
        except Exception as e:
            raise RedisSerializationError(f"Value序列化失败: {str(e)}") from e

    def _deserialize_value(self, value: bytes) -> Any:
        try:
            return self.value_deserializer(value) if value else None
        except Exception as e:
            raise RedisSerializationError(f"Value反序列化失败: {str(e)}") from e

    # -------------------- 连接管理 --------------------
    def _reconnect(self):
        """重新建立连接"""
        try:
            self._client.close()
        except Exception:
            pass
        self._client = self._init_client()

    def close(self):
        """资源清理"""
        self._client.close()
        # 等待续期线程终止
        for key, value in self._lock_renewers.items():
            thread, event = value
            event.set()
            thread.join(timeout=5)
            logger.debug("开始清理线程资源,标记event.identifier:{}", key)
        self._lock_renewers.clear()


# 声明client


if __name__ == '__main__':
    # ----------- 配置示例 -----------
    # 单节点配置
    standalone_config = {
        "mode": "standalone",
        "host": "10.194.65.131",
        "port": 6379,
        "password": "hgrica1@",
        "db": 11
    }

    # 集群配置
    cluster_config = {
        "mode": "cluster",
        "nodes": [
            {"host": "10.194.68.176", "port": 6391},
            {"host": "10.194.68.176", "port": 6392},
            {"host": "10.194.68.176", "port": 6393},
            {"host": "10.194.68.177", "port": 6394},
            {"host": "10.194.68.177", "port": 6395},
            {"host": "10.194.68.177", "port": 6396},
            {"host": "10.194.68.178", "port": 6397},
            {"host": "10.194.68.178", "port": 6398},
            {"host": "10.194.68.178", "port": 6399}
        ],
        "password": "hgrica1@"
    }

    # 哨兵模式配置
    sentinel_config = {
        "mode": "sentinel",
        "service_name": "mymaster",
        "password": "yourpassword",
        "db": 0,
        "nodes": [
            {"host": "10.194.68.176", "port": 26379},
            {"host": "10.194.68.177", "port": 26379},
            {"host": "10.194.68.178", "port": 26379},
        ],
    }

    # ----------- 初始化客户端 -----------
    # 单节点客户端（使用默认序列化）
    client = RedisClient(standalone_config)
    # client = RedisClient(standalone_config)

    # 自定义序列化示例（使用pickle）
    # import pickle
    #
    # custom_client = RedisClient(
    #     standalone_config,
    #     value_serializer=pickle.dumps,
    #     value_deserializer=pickle.loads
    # )

    # ----------- 基本操作示例 -----------
    # 设置/获取值
    client.set("user:alice", {"name": "Alice", "age": 30}, ex=3600)
    user = client.get("user:alice")  # 返回反序列化的字典
    print('user:alice:', type(user), user)

    client.set("user_test", "这是一次测试", ex=60)
    print("user_test:", type(client.get("user_test")), client.get("user_test"))  # 输出: {'name': 'Alice', 'age': 30}

    # 分布式锁
    lock_id = client.acquire_lock("order_lock", timeout=5)
    if lock_id:
        try:
            # 执行业务逻辑
            print("获得锁，执行业务...")
            # time.sleep(20)
        finally:
            client.release_lock("order_lock", lock_id)
            print("释放锁")

    # 哈希表操作示例
    client.hset("user:map", "profile", {"email": "alice@example.com"})
    client.hset("user:map", "other", {"name": "alice", "age": 35})
    print("hget:", type(client.hget("user:map", "profile")),
          client.hget("user:map", "profile"))  # 输出: {'email': 'alice@example.com'}

    # client.hset("users", "user001", {"email": "alice@example.com"})
    # print("hset:",client.hget("users", "user001"))  # 输出: {'email': 'alice@example.com'}

    # ----------- 集合操作示例 -----------
    client.sadd("user_tags", "python", "redis", "database")
    tags = client.smembers("user_tags")  # 返回 {"python", "redis", "database"}
    print('user_tags:', type(tags), tags)

    # 集合操作示例
    client.sadd("user_tags", "python", "redis", "java")
    set = client.smembers("user_tags")
    print("user_tags", type(set), set)  # 输出: {'python', 'redis'}

    # 模糊查询示例
    client.set("user:item1", {"username": "sawyer", "age": 35}, ex=300)
    client.set("user:item2", {"username": "sawyerlsy", "age": 35})
    scan_result = client.scan_keys("user:*")
    print("scan_result:", type(scan_result), scan_result)  # 输出: ['cache:item1', 'cache:item2']

    #
    mapping_id = client.hget('VS:PARAM:HMMAP', '350148070A')
    print("mapping_id:", type(mapping_id), mapping_id)
    mapping = client.get(f"VS:PARAM:HM:{mapping_id}")
    print("mapping:", type(mapping), mapping)

    uid = uuid.uuid4()
    print('uuid4:', uid, uid.hex, str(uid).replace("-", ""))
