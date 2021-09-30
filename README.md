# ConsulProme
This tool helps people who run Prometheus with consul for dynamic discovery services runs outside Kubernetes.
It can be executed by the shell, and support add/list/delete service and node in consul, add/delete job in [prometheus-config-style
configmap](deploy/prometheus/master.yaml).

## Why
As a cloud-native monitor service Prometheus has become ubiquitous,
However, there are still a lot of systems that run in non-cloud need to be monitored.

This is the role for `consul_sd_configs` which makes Prometheus dynamic discovery the services registered in
consul. The `file_sd_configs` should take into consideration, but it's not suitable for large-scale services.


## TODO
- [ ] replace kubectl to python requests.