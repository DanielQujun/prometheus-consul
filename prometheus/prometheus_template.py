#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: qujun
# datetime:9/27/21 11:41 AM
import yaml

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


def check_job_exist(file_path, job_name):
    with open(file_path, "r") as f:
        prometheus_file_yaml = yaml.load(f)
        for job in prometheus_file_yaml["scrape_configs"]:
            if job["job_name"] == job_name:
                return True
    return False


def update_prometheus_yaml(consul_url, file_path, job_name):
    job = prometheus_job.format(consul_url=consul_url, job_name=job_name)
    with open(file_path, "r") as f:
        prometheus_file_yaml = yaml.load(f)
        prometheus_file_yaml["scrape_configs"].append(yaml.load(job))
    with open(file_path, "w") as f:
        print(yaml.dump(prometheus_file_yaml, f, sort_keys=True, default_flow_style=False))


if __name__ == "__main__":
    job_name = "node-exporter"
    update_prometheus_yaml("127.0.0.1", "prometheus/prometheus.yaml", job_name)
