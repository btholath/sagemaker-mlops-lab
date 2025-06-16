"""
Ingest traffic data into SageMaker Feature Store from local machine using Boto3 + SageMaker SDK and environment variables.
"""

import pandas as pd
import boto3
import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="traffic/.env")

region = os.getenv("AWS_REGION")
role = os.getenv("SAGEMAKER_ROLE")
bucket = os.getenv("S3_BUCKET")
prefix = os.getenv("S3_PREFIX")
feature_group_name = os.getenv("FEATURE_GROUP_NAME")

# Initialize SageMaker session
session = sagemaker.Session()
df = pd.read_csv("/workspaces/sagemaker-mlops-lab/traffic/1_data_preparation/traffic_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"]).astype(str)  # Ensure ISO format

# Create Feature Group
record_identifier = "incident"
event_time_feature = "timestamp"

feature_group = FeatureGroup(name=feature_group_name, sagemaker_session=session)
feature_group.load_feature_definitions(data_frame=df)

feature_group.create(
    s3_uri=f"s3://{bucket}/{prefix}/feature-store/ingest/",
    record_identifier_name=record_identifier,
    event_time_feature_name=event_time_feature,
    role_arn=role,
    enable_online_store=True
)

feature_group.wait_for_create()
print(f"✅ Feature Group '{feature_group_name}' created successfully.")
