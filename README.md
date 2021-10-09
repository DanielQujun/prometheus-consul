# ConsulProme
This tool helps people who run Prometheus with consul for dynamic discovery services that runs outside Kubernetes.
we can execute it in Shell or deploy it in Kubernetes as you want. It goes support add/list/delete service and node in consul, add/delete job in [prometheus-config-style
configmap](deploy/prometheus/master.yaml).

## Why
As a cloud-native monitor service Prometheus has become ubiquitous,
However, there are still a lot of systems that run in non-cloud need to be monitored.

This is the role for `consul_sd_configs` which makes Prometheus dynamic discovery the services registered in
consul. The `file_sd_configs` should take into consideration, but it's not suitable for large-scale services.

On the other side, there are few blogs or tutorial for the best practice, furthermore,
it's not convenience for Operations Engineers to interact with the consul's API directly. for making our work more efficiently, I write this little tool.

## Background
[中文](docs/prometheus-with-consul.md)

## Build
```angular2html
bash -x build.sh
```

## Run it 
### In kubernetes 
```angular2html
kubectl apply -f deploy/consulProme/consul-prome.yaml
```
### local
```
pip install requests pyyaml absl-py -i https://pypi.tuna.tsinghua.edu.cn/simple
export CONSUL_HTTP_ADDR=http://192.168.0.78:32087
python3 main.py --help
```
## Use it
### list nodes registered in consul 
```
python3 main.py --o list_node
```
### list nodes registered in consul for a specified service name
```
python3 main.py --o list_service --job node-exporter
```
### add service to consul
```
python3 main.py --o add_service --job cadvisor --ip 192.168.0.220 --port 4195
```
> --job defines service name and prometheus job name, if the job do not exist in prometheus, it will be added.

### del service from consul
```
python3 main.py --o del_service --job cadvisor --ip 192.168.0.220 --port 4195
```
> It won't delete job from prometheus, so you need update its config by manual or use del_job which describe below

### add job for prometheus
```
python3 main.py --o add_job --job cadvisor-xx
```

### delete job from prometheus
```
python3 main.py --o del_job --job cadvisor-xx
```

## TODO
- [ ] replace kubectl to python requests.