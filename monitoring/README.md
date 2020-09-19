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