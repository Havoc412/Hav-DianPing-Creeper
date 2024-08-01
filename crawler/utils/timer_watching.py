import threading
import time
from crawler.utils.notice import notice

def wait_operation():
    notice("任务超时！！！")
    # input("输入各种继续执行：")

class TimerWatch:
    def __init__(self):
        self.timer = None
        self.timeout_duration = 30  # 设置超时时间（秒）

    def start_timer(self):
        # 如果定时器已经存在，则取消它
        if self.timer is not None:
            self.timer.cancel()
            # print("Timer cancelled.")

        # 创建并启动新的定时器
        self.timer = threading.Timer(self.timeout_duration, wait_operation)
        self.timer.start()
        print(f"Timer started for {self.timeout_duration} seconds.")

    def stop_timer(self):
        if self.timer is not None:
            self.timer.cancel()
            print("Timer stopped.")
