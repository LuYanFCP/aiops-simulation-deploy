
import random
import kubernetes as k8s


def get_pod_and_container_rand(namespace: str, v1client: k8s.kubernetes.client.CoreV1Api):
    query_res = v1client.list_namespaced_pod(namespace)
    pod_container_list = [(i.metadata.name, i.status.container_statuses[0].container_id) for i in query_res.items]
    # pod = random.randint(0, len(pod_container_list))
    
    return random.choice(pod_container_list)
    
        
# # config.host = "http://localhost"

# print("Listing pods with their IPs:")
# # ret = v1.list_pod_for_all_namespaces(watch=False)
# # ret = v1.list_namespaced_pod("sock-shop", )
# # for i in ret.items:
# #     print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
# #     # print(i.__dict__)
# # # print(dir(ret.items[0].status.init_container_statuses))
# # print(ret.items[0].status.container_statuses[0].container_id)  # 这里到container_id
# # print(type(ret.items[0].status.container_statuses))   



