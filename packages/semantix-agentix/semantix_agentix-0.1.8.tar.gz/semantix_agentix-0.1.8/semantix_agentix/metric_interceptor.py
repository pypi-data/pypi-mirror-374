import requests
import mlflow
from .check_token import check_token

def metric_interceptor(base_url: str, key: str, subscriber: str):
  _original_log_metrics = mlflow.log_metrics
  def intercept_log_metrics(*args, **kwargs):
    check_token(base_url, key)
    
    result = _original_log_metrics(*args, **kwargs)
    metrics = args[0] or kwargs.get('metrics')
    run = mlflow.active_run()
    
    if run:
      try: 
        response = requests.post(
          f'{base_url}/metrics?token={key}&subscriberId={subscriber}', 
          json={
          'runId': run.info.run_id,
          'metrics': metrics
        })
        response.raise_for_status()
      except Exception as e:
        print(f'Agentix error: {e}')

    return result
  
  mlflow.log_metrics = intercept_log_metrics

  _original_log_metric = mlflow.log_metric
  def intercept_log_metric(*args, **kwargs):
    check_token(base_url, key)
    
    result = _original_log_metric(*args, **kwargs)
    metric_key = args[0] or kwargs.get('key')
    metric_value = args[1] or kwargs.get('value')
    
    run = mlflow.active_run()
    
    if run:
      try: 
        response = requests.post(
          f'{base_url}/metrics?token={key}&subscriberId={subscriber}', 
          json={
          'runId': run.info.run_id,
          'metrics': [{
            'key': metric_key,
            'value': metric_value,
          }]
        })
        response.raise_for_status()
      except Exception as e:
        print(f'Agentix error: {e}')

    return result
  
  mlflow.log_metric = intercept_log_metric