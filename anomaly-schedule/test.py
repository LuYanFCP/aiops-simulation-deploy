from datetime import datetime
from io import SEEK_CUR
from unittest.main import main
import kubernetes as k8s
import unittest
from pkg_resources import get_provider
from pytz import country_timezones
# from .kube_apply import fromYaml, runUsageExample
import yaml
from anomaly_tools import Chaos, Record
from k8s_tools import get_pod_and_container_rand
class AnomalySchedulerTest(unittest.TestCase):
    # def __init__(self) -> None:
        
    
    def test_utils_k8s_apply_and_delete(self):
        config.load_kube_config("./config")
        # self.v1 = client.CoreV1Api()
        self.client = config.new_client_from_config(config_file="./config")
        runUsageExample(self.client)
        self.client.close()
    

# 测试Chaos

class ChaosTest(unittest.TestCase):
    
    def test_to_yaml(self):
        with open("test_chaos.yaml") as f:
            obj = yaml.load(f)
        print(obj)
        param = {'cpu-percent': '100'}
        k8s_param = {
                     'namespace'     : 'default', 
                     'names'           : 'carts-db-55fd8499f6-qnbjs', 
                     'container-ids' : '12389aeabc197090a60beb0a66c5e723032f714f8bd893198690eae60c1f2796'
                    }
        chaos = Chaos("test", 'container', 'cpu', 'fullload', param, k8s_param)
        print(chaos.to_k8s_yaml())
        func_obj = yaml.load(chaos.to_k8s_yaml())
        print(func_obj)
        print(obj == func_obj)
    
    def test_rand_chaos(self):
        k8s_client = k8s.config.new_client_from_config(config_file="./config")
        k8s_v1 = k8s.client.CoreV1Api(k8s_client)
        r = Record("./res.log")
        count = 10
        while count:
            chaos = Chaos.random_get_chaos("test", ['cpu'], 10, k8s_v1)        
            r.record(datetime.now(), chaos)
            count-=1
        r.close()

# 测试k8s_tool

class K8S_ToolTest(unittest.TestCase):
    def test_get_pod_rand(self):
        k8s_client = k8s.config.new_client_from_config(config_file="./config")
        k8s_v1 = k8s.client.CoreV1Api(k8s_client)
        print(get_pod_and_container_rand("sock-shop", k8s_v1))

if __name__ == '__main__':
    unittest.main()