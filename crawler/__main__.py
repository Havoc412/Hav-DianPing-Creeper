import threading

from crawler.core import application
from crawler.utils.notice import notice
import traceback

import datetime
import time

class DaZhongDianPing(application):
    def __init__(self, config_file, application):
        super().__init__(config_file, application)
        self.city_name = self.config["search_city"]["name"]  # 设定目标城市

        self.BACK_TASK = True  # 是否沿用上次的任务记录。


def main():
    # 爬取评论图片
    print("*****请注意更新Cookie和IP代理！！！*****")
    print("*****请注意更新Cookie和IP代理！！！*****")
    print("*****请注意登录官网，避免美团人机识别！！！*****")
    print("*****请注意登录官网，避免美团人机识别！！！*****")
    dianping = DaZhongDianPing(config_file="config/config.yaml", application="dazhongdianping")

    lastTime = datetime.datetime.now()

    try:
        dianping.crawl()
    except Exception as e:
        endTime = datetime.datetime.now()
        execution_time = endTime - lastTime
        execution_time_minutes = execution_time.total_seconds() / 60

        if execution_time_minutes > 2:
            notice(str(e) + "\n五分钟后将自动重启...")
            threading.Timer(5 * 60, main)
        else:
            # 打印完整的错误信息到控制台
            traceback.print_exc()
            notice(str(e) + "\n且短时间内意外中止，程序暂停。")



if __name__ == "__main__":
    main()


    