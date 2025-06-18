"""
Set up model monitoring using SageMaker Model Monitor from a local environment.
"""

import sagemaker
from sagemaker.model_monitor import DataCaptureConfig
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="traffic/.env")

endpoint_name = os.getenv("ENDPOINT_NAME")
bucket = os.getenv("S3_BUCKET")

session = sagemaker.Session()
role = os.getenv("SAGEMAKER_ROLE")

predictor = sagemaker.predictor.Predictor(
    endpoint_name=endpoint_name,
    sagemaker_session=session
)

# Enable Data Capture
data_capture_config = DataCaptureConfig(
    enable_capture=True,
    sampling_percentage=100,
    destination_s3_uri=f"s3://{bucket}/monitoring/capture",
    capture_options=["REQUEST", "RESPONSE"]
)

predictor.data_capture_config = data_capture_config

print("✅ Model monitoring enabled on endpoint.")
