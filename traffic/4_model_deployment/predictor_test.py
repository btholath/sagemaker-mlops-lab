"""
Send sample predictions to the deployed endpoint using Boto3 Predictor.

This script will:
- Connect to the deployed endpoint using the Predictor class
- Send test samples (from validation.csv) for prediction
- Print the returned inference results
"""

import os
import logging
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

if not endpoint_name:
    logger.error("❌ ENDPOINT_NAME not found in environment variables.")
    exit(1)

session = sagemaker.Session()

# ----------------- Connect to Endpoint -----------------
logger.info("🔌 Connecting to SageMaker endpoint: %s", endpoint_name)

predictor = Predictor(
    endpoint_name=endpoint_name,
    sagemaker_session=session
)

# ----------------- Load Sample Data -----------------
try:
    val_csv_path = "traffic/2_model_training/validation.csv"
    validation_df = pd.read_csv(val_csv_path)
    logger.info("📄 Loaded validation data from %s", val_csv_path)

    test_sample = validation_df.iloc[:5].values
    logger.info("📦 Sending %d sample records for inference", len(test_sample))

except Exception as e:
    logger.exception("❌ Failed to load or prepare test data.")
    raise

# ----------------- Send Predictions -----------------
try:
    preds = predictor.predict(test_sample)
    logger.info("📈 Predictions received:")
    print(preds)

except Exception as e:
    logger.exception("❌ Failed to get predictions from endpoint.")
    raise
