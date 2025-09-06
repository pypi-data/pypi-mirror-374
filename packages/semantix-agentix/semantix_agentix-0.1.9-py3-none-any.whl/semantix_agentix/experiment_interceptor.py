import requests
import mlflow
from .check_token import check_token

def experiment_interceptor(base_url: str, key: str, subscriber: str):
  _original_create_experiment = mlflow.create_experiment
  def intercept_create_experiment(*args, **kwargs):
    check_token(base_url, key)
    result = _original_create_experiment(*args, **kwargs)

    try: 
      experiment = mlflow.get_experiment(experiment_id=result)
      response = requests.post(f'{base_url}/experiments?token={key}&subscriberId={subscriber}', json={
        "experimentId": experiment.experiment_id,
        "name": experiment.name,
        "stage": experiment.lifecycle_stage,
        "createdAt": experiment.creation_time,
        "updatedAt": experiment.last_update_time,
      })
      response.raise_for_status()
    except Exception as e:
      print(f'Agentix error: {e}')

    return result

  mlflow.create_experiment = intercept_create_experiment

  _original_client_create_experiment = mlflow.MlflowClient.create_experiment
  def intercept_client_create_experiment(*args, **kwargs):
    check_token(base_url, key)
    result = _original_client_create_experiment(*args, **kwargs)

    try: 
      experiment = mlflow.MlflowClient.get_experiment(experiment_id=result)
      response = requests.post(f'{base_url}/experiments?token={key}&subscriberId={subscriber}', json={
        "experimentId": experiment.experiment_id,
        "name": experiment.name,
        "stage": experiment.lifecycle_stage,
        "createdAt": experiment.creation_time,
        "updatedAt": experiment.last_update_time,
      })
      response.raise_for_status()
    except Exception as e:
      print(f'Agentix error: {e}')

    return result

  mlflow.MlflowClient.create_experiment = intercept_client_create_experiment
  mlflow.tracking.MlflowClient.create_experiment = intercept_client_create_experiment

  _original_delete_experiment = mlflow.delete_experiment
  def intercept_delete_experiment(*args, **kwargs):
    check_token(base_url, key)
    result = _original_delete_experiment(*args, **kwargs)
    
    try: 
      experiment_id = kwargs.get("experiment_id") or args[0]
      response = requests.delete(f'{base_url}/experiments/{experiment_id}?token={key}&subscriberId={subscriber}')
      response.raise_for_status()
    except Exception as e:
      print(f'Agentix error: {e}')

    return result

  mlflow.delete_experiment = intercept_delete_experiment

  _original_client_delete_experiment = mlflow.MlflowClient.delete_experiment
  def intercept_client_delete_experiment(*args, **kwargs):
    check_token(base_url, key)
    result = _original_client_delete_experiment(*args, **kwargs)
    
    try: 
      experiment_id = kwargs.get("experiment_id") or args[0]
      response = requests.delete(f'{base_url}/experiments/{experiment_id}?token={key}&subscriberId={subscriber}')
      response.raise_for_status()
    except Exception as e:
      print(f'Agentix error: {e}')

    return result

  mlflow.MlflowClient.delete_experiment = intercept_client_delete_experiment
  mlflow.tracking.MlflowClient.delete_experiment = intercept_client_delete_experiment

  _original_set_experiment = mlflow.set_experiment
  def intercept_set_experiment(*args, **kwargs):
    check_token(base_url, key)
    experiment = _original_set_experiment(*args, **kwargs)
    
    try: 
      response = requests.post(f'{base_url}/experiments?token={key}&subscriberId={subscriber}', json={
        "experimentId": experiment.experiment_id,
        "name": experiment.name,
        "stage": experiment.lifecycle_stage,
        "createdAt": experiment.creation_time,
        "updatedAt": experiment.last_update_time,
      })
      response.raise_for_status()
    except Exception as e:
      print(f'Agentix error: {e}')

    return experiment

  mlflow.set_experiment = intercept_set_experiment