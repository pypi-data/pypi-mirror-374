

import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from decorators.singleton import (
    singleton,
    Singleton,
    SingletonMeta,
    thread_safe_singleton
)



class TestSingletonDecorator:
    """测试 @singleton 装饰器"""
    
    def test_singleton_basic_functionality(self):
        """测试基本单例功能"""
        @singleton
        class TestClass:
            def __init__(self):
                self.value = "test"
        
        instance1 = TestClass()
        instance2 = TestClass()
        
        assert instance1 is instance2
        assert instance1.value == "test"
        assert instance2.value == "test"
    
    def test_singleton_with_parameters(self):
        """测试带参数的单例类"""
        @singleton
        class TestClassWithParams:
            def __init__(self, name="default"):
                self.name = name
                self.counter = 0
        
        # 第一次创建时传入参数
        instance1 = TestClassWithParams("first")
        assert instance1.name == "first"
        
        # 第二次创建时参数被忽略，返回同一实例
        instance2 = TestClassWithParams("second")
        assert instance2.name == "first"  # 仍然是第一次的参数
        assert instance1 is instance2
    
    def test_singleton_thread_safety(self):
        """测试单例的线程安全性"""
        @singleton
        class ThreadSafeClass:
            def __init__(self):
                self.creation_time = time.time()
                time.sleep(0.01)  # 模拟初始化耗时
        
        instances = []
        
        def create_instance():
            return ThreadSafeClass()
        
        # 使用多线程同时创建实例
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_instance) for _ in range(10)]
            for future in as_completed(futures):
                instances.append(future.result())
        
        # 所有实例应该是同一个对象
        first_instance = instances[0]
        for instance in instances[1:]:
            assert instance is first_instance


tsd=TestSingletonDecorator()
tsd.test_singleton_basic_functionality()
tsd.test_singleton_with_parameters()
tsd.test_singleton_thread_safety()






class TestSingletonMeta:
    """测试 SingletonMeta 元类"""
    
    def test_singleton_meta_basic(self):
        """测试元类基本功能"""
        class TestClass(metaclass=SingletonMeta):
            def __init__(self):
                self.value = "meta_test"
        
        instance1 = TestClass()
        instance2 = TestClass()
        
        assert instance1 is instance2
        assert instance1.value == "meta_test"
    
    def test_singleton_meta_inheritance(self):
        """测试元类继承"""
        class BaseClass(metaclass=SingletonMeta):
            def __init__(self):
                self.base_value = "base"
        
        class DerivedClass(BaseClass):
            def __init__(self):
                super().__init__()
                self.derived_value = "derived"
        
        base1 = BaseClass()
        base2 = BaseClass()
        derived1 = DerivedClass()
        derived2 = DerivedClass()
        
        # 同一类的实例应该相同
        assert base1 is base2
        assert derived1 is derived2
        
        # 不同类的实例应该不同
        assert base1 is not derived1
    
    def test_singleton_meta_reset(self):
        """测试重置所有实例"""
        class TestClass(metaclass=SingletonMeta):
            def __init__(self):
                self.value = "test"
        
        instance1 = TestClass()
        
        # 重置所有实例
        SingletonMeta.reset_all_instances()
        
        # 重置后创建新实例
        instance2 = TestClass()
        
        # 应该是不同的实例
        assert instance1 is not instance2
    
    def test_singleton_meta_instance_info(self):
        """测试获取实例信息"""
        class TestClass1(metaclass=SingletonMeta):
            pass
        
        class TestClass2(metaclass=SingletonMeta):
            pass
        
        # 清理之前的实例
        SingletonMeta.reset_all_instances()
        
        instance1 = TestClass1()
        instance2 = TestClass2()
        
        info = SingletonMeta.get_instance_info()
        
        assert "TestClass1" in info
        assert "TestClass2" in info
        assert info["TestClass1"] == id(instance1)
        assert info["TestClass2"] == id(instance2)


class TestSingletonDecorator2:
    """测试 @Singleton 装饰器"""
    
    def test_singleton_decorator_basic(self):
        """测试装饰器基本功能"""
        @Singleton
        class TestClass:
            def __init__(self):
                if hasattr(self, '_initialized'):
                    return
                self._initialized = True
                self.value = "base_test"
        
        instance1 = TestClass()
        instance2 = TestClass()
        
        assert instance1 is instance2
        assert instance1.value == "base_test"
    
    def test_singleton_decorator_with_reset(self):
        """测试装饰器重置功能"""
        @Singleton
        class TestClass:
            def __init__(self):
                if hasattr(self, '_initialized'):
                    return
                self._initialized = True
                self.value = "test"
        
        instance1 = TestClass()
        
        # 重置实例
        TestClass.reset_instance()
        
        # 创建新实例
        instance2 = TestClass()
        
        # 应该是不同的实例
        assert instance1 is not instance2
        assert TestClass.get_instance_count() == 1


tsb=TestSingletonDecorator2()
tsb.test_singleton_decorator_basic()  # 现在使用装饰器语法
tsb.test_singleton_decorator_with_reset()  







class TestThreadSafeSingleton:
    """测试 thread_safe_singleton 装饰器"""
    
    def test_thread_safe_singleton_basic(self):
        """测试基本功能"""
        @thread_safe_singleton
        class TestClass:
            def __init__(self):
                self.value = "thread_safe"
        
        instance1 = TestClass()
        instance2 = TestClass()
        
        assert instance1 is instance2
        assert instance1.value == "thread_safe"
    
    def test_thread_safe_singleton_reset(self):
        """测试重置实例功能"""
        @thread_safe_singleton
        class TestClass:
            def __init__(self):
                self.value = "test"
        
        instance1 = TestClass()
        
        # 重置实例
        TestClass.reset_instance()
        
        # 创建新实例
        instance2 = TestClass()
        
        # 应该是不同的实例
        assert instance1 is not instance2
    
    def test_thread_safe_singleton_instance_count(self):
        """测试实例计数功能"""
        @thread_safe_singleton
        class TestClass:
            def __init__(self):
                self.value = "test"
        
        # 初始时没有实例
        assert TestClass.get_instance_count() == 0
        
        # 创建实例后计数为1
        instance = TestClass()
        assert TestClass.get_instance_count() == 1
        
        # 再次获取实例，计数仍为1
        instance2 = TestClass()
        assert TestClass.get_instance_count() == 1
        assert instance is instance2
    
    def test_thread_safe_singleton_concurrent_access(self):
        """测试并发访问的线程安全性"""
        @thread_safe_singleton
        class ConcurrentClass:
            def __init__(self):
                self.creation_thread = threading.current_thread().name
                self.creation_time = time.time()
                time.sleep(0.01)  # 模拟初始化耗时
        
        instances = []
        creation_times = []
        
        def create_instance():
            instance = ConcurrentClass()
            instances.append(instance)
            creation_times.append(instance.creation_time)
            return instance
        
        # 使用多线程并发创建
        threads = []
        for i in range(20):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)
        
        # 同时启动所有线程
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有实例都是同一个对象
        first_instance = instances[0]
        for instance in instances[1:]:
            assert instance is first_instance
        
        # 验证只创建了一次（所有创建时间应该相同）
        first_time = creation_times[0]
        for creation_time in creation_times[1:]:
            assert creation_time == first_time


class TestSingletonEdgeCases:
    """测试单例模式的边界情况"""
    
    def test_singleton_with_exception_in_init(self):
        """测试初始化时抛出异常的情况"""
        @singleton
        class ExceptionClass:
            def __init__(self):
                raise ValueError("Initialization failed")
        
        # 第一次创建应该抛出异常
        with pytest.raises(ValueError):
            ExceptionClass()
        
        # 第二次创建也应该抛出异常（因为没有成功创建实例）
        with pytest.raises(ValueError):
            ExceptionClass()
    
    def test_singleton_with_different_decorators(self):
        """测试不同单例装饰器的独立性"""
        @singleton
        class SingletonClass:
            def __init__(self):
                self.type = "singleton"
        
        @thread_safe_singleton
        class ThreadSafeClass:
            def __init__(self):
                self.type = "thread_safe"
        
        class MetaClass(metaclass=SingletonMeta):
            def __init__(self):
                self.type = "meta"
        
        s1 = SingletonClass()
        s2 = SingletonClass()
        t1 = ThreadSafeClass()
        t2 = ThreadSafeClass()
        m1 = MetaClass()
        m2 = MetaClass()
        
        # 同类型的实例应该相同
        assert s1 is s2
        assert t1 is t2
        assert m1 is m2
        
        # 不同类型的实例应该不同
        assert s1 is not t1
        assert s1 is not m1
        assert t1 is not m1
    
    def test_singleton_attribute_modification(self):
        """测试单例实例属性修改"""
        @singleton
        class ModifiableClass:
            def __init__(self):
                self.counter = 0
            
            def increment(self):
                self.counter += 1
        
        instance1 = ModifiableClass()
        instance2 = ModifiableClass()
        
        # 修改一个实例的属性
        instance1.increment()
        
        # 另一个实例应该看到相同的变化
        assert instance2.counter == 1
        assert instance1.counter == instance2.counter


# 性能测试
class TestSingletonPerformance:
    """单例模式性能测试"""
    
    def test_singleton_creation_performance(self):
        """测试单例创建性能"""
        @singleton
        class PerformanceClass:
            def __init__(self):
                self.value = "performance_test"
        
        # 第一次创建（实际初始化）
        start_time = time.time()
        instance1 = PerformanceClass()
        first_creation_time = time.time() - start_time
        
        # 后续创建（直接返回现有实例）
        start_time = time.time()
        for _ in range(1000):
            instance = PerformanceClass()
            assert instance is instance1
        subsequent_creation_time = time.time() - start_time
        
        # 后续创建应该比第一次创建快很多
        assert subsequent_creation_time < first_creation_time * 10


