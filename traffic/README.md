# sagemaker-mlops-lab
A hands-on lab collection of small, real-world machine learning projects using Amazon SageMaker—covering data preparation, training, tuning, deployment, and model monitoring


# Initial setup
```bash
mkdir -p traffic/{1_data_preparation,2_model_training,3_model_tuning,4_model_deployment,5_model_monitoring,notebooks,flows} && \
touch traffic/README.md traffic/requirements.txt && \
touch traffic/1_data_preparation/{feature_store_ingest.py,traffic_data.csv} && \
touch traffic/2_model_training/{xgb_train_from_featurestore.py,train.csv,validation.csv} && \
touch traffic/3_model_tuning/{hyperparameter_tuning_job.py,config.yaml} && \
touch traffic/4_model_deployment/{deploy_model.py,predictor_test.py} && \
touch traffic/5_model_monitoring/{model_monitor_setup.py,baseline_constraints.json} && \
touch traffic/notebooks/{FeatureStore.ipynb,xgb-training.ipynb} && \
touch traffic/flows/FeatureStoreExport.flow
```

## 🔧 Project Modules

| Module | Description |
|--------|-------------|
| `1_data_preparation/` | Create feature groups and ingest datasets to SageMaker Feature Store |
| `2_model_training/`   | Train an XGBoost model using built-in algorithms and Feature Store queries |
| `3_model_tuning/`     | Run SageMaker hyperparameter tuning jobs for better model performance |
| `4_model_deployment/` | Deploy the model to a real-time endpoint and invoke it |
| `5_model_monitoring/` | Enable data capture, baseline monitoring, and drift detection |

---

# Option 1: Local development using Boto3 + SageMaker SDK:
- 📁 traffic/1_data_preparation/feature_store_ingest.py
    - ✅ Reads traffic_data.csv
    - ✅ Converts timestamp to ISO format
    - ✅ Creates a Feature Group in SageMaker
    - ✅ Uploads all records to the Feature Store

- 📁 traffic/2_model_training/xgb_train_from_featurestore.py
    - ✅ Queries the Feature Store via Athena
    - ✅ Loads and cleans data
    - ✅ Splits data for training
    - ✅ Trains XGBoost with ml.m5.large
    - ✅ Uploads training CSV to S3

- 📁 traffic/3_model_tuning/hyperparameter_tuning_job.py
    - ✅ Defines a tuning job using SageMaker’s HPO
    - ✅ Optimizes max_depth, eta, gamma, etc.
    - ✅ Metric: validation:auc
    - ✅ Launches max_jobs=10, parallel=2

- 📁 traffic/4_model_deployment/deploy_model.py
    - ✅ Loads model artifact from S3
    - ✅ Deploys as a real-time SageMaker endpoint

- 📁 traffic/4_model_deployment/predictor_test.py
    - ✅ Reads validation.csv
    - ✅ Sends sample rows for prediction
    - ✅ Prints predictions from the endpoint

- 📁 traffic/5_model_monitoring/model_monitor_setup.py
    - ✅ Enables data capture on deployed endpoint
    - ✅ Stores requests/responses in S3
    - ✅ Prepares for future baseline drift detection


# 📌 List of python packages:
- ✅ boto3: Required for AWS client access (e.g., S3, SageMaker Feature Store)
- ✅ sagemaker: AWS SageMaker Python SDK
- ✅ pandas: For CSV handling, dataframes, transformations
- ✅ scikit-learn: For train/test split and metrics
- ✅ xgboost: For model training using built-in or local mode
- ✅ python-dotenv: For loading .env configurations


# Setup python virtual environment
```bash
@btholath ➜ /workspaces/sagemaker-mlops-lab (main) $ python -m venv .venv
@btholath ➜ /workspaces/sagemaker-mlops-lab (main) $ source .venv/bin/activate
@btholath ➜ /workspaces/sagemaker-mlops-lab (main) $ pip install --upgrade pip
(.venv) @btholath ➜ /workspaces/sagemaker-mlops-lab (main) $ pip install -r ./traffic/requirements.txt
```

# cleanup aws resources
```bash
aws sagemaker delete-feature-group --feature-group-name traffic-feature-group-local
aws sagemaker list-feature-groups
```        

# Setup AWS CLI
```bash
(.venv) @btholath ➜ /workspaces
(.venv) @btholath ➜ /workspacescurl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
(.venv) @btholath ➜ /workspacesunzip awscliv2.zip
(.venv) @btholath ➜ /workspacessudo ./aws/install
or
(.venv) @btholath ➜ /workspaces./aws/install -i ~/.local/aws-cli -b ~/.local/bin
export PATH=$PATH:~/.local/bin
(.venv) @btholath ➜ /workspaces/usr/local/bin/aws --version 
(.venv) @btholath ➜ /workspaces $ aws configure
(.venv) @btholath ➜ /workspaces $ aws sts get-caller-identity
```

# Pre-requisites
- Global Setup (Before Any Script)
    - 1. Environment
    -   Python 3.8+ installed
    - Virtual environment activated (python -m venv .venv && source .venv/bin/activate)
      Required packages installed: pip install -r traffic/requirements.txt

- 2 .env File Present at traffic/.env
    AWS_REGION=us-west-2
    SAGEMAKER_ROLE=arn:aws:iam::<your-account>:role/<SageMakerExecutionRole>
    S3_BUCKET=sagemaker-traffic-prediction-bucket
    S3_PREFIX=traffic-pipeline
    FEATURE_GROUP_NAME=traffic-feature-group-local
    ENDPOINT_NAME=xgboost-traffic-local-endpoint

- 3. IAM Role Permissions (SAGEMAKER_ROLE)
    Make sure the IAM role has access to:
    AmazonS3FullAccess
    AmazonSageMakerFullAccess
    AthenaFullAccess
    GlueFullAccess (for Feature Store query)

#🚦 Script-wise Prerequisites
# 📁 1_data_preparation/feature_store_ingest.py
 - ✅ Before Running:
    - File traffic/1_data_preparation/traffic_data.csv must exist.
    - Ensure the FEATURE_GROUP_NAME doesn't already exist (or handle overwrite).
    - Feature Store + Athena + Glue permissions granted.

# 📁 2_model_training/xgb_train_from_featurestore.py
- ✅ Before Running:
    - feature_store_ingest.py has already run and populated the Feature Group.
    - Athena has permission to read query results.
    - .env variables are valid and consistent.

# 📁 3_model_tuning/hyperparameter_tuning_job.py
- ✅ Before Running:
    - xgb_train_from_featurestore.py has generated and uploaded train.csv to S3.
    - S3 path s3://$S3_BUCKET/$S3_PREFIX/train/train.csv exists.
    - IAM Role has SageMakerFullAccess.

# 📁 4_model_deployment/deploy_model.py
- ✅ Before Running:
    - xgb_train_from_featurestore.py or tuning job has produced a model artifact at:
    - s3://$S3_BUCKET/$S3_PREFIX/output/xgboost-traffic-local/output/model.tar.gz

# 📁 4_model_deployment/predictor_test.py
- ✅ Before Running:
    - Endpoint specified in ENDPOINT_NAME has been deployed and is InService.
    - File traffic/2_model_training/validation.csv exists and contains feature-aligned samples.

# 📁 5_model_monitoring/model_monitor_setup.py
- ✅ Before Running:
    - A live endpoint already exists.
    - You want to start logging inference data.
    - S3 destination in .env is ready for data capture.


# To delete all AWS resources created for your traffic prediction project, you need to clean up:
- ✅ SageMaker Feature Group
- ✅ S3 data artifacts
- ✅ SageMaker Model, Endpoint, Endpoint Configuration
- ✅ SageMaker Training Jobs, Tuning Jobs (optional cleanup)
- ✅ Athena query results (optional)

# 🧨 Option 1: AWS CLI Commands
# 🔥 Delete SageMaker Endpoint and Config
```bash
aws sagemaker delete-endpoint --endpoint-name xgboost-traffic-local-endpoint
aws sagemaker delete-endpoint-config --endpoint-config-name xgboost-traffic-local-endpoint
```

# 🔥 Delete SageMaker Model
```bash
aws sagemaker delete-model --model-name xgboost-traffic-local-endpoint
```
# 🔥 Delete SageMaker Feature Group
```bash
aws sagemaker delete-feature-group --feature-group-name traffic-feature-group-local
```
🕒 This may take time if the Feature Store is still ingesting data.

# 🔥 Delete S3 Bucket Contents
```bash
aws s3 rm s3://sagemaker-traffic-prediction-bucket/ --recursive
```
Replace with your actual bucket from .env.