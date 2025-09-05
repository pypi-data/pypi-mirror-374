import requests
import mlflow
from .check_token import check_token

def model_interceptor(base_url: str, key: str, subscriber: str):
  _original_create_model = mlflow.MlflowClient.create_registered_model
  def intercept_create_model(*args, **kwargs):
    check_token(base_url, key)
    result = _original_create_model(*args, **kwargs)

    try: 
      response = requests.post(
        f'{base_url}/models?token={key}&subscriberId={subscriber}', 
        json={
        'name': result.name,
        'description': result.description,
        'createdAt': result.creation_timestamp,
        'updatedAt': result.last_updated_timestamp,
      })
      response.raise_for_status()
    except Exception as e:
      print(f'Agentix error: {e}')

    return result

  mlflow.MlflowClient.create_registered_model = intercept_create_model
  mlflow.tracking.MlflowClient.create_registered_model = intercept_create_model

  _original_delete_model = mlflow.MlflowClient.delete_registered_model
  def intercept_delete_model(*args, **kwargs):
    check_token(base_url, key)
    result = _original_delete_model(*args, **kwargs)

    try: 
      response = requests.delete(f'{base_url}/models/{result.name}?token={key}&subscriberId={subscriber}')
      response.raise_for_status()
    except Exception as e:
      print(f'Agentix error: {e}')

    return result

  mlflow.MlflowClient.delete_registered_model = intercept_delete_model
  mlflow.tracking.MlflowClient.delete_registered_model = intercept_delete_model

  def flavor_interceptor_factory(flavor):
    def intercept_log_model(*args, **kwargs):
        check_token(base_url, key)
        result = flavor(*args, **kwargs)
        
        try:
          response = requests.post(
            f'{base_url}/logged-models?token={key}&subscriberId={subscriber}', 
            json={
                "name": getattr(result, "name", None),
                "runId": getattr(result, "run_id", None),
                "metrics": getattr(result, "metrics", None),
                "flavors": getattr(result, "flavors", None),
                "modelId": getattr(result, "model_id", None),
                "createdAt": getattr(result, "creation_timestamp", None),
                "modelVersion": getattr(result, "registered_model_version", None),
            })
          response.raise_for_status()
        except Exception as e:
          print(f'Agentix error: {e}')

        return result  
    
    return intercept_log_model
  
  for attr_name in dir(mlflow):
    try:
      flavor = getattr(mlflow, attr_name)
      if hasattr(flavor, 'log_model'):
        original_log_model = getattr(flavor, 'log_model')
        
        if hasattr(original_log_model, '_is_patched'):
          continue
        
        interceptor = flavor_interceptor_factory(original_log_model)
        interceptor._is_patched = True
        setattr(flavor, 'log_model', interceptor)
        
    except ModuleNotFoundError:
      continue
    except Exception:
      continue