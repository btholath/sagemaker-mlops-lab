import boto3

# Constants
REGION = "us-east-1"
BUCKET_NAME = "sagemaker-traffic-prediction-bucket"
S3_OUTPUT_PREFIX = "traffic-pipeline/output/"
TRAINING_JOB_NAME_PREFIX = "sagemaker-xgboost"

# Boto3 clients/resources
sagemaker = boto3.client("sagemaker", region_name=REGION)
s3 = boto3.resource("s3")


# --- SageMaker Resource Cleanup Functions ---

def delete_all_training_jobs(name_prefix=None):
    print("🔍 Deleting SageMaker training jobs...")
    paginator = sagemaker.get_paginator("list_training_jobs")
    params = {
        "SortBy": "CreationTime",
        "SortOrder": "Descending"
    }
    if name_prefix:
        params["NameContains"] = name_prefix

    for page in paginator.paginate(**params):
        for job in page["TrainingJobSummaries"]:
            job_name = job["TrainingJobName"]
            status = job["TrainingJobStatus"]

            print(f"Processing: {job_name} [Status: {status}]")

            if status in ["InProgress", "Stopping"]:
                try:
                    print(f"🛑 Stopping training job: {job_name}")
                    sagemaker.stop_training_job(TrainingJobName=job_name)
                except Exception as e:
                    print(f"❌ Could not stop {job_name}: {e}")

            print(f"⚠️ Cannot directly delete training job '{job_name}'. Delete associated models, endpoints, and S3 artifacts manually if needed.")


def delete_models():
    print("🔍 Deleting SageMaker models...")
    try:
        response = sagemaker.list_models()
        for model in response["Models"]:
            name = model["ModelName"]
            print(f"🗑️ Deleting model: {name}")
            sagemaker.delete_model(ModelName=name)
    except Exception as e:
        print(f"⚠️ Error deleting models: {e}")


def delete_endpoints():
    print("🔍 Deleting SageMaker endpoints...")
    try:
        endpoints = sagemaker.list_endpoints()["Endpoints"]
        for ep in endpoints:
            name = ep["EndpointName"]
            print(f"🛑 Deleting endpoint: {name}")
            sagemaker.delete_endpoint(EndpointName=name)
    except Exception as e:
        print(f"⚠️ Error deleting endpoints: {e}")


def delete_endpoint_configs():
    print("🔍 Deleting SageMaker endpoint configurations...")
    try:
        configs = sagemaker.list_endpoint_configs()["EndpointConfigs"]
        for cfg in configs:
            name = cfg["EndpointConfigName"]
            print(f"🗑️ Deleting endpoint config: {name}")
            sagemaker.delete_endpoint_config(EndpointConfigName=name)
    except Exception as e:
        print(f"⚠️ Error deleting endpoint configs: {e}")


# --- S3 Cleanup Function ---

def delete_s3_output_artifacts():
    print(f"🔍 Deleting S3 artifacts from s3://{BUCKET_NAME}/{S3_OUTPUT_PREFIX}...")
    try:
        bucket = s3.Bucket(BUCKET_NAME)
        response = bucket.objects.filter(Prefix=S3_OUTPUT_PREFIX).delete()
        print("✅ Deleted S3 output artifacts.")
    except Exception as e:
        print(f"❌ Failed to delete S3 artifacts: {e}")


# --- Main Cleanup Flow ---

def main():
    delete_all_training_jobs(name_prefix=TRAINING_JOB_NAME_PREFIX)
    delete_endpoints()
    delete_endpoint_configs()
    delete_models()
    delete_s3_output_artifacts()


if __name__ == "__main__":
    main()
