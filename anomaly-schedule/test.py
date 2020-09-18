from io import SEEK_CUR
from kubernetes import client, config
import unittest
from kube_apply import fromYaml, runUsageExample


class AnomalySchedulerTest(unittest.TestCase):
    # def __init__(self) -> None:
        
    
    def test_utils_k8s_apply_and_delete(self):
        config.load_kube_config("./config")
        # self.v1 = client.CoreV1Api()
        self.client = config.new_client_from_config(config_file="./config")
        runUsageExample(self.client)
        self.client.close()