import asyncio
import threading

class AsyncThread(threading.Thread):
    def __init__(self, async_func, *args, **kwargs):
        """
        初始化异步线程
        :param async_func: 需要执行的异步方法
        :param args: 传递给异步方法的位置参数
        :param kwargs: 传递给异步方法的关键字参数
        """
        super().__init__()
        self.async_func = async_func
        self.args = args
        self.kwargs = kwargs
        self.loop = asyncio.new_event_loop()  # 为该线程创建独立的事件循环

    def run(self):
        """在线程中运行异步方法"""
        asyncio.set_event_loop(self.loop)  # 绑定事件循环到当前线程
        self.loop.run_until_complete(self.async_func(*self.args, **self.kwargs))
        self.loop.close()