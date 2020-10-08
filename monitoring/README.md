# monitoring 部分

## monitor核心部分

这里直接使用了[microservices-demo/deploy](https://github.com/microservices-demo/microservices-demo/tree/master/deploy/kubernetes/manifests-monitoring)的部分，在这个基础上主要是将`app/v1beta`更换为`app/v1`的

主要目标是监控部分的内容，核心是`prometheus`。使用`prometheus`作为收集数据的部分，而`grafana`是一个可视化展示各个指标。

在原来的基础上增加的内容

监控增加

+ 使用`cadvisor`对所有的节点的container进行监控。
+ 增加的对所有节点的`Node-exporter`的部署和监控。

修改的小部分

+ 很多插件更换为国内的源或者dockerhub的源。
+ 部分容器修改了部分的权限问题，比如prometheus的权限问题，增加prometheus对kubectl的`cadvisor`部分的权限。

## usage

```bash
cd monitoring
kubectl apply -f ./
```

得到如下的场景

```bash
kubectl get pod -n monitoring
-----
NAME                                            READY   STATUS    RESTARTS   AGE
kube-state-metrics-deployment-88db6c85b-88dfh   1/1     Running   0          3m19s
node-directory-size-metrics-45gvt               2/2     Running   0          7m46s
node-directory-size-metrics-ghrgb               2/2     Running   0          7m45s
node-directory-size-metrics-lw4p8               2/2     Running   0          7m45s
node-exporter-68cpp                             1/1     Running   0          7m47s
node-exporter-f7vtv                             1/1     Running   0          7m47s
node-exporter-tphht                             1/1     Running   0          7m47s
node-exporter-z86q8                             1/1     Running   0          7m47s
prometheus-deployment-7c748db586-68ddf          1/1     Running   0          12s
```

即为成功。

### grafana

#### 使用旧版grafana

```bash
kubectl apply -f grafana
```

#### 使用最新版grafana

```bash
kubectl apply -f grafana-lastest
```

但是最新版本一直无法适配之前的`dashboard json`

可以手动载入`monitoring/grafana-latest/sock-shop-config`中的配置。

更多监控可以使用

## 更新日志

### 10.7更新

+ 更新 prometheus的版本
+ 更新了 grafana版本

### 10.8更新

增加grafana latest版本的适配。`monitoring/grafana-latest`

## BUG修复日志

### 10.7 无法部署

1. 修改了`Node-Exporter`的问题

```log
Error from server (BadRequest): error when creating "Node-exporter.yaml": DaemonSet in version "v1" cannot be handled as a DaemonSet: v1.DaemonSet.Spec: v1.DaemonSetSpec.Template: v1.PodTemplateSpec.Spec: v1.PodSpec.HostIPC: Containers: []v1.Container: v1.Container.Resources: v1.ResourceRequirements.Requests: unmarshalerDecoder: quantities must match the regular expression '^([+-]?[0-9.]+)([eEinumkKMGTP]*[-+]?[0-9]*)$', error found in #10 byte of ...|onitoring"}}}],"host|..., bigger context ...|}],"resources":{"requests":{"cpu":"0.15monitoring"}}}],"hostIPC":true,"hostNetwork":true,"hostPID":t|...
```

问题： 资源 "resources":{"requests":{"cpu":"0.15monitoring"}}}] 这个限制不识别，`"cpu":"0.15monitoring"`这个当时打错了。后来考虑无所有限制CPU，因此就去掉了。

2. 修改了`prometheus`的配置问题

```log
time="2020-10-07T13:02:15Z" level=error msg="Error loading config: couldn't load configuration (-config.file=/etc/prometheus/prometheus.yml): unknown fields in scrape_config: job_name-" source="main.go:150" 
```

修正了手误添加`-`的bug

3. 修正了kube-state-dep中container的位置，去掉了`google`的源。

