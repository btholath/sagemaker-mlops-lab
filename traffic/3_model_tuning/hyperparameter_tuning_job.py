"""
Run a hyperparameter tuning job for XGBoost using SageMaker SDK.
"""

import os
from dotenv import load_dotenv
import sagemaker
from sagemaker.inputs import TrainingInput
from sagemaker.tuner import HyperparameterTuner, IntegerParameter, ContinuousParameter
from sagemaker.xgboost.estimator import XGBoost

# Load environment variables
load_dotenv("../.env")

region = os.getenv("AWS_REGION")
role = os.getenv("SAGEMAKER_ROLE")
bucket = os.getenv("S3_BUCKET")
prefix = os.getenv("S3_PREFIX")

# Initialize SageMaker session
session = sagemaker.Session()

# Training data location
s3_train_path = f"s3://{bucket}/{prefix}/train"

# Define XGBoost estimator
xgb_estimator = XGBoost(
    entry_point="train_script.py",  # ✅ Must be the script filename
    framework_version="1.3-1",
    instance_type="ml.m5.large",
    instance_count=1,
    output_path=f"s3://{bucket}/{prefix}/output",
    role=role,
    sagemaker_session=session,
    hyperparameters={
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "num_round": 100
    },
    metric_definitions=[
        {
            "Name": "validation:auc",
            "Regex": ".*\\[[0-9]+\\].*validation-auc:([0-9\\.]+)"
        }
    ]
)

# Define hyperparameter ranges
hyperparameter_ranges = {
    "max_depth": IntegerParameter(3, 10),
    "eta": ContinuousParameter(0.1, 0.5),
    "gamma": ContinuousParameter(0, 10),
    "min_child_weight": IntegerParameter(1, 10),
    "subsample": ContinuousParameter(0.5, 1)
}

# Set up hyperparameter tuning job
tuner = HyperparameterTuner(
    estimator=xgb_estimator,
    objective_metric_name="validation:auc",
    hyperparameter_ranges=hyperparameter_ranges,
    objective_type="Maximize",
    max_jobs=10,
    max_parallel_jobs=2
)

# Start tuning job
tuner.fit({"train": TrainingInput(s3_train_path, content_type="csv")})
print("🚀 Hyperparameter tuning job started.")
