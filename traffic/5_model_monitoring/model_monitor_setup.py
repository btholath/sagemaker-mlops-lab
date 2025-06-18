"""
Set up model monitoring using SageMaker Model Monitor from a local environment.
Enables data capture on an endpoint to monitor incoming requests and responses.
"""

import os
import logging
from dotenv import load_dotenv
import sagemaker
from sagemaker.model_monitor import DataCaptureConfig
from sagemaker.predictor import Predictor

# ---------------------- Logger Setup ----------------------
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------------- Load Environment ----------------------
load_dotenv(dotenv_path="../.env")
endpoint_name = os.getenv("ENDPOINT_NAME")
bucket = os.getenv("S3_BUCKET")
role = os.getenv("SAGEMAKER_ROLE")

if not all([endpoint_name, bucket, role]):
    logger.error("❌ Required environment variables missing.")
    exit(1)

# ---------------------- SageMaker Session ----------------------
session = sagemaker.Session()
logger.info("🔁 Connected to SageMaker session in region: %s", session.boto_region_name)

# ---------------------- Predictor Setup ----------------------
predictor = Predictor(
    endpoint_name=endpoint_name,
    sagemaker_session=session
)

# ---------------------- Enable Data Capture ----------------------
capture_prefix = "monitoring/capture"
destination_s3_uri = f"s3://{bucket}/{capture_prefix}"

data_capture_config = DataCaptureConfig(
    enable_capture=True,
    sampling_percentage=100,
    destination_s3_uri=destination_s3_uri,
    capture_options=["REQUEST", "RESPONSE"],
    csv_content_types=["text/csv"],
    json_content_types=["application/json"]
)

predictor.data_capture_config = data_capture_config

logger.info("✅ Data capture enabled on endpoint: %s", endpoint_name)
logger.info("📦 Sampling 100%% of traffic")
logger.info("📁 Captured data will be stored in: %s", destination_s3_uri)

# ---------------------- Optional: Log for Future Monitoring Features ----------------------
# TODO: Add scheduled monitoring jobs using Baseline + Statistics + Constraints
# TODO: Stream CloudWatch logs or trigger alarms if error rate spikes

# ------------------------------------------------------------
# Run inference calls now to actually generate captured data!
# You can later validate captured requests in S3 monitoring/capture/
# ------------------------------------------------------------
