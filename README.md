# ConsulProme
This tool helps people who run Prometheus with consul for dynamic discovery services runs outside Kubernetes.
we can execute it in Shell or deploy it in Kubernetes as you want. It goes support add/list/delete service and node in consul, add/delete job in [prometheus-config-style
configmap](deploy/prometheus/master.yaml).

## Why
As a cloud-native monitor service Prometheus has become ubiquitous,
However, there are still a lot of systems that run in non-cloud need to be monitored.

This is the role for `consul_sd_configs` which makes Prometheus dynamic discovery the services registered in
consul. The `file_sd_configs` should take into consideration, but it's not suitable for large-scale services.

On the other side, there are few blogs or tutorial to guides us to run best practice, furthermore,
it's not convenience for Operations Engineers to operator the consul's api directly. So I write this little tool
try to make our work more efficiently.

## background
[中文](docs/prometheus-with-consul.md)

## TODO
- [ ] replace kubectl to python requests.