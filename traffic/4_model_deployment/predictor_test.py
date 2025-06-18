"""
Send sample predictions to the deployed endpoint using Boto3 Predictor.

This script will:
- Connect to the deployed endpoint using the Predictor class
- Download validation.csv from S3
- Send test samples for prediction
- Print the returned inference results
"""

import os
import logging
import boto3
import pandas as pd
import sagemaker
from sagemaker.predictor import Predictor
from dotenv import load_dotenv

# ----------------- Logger Setup -----------------
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------- Load Configuration -----------------
load_dotenv(dotenv_path="../.env")
endpoint_name = os.getenv("ENDPOINT_NAME")
bucket = os.getenv("S3_BUCKET")
validation_key = "traffic-pipeline/validation/validation.csv"
local_path = "/tmp/validation.csv"

if not endpoint_name:
    logger.error("❌ ENDPOINT_NAME not found in environment variables.")
    exit(1)

if not bucket:
    logger.error("❌ S3_BUCKET not found in environment variables.")
    exit(1)

# ----------------- Download from S3 -----------------
try:
    logger.info("⬇️ Downloading validation.csv from s3://%s/%s", bucket, validation_key)
    s3 = boto3.client("s3")
    s3.download_file(bucket, validation_key, local_path)
    logger.info("✅ Downloaded to %s", local_path)

except Exception as e:
    logger.exception("❌ Failed to download validation.csv from S3.")
    raise

# ----------------- Load Sample Data -----------------
try:
    validation_df = pd.read_csv(local_path)
    test_sample = validation_df.iloc[:5].values
    logger.info("📦 Prepared %d records for inference", len(test_sample))

except Exception as e:
    logger.exception("❌ Failed to load validation CSV.")
    raise

# ----------------- Connect to Endpoint -----------------
try:
    logger.info("🔌 Connecting to endpoint: %s", endpoint_name)
    session = sagemaker.Session()

    from sagemaker.serializers import CSVSerializer

    predictor = Predictor(
        endpoint_name=endpoint_name,
        sagemaker_session=session,
        serializer=CSVSerializer()
    )
    # ----------------- Send Predictions -----------------
    try:
        import numpy as np

        # Convert NumPy array to CSV string (no header, no index)
        csv_data = pd.DataFrame(test_sample).to_csv(header=False, index=False).encode("utf-8")
        import numpy as np
        test_sample = validation_df.drop(columns=["incident"]).iloc[:5].values  # Remove label column

        preds = predictor.predict(
            data=test_sample
        )
        logger.info("📈 Predictions received:")
        print(preds)
        decoded = preds.decode("utf-8").strip().split("\n")
        print("✅ Predictions:")
        for i, p in enumerate(decoded, 1):
            print(f"Sample {i}: Probability = {float(p):.4f}")

        binary_preds = [1 if float(p) > 0.5 else 0 for p in decoded]
   
    except Exception as e:
        logger.exception("❌ Failed to get predictions from endpoint.")
        raise


except Exception as e:
    logger.exception("❌ Failed to get predictions from endpoint.")
    raise
