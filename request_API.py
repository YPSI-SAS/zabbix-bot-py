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
      'output': ['name','status'],
      'sortfield':'name'
    }
    status_code, text = self.request_post(params=params, method='host.get')
    json_data = json.loads(text)
    if status_code==200:
      return json_data['result']
    else:
      return {}