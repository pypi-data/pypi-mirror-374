import threading


class SingletonMeta(type):
    """
    singleton meta class
    使用元类来实现单例模式。

    优点：
    简单易用，无需考虑多线程问题
    避免了复杂的初始化过程，保证了实例的唯一性

    缺点：
    没有接口，不能实现子类定制化

    适用场景：
    资源共享和状态一致性，如数据库连接池、线程池、缓存等
    频繁实例化的对象，如配置对象、日志对象、线程局部变量等

    实现原理:
    元类（metaclass）：在类创建时，解释器会自动调用元类，并将类的定义作为参数传入。

    特点:
    参数处理：自动传递初始化参数到首次实例化
    线程安全双重检查锁Dcl避免重复创建实例
    继承性所有使用该元类的子类自动成为单例

    使用方式：直接继承 SingletonMeta 即可，无需额外操作

    """

    # 所有使用 SingletonMeta 的类共享同一把锁，可能导致不相关的类实例化时产生不必要的锁竞争.改为使用init方法每个类独立锁
    # _instances = {}
    # _lock = threading.Lock()

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._instances = {}
        cls._lock = threading.Lock()  # 每个类独立锁

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
