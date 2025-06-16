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

Option 1: Local development using Boto3 + SageMaker SDK:

# 1️⃣ traffic/1_data_preparation/feature_store_ingest.py
- Reads traffic_data.csv
- Converts timestamps
- Creates a Feature Group in SageMaker Feature Store
- Uploads data and waits for completion

# 2️⃣ traffic/2_model_training/xgb_train_from_featurestore.py
- Queries Feature Store using Athena
- Loads into a Pandas DataFrame
- Trains an XGBoost binary classification model
- Saves and uploads the training dataset
- Trains the model on SageMaker with ml.m5.large instance

