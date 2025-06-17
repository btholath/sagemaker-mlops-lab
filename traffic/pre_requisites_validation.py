import os
import boto3
import pandas as pd
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv(dotenv_path="./.env")

AWS_REGION = os.getenv("AWS_REGION")
ROLE_ARN = os.getenv("SAGEMAKER_ROLE")
ROLE_NAME = ROLE_ARN.split("/")[-1]
BUCKET_NAME = os.getenv("S3_BUCKET")

# Initialize boto3 clients
iam_client = boto3.client("iam", region_name=AWS_REGION)
s3_client = boto3.client("s3", region_name=AWS_REGION)

def check_bucket_exists(bucket_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        return "✅", "Bucket exists"
    except ClientError as e:
        return "❌", e.response["Error"]["Message"]

def check_iam_role_exists(role_name):
    try:
        iam_client.get_role(RoleName=role_name)
        return "✅", "Role exists"
    except ClientError as e:
        return "❌", e.response["Error"]["Message"]

def check_policy_attached(role_name, policy_fragment):
    try:
        attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)
        for policy in attached_policies['AttachedPolicies']:
            if policy_fragment in policy['PolicyName']:
                return "✅", policy['PolicyName']
        return "❌", f"{policy_fragment} not found"
    except ClientError as e:
        return "❌", e.response["Error"]["Message"]

# Run validations
checks = []

# Check S3 bucket
status, detail = check_bucket_exists(BUCKET_NAME)
checks.append({"Check": "S3 Bucket Exists", "Status": status, "Details": detail})

# Check IAM role
status, detail = check_iam_role_exists(ROLE_NAME)
checks.append({"Check": "IAM Role Exists", "Status": status, "Details": detail})

# Check IAM policies
required_policies = [
    "AmazonS3FullAccess",
    "AmazonSageMakerFullAccess",
    "AmazonSageMakerFeatureStoreAccess"
]

for policy in required_policies:
    status, detail = check_policy_attached(ROLE_NAME, policy)
    checks.append({"Check": f"Policy Attached: {policy}", "Status": status, "Details": detail})

# Display results
df = pd.DataFrame(checks)
print(df.to_markdown(index=False))
