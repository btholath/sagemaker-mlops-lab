"""   
traffic/2_model_training/xgb_train_from_featurestore.py
Train XGBoost model from Feature Store data using SageMaker SDK locally.

1. Queries Feature Store using Athena
2. Loads into a Pandas DataFrame
3. Trains an XGBoost binary classification model
4. Saves and uploads the training dataset
5. Trains the model on SageMaker with ml.m5.large instance

- It reads that spreadsheet using a tool called Athena.
- Cleans up the data (removes empty rows).
- Splits the data into two parts: one for learning, and one to test how well it learned.
- Saves the training part as a file and uploads it to the cloud.
- Trains a smart traffic-prediction model using a technique called XGBoost.
- When it’s done, the trained model is stored in S3 for later use (like making predictions).
"""

import boto3
import sagemaker
from sagemaker.feature_store.feature_group import FeatureGroup
from sagemaker.inputs import TrainingInput
from sagemaker.xgboost.estimator import XGBoost
from sagemaker.estimator import Estimator
import pandas as pd
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="../.env")

region = os.getenv("AWS_REGION")
role = os.getenv("SAGEMAKER_ROLE")
bucket = os.getenv("S3_BUCKET")
prefix = os.getenv("S3_PREFIX")
feature_group_name = os.getenv("FEATURE_GROUP_NAME")

# Setup
session = sagemaker.Session()

# Connect to Feature Store (via Athena)
# Athena queries the parquet dataset automatically managed by SageMaker.
feature_group = FeatureGroup(name=feature_group_name, sagemaker_session=session)
query = feature_group.athena_query()
query_string = f'SELECT * FROM "{query.table_name}"'
print(query_string)
query.run(query_string=query_string, output_location=f"s3://{bucket}/{prefix}/athena/")
query.wait()

# Loads data into a Pandas DataFrame, Drops rows with missing values.
df = query.as_dataframe()
print(f"📊 Records retrieved from Feature Store: {len(df)}")

if df.empty:
    raise ValueError("❌ No data retrieved from Feature Store via Athena. Please verify the feature group and ingestion.")

print(f"🧾 Columns in dataframe: {df.columns.tolist()}")

# Row-wise deletion of any observation (record) containing NaN.
# Helps prevent training errors due to incomplete feature vectors.
df = df.dropna()

# This removes the incident column from the data table and keeps the rest. 
# The result — X — is the input data used to predict something.
# creates the feature matrix X by excluding the target variable (incident). 
# It contains independent variables used to train the model.
X = df.drop(columns=["incident"])

# This picks out just the incident column — the answer we want the model to learn to predict.
# Think of y as: “The actual incident outcome — yes or no.”
# This is the target vector y, which holds the dependent variable. 
# It's the label the model tries to predict based on the features in X.
y = df["incident"]

# Summary:
# X: All columns except "incident" → features
# y: Only the "incident" column → target

# You're dividing your data into two parts:
# Training Set: The part the model learns from.
# Validation Set: The part you use to test if the model learned well.
# train_test_split is a utility from Scikit-Learn used to split arrays or dataframes into random train and test subsets.
# X = feature matrix; y = target vector.
# test_size=0.2 means 20% of the data goes into the validation set, and 80% into the training set.
# random_state=42 ensures the split is reproducible. (Using the same seed always results in the same split.)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

#Output:
# Full Dataset (X, y)
# │
# ├── Training Set: 80% → X_train, y_train
# └── Validation Set: 20% → X_val, y_val
# X_train: features for training (Your feature matrix (predictor variables))
# X_val: features for validation
# y_train: target for training  (Your target variable (label).)
# y_val: target for validation

# Save to CSV
# Combines them column-wise into a single DataFrame where y_train is the first column and the features follow.
# This format (label, feature1, feature2, ..., featureN) is required for XGBoost’s built-in CSV training format.
train_data = pd.concat([y_train, X_train], axis=1)
train_data.to_csv("train.csv", index=False, header=False)
s3_train_path = session.upload_data("train.csv", bucket=bucket, key_prefix=f"{prefix}/train")

# Train Model
# trains a machine learning model using Amazon SageMaker and the XGBoost algorithm.
# Here's the CSV file I uploaded to S3. Use a smart algorithm called XGBoost to learn from it. Spin up a virtual machine (ml.m5.large) to do the work. Once done, save the model in this S3 bucket.
container_uri = sagemaker.image_uris.retrieve(
    framework="xgboost",
    region=region,
    version="1.3-1"
)
"""
xgb = XGBoost(
    entry_point=None,   # No custom script; use SageMaker's built-in XGBoost container
    framework_version="1.3-1",  # Specifies XGBoost version
    instance_type="ml.m5.large",  # EC2 instance type for training
    instance_count=1,  # Single instance for training
    output_path=f"s3://{bucket}/{prefix}/output",  # Where to save the trained model in S3
    role=role,  # IAM role with permissions for training and S3 access
    objective="binary:logistic",  # Objective for binary classification problems
    num_round=100,  # Number of boosting rounds (iterations)
    sagemaker_session=session  # SageMaker session context
)
"""
xgb = Estimator(
    image_uri=container_uri,
    role=role,
    instance_count=1,
    instance_type="ml.m5.large",
    output_path=f"s3://{bucket}/{prefix}/output",
    sagemaker_session=session,
    hyperparameters={
        "objective": "binary:logistic",
        "num_round": 100,
    }
)
# Starts the training job using the training data you uploaded (train.csv).
# SageMaker will:
#  Launch a training container
#  Feed the training data to XGBoost
#  Optimize the model weights
#  Save the final model to the output_path in S3
xgb.fit({"train": TrainingInput(s3_train_path, content_type="csv")})
print("✅ Model training completed.")