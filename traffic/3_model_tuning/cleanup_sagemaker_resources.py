import os
import boto3
from dotenv import load_dotenv

# Load .env values
load_dotenv(dotenv_path="../.env")

region = os.getenv("AWS_REGION")
role = os.getenv("SAGEMAKER_ROLE")
bucket_name = os.getenv("S3_BUCKET")
prefix = os.getenv("S3_PREFIX")
endpoint_name = os.getenv("ENDPOINT_NAME")

# Initialize clients
sm_client = boto3.client("sagemaker", region_name=region)
s3 = boto3.resource("s3", region_name=region)

# Helper: Delete training jobs
def delete_training_jobs(job_names):
    for job_name in job_names:
        try:
            print(f"🗑 Deleting training job: {job_name}")
            sm_client.delete_training_job(TrainingJobName=job_name)
        except Exception as e:
            print(f"⚠️ Could not delete {job_name}: {e}")

# Helper: Delete models
def delete_models():
    models = sm_client.list_models()["Models"]
    for model in models:
        model_name = model["ModelName"]
        print(f"🗑 Deleting model: {model_name}")
        try:
            sm_client.delete_model(ModelName=model_name)
        except Exception as e:
            print(f"⚠️ Could not delete model {model_name}: {e}")

# Helper: Delete endpoint and config
def delete_endpoint_and_config(endpoint):
    try:
        print(f"🗑 Deleting endpoint: {endpoint}")
        sm_client.delete_endpoint(EndpointName=endpoint)
        sm_client.delete_endpoint_config(EndpointConfigName=endpoint)
        print(f"✅ Deleted endpoint and config: {endpoint}")
    except sm_client.exceptions.ClientError as e:
        print(f"⚠️ Could not delete endpoint/config: {e}")

# Helper: Clean up S3 output
def delete_s3_output(bucket, prefix):
    print(f"🧹 Deleting s3://{bucket}/{prefix}/output/")
    output_prefix = f"{prefix}/output/"
    deleted = s3.Bucket(bucket).objects.filter(Prefix=output_prefix)
    for obj in deleted:
        print(f"🗑 Deleting {obj.key}")
        obj.delete()

# Step 1: Delete all failed tuning jobs and their training jobs
tuning_jobs = sm_client.list_hyper_parameter_tuning_jobs(MaxResults=50)["HyperParameterTuningJobSummaries"]
for tuning in tuning_jobs:
    name = tuning["HyperParameterTuningJobName"]
    status = tuning["HyperParameterTuningJobStatus"]
    if status == "Failed":
        print(f"\n🗑 Tuning job: {name} (Status: {status})")

        # Get associated training jobs
        response = sm_client.list_training_jobs_for_hyper_parameter_tuning_job(
            HyperParameterTuningJobName=name
        )
        training_jobs = [t["TrainingJobName"] for t in response["TrainingJobSummaries"]]
        delete_training_jobs(training_jobs)

        # Delete tuning job
        try:
            sm_client.delete_hyper_parameter_tuning_job(HyperParameterTuningJobName=name)
            print(f"✅ Deleted tuning job: {name}")
        except Exception as e:
            print(f"⚠️ Could not delete tuning job {name}: {e}")

# Step 2: Delete orphaned models
delete_models()

# Step 3: Delete endpoint and config
delete_endpoint_and_config(endpoint_name)

# Step 4: Clean S3 output
delete_s3_output(bucket_name, prefix)
