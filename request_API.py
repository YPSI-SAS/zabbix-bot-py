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
      'sortfield':'name',
      "selectInterfaces":["available"]
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
      'searchWildcardsEnabled': True,
      "selectInterfaces":["available"]
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
        ],
      "selectInterfaces":["available"]
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
      'groupids': id_hostgroup,
      "selectInterfaces":["available"]
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
        "selectTags": ["tag","value"],
        "selectInterfaces":["available"]
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

  #get_list_triggers_by_host permits to get all triggers of the selected host
  def get_list_triggers_by_host(self, id_host):
    params = {
      "hostids":id_host,
      "sortfield":"description",
      "output": ["triggerid", "description", "status"],
    }
    status_code, text = self.request_post(params=params, method='trigger.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #get_list_triggers_by_item permits to get all triggers of the selected item
  def get_list_triggers_by_item(self, id_item):
    params = {
      "itemids":id_item,
      "sortfield":"description",
      "output": ["triggerid", "description", "status"],
    }
    status_code, text = self.request_post(params=params, method='trigger.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #get_trigger_info permits to get all information of the selected trigger
  def get_trigger_info(self, id_trigger):
    params = {
      "triggerids":id_trigger,
      "output": ["triggerid", "description", "status", "value","priority", "lastchange", "expression"],
      "selectTags": ["tag", "value"],
      "selectHosts":["hostid","name"],
      "selectItems":["hostid", "name"],
      "expandExpression": "true"
    }
    status_code, text = self.request_post(params=params, method='trigger.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #get_trigger_problem permits to get all problems of the selected trigger
  def get_trigger_problem(self, id_trigger):
    params = {
      "objectids":id_trigger,
      "output": ["eventid","name","clock","acknowledged","severity"]
    }
    status_code, text = self.request_post(params=params, method='problem.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #update_trigger_status permits to update status of trigger
  def update_trigger_status(self, id_trigger, status):
    params = {
      "triggerid":id_trigger,
      "status": status
    }
    status_code, text = self.request_post(params=params, method='trigger.update')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #get_list_problems_by_host permits to get all problems of the selected host
  def get_list_problems_by_host(self, id_host):
    params = {
      "hostids":id_host,
      "output": ["eventid","name","clock","acknowledged","severity"],
    }
    status_code, text = self.request_post(params=params, method='problem.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}
  
  #get_list_problems_by_trigger permits to get all problems of the selected trigger
  def get_list_problems_by_trigger(self, id_trigger):
    params = {
      "objectids":id_trigger,
      "output": ["eventid","name","clock","acknowledged","severity"],
    }
    status_code, text = self.request_post(params=params, method='problem.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #get_event_info permits to get all information of the selected event
  def get_event_info(self, id_event):
    params = {
      "eventids":id_event,
      "output": ["eventid", "object", "objectid", "name", "clock", "acknowledged", "severity"],
      "selectTags": ["tag", "value"],
      "selectHosts":["hostid","name"]
    }
    status_code, text = self.request_post(params=params, method='event.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}

  #action_event permits to action event
  def action_event(self, id_event, action, message=None, severity=None):
    if message==None and severity==None:
      params = {
        "eventids":id_event,
        "action": action
      }
    elif message !=None:
      params = {
        "eventids":id_event,
        "action": action,
        "message":message
      }
    elif severity!=None:
      params = {
        "eventids":id_event,
        "action": action,
        "severity":severity
      }
    status_code, text = self.request_post(params=params, method='event.acknowledge')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}
  
  #get_list_problems permits to get all problems
  def get_list_problems(self):
    params = {
      "output": ["eventid","name","clock","acknowledged","severity"],
    }
    status_code, text = self.request_post(params=params, method='problem.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}