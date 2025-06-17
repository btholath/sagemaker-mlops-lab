import boto3
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

region = os.getenv("AWS_REGION")
feature_group_name = os.getenv("FEATURE_GROUP_NAME")

sagemaker = boto3.client("sagemaker", region_name=region)

try:
    response = sagemaker.delete_feature_group(FeatureGroupName=feature_group_name)
    print(f"✅ Deleted Feature Group: {feature_group_name}")
except Exception as e:
    print(f"❌ Failed to delete Feature Group: {e}")


bucket = os.getenv("S3_BUCKET")
prefix = os.getenv("S3_PREFIX")
s3 = boto3.resource("s3", region_name=region)

def delete_s3_prefix(bucket_name, prefix):
    bucket_obj = s3.Bucket(bucket_name)
    objects_to_delete = [{"Key": obj.key} for obj in bucket_obj.objects.filter(Prefix=prefix)]

    if not objects_to_delete:
        print(f"ℹ️ No objects found under: s3://{bucket_name}/{prefix}")
        return

    # S3 allows max 1000 objects per delete request
    for i in range(0, len(objects_to_delete), 1000):
        chunk = objects_to_delete[i:i + 1000]
        response = bucket_obj.delete_objects(Delete={"Objects": chunk})
        print(f"✅ Deleted {len(chunk)} objects under: s3://{bucket_name}/{prefix}")

# Usage
delete_s3_prefix(bucket, f"{prefix}/feature-store/")
delete_s3_prefix(bucket, f"{prefix}/train/")

# Delete model artifacts and training jobs
training_jobs = sagemaker.list_training_jobs(NameContains="sagemaker-xgboost")["TrainingJobSummaries"]

for job in training_jobs:
    job_name = job["TrainingJobName"]
    try:
        sagemaker.delete_training_job(TrainingJobName=job_name)
        print(f"✅ Deleted training job: {job_name}")
    except Exception as e:
        print(f"❌ Failed to delete training job {job_name}: {e}")

        