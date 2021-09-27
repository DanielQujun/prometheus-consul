#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: qujun
# datetime:9/27/21 11:55 AM
import datetime
import subprocess


def update_configmap(prometheus_config_path, prometheus_file, configmapname):
    save_old_cm = "kubectl get cm {configmapname} -n kube-system -o yaml >{prometheus_config_path}/{configmapname}-{time}.yaml".\
        format(prometheus_config_path=prometheus_config_path,
                configmapname=configmapname,
                time=datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))
    ret = subprocess.run(save_old_cm,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",timeout=1)
    if ret.returncode == 0:
        print("success:",ret)
    else:
        print("error:",ret)
        return
    dry_run_cmd = "kubectl create cm {configmapname} -n kube-system --from-file=prometheus.yaml={prometheus_file} --dry-run -o yaml >{prometheus_config_path}/{configmapname}-new.yaml".\
        format(prometheus_config_path=prometheus_config_path, configmapname=configmapname, prometheus_file=prometheus_file)
    ret = subprocess.run(dry_run_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",timeout=1)
    if ret.returncode == 0:
        print("success:",ret)
    else:
        print("error:",ret)
        return

    update_cmd = "kubectl apply -n kube-system -f {prometheus_config_path}/{configmapname}-new.yaml". \
        format(configmapname=configmapname, prometheus_config_path=prometheus_config_path,prometheus_file=prometheus_file)
    ret = subprocess.run(update_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",timeout=1)
    if ret.returncode == 0:
        print("success:",ret)
    else:
        print("error:",ret)
        return


if __name__ == "__main__":
    update_configmap("./prometheus.yaml", "steamer-prometheus-master-config")