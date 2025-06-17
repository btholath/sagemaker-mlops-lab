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
    
    # 5. Run Athena Query to Count Records
    print("5. Count records via Athena")

    if fg_desc:
        table_name = fg_desc.get("OfflineStoreConfig", {}).get("DataCatalogConfig", {}).get("TableName")
        database_name = fg_desc.get("OfflineStoreConfig", {}).get("DataCatalogConfig", {}).get("Database")
        if table_name and database_name:
            output_s3_uri = f"s3://{bucket}/{prefix}/athena/results/"
            query_string = f'SELECT COUNT(*) AS record_count FROM "{database_name}"."{table_name}"'

            try:
                response = athena.start_query_execution(
                    QueryString=query_string,
                    QueryExecutionContext={"Database": database_name},
                    ResultConfiguration={"OutputLocation": output_s3_uri},
                )
                query_execution_id = response["QueryExecutionId"]

                # Wait for query to complete
                while True:
                    status = athena.get_query_execution(QueryExecutionId=query_execution_id)["QueryExecution"]["Status"]["State"]
                    if status in ["SUCCEEDED", "FAILED", "CANCELLED"]:
                        break
                    time.sleep(2)

                if status == "SUCCEEDED":
                    result_response = athena.get_query_results(QueryExecutionId=query_execution_id)
                    count = int(result_response["ResultSet"]["Rows"][1]["Data"][0]["VarCharValue"])
                    results.append(["Athena Record Count", "✅", f"{count:,} rows"])
                else:
                    results.append(["Athena Record Count", "❌", f"Query failed with status: {status}"])

            except Exception as e:
                results.append(["Athena Record Count", "❌", str(e)])
    else:
        results.append(["Athena Record Count", "❌", "Missing DataCatalogConfig (table/database name)"])
        

# Output results
df = pd.DataFrame(results, columns=["Check", "Status", "Details"])
print(df.to_markdown(index=False))