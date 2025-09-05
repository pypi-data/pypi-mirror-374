import requests
import mlflow
from .check_token import check_token

def run_interceptor(base_url: str, key: str, subscriber: str):
  _original_end_run = mlflow.end_run
  def intercept_end_run(*args, **kwargs):
    check_token(base_url, key)
    
    run = mlflow.active_run()
    result = _original_end_run(*args, **kwargs)
    
    mlflow.search_traces
    
    try: 
      response = requests.post(
        f'{base_url}/runs?token={key}&subscriberId={subscriber}', 
        json={
        'runId': run.info.run_id,
        'status': run.info.status,
        'params': run.data.params,
        'userId': run.info.user_id,
        'metrics': run.data.metrics,
        'runName': run.info.run_name,
        'endTime': run.info.end_time,
        'startTime': run.info.start_time,
        'experimentId': run.info.experiment_id
      })
      response.raise_for_status()
    except Exception as e:
      print(f'Agentix error: {e}')

    return result
  
  mlflow.end_run = intercept_end_run