from datetime import datetime
from typing import List
import os
import yaml
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from utils import get_log, get_now
from kube_apply import fromYaml
import kubernetes as k8s
from k8s_tools import get_pod_and_container_rand
import random
import json

CHAOS_ACTIONS = {'cpu': ['fullload']}
CHAOS_PARAM = {}



class Chaos:
    """
    
    status:
     + 测试完成
    
    """    
    
    def __init__(self, _name, _scope, _target, _actions, _param, _k8s_params) -> None:
        self.name = _name
        self.scope = _scope  # 粒度
        self.target = _target  # 目标
        self.actions = _actions  # 测试项目
        self.desc = ''  #
        self.params = _param  # 异常的参数
        self.k8s_param = _k8s_params  # container-ids, namespace, pod-names
    
    def to_json(self) -> str:
        
        obj_dict = {
            "name"      : self.name       ,
            "scope"     : self.scope      ,
            "target"    : self.target     ,
            "actions"   : self.actions    ,
            "desc"      : self.desc       ,
            "params"    : self.params     ,
            "k8s_param" : self.k8s_param  
        }
        return json.dumps(obj_dict)
        
    def to_k8s_yaml(self) -> str:
        """
        主要功能是通过Chaos对象生成k8s所需要的yaml文件
        
        Returns
        -------
        str
            K8S_yaml raw file
        """        
        # 固定部分
        k8s_yaml = {}
        k8s_yaml['apiVersion'] = 'chaosblade.io/v1alpha1'
        k8s_yaml['kind'] = 'ChaosBlade'
        k8s_yaml['metadata'] = {'name': self.name}
        k8s_yaml['spec'] = {}
        
        # 可变部分
        k8s_yaml['spec']['experiments'] = []
        
        # 比较容易的
        experiment = {
            'scope': self.scope,
            'target': self.target,
            'action': self.actions,
            'desc': self.desc,
            'matchers': []
        }
        
        k8s_yaml['spec']['experiments'].append(experiment)
        
        # 对详细参数进行重构
        experiment['matchers']  # 向这里append
        
        # 目标容器的位置
        for name, value in self.k8s_param.items():
            experiment['matchers'].append({'name': name, 'value': [value]}) 
        # # namespace
        # experiment['matchers'].append({'name': 'namespace', 'value': [self.k8s_param['namespace']]}) 
        # # pod
        # experiment['matchers'].append({'name': 'names', 'value': [self.k8s_param['pod']]}) 
        # # container
        # experiment['matchers'].append({'name': 'container-ids', 'value': [self.k8s_param['container-ids']]}) 
        
        # 下面的具体的异常参数
        for name, value in self.params.items():
            experiment['matchers'].append({'name': name, 'value': [value]}) 
        
        return yaml.dump(k8s_yaml)
    
    @staticmethod
    def random_get_chaos(name: str, kinds: List[str], duration: int, v1client):
        
        scope = 'container'
        target = random.choice(kinds)
        actions = random.choice(CHAOS_ACTIONS[target]) # 随机选择一种target的一种actions
        params = {}
        k8s_param = {}
        k8s_param['names'], k8s_param['container_ids'] = get_pod_and_container_rand('sock-shop', v1client)
        k8s_param['namespace'] = 'sock-shop'
        params = {'cpu-percent': '100', 'waiting-time': f'{duration}m'}
        return Chaos(name, scope, target, actions, params, k8s_param)

class Record:
    """[summary]
    TO-DO:
        - [x] 实现一个类似于logger一样一行一行持续写如的类
    status：
        正在测试
    """    
    def __init__(self, file_path) -> None:
        self.fp = open(file_path, 'w', encoding='utf-8')
        # self.fp.writelines("[")
        
    def record(self, date:datetime,  chaos):
        json_record = {
            'datetime': str(date),
            'chaos': chaos.to_json()}
        self.fp.write(f"{json.dumps(json_record)}\n")
        self.fp.flush()   # 刷新缓冲区
    
    def close(self):
        self.fp.close()

class AnomalyScheduler:
    
    def __init__(self, args) -> None:
        self.config =  AnomalyScheduler.parse_config(args.config_file)
        self.logger = get_log("anomaly_schedule", args.log_name, log_dir=args.log_dir)  # 初始化log
        self.schedulers = BlockingScheduler()
        # 初始化异常参数
        self.anomaly_nums = self.config['anomaly_nums']
        self.interval_time = self.config['interval_time']  # 单位是分钟
        self.interval_time_rand_gas = self.config['interval_time_rand_gas']  # 也是分钟
        self.interval_kinds = self.config['anomaly_kinds']
        self.anomaly_time = self.config['anomaly_time']   # 异常持续时间
        self.anomaly_time_gas = self.config['anomaly_time_gas']  # 异常持续时间随机变动
        
        # 记录的位置
        self.record_path = self.config['record_file_path']
        self.record = Record(self.record_path)
        
        self.job_name = "AnomalyScheduler"
        # self.__init_schedulers()
        
        # k8s client obj
        self.k8s_client = k8s.config.new_client_from_config(config_file="./config")
        self.k8s_v1 = k8s.client.CoreV1Api(self.k8s_client)
        
        
    def __init_schedulers(self):
        pass
            # self.logger
        
    
    def jobs(self):
        """
        目标是一个迭代的jobs，从产生每一次运行完毕后都会，从任务队列中选取新的jobs，当认为队列中没有新的时候则直接结束。
        """
        count = 1  # 异常计数器
        def job():
            nonlocal count  # 修改闭包的变量
            if count != 1:
                self.schedulers.remove_job(self.job_name)  # 先删除
            anomaly_duration = self.__get_next_duration(self.anomaly_time, self.anomaly_time_gas)
            
            # 创建异常对象
            chaos = Chaos.random_get_chaos(f"chaos_{count}", self.interval_kinds, anomaly_duration, self.k8s_v1)
            
            # 得到raw_yaml
            error_yaml_raw_data = chaos.to_k8s_yaml()
            
            # 注入开始
            begin_time = datetime.now()
            fromYaml(error_yaml_raw_data, client=self.k8s_client)
            self.logger.info(f"第{count}个异常开始注入!, 异常的种类为： {chaos.target}-{chaos.actions}-{chaos.k8s_param['names']} 注入异常的时间为: {str(begin_time)}, 持续时间为{anomaly_duration}min!")
            
            # 写入记录
            self.record.record(begin_time, chaos)
            
            # 下一次异常注入
            next_duration = self.__get_next_duration(self.anomaly_time, self.anomaly_time_gas)
        
            if count < self.anomaly_nums:
                self.schedulers.add_job(job, "interval", minutes=next_duration, id=self.job_name)
            else:
                # 结束
                try:
                    self.scheduler.remove_job(self.job_name)  # 先删除
                except Exception:
                    return
            count+=1
        
        # 开始
        time.sleep(60) # 前十分钟没有异常
        # time.sleep(60*10) # 前十分钟没有异常
        print("开始")
        self.logger.info("开始第一个异常!!!!")
        job()
                
    def __get_next_duration(self, base_time, rand_gas):
        return random.randint(-rand_gas, rand_gas) + base_time      
    
    def start(self) -> None:
        self.jobs()
        self.schedulers.start()
            
    @staticmethod
    def parse_config(path: str):
        """解析具体的config文件

        Parameters
        ----------
        path : str
            配置文件的路径

        Raises
        ------
        FileExistsError/home/luyan/anaconda3/lib/python3.7/site-packages/apscheduler/executors/base.py
            如果文件路径错误，会报错
        """        
        if not os.path.exists(path):
            raise FileExistsError("config的路径不存在，或者路径错误！")
        # print(os.path.splitext(path))
        if os.path.splitext(path)[-1][1:] not in ["yaml", "yml"]:
            raise FileExistsError("文件的格式错误！")
        
        with open(path, "r") as f:
            obj = yaml.load(f)
        
        return obj