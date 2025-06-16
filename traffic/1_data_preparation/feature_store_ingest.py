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
df["timestamp"] = pd.to_datetime(df["timestamp"]).astype(str)




# Define FeatureGroup
record_identifier = "incident"
event_time_feature = "timestamp"

feature_group = FeatureGroup(name=feature_group_name, sagemaker_session=session)
feature_group.load_feature_definitions(data_frame=df)

# Create the Feature Group
feature_group.create(
    s3_uri=f"s3://{bucket}/{prefix}/feature-store/ingest/",
    record_identifier_name=record_identifier,
    event_time_feature_name=event_time_feature,
    role_arn=role,
    enable_online_store=True
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
