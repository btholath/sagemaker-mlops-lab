# To create an IAM role for SageMaker, attach required policies, and allow the user course-boto to assume it, follow these steps:

# ✅ Step-by-Step: Create IAM Role via AWS CLI
- 🔹 Step 1: Create Trust Policy
- Save this JSON as trust-policy.json:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sagemaker.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

Then run:
```bash
aws iam create-role \
  --role-name SageMakerExecutionRole-TrafficML \
  --assume-role-policy-document file://trust-policy.json
```

- 🔹 Step 2: Attach Managed Policies to Role
```bash
aws iam attach-role-policy \
  --role-name SageMakerExecutionRole-TrafficML \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy \
  --role-name SageMakerExecutionRole-TrafficML \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name SageMakerExecutionRole-TrafficML \
  --policy-arn arn:aws:iam::aws:policy/AmazonAthenaFullAccess

aws iam attach-role-policy \
  --role-name SageMakerExecutionRole-TrafficML \
  --policy-arn arn:aws:iam::aws:policy/AWSGlueConsoleFullAccess
- 🔹 Step 3: Allow course-boto to Assume This Role (optional for CLI access)
If you want course-boto user to assume this role, create a policy like:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::637423309379:role/SageMakerExecutionRole-TrafficML"
    }
  ]
}
Save it as assume-sagemaker-role.json, then attach it:

```bash
aws iam put-user-policy \
  --user-name course-boto \
  --policy-name AssumeSageMakerRole \
  --policy-document file://assume-sagemaker-role.json

# ✅ Final Output
You can now use this IAM role ARN in .env:
SAGEMAKER_ROLE=arn:aws:iam::637423309379:role/SageMakerExecutionRole-TrafficML
