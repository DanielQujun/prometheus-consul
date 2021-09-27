#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: qujun
# datetime:9/27/21 1:48 PM
import requests

register_api = "/v1/catalog/register"

node_exporter_template = '''
{{
  "Node": "{node_address}",
  "Address": "{node_address}",
  "NodeMeta": {{
    "external-node": "true",
    "external-probe": "true"
  }},
  "Service": {{
    "ID": "{jobname}-{node_address}",
    "Service": "{jobname}",
    "Tags": ["{jobname}", "prometheus"],
    "Port": {target_port}
  }},
  "Checks": []
}}
'''


def add_service(consulurl, jobname, node_address, target_port):
    content_header = {"Content-type": "application/json"}
    put_data = node_exporter_template.format(jobname=jobname, node_address=node_address, target_port=target_port)
    ret = requests.put(url=consulurl+register_api, data=put_data, headers=content_header)
    print(ret)