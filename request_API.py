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
