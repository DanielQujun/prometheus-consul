from consul import consul
import sys
import prometheus
import os

pwd_path = os.path.abspath(os.path.dirname(__file__))

consul_url = "http://192.168.0.78:31000"

prometheus_config_path = os.path.join(pwd_path, "./prometheus-config")
prometheus_yaml_path = os.path.join(pwd_path, "./prometheus-config/prometheus.yaml")
prometheus_configmap_name = "steamer-prometheus-master-config"

if __name__ == '__main__':
    jobname= sys.argv[1]
    node_address = sys.argv[2]
    target_port = sys.argv[3]
    consul.add_service(consul_url, jobname, node_address, target_port)
    if prometheus.check_job_exist(prometheus_yaml_path, jobname):
        print("prometheus configmap does not  neeed update!")
    else:
        print("going to update prometheus configmap!")
        prometheus.update_prometheus_yaml(consul_url, prometheus_yaml_path, jobname)
        prometheus.update_configmap(prometheus_config_path, prometheus_yaml_path, prometheus_configmap_name)
