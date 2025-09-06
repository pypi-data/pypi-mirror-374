# Semantix Agentix

A Python library for AI governance and experiment tracking that integrates with MLflow to provide comprehensive monitoring and management of machine learning experiments.

## Overview

Semantix Agentix is designed to work seamlessly with MLflow, providing enhanced tracking capabilities and governance features for machine learning projects. The library automatically intercepts MLflow operations and sends data to the Semantix AI governance platform for monitoring and analysis.

## Prerequisites

Before using Semantix Agentix, you need to have MLflow running locally or have access to an MLflow tracking server.

### Starting MLflow

To start MLflow locally, run the following command in your terminal:

```bash
mlflow server --host 127.0.0.1 --port 5000
```

This will start MLflow on `http://127.0.0.1:5000`.

## Installation

Install the package using pip:

```bash
pip install semantix-agentix
```

## Quick Start

Here's how to get started with Semantix Agentix:

```python
from semantix_agentix import agentix
import mlflow

# Initialize Agentix with your token
agentix(token="your-token-here", development=True)

# Configure MLflow
mlflow.set_tracking_uri('http://127.0.0.1:5000')
mlflow.set_experiment(experiment_name="agentix")
```

## Configuration

### Development vs Production

The library supports two environments:

- **Development**: Set `development=True` to use the development API endpoint
- **Production**: Set `development=False` (default) to use the production API endpoint

### Authentication

You need a valid token to use Semantix Agentix. The token is validated against the Semantix platform when initializing the library.

## Features

- **Automatic MLflow Integration**: Seamlessly integrates with existing MLflow workflows
- **Experiment Tracking**: Monitors and tracks MLflow experiments
- **Model Monitoring**: Tracks model versions and metadata
- **Run Interception**: Captures run data and metrics
- **Trace Management**: Provides methods to save and manage MLflow traces
- **AI Governance**: Sends data to Semantix platform for governance and compliance

## API Reference

### `agentix(token, development=False)`

Initialize the Agentix library.

**Parameters:**

- `token` (str): Your Semantix Agentix authentication token
- `development` (bool): Whether to use development environment (default: False)

**Raises:**

- `ValueError`: If the token is invalid or authentication fails

### `save_traces(trace_id, experiment_id)`

Save MLflow traces to the Semantix platform.

**Parameters:**

- `trace_id` (str): The MLflow trace ID
- `experiment_id` (str): The experiment ID to associate the trace with

## Example Usage

### Basic MLflow Integration

```python
from semantix_agentix import agentix
import mlflow
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Initialize Agentix
agentix(token="your-token-here", development=True)

# Configure MLflow
mlflow.set_tracking_uri('http://127.0.0.1:5000')
mlflow.set_experiment(experiment_name="my_experiment")

# Your MLflow code
with mlflow.start_run():
    # Load and prepare data
    data = pd.read_csv('your_data.csv')
    X_train, X_test, y_train, y_test = train_test_split(
        data.drop('target', axis=1),
        data['target'],
        test_size=0.2
    )

    # Train model
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    # Log metrics
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)

    # Log model
    mlflow.sklearn.log_model(model, "model")
```

### Production Model Tracing

For production environments where you need to trace running models and capture detailed execution data, use MLflow tracing with Agentix:

```python
import os
from semantix_agentix import agentix
import mlflow
from mlflow.tracing.attributes import SpanAttributeKey

# Initialize Agentix
agentix_instance = agentix(token="your-token-here", development=False)

# Configure MLflow
mlflow.set_tracking_uri('http://127.0.0.1:5000')
mlflow.set_experiment(experiment_name="production_model")

def production_model_inference(query, index_path, experiment):
    """
    Example of production model inference with tracing.
    This pattern is ideal for monitoring running models in production.
    """
    # Check if MLflow tracking is enabled via environment variable
    use_mlflow = os.environ.get("MLFLOW_TRACKING", "False").lower() == "true"

    if use_mlflow:
        with mlflow.start_run(log_system_metrics=True):
            with mlflow.start_span(name="API") as span:
                # Set input data for tracing
                span.set_inputs({"message": query})

                # Your model inference logic here
                query_engine = get_query_engine(index_path=index_path, streaming=False)
                token_counter.reset_counts()
                response = query_engine.query(query)

                # Capture token usage metrics
                output_tokens = counter.completion_llm_token_count
                input_tokens = counter.prompt_llm_token_count
                token_counter.reset_counts()

                # Prepare usage data
                usage_data = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                }

                # Set span attributes with usage data
                span.set_attributes(usage_data)
                span.set_outputs({"response": response.response or "None"})

            # Get trace ID for saving to Agentix
            trace_id = span.get_attribute(SpanAttributeKey.REQUEST_ID)

            # Save traces to Semantix platform for governance
            agentix_instance.save_traces(trace_id=trace_id, experiment_id=experiment.experiment_id)

            return response.response or "None", usage_data

    else:
        # Fallback for when MLflow tracking is disabled
        query_engine = get_query_engine(index_path=index_path, streaming=False)
        response = query_engine.query(query)
        return response.response or "None", {}
```

### Environment Configuration

For production tracing, set the environment variable to enable MLflow tracking:

```bash
export MLFLOW_TRACKING=true
```

Or in your application:

```python
import os
os.environ["MLFLOW_TRACKING"] = "true"
```

This tracing approach is particularly useful for:

- **Production Monitoring**: Track model performance and usage in real-time
- **Token Usage Tracking**: Monitor LLM token consumption and costs
- **Input/Output Logging**: Capture model inputs and outputs for analysis
- **System Metrics**: Log system performance metrics during inference
- **Governance Compliance**: Send trace data to Semantix for AI governance

## Dependencies

- `mlflow>=3.3.1`
- `psycopg2-binary>=2.9.10`
- `setuptools>=77.0.3`
- `wheel>=0.45.0`
- `twine>=6.2.0`

## Error Handling

The library includes comprehensive error handling:

- Invalid tokens will raise a `ValueError`
- Network errors are caught and logged
- MLflow integration errors are handled gracefully

## Support

For support and questions, please contact the Semantix team or refer to the official documentation.

## License

This project is licensed under the terms specified in the LICENSE file.
