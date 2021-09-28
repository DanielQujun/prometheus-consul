#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: qujun
# datetime:9/27/21 1:48 PM
import requests
import json



add_service_template = '''
{{
  "Node": "{node_address}",
  "Address": "{node_address}",
  "NodeMeta": {{
    "external-node": "true",
    "external-probe": "true"
  }},
  "Service": {{
    "ID": "{jobname}-{node_address}-{target_port}",
    "Service": "{jobname}",
    "Tags": ["{jobname}", "prometheus"],
    "Port": {target_port}
  }},
  "Checks": []
}}
'''

del_service_template = '''
{{
  "Node": "{node_address}",
  "Datacenter": "dc1",
  "ServiceID": "{jobname}-{node_address}-{target_port}"
}}
'''


class Consul:

    register_api = "/v1/catalog/register"
    deregister_api = "/v1/catalog/deregister"
    list_api = "/v1/catalog/service/"

    def __init__(self, consulurl):
        self.consulUrl = consulurl

    def add_service(self, jobname, node_address, target_port):
        content_header = {"Content-type": "application/json"}
        put_data = add_service_template.format(jobname=jobname, node_address=node_address, target_port=target_port)
        ret = requests.put(url=self.consulUrl+self.register_api, data=put_data, headers=content_header)
        print(ret.status_code)

    def del_service(self, jobname, node_address, target_port):
        content_header = {"Content-type": "application/json"}
        put_data = del_service_template.format(jobname=jobname, node_address=node_address, target_port=target_port)
        ret = requests.put(url=self.consulUrl+self.deregister_api, data=put_data, headers=content_header)
        print(ret.status_code)

    def list_service(self, jobname):
        content_header = {"Content-type": "application/json"}
        ret = requests.get(url=self.consulUrl+self.list_api + jobname, headers=content_header)
        print(json.dumps(ret.json(), sort_keys=True, indent=4, separators=(',', ':')))
