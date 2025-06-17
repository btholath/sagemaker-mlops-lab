import time
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


sagemaker = boto3.client("sagemaker", region_name=region)

def stop_and_delete_training_jobs(prefix=None):
    print("🔍 Listing SageMaker training jobs...")
    paginator = sagemaker.get_paginator("list_training_jobs")
    training_jobs = []

    for page in paginator.paginate():
        for job in page["TrainingJobSummaries"]:
            name = job["TrainingJobName"]
            if prefix and not name.startswith(prefix):
                continue
            training_jobs.append(job)

    for job in training_jobs:
        job_name = job["TrainingJobName"]
        status = job["TrainingJobStatus"]
        print(f"➡️ Processing training job: {job_name} (status: {status})")

        # Stop job if it's running
        if status in ["InProgress", "Stopping"]:
            print(f"⏹️ Stopping job: {job_name}")
            sagemaker.stop_training_job(TrainingJobName=job_name)
            # Wait for the job to stop
            while True:
                desc = sagemaker.describe_training_job(TrainingJobName=job_name)
                if desc["TrainingJobStatus"] in ["Stopped", "Failed", "Completed"]:
                    print(f"✅ Job {job_name} has stopped.")
                    break
                print(f"⏳ Waiting for job {job_name} to stop...")
                time.sleep(10)

        # Delete associated model (optional, assumes model name == job name)
        try:
            sagemaker.delete_model(ModelName=job_name)
            print(f"🗑️ Deleted model: {job_name}")
        except sagemaker.exceptions.ClientError as e:
            if "Could not find model" in str(e):
                print(f"⚠️ No model found for: {job_name}")
            else:
                print(f"❌ Error deleting model {job_name}: {e}")

        # Optionally: remove output artifacts from S3 if you track them

    print("✅ Cleanup completed for training jobs and associated models.")

# Run cleanup
stop_and_delete_training_jobs(prefix="sagemaker-xgboost")  # change/remove prefix as needed
