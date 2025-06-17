# Step 1: Create the missing S3 bucket
Run this AWS CLI command (make sure AWS CLI is configured):
```bash
aws s3api create-bucket \
  --bucket sagemaker-traffic-prediction-bucket \
  --region us-east-1 \
  --create-bucket-configuration LocationConstraint=us-east-1
❗If you're in us-east-1, remove --create-bucket-configuration:

aws s3api create-bucket --bucket sagemaker-traffic-prediction-bucket --region us-east-1
```
# ✅ Step 2: Confirm Role Permissions
 - Ensure that the IAM role (SageMakerExecutionRole-TrafficML) has these permissions:
    - AmazonSageMakerFullAccess ✅
    - AmazonS3FullAccess or access to that bucket ✅
    - AmazonSageMakerFeatureStoreAccess ✅

To attach via CLI:
```bash
aws iam attach-role-policy \
  --role-name SageMakerExecutionRole-TrafficML \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFeatureStoreAccess
```
- ✅ Step 3: Retry the Python script
Once the bucket exists and permissions are correct:
```bash
cd traffic/1_data_preparation
python feature_store_ingest.py
```
