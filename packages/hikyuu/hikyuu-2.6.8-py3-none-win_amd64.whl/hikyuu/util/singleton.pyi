from __future__ import annotations
import _thread
import threading as threading
import typing
__all__ = ['SingletonType', 'threading']
class SingletonType(type):
    """
    基于 metalclass 实现单例
    
    示例：
    class MyClass(metaclass=SingletonType):
        def __init__(self,name):
            self.name = name
    """
    __firstlineno__: typing.ClassVar[int] = 13
    __static_attributes__: typing.ClassVar[tuple] = tuple()
    _instance_lock: typing.ClassVar[_thread.lock]  # value = <unlocked _thread.lock object at 0x0000020A83F47880>
    @classmethod
    def __call__(cls, *args, **kwargs):
        ...
