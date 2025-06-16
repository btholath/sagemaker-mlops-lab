"""
Run a hyperparameter tuning job for XGBoost using SageMaker SDK locally.
"""

import sagemaker
from sagemaker.tuner import HyperparameterTuner, IntegerParameter, ContinuousParameter
from sagemaker.inputs import TrainingInput
from sagemaker.xgboost.estimator import XGBoost
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="traffic/.env")

region = os.getenv("AWS_REGION")
role = os.getenv("SAGEMAKER_ROLE")
bucket = os.getenv("S3_BUCKET")
prefix = os.getenv("S3_PREFIX")

session = sagemaker.Session()

# Reuse training input path
s3_train_path = f"s3://{bucket}/{prefix}/train/train.csv"

# Estimator
xgb = XGBoost(
    entry_point=None,
    framework_version="1.3-1",
    instance_type="ml.m5.large",
    instance_count=1,
    output_path=f"s3://{bucket}/{prefix}/output",
    role=role,
    objective="binary:logistic",
    sagemaker_session=session
)

# Hyperparameter ranges
hyperparameter_ranges = {
    "max_depth": IntegerParameter(3, 10),
    "eta": ContinuousParameter(0.1, 0.5),
    "gamma": ContinuousParameter(0, 10),
    "min_child_weight": IntegerParameter(1, 10),
    "subsample": ContinuousParameter(0.5, 1)
}

# Objective
tuner = HyperparameterTuner(
    estimator=xgb,
    objective_metric_name="validation:auc",
    hyperparameter_ranges=hyperparameter_ranges,
    objective_type="Maximize",
    max_jobs=10,
    max_parallel_jobs=2
)

# Start tuning job
tuner.fit({"train": TrainingInput(s3_train_path, content_type="csv")})
print("🚀 Hyperparameter tuning job started.")


# Save the updated script
tuning_script_path.write_text(updated_tuning_script)
tuning_script_path.as_posix()