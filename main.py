#!/usr/bin/env python3
from consul import consul
import prometheus
import os
from absl import app
from absl import flags


pwd_path = os.path.abspath(os.path.dirname(__file__))

consul_url = os.environ.get("CONSUL_URL", "http://192.168.0.78:32087")

prometheus_config_path = os.path.join(pwd_path, "./prometheus-config")
prometheus_yaml_path = os.path.join(pwd_path, "./prometheus-config/prometheus.yaml")
prometheus_configmap_name = "steamer-prometheus-master-config"

FLAGS = flags.FLAGS

flags.DEFINE_string('o', "list_service", u"add_service: 添加服务,需要jobname、ip、port参数，\n"
                                  u"如果jobname在prometheus中不存在,则自动添加;\n\n"
                                  u"del_service: 删除服务,需要jobname、ip、port参数;\n\n"    
                                  u"list_service: 查询某个jobname下面注册了哪些节点;\n\n"
                                  u"add_job: 添加prometheus job;\n\n"
                                  u"del_job: 删除prometheus job;\n\n"
                                  u"list_node: 删除prometheus job;\n\n")
flags.DEFINE_string('job', "", u"添加服务在哪个job之下，或给prometheus添加的job名")
flags.DEFINE_string('ip', "", u"服务的ip")
flags.DEFINE_string('port', "", u"服务的端口")


def main(argv):
    del argv

    if FLAGS.o == "add_service":
        if FLAGS.job == "" or FLAGS.ip == "" or FLAGS.port == "":
            print("need jobname, ip, port!")
            exit()
        c = consul.Consul(consul_url)
        c.add_service(FLAGS.job, FLAGS.ip, FLAGS.port)
        p = prometheus.Prometheus(prometheus_config_path, prometheus_yaml_path, prometheus_configmap_name)
        if p.check_job_exist_from_cm(FLAGS.job):
            print("job: %s exist in config, skip~" % FLAGS.job)
        else:
            print("going to update prometheus configmap!")
            p.update_configmap("add", FLAGS.job)

    elif FLAGS.o == "del_service":
        if FLAGS.job == "" or FLAGS.ip == "" or FLAGS.port == "":
            print("need jobname, ip, port!")
            exit()
        c = consul.Consul(consul_url)
        c.del_service(FLAGS.job, FLAGS.ip, FLAGS.port)

    elif FLAGS.o == "del_node":
        if FLAGS.ip == "":
            print("need node ip!")
            exit()
        c = consul.Consul(consul_url)
        c.del_node(FLAGS.ip)
    elif FLAGS.o == "list_node":
        c = consul.Consul(consul_url)
        c.list_node()

    elif FLAGS.o == "list_service":
        if FLAGS.job == "":
            print("need jobname!")
            exit()
        c = consul.Consul(consul_url)
        c.list_service(FLAGS.job)

    elif FLAGS.o == "add_job":
        if FLAGS.job == "":
            print("need jobname")
            exit()
        p = prometheus.Prometheus(prometheus_config_path, prometheus_yaml_path, prometheus_configmap_name)
        if p.check_job_exist_from_cm(FLAGS.job):
            print("job: %s exist in config, skip~" % FLAGS.job)
        else:
            print("going to update prometheus configmap!")
            p.update_configmap("add", FLAGS.job)

    elif FLAGS.o == "del_job":
        if FLAGS.job == "":
            print("need jobname!")
            exit()
        p = prometheus.Prometheus(prometheus_config_path, prometheus_yaml_path, prometheus_configmap_name)
        if p.check_job_exist_from_cm(FLAGS.job):
            print("job: %s exist in config, going to delete" % FLAGS.job)
            p.update_configmap("del", FLAGS.job)
        else:
            print("job %s do not exist in configmap %s!"%(FLAGS.job, prometheus_configmap_name))

    else:
        print("operation %s not defined, see python3 main.py --help!" % FLAGS.o)


if __name__ == '__main__':
    app.run(main)

