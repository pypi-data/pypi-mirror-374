# %%
import requests

from .experiment_interceptor import experiment_interceptor
from .model_interceptor import model_interceptor
from .run_interceptor import run_interceptor
from .trace_interceptor import trace_interceptor
from .metric_interceptor import metric_interceptor

class agentix:
  def __init__(self, token: str, development: bool = False): 
    self.__base_url = (
      'https://ai-governance-dev.linkapi.com.br/api'
      if development == True
      else 'https://ai-governance.linkapi.com.br/api'
    )
    
    # AUTH
    self.__auth(token)

    # INTERCEPTORS
    experiment_interceptor(
      base_url=self.__base_url, 
      key=self.__token.get("key"), 
      subscriber=self.__token.get("subscriberId")
      )
  
    model_interceptor(
      base_url=self.__base_url, 
      key=self.__token.get("key"), 
      subscriber=self.__token.get("subscriberId")
      )
    
    run_interceptor(
      base_url=self.__base_url, 
      key=self.__token.get("key"), 
      subscriber=self.__token.get("subscriberId")
      )
    
    trace_interceptor(
      base_url=self.__base_url, 
      key=self.__token.get("key"), 
      subscriber=self.__token.get("subscriberId")
      )
    
    metric_interceptor(
      base_url=self.__base_url, 
      key=self.__token.get("key"), 
      subscriber=self.__token.get("subscriberId")
      )

  def __auth(self, token: str):
    response = requests.get(f'{self.__base_url}/tokens/{token}/check')
    data = response.json()
    print(data)

    if response.status_code != 200:
      raise ValueError(f"Error {response.status_code}: {data}")
    
    if not data.get("isValid", False):
      raise ValueError("Invalid token")

    self.__token = data.get("token")
    
    return True
    
