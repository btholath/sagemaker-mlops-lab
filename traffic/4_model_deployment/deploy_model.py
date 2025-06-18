"""
Deploy the trained XGBoost model to a SageMaker endpoint.

This script will:
- Load the model artifact from S3 (model.tar.gz)
- Deploy it to a new or existing SageMaker endpoint using the endpoint name from .env
- Use instance type like ml.m5.large for hosting
"""

import os
import logging
from dotenv import load_dotenv
import sagemaker
from sagemaker.xgboost.model import XGBoostModel

# ----------------- Logger Setup -----------------
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------- Load Config -----------------
load_dotenv(dotenv_path="../.env")
region = os.getenv("AWS_REGION")
role = os.getenv("SAGEMAKER_ROLE")
bucket = os.getenv("S3_BUCKET")
prefix = os.getenv("S3_PREFIX")
endpoint_name = os.getenv("ENDPOINT_NAME")

session = sagemaker.Session()

# ----------------- Model Path -----------------
# Example: xgboost-traffic-local or a specific training job output
# model_artifact = f"s3://{bucket}/{prefix}/output/xgboost-traffic-local/output/model.tar.gz"
model_artifact = f"s3://{bucket}/{prefix}/output/sagemaker-xgboost-2025-06-18-21-28-12-436/output/model.tar.gz"

logger.info("🚀 Deploying model from: %s", model_artifact)
logger.info("🛠️ Using endpoint: %s", endpoint_name)

# ----------------- Deploy Model -----------------
try:
    xgb_model = XGBoostModel(
        model_data=model_artifact,
        role=role,
        framework_version="1.3-1",
        sagemaker_session=session
    )

    predictor = xgb_model.deploy(
        endpoint_name=endpoint_name,
        instance_type="ml.m5.large",
        initial_instance_count=1
    )

    logger.info("✅ Endpoint deployed: %s", predictor.endpoint_name)

except Exception as e:
    logger.exception("❌ Failed to deploy the model.")
    raise
