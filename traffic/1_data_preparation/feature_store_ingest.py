"""
Ingest traffic data into SageMaker Feature Store from local machine using Boto3 + SageMaker SDK and environment variables.
"""

import os
import pandas as pd
import boto3
import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup
from dotenv import load_dotenv

# Load environment variables from ../.env
load_dotenv(dotenv_path="../.env")

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
df = pd.read_csv(csv_path)

# Convert timestamp column to ISO 8601 string
print(df["timestamp"].head())
#df["timestamp"] = pd.to_datetime(df["timestamp"]).astype(str)
#df["timestamp"] = pd.to_datetime(df["timestamp"], format="%m/%d/%y %H:%M").astype(str)

# # Original timestamp format: 1/1/23 0:00
df["timestamp"] = pd.to_datetime(df["timestamp"], format="%m/%d/%y %H:%M")
# # Convert to required ISO 8601 format
df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")



# Define FeatureGroup
record_identifier = "incident"
event_time_feature = "timestamp"

feature_group = FeatureGroup(name=feature_group_name, sagemaker_session=session)
feature_group.load_feature_definitions(data_frame=df) # Registering the schema from a Pandas DataFrame

# Create the Feature Group (Writes the schema to SageMaker Feature Store)
feature_group.create(
    s3_uri=f"s3://{bucket}/{prefix}/feature-store/ingest/", # Sets up offline (S3)
    record_identifier_name=record_identifier,
    event_time_feature_name=event_time_feature,
    role_arn=role,
    enable_online_store=True #online (real-time) storage backends
)

# Wait for creation to complete
import time

status = None
while status != "Created":
    status = feature_group.describe().get("FeatureGroupStatus")
    print(f"⏳ Feature Group status: {status}")
    if status in ("Failed", "Deleting"):
        raise RuntimeError(f"❌ Feature Group creation failed with status: {status}")
    time.sleep(10)

print(f"✅ Feature Group '{feature_group_name}' created successfully.")


# 🔄 Ingest data into Feature Store
print(f"📥 Ingesting {len(df)} records into Feature Store...")
feature_group.ingest(data_frame=df, max_workers=3, wait=True)

print("✅ Data ingestion completed successfully.")
