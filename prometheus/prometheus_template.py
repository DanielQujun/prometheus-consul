#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: qujun
# datetime:9/27/21 11:41 AM
import yaml
import datetime
import subprocess

prometheus_job = """
job_name: '{job_name}'
consul_sd_configs:
- server: {consul_url}
  services: ["{job_name}"]
relabel_configs:
- source_labels: ['__address__']
  action: 'replace'
  target_label: 'node_ip'
  separator: ';'
  regex: '(.+)(?::\d+)'
  replacement: '$1'
"""


class Prometheus:
    def __init__(self, config_dir, file_path, prometheus_configmap_name, consul_fqdn="prometheus-consul-server.consul:8500"):
        self.config_dir = config_dir
        self.file_path = file_path
        self.prometheus_configmap_name = prometheus_configmap_name
        self.consul_fqdn = consul_fqdn

    def check_job_exist_from_cm(self, job_name):
        get_cm = "kubectl get cm {configmapname} -n kube-system -o yaml ". \
            format(configmapname=self.prometheus_configmap_name)
        ret = subprocess.run(get_cm,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",timeout=5)
        if ret.returncode == 0:
            prometheus_cm_yaml = yaml.load(ret.stdout, Loader=yaml.FullLoader)
            prometheus_file_yaml = yaml.load(prometheus_cm_yaml["data"]["prometheus.yaml"], Loader=yaml.FullLoader)
            for job in prometheus_file_yaml["scrape_configs"]:
                if job["job_name"] == job_name:
                    return True
        else:
            print("error:", ret)
            return False

    def add_job_to_prometheus_yaml(self, prometheus_file_yaml, job_name):
        job = prometheus_job.format(consul_url=self.consul_fqdn, job_name=job_name)

        prometheus_file_yaml["scrape_configs"].append(yaml.load(job, Loader=yaml.FullLoader))
        return yaml.dump(prometheus_file_yaml, sort_keys=True, default_flow_style=False)

    def del_job_from_prometheus_yaml(self, prometheus_file_yaml, job_name):
        job_inx = -1

        for idx in range(len(prometheus_file_yaml["scrape_configs"])):
            if prometheus_file_yaml["scrape_configs"][idx]["job_name"] == job_name:
                print("find job %s in prometheus file" % job_name)
                job_inx = idx

        if job_inx != -1:
            del prometheus_file_yaml["scrape_configs"][job_inx]
        else:
            print("job %s not exist in prometheus file!")
            return ""

        return yaml.dump(prometheus_file_yaml, sort_keys=True, default_flow_style=False)

    def update_configmap(self, op, job_name):
        now = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
        old_cm_file = "{prometheus_config_path}/{configmapname}-{time}.yaml". \
                        format(prometheus_config_path=self.config_dir,
                                                  configmapname=self.prometheus_configmap_name, time=now)

        new_cm_file = "{prometheus_config_path}/{configmapname}-new.yaml". \
            format(prometheus_config_path=self.config_dir,configmapname=self.prometheus_configmap_name)

        save_old_cm = "kubectl get cm {configmapname} -n kube-system -o yaml >{old_cm_file}". \
            format(old_cm_file=old_cm_file,
                   configmapname=self.prometheus_configmap_name)
        ret = subprocess.run(save_old_cm,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",timeout=5)
        if ret.returncode == 0:
            print("success:", ret)
        else:
            print("error:", ret)
            return
        with open(old_cm_file, "r") as f:
            prometheus_cm_yaml = yaml.load(f, Loader=yaml.FullLoader)
        prometheus_file_yaml = yaml.load(prometheus_cm_yaml["data"]["prometheus.yaml"], Loader=yaml.FullLoader)
        if op == "add":
            prometheus_file_yaml_string = self.add_job_to_prometheus_yaml(prometheus_file_yaml, job_name)
        elif op == "del":
            prometheus_file_yaml_string = self.del_job_from_prometheus_yaml(prometheus_file_yaml, job_name)
        else:
            print("bad operation for prometheus cm!")
            return
        prometheus_cm_yaml["data"]["prometheus.yaml"] = prometheus_file_yaml_string

        # remove resourceVersion and last-applied-configuration
        if prometheus_cm_yaml.get("metadata") and prometheus_cm_yaml["metadata"].get("annotations") and \
           prometheus_cm_yaml["metadata"]["annotations"].get("kubectl.kubernetes.io/last-applied-configuration"):
            del prometheus_cm_yaml["metadata"]["annotations"]["kubectl.kubernetes.io/last-applied-configuration"]

        del prometheus_cm_yaml["metadata"]["resourceVersion"]

        with open(new_cm_file, "w") as f:
            yaml.dump(prometheus_cm_yaml, f, sort_keys=True, default_flow_style=False)

        update_cmd = "kubectl apply -n kube-system -f {new_cm_file}".format(new_cm_file=new_cm_file)
        ret = subprocess.run(update_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", timeout=5)
        if ret.returncode == 0:
            print("success:",ret)
        else:
            print("error:",ret)
            return


if __name__ == "__main__":
    job_name = "node-exporter"
    p = Prometheus("prometheus/prometheus.yaml")
