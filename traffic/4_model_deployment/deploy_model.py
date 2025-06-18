"""
Deploy the trained XGBoost model to a SageMaker endpoint.
"""

import sagemaker
from sagemaker.xgboost.model import XGBoostModel
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="traffic/.env")

region = os.getenv("AWS_REGION")
role = os.getenv("SAGEMAKER_ROLE")
bucket = os.getenv("S3_BUCKET")
prefix = os.getenv("S3_PREFIX")
endpoint_name = os.getenv("ENDPOINT_NAME")

session = sagemaker.Session()

# Model artifact location
model_artifact = f"s3://{bucket}/{prefix}/output/xgboost-traffic-local/output/model.tar.gz"

# Deploy
xgb_model = XGBoostModel(model_data=model_artifact,
                         role=role,
                         framework_version="1.3-1",
                         sagemaker_session=session)

predictor = xgb_model.deploy(
    endpoint_name=endpoint_name,
    instance_type="ml.m5.large",
    initial_instance_count=1
)

print(f"✅ Endpoint deployed: {predictor.endpoint_name}")
