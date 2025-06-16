# Create starter Python files for Option 1: Local development with Boto3 + SageMaker SDK

file_contents = {
    "traffic/1_data_preparation/feature_store_ingest.py": '''\
"""
Ingest traffic data into SageMaker Feature Store from local machine using Boto3 + SageMaker SDK.
"""

import pandas as pd
import boto3
import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup

# Initialize session
session = sagemaker.Session()
region = session.boto_region_name
role = sagemaker.get_execution_role()
bucket = session.default_bucket()

# Load local CSV
df = pd.read_csv("traffic/1_data_preparation/traffic_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"]).astype(str)  # Convert to ISO format string

# Create Feature Group
feature_group_name = "traffic-feature-group-local"
record_identifier = "incident"
event_time_feature = "timestamp"

feature_group = FeatureGroup(name=feature_group_name, sagemaker_session=session)
feature_group.load_feature_definitions(data_frame=df)

# Create Feature Group
feature_group.create(
    s3_uri=f"s3://{bucket}/feature-store/ingest/",
    record_identifier_name=record_identifier,
    event_time_feature_name=event_time_feature,
    role_arn=role,
    enable_online_store=True
)

# Wait for Feature Group creation
feature_group.wait_for_create()
print(f"✅ Feature Group '{feature_group_name}' created successfully.")
