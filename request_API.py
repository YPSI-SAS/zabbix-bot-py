from posixpath import split, splitext
from pytest import param
import requests
import json

class API:
  def __init__(self, url, token) -> None:
      self.url = url
      self.token = token

  #request_post permits to send a post request to API
  def request_post(self, params, method):
    payload = {'jsonrpc':'2.0','method':method,'params':params, 'auth': self.token, 'id':1}
    headers = {'content-type': 'application/json'}
    r=requests.post(self.url+'/api_jsonrpc.php',headers=headers,json=payload)
    return r.status_code,r.text

  #get_list_hosts permits to get all hosts
  def get_list_hosts(self):
    params = {
      'output': ['name','status', 'hostid'],
      'sortfield':'name'
    }
    status_code, text = self.request_post(params=params, method='host.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #get_list_hosts_with_name permits to get all hosts with a specific name
  def get_list_hosts_with_name(self, name):
    params = {
      'output': ['name','status', 'hostid'],
      'sortfield':'name',
      'search': {
            'host': '*'+name+'*'
        },
      'searchWildcardsEnabled': True
    }
    status_code, text = self.request_post(params=params, method='host.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}
  
  #get_list_hosts_with_tag permits to get all hosts with a specific tag
  def get_list_hosts_with_tag(self, tag):
    tags = tag.split("=")
    params = {
      'output': ['name','status', 'hostid'],
      'sortfield':'name',
      'tags': [
            {
                'tag': tags[0],
                'value': tags[1]
            }
        ]
    }
    status_code, text = self.request_post(params=params, method='host.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #get_list_hostgroups permits to get all hosts groups
  def get_list_hostgroups(self):
    params = {
      'output': ['name','groupid']
    }
    status_code, text = self.request_post(params=params, method='hostgroup.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}
  
  #get_list_hosts_with_hostgroup permits to get all hosts in hosts group
  def get_list_hosts_with_hostgroup(self, id_hostgroup):
    params = {
      'output': ['name','status', 'hostid'],
      'sortfield':'name',
      'groupids': id_hostgroup
    }
    status_code, text = self.request_post(params=params, method='host.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #get_host_info permits to get all information of the selected host
  def get_host_info(self, id_host):
    params = {
      "hostids":id_host,
        "output": ["name","status","hostid"],
        "selectItems": ["name","itemid"],
        "selectTriggers": ["triggerid","description","value","priority"],
        "selectTags": ["tag","value"]
    }
    status_code, text = self.request_post(params=params, method='host.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}
  
  #get_host_problem permits to get all problems of the selected host
  def get_host_problem(self, id_host):
    params = {
      "hostids":id_host,
      "output": ["eventid","name","clock","acknowledged","severity"]
    }
    status_code, text = self.request_post(params=params, method='problem.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #update_host_status permits to update status of host
  def update_host_status(self, id_host, status):
    params = {
      "hostid":id_host,
      "status": status
    }
    status_code, text = self.request_post(params=params, method='host.update')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}
  
  #get_list_items permits to get all items of the selected host
  def get_list_items(self, id_host):
    params = {
      "hostids":id_host,
      "sortfield":"name",
      "output":["name","itemid","status"],
    }
    status_code, text = self.request_post(params=params, method='item.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}
  
  #get_item_info permits to get all information of the selected item
  def get_item_info(self, id_item):
    params = {
      "itemids":id_item,
      "output":["name","itemid","lastclock","lastvalue","status", "value_type","units"],
      "selectHosts":["hostid","name"],
      "selectTriggers": ["triggerid","description","value","priority"],
      "selectTags": ["tag","value"]
    }
    status_code, text = self.request_post(params=params, method='item.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #update_item_status permits to update status of item
  def update_item_status(self, id_item, status):
    params = {
      "itemid":id_item,
      "status": status
    }
    status_code, text = self.request_post(params=params, method='item.update')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}