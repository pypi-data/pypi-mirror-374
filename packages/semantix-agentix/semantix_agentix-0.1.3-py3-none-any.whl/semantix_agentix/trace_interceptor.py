import requests
import mlflow
from .check_token import check_token

def trace_interceptor(base_url: str, key: str, subscriber: str):
  _original_log_trace = mlflow.log_trace
  def intercept_log_trace(*args, **kwargs):
    check_token(base_url, key)
    
    result = _original_log_trace(*args, **kwargs)
    trace = mlflow.get_trace(trace_id=result, silent=True)

    try: 
      response = requests.post(
        f'{base_url}/traces?token={key}&subscriberId={subscriber}', 
        json={
        'request': trace.data.request,
        'response': trace.data.response,
        'tokenUsage': trace.info.token_usage,
        'timestamp': trace.info.timestamp_ms,
        'experimentId': trace.info.experiment_id,
        'executionTime': trace.info.execution_time_ms,
        'outputs': trace.data.intermediate_outputs,
      })
      response.raise_for_status()
    except Exception as e:
      print(f'Agentix error: {e}')

    return result
  
  mlflow.log_trace = intercept_log_trace