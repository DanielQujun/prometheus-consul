## 什么是consul
consul支持服务动态发现，客户端可注册服务，通过DNS或HTTP协议发现服务;支持健康状态检查，检查对象可以是service或者是节点;支持Mtls双向加密，为服务创建和分发证书;支持作为kV存储，用于动态配置管理、选举配置等;支持多数据中心;支持暴露xDS协议，使用内置proxy或外部proxy实现流量控制。
### 工作模式

![image](https://www.consul.io/img/consul-arch.png)
consul有两种工作模式: server、client
server: 负责持久化数据存储，server之间采取了一致性协议，推荐三或五个节点，性能会随着节点数增加而下降。server同时也具备agent的功能。一个datacent的server之间选举出一个leader节点，leader会负责处理所有查询及事务，非leader节点接收到rpc请求会转给leader进行处理。
agent(client): 负责对service的健康检查、通过gossip协议发现集群内的服务、作为消息层传递重要消息，如leader选举、缓存从server接收到的数据，如Connect certificates和intentions，这时候通过agent的api查询速度会更快，即便server挂掉能获取结果，增加了一定的可用性。

### 基本概念说明:
* node: 在consul中注册的节点，节点可关联多个service
* service: 一个具体的应用服务

## prometheus动态发现示例
```
global:
  evaluation_interval: 1m
  scrape_interval: 30s
  scrape_timeout: 5s
rule_files:
scrape_configs:
  - job_name: 'consul'
    consul_sd_configs:
    - server: 10.102.176.239
    relabel_configs:  // 为采集的metrics添加node_ip的标签
    - source_labels: ['__address__']
      action: 'replace'
      target_label: 'node_ip'
      separator: ';'
      regex: '(.+)(?::\d+)'
      replacement: '$1'
    - source_labels: ['__meta_consul_service']  // 根据service名称来动态生成job名
      action: 'replace'
      target_label: 'job'
      separator: ';'
      regex: '(.*)'
      replacement: '$1'
```

## 详细配置
### 在consul中注册prometheus的target
1. 注册service可以通过[catalog](hhttps://www.consul.io/api-docs/catalog)或者[agent](https://www.consul.io/api-docs/agent/service)的api接口，外部服务通过consul的catalog接口注册，不要使用agent api，因为不太可能每个监控节点上了启动了consul的agent。所以下面的注册body中显式的定义了address字段。
```
{
  "Node": "192.168.0.192", // 注册的node名称
  "Address": "192.168.0.192",  // 注册的node地址
  "NodeMeta": {  // nodeMeta元数据信息，目前来看只有标记作用
    "external-node": "true",
    "external-probe": "true"
  },
  "Service": { // 注册service
    "ID": "node_exporter-192.168.0.192",  // service的唯一ID
    "Service": "node_exporter",  // service的名称，一个service名称下可以有多个service实例
    "Tags": ["node_exporter", "prometheus"], // 给service打tag
    "Port": 9100 // service的端口
  },
  // 此node的健康状态检查
  "Checks": [
    {
      "Name": "http-check",
      "status": "passing",
      "Definition": {
        "http": "http://192.168.0.192:9100",
        "interval": "30s"
      }
    }
  ]
}
```
将上面的内容保存为node-exporter.json,执行注册命令:
```
10.102.176.239为consul集群中任意地址，8500为其管理端口
curl -vv -X PUT --data @node-exporter.json http://10.102.176.239:8500/v1/catalog/register
```

### prometheus中配置动态发现
```
global:
  evaluation_interval: 1m
  scrape_interval: 30s
  scrape_timeout: 5s
rule_files:
scrape_configs:
  - job_name: 'node-exporter' 
    consul_sd_configs:
    - server: 10.102.176.239
      services: ["node-exporter"]  // 采用了services名称来过滤服务，不同的服务用不同的job，方便定制化配置
    relabel_configs:
    - source_labels: ['__address__']
      action: 'replace'
      target_label: 'node_ip'
      separator: ';'
      regex: '(.+)(?::\d+)'
      replacement: '$1'

```

### 删除某个服务
删除服务可以分为几种方式:
* 直接将node删除，则此node下的所有服务都被删除，需要小心使用。
```
curl -vv -X PUT -d '{"Datacenter": "dc1", "Node": "192.168.0.220"}'\
 http://10.97.245.71/v1/catalog/deregister
```
* 删除某个node上的service
```
curl -vv -X PUT -d '{"Datacenter": "dc1", "ServiceID": "web", "Node": "192.168.0.220"}' \
http://10.97.245.71/v1/catalog/deregister
```

* 删除通过agent接口注册的service
```
curl -v -X PUT -d'{"ServiceID": "web", "Node": "prometheus-consul-server-2", "Datacenter": "dc1"}'  \
192.178.80.47:8500/v1/catalog/deregister
```


## _metadata字段说明
* __meta_consul_address: the address of the target
* __meta_consul_dc: the datacenter name for the target
* __meta_consul_health: the health status of the service
* \_\_meta_consul_metadata_\<key\>: each node metadata key value of the target
* __meta_consul_node: the node name defined for the target
* __meta_consul_service_address: the service address of the target
* __meta_consul_service_id: the service ID of the target
* \_\_meta_consul_service_metadata_\<key>: each service metadata key value of the target
* __meta_consul_service_port: the service port of the target
* __meta_consul_service: the name of the service the target belongs to
* \_\_meta_consul_tagged_address_\<key>: each node tagged address key value of the target
* __meta_consul_tags: the list of tags of the target joined by the tag separator

## 补充说明
1. consul挂掉之后,prometheus的动态发现失效，target也随之停止，三个consul节点最多只能挂掉1个，否则将不能正常提供服务。
2. prometheus里面配置了job，但是如果没有发现到target，则prometheus页面上不会显示这个job，只能从配置文件里看。
3. dns解析
```
# 解析node
dig @10.102.88.150 192.168.0.191.node.dc1.consul

# 解析service
dig @10.102.88.150 web.service.dc1.consul

```
