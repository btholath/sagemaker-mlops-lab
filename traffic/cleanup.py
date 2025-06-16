import boto3
import os
from dotenv import load_dotenv

# Load env
load_dotenv("traffic/.env")

region = os.getenv("AWS_REGION")
endpoint_name = os.getenv("ENDPOINT_NAME")
feature_group_name = os.getenv("FEATURE_GROUP_NAME")
bucket = os.getenv("S3_BUCKET")

sm_client = boto3.client("sagemaker", region_name=region)
s3 = boto3.resource("s3")

# Delete Endpoint
try:
    sm_client.delete_endpoint(EndpointName=endpoint_name)
    sm_client.delete_endpoint_config(EndpointConfigName=endpoint_name)
    sm_client.delete_model(ModelName=endpoint_name)
    print(f"✅ Deleted endpoint, config, and model: {endpoint_name}")
except sm_client.exceptions.ClientError as e:
    print(f"⚠️ Endpoint deletion error: {e}")

# Delete Feature Group
try:
    sm_client.delete_feature_group(FeatureGroupName=feature_group_name)
    print(f"✅ Deleted feature group: {feature_group_name}")
except sm_client.exceptions.ClientError as e:
    print(f"⚠️ Feature group deletion error: {e}")

# Delete S3 contents
bucket_obj = s3.Bucket(bucket)
bucket_obj.objects.all().delete()
print(f"✅ Deleted all contents in S3 bucket: {bucket}")
