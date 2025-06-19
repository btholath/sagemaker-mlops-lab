"""
Run a hyperparameter tuning job for XGBoost using SageMaker SDK.
"""

import os
import logging
from dotenv import load_dotenv
import sagemaker
from sagemaker.inputs import TrainingInput
from sagemaker.tuner import HyperparameterTuner, IntegerParameter, ContinuousParameter
from sagemaker.xgboost.estimator import XGBoost

# ─────────────────────────────────────────────────────────────
# Configure logging
# ─────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Load environment variables
# ─────────────────────────────────────────────────────────────
# Load environment variables
load_dotenv("../.env")
region = os.getenv("AWS_REGION")
role = os.getenv("SAGEMAKER_ROLE")
bucket = os.getenv("S3_BUCKET")
prefix = os.getenv("S3_PREFIX")

logger.info(f"AWS Region: {region}")
logger.info(f"Using S3 Bucket: {bucket}")
logger.info(f"S3 Prefix: {prefix}")

# ─────────────────────────────────────────────────────────────
# Initialize SageMaker session
# ─────────────────────────────────────────────────────────────
# Initialize SageMaker session
session = sagemaker.Session()

# Training data location
s3_train_path = f"s3://{bucket}/{prefix}/train"
output_path = f"s3://{bucket}/{prefix}/output"

# ─────────────────────────────────────────────────────────────
# Define XGBoost Estimator
# ─────────────────────────────────────────────────────────────
logger.info("Configuring XGBoost Estimator...")
xgb_estimator = XGBoost(
    entry_point="train_script.py",  # ✅ Must be the script filename
    framework_version="1.3-1",
    instance_type="ml.m5.large",
    instance_count=1,
    output_path=output_path, # Ensures SageMaker uploads everything from /opt/ml/output/
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

# ─────────────────────────────────────────────────────────────
# Define hyperparameter search space
# ─────────────────────────────────────────────────────────────
# max_depth - The maximum depth per tree. A deeper tree might increase the performance, but also the complexity and chances to overfit.
# eta - learning rate
# gamma - Gamma is a pseudo-regularisation parameter (Lagrangian multiplier), and depends on the other parameters. The higher Gamma is, the higher the regularization.
# subsample - Represents the fraction of observations to be sampled for each tree. A lower values prevent overfitting but might lead to under-fitting.

logger.info("Defining hyperparameter search ranges...")
hyperparameter_ranges = {
    "max_depth": IntegerParameter(3, 10),
    "eta": ContinuousParameter(0.1, 0.5),
    "gamma": ContinuousParameter(0, 10),
    "min_child_weight": IntegerParameter(1, 10),
    "subsample": ContinuousParameter(0.5, 1)
}

# ─────────────────────────────────────────────────────────────
# Create Hyperparameter Tuner
# ─────────────────────────────────────────────────────────────
logger.info("Initializing Hyperparameter Tuner...")
tuner = HyperparameterTuner(
    estimator=xgb_estimator,
    objective_metric_name="validation:auc",
    hyperparameter_ranges=hyperparameter_ranges,
    objective_type="Maximize",
    max_jobs=10,
    max_parallel_jobs=2
)

# ─────────────────────────────────────────────────────────────
# Launch tuning job
# ─────────────────────────────────────────────────────────────
logger.info("Launching hyperparameter tuning job...")
tuner.fit({"train": TrainingInput(s3_train_path, content_type="csv")})
logger.info("🚀 Hyperparameter tuning job started.")
