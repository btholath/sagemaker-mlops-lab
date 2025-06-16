"""   
traffic/2_model_training/xgb_train_from_featurestore.py
Train XGBoost model from Feature Store data using SageMaker SDK locally.

1. Queries Feature Store using Athena
2. Loads into a Pandas DataFrame
3. Trains an XGBoost binary classification model
4. Saves and uploads the training dataset
5. Trains the model on SageMaker with ml.m5.large instance
"""

import boto3
import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup
from sagemaker.inputs import TrainingInput
from sagemaker.xgboost.estimator import XGBoost
import pandas as pd
from sklearn.model_selection import train_test_split

# Setup
session = sagemaker.Session()
role = sagemaker.get_execution_role()
bucket = session.default_bucket()
prefix = "xgboost-traffic-local"

# Connect to Feature Store
feature_group = FeatureGroup(name="traffic-feature-group-local", sagemaker_session=session)
query = feature_group.athena_query()
query_string = f'SELECT * FROM "{query.table_name}"'
query.run(query_string=query_string, output_location=f"s3://{bucket}/{prefix}/athena/")
query.wait()

# Load Data
df = query.as_dataframe()
df = df.dropna()
X = df.drop(columns=["incident"])
y = df["incident"]
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Save to CSV
train_data = pd.concat([y_train, X_train], axis=1)
train_data.to_csv("train.csv", index=False, header=False)
s3_train_path = session.upload_data("train.csv", bucket=bucket, key_prefix=f"{prefix}/train")

# Train Model
xgb = XGBoost(
    entry_point=None,
    framework_version="1.3-1",
    instance_type="ml.m5.large",
    instance_count=1,
    output_path=f"s3://{bucket}/{prefix}/output",
    role=role,
    objective="binary:logistic",
    num_round=100,
    sagemaker_session=session
)

xgb.fit({"train": TrainingInput(s3_train_path, content_type="csv")})
print("✅ Model training completed.")

# Write the files
for path, content in file_contents.items():
    with open(path, "w") as f:
        f.write(content)
