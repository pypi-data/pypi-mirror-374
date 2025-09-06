import requests

def check_token(base_url: str, key: str):
  response = requests.get(f'{base_url}/tokens/{key}/check')
  data = response.json()

  if response.status_code != 200:
    raise ValueError(f"Error {response.status_code}: {data}")
  
  if not data.get("isValid", False):
    raise ValueError("Invalid token")
  
  return True