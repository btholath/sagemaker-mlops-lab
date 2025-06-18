"""
Ingest traffic data into SageMaker Feature Store from local machine using Boto3 + SageMaker SDK and environment variables.
"""

import os
import pandas as pd
import boto3
import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup
from dotenv import load_dotenv
import logging

# Load environment variables from ../.env
load_dotenv(dotenv_path="../.env")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Extract environment variables
region = os.getenv("AWS_REGION")
role = os.getenv("SAGEMAKER_ROLE")
bucket = os.getenv("S3_BUCKET")
prefix = os.getenv("S3_PREFIX")
feature_group_name = os.getenv("FEATURE_GROUP_NAME")

if not role:
    raise ValueError("❌ SAGEMAKER_ROLE not found. Check your .env file path and contents.")

# Initialize SageMaker session
boto_session = boto3.Session(region_name=region)
session = sagemaker.Session(boto_session=boto_session)

# Load traffic data CSV
csv_path = "traffic_data.csv"  # assumes file is in current directory
try:
    df = pd.read_csv(csv_path)
    logger.info(f"✅ Loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns.")
except Exception as e:
    logger.error("❌ Error loading dataset.", exc_info=True)
    raise e


# Data Validation: Check for missing values
missing_values = df.isnull().sum().sum()
if missing_values > 0:
    raise ValueError(f"❌ Dataset contains {missing_values} missing values. Please clean the data before ingestion.")



# Ensure timestamp format consistency
"""
try:
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%m/%d/%y %H:%M").dt.strftime("%Y-%m-%dT%H:%M:%SZ")
except Exception as e:
    logger.error("❌ Timestamp format mismatch. Ensure it follows MM/DD/YY HH:MM format.", exc_info=True)
    raise e
"""
# Convert timestamp column to ISO 8601 string
print(df["timestamp"].head())

try:
    # # Original timestamp format: 1/1/23 0:00
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%m/%d/%y %H:%M")
    # # Convert to required ISO 8601 format
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
except Exception as e:
    logger.error("❌ Timestamp format mismatch. Ensure it follows MM/DD/YY HH:MM format.", exc_info=True)
    raise e

# Define FeatureGroup
record_identifier = "incident"
event_time_feature = "timestamp"

feature_group = FeatureGroup(name=feature_group_name, sagemaker_session=session)
feature_group.load_feature_definitions(data_frame=df) # Registering the schema from a Pandas DataFrame

# Create the Feature Group (Writes the schema to SageMaker Feature Store)
# Create the Feature Group
try:
    feature_group.create(
        s3_uri=f"s3://{bucket}/{prefix}/feature-store/ingest/",
        record_identifier_name=record_identifier,
        event_time_feature_name=event_time_feature,
        role_arn=role,
        enable_online_store=True
    )
except Exception as e:
    logger.error("❌ Error creating Feature Group.", exc_info=True)
    raise e


# Wait for creation to complete
import time

# Monitor Feature Group creation status
while True:
    status = feature_group.describe().get("FeatureGroupStatus")
    logger.info(f"⏳ Feature Group status: {status}")
    if status == "Created":
        logger.info(f"✅ Feature Group '{feature_group_name}' successfully created.")
        break
    elif status in ("Failed", "Deleting"):
        raise RuntimeError(f"❌ Feature Group creation failed with status: {status}")
    time.sleep(10)



# 🔄 Ingest data into Feature Store
try:
    logger.info(f"📥 Ingesting {len(df)} records into Feature Store...")
    ingestion_start_time = time.time()
    feature_group.ingest(data_frame=df, max_workers=3, wait=True)
    ingestion_end_time = time.time()
    elapsed_time = round(ingestion_end_time - ingestion_start_time, 2)
    logger.info(f"✅ Data ingestion completed successfully in {elapsed_time} seconds.")
except Exception as e:
    logger.error("❌ Error during data ingestion.", exc_info=True)
    raise e



# Metadata Tracking: Log ingestion statistics
logger.info(f"📊 Ingested {df.shape[0]} records with {df.shape[1]} features.")
