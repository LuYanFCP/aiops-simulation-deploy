from argparse import Action
from ast import parse
from os import sched_getscheduler, uname
from sys import implementation
import argparse
from anomaly_tools import AnomalyScheduler

# sched = BlockingScheduler()
# @sched.scheduled_job('cron', day_of_week='mon-fri', hour='0-23', minute='0-59', second='*/1')
# def count_second():
#     print("a second later!!! ->{}".format(str(datetime.datetime.fromtimestamp(time.time()))))

# sched.start()

def get_args():
    """
    输入参数
    """
    args_parse = argparse.ArgumentParser(description="异常注入的脚本")
    args_parse.add_argument("-f", "--config-file", help="配置脚本的位置，只支持格式yaml!", type=str)
    args_parse.add_argument("-o", "--output", help="输出文件的位置, 输出的格式为yaml!", type=str)
    args_parse.add_argument("--log-name", help="文件log的名称", type=str, default="")
    args_parse.add_argument("--log-dir", help="增加log_dir放置的位置！", type=str)
    return args_parse.parse_args()


def main():
    args = get_args()
    scheuler = AnomalyScheduler(args=args)
    scheuler.start()
    
if __name__ == "__main__":
    main()
    