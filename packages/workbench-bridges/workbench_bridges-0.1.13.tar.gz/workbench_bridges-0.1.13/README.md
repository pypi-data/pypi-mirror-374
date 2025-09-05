# Workbench Bridges
End User Application Bridges to Workbench/AWS ML Pipelines.

## Installation
```
pip install workbench-bridges
```

## Examples
Application invocation of an Endpoint on AWS.

```
import pandas as pd

# Workbench-Bridges Imports
from workbench_bridges.endpoints.fast_inference import fast_inference


if __name__ == "__main__":

    # Data will be passed in from the End-User Application
    eval_df = pd.read_csv("test_evaluation_data.csv")

    # Run inference on AWS Endpoint
    endpoint_name = "test-my-endpoint"
    results = fast_inference(endpoint_name, eval_df)

    # A Dataframe with Predictions is returned
    print(results)
```
