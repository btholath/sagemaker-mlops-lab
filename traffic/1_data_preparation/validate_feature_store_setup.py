import boto3
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time

# Load environment variables
load_dotenv(dotenv_path="../.env")

region = os.getenv("AWS_REGION")
bucket = os.getenv("S3_BUCKET")
prefix = os.getenv("S3_PREFIX")
feature_group_name = os.getenv("FEATURE_GROUP_NAME")
role_arn = os.getenv("SAGEMAKER_ROLE")

# Boto3 clients
sagemaker = boto3.client("sagemaker", region_name=region)
s3 = boto3.client("s3", region_name=region)
iam = boto3.client("iam", region_name=region)
athena = boto3.client("athena", region_name=region)
featurestore_runtime = boto3.client("sagemaker-featurestore-runtime", region_name=region)

results = []

# 1. Validate Feature Group
print("1. Validate Feature Group")
try:
    fg_desc = sagemaker.describe_feature_group(FeatureGroupName=feature_group_name)
    results.append(["Feature Group Exists", "✅", fg_desc["FeatureGroupStatus"]])
except sagemaker.exceptions.ResourceNotFound:
    results.append(["Feature Group Exists", "❌", "Not found"])
    fg_desc = {}

# 2. Validate Feature Group Status
print("2. Validate Feature Group Status")
if fg_desc:
    status = fg_desc["FeatureGroupStatus"]
    results.append(["Feature Group Status", "✅" if status == "Created" else "⚠️", status])

    # 3. Validate S3 Offline Store URI
    print("3. Validate S3 Offline Store URI")
    s3_uri = fg_desc.get("OfflineStoreConfig", {}).get("S3StorageConfig", {}).get("S3Uri", "")
    if s3_uri:
        bucket_name = s3_uri.replace("s3://", "").split("/")[0]
        try:
            s3.head_bucket(Bucket=bucket_name)
            results.append(["Offline Store S3 Bucket Exists", "✅", bucket_name])
        except Exception as e:
            results.append(["Offline Store S3 Bucket Exists", "❌", str(e)])
    else:
        results.append(["Offline Store S3 URI", "❌", "Not configured"])

    # 4. Validate IAM Role and Policies
    print("4. Validate IAM Role and Policies")
    try:
        attached_policies = iam.list_attached_role_policies(RoleName=role_arn.split("/")[-1])
        policy_names = [p["PolicyName"] for p in attached_policies["AttachedPolicies"]]
        required_policies = [
            "AmazonSageMakerFullAccess",
            "AmazonS3FullAccess",
            "AmazonSageMakerFeatureStoreAccess"
        ]
        for policy in required_policies:
            status = "✅" if policy in policy_names else "❌"
            results.append([f"Policy Attached: {policy}", status, policy])
    except Exception as e:
        results.append(["IAM Role Check", "❌", str(e)])

# Output results
df = pd.DataFrame(results, columns=["Check", "Status", "Details"])
print(df.to_markdown(index=False))