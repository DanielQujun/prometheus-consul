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
    def __init__(self, consul_url, config_dir, file_path, prometheus_configmap_name):
        self.config_dir = config_dir
        self.file_path = file_path
        self.consul_url = consul_url
        self.prometheus_configmap_name = prometheus_configmap_name

    def check_job_exist(self, job_name):
        with open(self.file_path, "r") as f:
            prometheus_file_yaml = yaml.load(f, Loader=yaml.FullLoader)
            for job in prometheus_file_yaml["scrape_configs"]:
                if job["job_name"] == job_name:
                    return True
        return False

    def add_job_to_prometheus_yaml(self, job_name):
        job = prometheus_job.format(consul_url=self.consul_url, job_name=job_name)
        with open(self.file_path, "r") as f:
            prometheus_file_yaml = yaml.load(f, Loader=yaml.FullLoader)
            prometheus_file_yaml["scrape_configs"].append(yaml.load(job, Loader=yaml.FullLoader))
        with open(self.file_path, "w") as f:
            yaml.dump(prometheus_file_yaml, f, sort_keys=True, default_flow_style=False)

    def del_job_from_prometheus_yaml(self, job_name):
        job_inx = -1
        with open(self.file_path, "r") as f:
            prometheus_file_yaml = yaml.load(f, Loader=yaml.FullLoader)
            for idx in range(len(prometheus_file_yaml["scrape_configs"])):
                if prometheus_file_yaml["scrape_configs"][idx]["job_name"] == job_name:
                    print("find job %s in prometheus file" % job_name)
                    job_inx = idx

        if job_inx != -1:
            del prometheus_file_yaml["scrape_configs"][job_inx]
        else:
            print("job %s not exist in prometheus file!")
            return False
        with open(self.file_path, "w") as f:
            yaml.dump(prometheus_file_yaml, f, sort_keys=True, default_flow_style=False)
        return True

    def update_configmap(self):
        save_old_cm = "kubectl get cm {configmapname} -n kube-system -o yaml >{prometheus_config_path}/{configmapname}-{time}.yaml". \
            format(prometheus_config_path=self.config_dir,
                   configmapname=self.prometheus_configmap_name,
                   time=datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))
        ret = subprocess.run(save_old_cm,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",timeout=1)
        if ret.returncode == 0:
            print("success:", ret)
        else:
            print("error:", ret)
            return
        dry_run_cmd = "kubectl create cm {configmapname} -n kube-system --from-file=prometheus.yaml={prometheus_file} " \
                      "--dry-run -o yaml >{prometheus_config_path}/{configmapname}-new.yaml". \
            format(prometheus_config_path=self.config_dir, configmapname=self.prometheus_configmap_name, prometheus_file=self.file_path)
        ret = subprocess.run(dry_run_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",timeout=1)
        if ret.returncode == 0:
            print("success:",ret)
        else:
            print("error:",ret)
            return

        update_cmd = "kubectl apply -n kube-system -f {prometheus_config_path}/{configmapname}-new.yaml". \
            format(configmapname=self.prometheus_configmap_name, prometheus_config_path=self.config_dir,prometheus_file=self.file_path)
        ret = subprocess.run(update_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", timeout=1)
        if ret.returncode == 0:
            print("success:",ret)
        else:
            print("error:",ret)
            return


if __name__ == "__main__":
    job_name = "node-exporter"
    p = Prometheus("prometheus/prometheus.yaml")
    p.update_prometheus_yaml(job_name)
    p.update_configmap("./prometheus.yaml", "steamer-prometheus-master-config")
