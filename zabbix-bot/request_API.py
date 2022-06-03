from posixpath import split, splitext
from pytest import param
import requests
import json
import logging

logger = logging.getLogger(__name__)

class ZabbixAPIException(Exception):
    pass

class API:
    def __init__(self, url, username, password) -> None:
        self.url = url
        try:
            self.token = self.request_login(username=username, password=password)
        except Exception as e:
            logger.error('Problems getting token authentication - %s', e)
            raise ZabbixAPIException(e) 
            

    def request_post(self, params, method, login=None):
        """Send a post request to API"""
        if login == True:
            payload = {'jsonrpc': '2.0', 'method': method,
                   'params': params, 'id': 1}
        else:
            payload = {'jsonrpc': '2.0', 'method': method,
                    'params': params, 'auth': self.token, 'id': 1}

        logger.debug("Sending: %s", json.dumps(payload))

        headers = {'content-type': 'application/json'}
        r = requests.post(self.url+'/api_jsonrpc.php',
                          headers=headers, json=payload)
        
        if not len(r.text):
            raise ZabbixAPIException("Received empty response")
        
        try:
            json_data = json.loads(r.text)
        except ValueError:
            raise ZabbixAPIException(
                "Unable to parse json: %s" % r.text
            )
        logger.debug("Response Body: %s", json.dumps(json_data))

        if 'error' in json_data:  
            if json_data['error']['data'] == 'Login name or password is incorrect.':
                
                msg = "Error {code}: {message}: {data}".format(
                    code=json_data['error']['code'],
                    message=json_data['error']['message'],
                    data=json_data['error']['data'])

            else:

                msg = "Error {code}: {message}: {data} while sending {json}".format(
                    code=json_data['error']['code'],
                    message=json_data['error']['message'],
                    data=json_data['error']['data'],
                    json=str(payload))
            logger.error(msg)
            raise ZabbixAPIException(msg, json_data['error']['code'])
        
        
        return json_data['result']
        


    def request_login(self, username, password):
        """Get token to authenticate user"""
        params = {
            "user" : username,
            "password": password
        }
        return self.request_post(params=params, method='user.login', login=True)
        

    def get_list_hosts(self):
        """Get all hosts"""
        params = {
            'output': ['name', 'status', 'hostid'],
            'sortfield': 'name',
            "selectInterfaces": ["available"]
        }
        return self.request_post(params=params, method='host.get')
        

    def get_list_hosts_with_name(self, name):
        """Get all hosts with a specific name"""
        params = {
            'output': ['name', 'status', 'hostid'],
            'sortfield': 'name',
            'search': {
                'host': '*'+name+'*'
            },
            'searchWildcardsEnabled': True,
            "selectInterfaces": ["available"]
        }
        return self.request_post(params=params, method='host.get')
        

    def get_list_hosts_with_tag(self, tag):
        """Get all hosts with a specific tag"""
        tags = tag.split("=")
        params = {
            'output': ['name', 'status', 'hostid'],
            'sortfield': 'name',
            'tags': [
                {
                    'tag': tags[0],
                    'value': tags[1]
                }
            ],
            "selectInterfaces": ["available"]
        }
        return self.request_post(params=params, method='host.get')
        

    def get_list_hostgroups(self):
        """Get all hosts groups"""
        params = {
            'output': ['name', 'groupid']
        }
        return  self.request_post(params=params, method='hostgroup.get')
        

    def get_list_hosts_with_hostgroup(self, id_hostgroup):
        """Get all hosts in hosts group"""
        params = {
            'output': ['name', 'status', 'hostid'],
            'sortfield': 'name',
            'groupids': id_hostgroup,
            "selectInterfaces": ["available"]
        }
        return self.request_post(params=params, method='host.get')
        

    def get_host_info(self, id_host):
        """Get all information of the selected host"""
        params = {
            "hostids": id_host,
            "output": ["name", "status", "hostid"],
            "selectItems": ["name", "itemid", "lastvalue", "lastclock"],
            "selectTriggers": ["triggerid", "description", "value", "priority"],
            "selectTags": ["tag", "value"],
            "selectInventory": ["location_lat", "location_lon"],
            "selectInterfaces": ["available"],
            "selectGroups": ["name", "groupid"]
        }
        return self.request_post(params=params, method='host.get')
        

    def get_host_problem(self, id_host):
        """Get all problems of the selected host"""
        params = {
            "hostids": id_host,
            "output": ["eventid", "name", "clock", "acknowledged", "severity"]
        }
        return self.request_post(params=params, method='problem.get')
        

    def update_host_status(self, id_host, status):
        """Update status of host"""
        params = {
            "hostid": id_host,
            "status": status
        }
        return self.request_post(params=params, method='host.update')

    def get_list_items(self, id_host):
        """Get all items of the selected host"""
        params = {
            "hostids": id_host,
            "sortfield": "name",
            "output": ["name", "itemid", "status"],
        }
        return self.request_post(params=params, method='item.get')
        

    def get_item_info(self, id_item):
        """Get all information of the selected item"""
        params = {
            "itemids": id_item,
            "output": ["name", "itemid", "lastclock", "lastvalue", "status", "value_type", "units"],
            "selectHosts": ["hostid", "name"],
            "selectTriggers": ["triggerid", "description", "value", "priority"],
            "selectTags": ["tag", "value"]
        }
        return self.request_post(params=params, method='item.get')
        

    def update_item_status(self, id_item, status):
        """Update status of item"""
        params = {
            "itemid": id_item,
            "status": status
        }
        return self.request_post(params=params, method='item.update')
        
    def get_list_triggers_by_host(self, id_host):
        """Get all triggers of the selected host"""
        params = {
            "hostids": id_host,
            "sortfield": "description",
            "output": ["triggerid", "description", "status"],
        }
        return self.request_post(params=params, method='trigger.get')
        

    def get_list_triggers_by_item(self, id_item):
        """Get all triggers of the selected item"""
        params = {
            "itemids": id_item,
            "sortfield": "description",
            "output": ["triggerid", "description", "status"],
        }
        return self.request_post(params=params, method='trigger.get')
        

    def get_trigger_info(self, id_trigger):
        """Get all information of the selected trigger"""
        params = {
            "triggerids": id_trigger,
            "output": ["triggerid", "description", "status", "value", "priority", "lastchange", "expression"],
            "selectTags": ["tag", "value"],
            "selectHosts": ["hostid", "name"],
            "selectItems": ["hostid", "name"],
            "expandExpression": "true"
        }
        return self.request_post(params=params, method='trigger.get')
        

    def get_trigger_problem(self, id_trigger):
        """Get all problems of the selected trigger"""
        params = {
            "objectids": id_trigger,
            "output": ["eventid", "name", "clock", "acknowledged", "severity"]
        }
        return self.request_post(params=params, method='problem.get')
        

    def update_trigger_status(self, id_trigger, status):
        """Update status of trigger"""
        params = {
            "triggerid": id_trigger,
            "status": status
        }
        return self.request_post(params=params,method='trigger.update')
        

    def get_list_problems_by_host(self, id_host):
        """Get all problems of the selected host"""
        params = {
            "hostids": id_host,
            "output": ["eventid", "name", "clock", "acknowledged", "severity"],
        }
        return self.request_post(params=params,method='problem.get')
        

    def get_list_problems_by_trigger(self, id_trigger):
        """Get all problems of the selected trigger"""
        params = {
            "objectids": id_trigger,
            "output": ["eventid", "name", "clock", "acknowledged", "severity"],
        }
        return self.request_post(params=params,method='problem.get')
        

    def get_event_info(self, id_event):
        """Get all information of the selected event"""
        params = {
            "eventids": id_event,
            "output": ["eventid", "object", "objectid", "name", "clock", "acknowledged", "severity"],
            "selectTags": ["tag", "value"],
            "selectHosts": ["hostid", "name"]
        }
        return self.request_post(params=params,method='event.get')
        

    def action_event(self, id_event, action, message=None, severity=None):
        """Send action event"""
        if message == None and severity == None:
            params = {
                "eventids": id_event,
                "action": action
            }
        elif message != None:
            params = {
                "eventids": id_event,
                "action": action,
                "message": message
            }
        elif severity != None:
            params = {
                "eventids": id_event,
                "action": action,
                "severity": severity
            }
        return self.request_post(params=params,method='event.acknowledge')
        

    def get_list_problems(self):
        """Get all problems"""
        params = {
            "output": ["eventid", "name", "clock", "acknowledged", "severity"],
        }
        return self.request_post(params=params, method='problem.get')
        

    def get_list_history_item(self, item_id, history):
        """Get history values for item"""
        params = {
            "itemids": item_id,
            "history": history,
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": 60
        }
        return self.request_post(params=params,method='history.get')
        

    def get_list_maintenances(self):
        """Get all maintenances"""
        params = {}
        return self.request_post(params=params,method='maintenance.get')
        

    def get_list_services(self):
        """Get all services"""
        params = {
            'output': ['name', 'serviceid', 'status']
        }
        return self.request_post(params=params,method='service.get')
        

    def get_service_info(self, serviceid):
        """Get information service"""
        params = {
            'serviceids': serviceid,
            "output": "extend",
            "selectChildren": "extend",
            "selectParents": "extend",
            "selectTags": "extend",
            "selectProblemEvents": "extend",
            "selectProblemTags": "extend"
        }
        return self.request_post(params=params,method='service.get')
        

    def get_list_services_parent_child(self, parentid):
        """Get all services"""
        services = list()
        parentid_split = parentid.split(";")
        for id in parentid_split:
            if id != '':
                services.append(id)
        params = {
            'serviceids': services,
            'output': ['name', 'serviceid', 'status']
        }
        return self.request_post(params=params,method='service.get')
        

    def get_list_problems_by_service(self, problemid):
        """Get all problems"""
        events = list()
        problemid_split = problemid.split(";")
        for id in problemid_split:
            if id != '':
                events.append(id)
        params = {
            "eventids": events,
            "output": ["eventid", "name", "clock", "acknowledged", "severity"],
        }
        return self.request_post(params=params,method='problem.get')
        

    def get_sla_by_service(self, service_id=None, sla_id=None):
        """Get SLA values"""
        if sla_id == None:
            params = {
                "serviceids": service_id,
                "output": ["slaid", "name", "slo", "period"]
            }
        else:
            params = {
                "slaids": sla_id,
                "output": ["slaid", "name", "slo", "period"]
            }
        return self.request_post(params=params,method='sla.get')
        

    def get_sla_report_by_service(self, sla_id, service_id):
        """Get SLA report for service"""
        params = {
            "serviceids": service_id,
            "slaid": sla_id
        }
        return self.request_post(params=params,method='sla.getsli')
        

    def get_problem_info(self, id_event):
        """Get all information of the problem"""
        params = {
            "eventids": id_event,
            "output": "extend",
            "selectTags": ["tag", "value"],
            "selectHosts": ["hostid", "name"],
            "select_acknowledges": "extend",
            "selectRelatedObject": "extend",
            "select_alerts":"extend"
        }
        return self.request_post(params=params,method='event.get')
        